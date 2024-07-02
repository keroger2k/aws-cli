import boto3

class Resource:
    # A class for creating boto3 "Resource" interfaces to AWS services

    def __init__(self, region, aws_key, aws_secret):
        # Resource instance
        self.region = region
        self.key_id = aws_key
        self.secret_key = aws_secret

    def ec2_role_client(self, role):
        # Create and return a Resource for interacting with EC2 instances
        sts_client = boto3.client('sts')

        assumed_role_object=sts_client.assume_role(
            RoleArn=role,
            RoleSessionName="AssumeRoleSession1"
        )

        credentials=assumed_role_object['Credentials']

        session=boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
        )

        return session.client("ec2", region_name="us-gov-west-1")


    def ec2_client(self):
        # Create and return a Client for interacting with EC2
        ec2 = boto3.client("ec2", aws_access_key_id=self.key_id,
                           aws_secret_access_key=self.secret_key,
                           region_name=self.region)
        return ec2