# cattleman
Python application for additional orchestration work on top of Rancher

When executing the following are required environment variables to be passed to the container or set before running the script locally. 
```
RANCHER_URL Url of your rancher endpoint for cattleman to hit the api)
RANCHER_USER username/public_name of rancher api key
RANCHER_KEY password/secret key of rancher api key
ASG_NAME Name of your autoscaling group in the AWS console
AWS_ACCESS_KEY_ID AWS Access Key
AWS_SECRET_ACCESS_KEY AWS Secret Key
AWS_DEFAULT_REGION Default AWS region
```
