#!/usr/bin/env python3
import os
import sys
import requests
import logging
import boto3
import pprint
import threading
import socket
from requests.auth import HTTPBasicAuth
from botocore.exceptions import ClientError
from time import sleep


class cattleman(object):
    def __init__(self):
        self.api_user = os.getenv('RANCHER_USER')
        self.api_key = os.getenv('RANCHER_KEY')
        self.api_url = os.getenv('RANCHER_URL')
        self.asg_name = os.getenv('ASG_NAME')
        if not self.api_user or not self.api_key or not self.api_url or not self.asg_name:
            logger.error("RANCHER_USER, RANCHER_KEY, RANCHER_URL and ASG_NAME are required env vars")
            sys.exit(1)
        self.api_project = self.get_project(os.getenv('RANCHER_ENV', 'Default'))

    def get_project(self, rancher_env):
        projects = requests.get('{0}/v1/projects'.format(self.api_url),
                                auth=HTTPBasicAuth(self.api_user, self.api_key))

        for project in projects.json()['data']:
            if rancher_env == project['name']:
                return project['id']
            else:
                logger.error("Specificed rancher environment or 'Default' does not exist")

    def test_connection(self):
        logger.info("Connecting to the Rancher API...")
        connection = requests.get('{0}/v1/'.format(self.api_url),
                                  auth=HTTPBasicAuth(self.api_user, self.api_key))
        if connection.status_code == 200:
            logger.info("Connected to the Rancher API")
        else:
            logger.error(connection.json())

    def get_all_memory_info(self):
        memory = {}
        hosts = requests.get('{0}/v1/projects/{1}/hosts/'.format(self.api_url,
                                                                 self.api_project),
                             auth=HTTPBasicAuth(self.api_user, self.api_key))
        for host in hosts.json()['data']:
            memory[host['id']] = host['info']['memoryInfo']
        return memory

    def decider(self):
        memory = self.get_all_memory_info()
        logger.debug("Memory Dict:\n" + pprint.pformat(memory))
        hosts = len(memory.keys())
        low_mem = []
        for host, mem in memory.items():
            if mem['memAvailable'] / mem['memTotal'] <= 0.35:
                low_mem.append(host)
        if len(low_mem) == hosts:
            logger.info("Trigger Scale Up")
            self.scale_up()
        else:
            logger.info("Doing nothing..")

    def scale_up(self):
        client = boto3.client('autoscaling')
        current_capacity = client.describe_auto_scaling_groups(AutoScalingGroupNames=[self.asg_name])['AutoScalingGroups'][0]['DesiredCapacity']
        desired_capacity = current_capacity + 1
        try:
            response = client.set_desired_capacity(
                          AutoScalingGroupName=self.asg_name,
                          DesiredCapacity=desired_capacity,
                          HonorCooldown=True)
        except ClientError as e:
            logger.error("Cooldown in effect, no action taken")


def ping(delay, run_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', 1313)
    logger.debug('starting up on {0}'.format(server_address))
    sock.bind(server_address)
    sock.listen(1)

    while run_event.is_set():
        logger.debug('waiting for a connection')
        connection, client_address = sock.accept()
        try:
            logger.debug('client connected: {0}'.format(client_address))
            message = b'PONG'
            connection.sendall(message)
            connection.close()
        finally:
            connection.close()


def run_cattleman(delay, run_event):
    app = cattleman()
    app.test_connection()
    while run_event.is_set():
        app.decider()
        logger.info('Sleeping 1 minute')
        sleep(60)

if __name__ == "__main__":
    # setup_logging
    logger = logging.getLogger('Cattleman')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    logger.debug('Logging Started')

    run_event = threading.Event()
    run_event.set()

    jobs = []

    main_thread = threading.Thread(target=run_cattleman, args=(1, run_event))
    jobs.append(main_thread)

    status_thread = threading.Thread(target=ping, args=(1, run_event))
    jobs.append(status_thread)

    try:
        for job in jobs:
            job.start()
    except (KeyboardInterrupt, SystemExit):
        run_event.clear()
        for job in jobs:
            job.join()
