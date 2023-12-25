import os
import boto3
from botocore.exceptions import NoCredentialsError

def create_vpc():

    try:
        # Create VPC - Let's keep it simple
        ec2_resource = boto3.resource('ec2')
        vpc = ec2_resource.create_vpc(CidrBlock='10.5.0.0/16')

        # Let's do some waiting
        vpc.wait_until_available()

        # What shall we name you?
        vpc.create_tags(Tags=[{"Key": "Name", "Value": "i-am-a-cool-vpc"}])

        # Enable pub DNS
        ec2_client = boto3.client('ec2')
        ec2_client.modify_vpc_attribute(VpcId = vpc.id , EnableDnsSupport = {'Value': True})
        ec2_client.modify_vpc_attribute(VpcId = vpc.id , EnableDnsHostnames = {'Value': True})

        # Return id
        print("VPC ID: " + vpc.id)

    except NoCredentialsError:
        print("No credentials found")

if __name__ == "__main__":

    create_vpc()
