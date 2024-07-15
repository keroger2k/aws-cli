import boto3

class AWSClient:

    DEFAULT_REGION = 'us-gov-west-1'

    def __init__(self, resource):
         self.resource = resource
 
    def get_user_client(self):
        # Create and return a Client for interacting with EC2
        ec2 = boto3.client("ec2", aws_access_key_id=self.key_id,
                           aws_secret_access_key=self.secret_key,
                           region_name=self.region)
        return ec2

    def get_role_client(self, role):
            
            sts_client = boto3.client('sts')

            assumed_role_object=sts_client.assume_role(
                RoleArn=role,
                RoleSessionName="AssumeRoleSession"
            )

            credentials=assumed_role_object['Credentials']

            session=boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
            )

            return session.client("ec2", region_name=self.DEFAULT_REGION)