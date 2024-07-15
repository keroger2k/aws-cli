import boto3

class Resource:
    # A class for creating boto3 "Resource" interfaces to AWS services

    def __init__(self, region, aws_key, aws_secret):
        # Resource instance
        self.region = region
        self.key_id = aws_key
        self.secret_key = aws_secret