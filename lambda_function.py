import os
import io
import boto3
import json

# grab environment variables
global region
region = 'us-east-2'

ENDPOINT_NAME = "fraude-application"
runtime= boto3.client('runtime.sagemaker')

def check_status(app_name):
    sage_client = boto3.client('sagemaker', region_name=region)
    endpoint_description = sage_client.describe_endpoint(EndpointName=app_name)
    endpoint_status = endpoint_description['EndpointStatus']
    return endpoint_status
    
def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    data = json.loads(json.dumps(event))
    payload = data['data']
    print("payload:")
    print(payload)
    print("json.dumps(payload):")
    print(json.dumps(payload))
    print('Application status is {}'.format(check_status(ENDPOINT_NAME)))
    
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                       Body=json.dumps(payload),
                                       ContentType = 'application/json; format=pandas-split')
    print(response)
    result = json.loads(response['Body'].read().decode())
    print(result)
    
    return result[0]
