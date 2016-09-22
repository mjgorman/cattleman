#!/usr/bin/env python3
import os
import sys
import requests
import logging
from requests.auth import HTTPBasicAuth


class cattleman(object):
    def __init__(self):
        self.api_user = os.getenv('RANCHER_USER')
        self.api_key = os.getenv('RANCHER_KEY')
        self.api_url = os.getenv('RANCHER_URL')
        if not self.api_user or not self.api_key or not self.api_url:
            logger.error("RANCHER_USER, RANCHER_KEY and RANCHER_URL are required env vars")
            sys.exit(1)
        self.api_project = self.get_project(os.getenv('RANCHER_ENV', 'Default'))

    def get_project(self, rancher_env):
        projects = requests.get('{0}/v1/projects'.format(self.api_url),
                                auth=HTTPBasicAuth(self.api_user, self.api_key))

        for project in projects.json()['data']:
            if rancher_env == project['name']:
                return project['id']
            else:
                logger.error("Specificed rancher environment or 'Default' environment does not exist")

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
    app = cattleman()
    app.test_connection()
