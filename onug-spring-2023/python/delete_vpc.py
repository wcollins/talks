import os
import argparse
import boto3
from botocore.exceptions import NoCredentialsError

def delete_vpc(vpc_id):

    try:
        # Create session
        ec2_resource = boto3.resource('ec2')

        # Call VPC using id
        vpc = ec2_resource.Vpc(vpc_id)

        # Delete all associated resources first
        for subnet in vpc.subnets.all():
            subnet.delete()

        for route_table in vpc.route_tables.all():
            if not route_table.associations:
                route_table.delete()

        for sg in vpc.security_groups.all():
            if sg.group_name != 'default':
                sg.delete()

        for network_acl in vpc.network_acls.all():
            if not network_acl.is_default:
                network_acl.delete()

        # Delete VPC
        vpc.delete()

        # Was I successful?
        print(f"VPC {vpc_id} has been deleted")

    except NoCredentialsError:
        print("No credentials found")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Delete a VPC')
    parser.add_argument('vpc_id', help='The ID of the VPC to delete')

    args = parser.parse_args()

    delete_vpc(args.vpc_id)