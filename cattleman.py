#!/usr/bin/env python3
import os
import sys
import requests
from requests.auth import HTTPBasicAuth


class cattleman(object):
    def __init__(self):
        self.api_user = os.getenv('RANCHER_USER')
        self.api_key = os.getenv('RANCHER_KEY')
        self.api_url = os.getenv('RANCHER_URL')
        if not self.api_user or not self.api_key or not self.api_url:
            print("Please set RANCHER_USER, RANCHER_KEY and RANCHER_URL Environment Variables")
            sys.exit(1)

    def test_connection(self):
        print("Connecting to the Rancher API...")
        connection = requests.get('{0}/v1/'.format(self.api_url),
                                  auth=HTTPBasicAuth(self.api_user, self.api_key))
        if connection.status_code == 200:
            print("Connected to the Rancher API")
        else:
            print(connection.json())

if __name__ == "__main__":
    app = cattleman()
    app.test_connection()
