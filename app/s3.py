import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parents[1] / '.env')

# Defining bucket from environment variables
bucket = os.getenv('BUCKET_NAME')
region_name = os.getenv('REGION')
use_ssl = True
aws_access_key_id = os.getenv('ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('ACCESS_KEY')

# Create S3 client
s3 = boto3.resource(
    's3',
    region_name=region_name,
    use_ssl=True,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
import pdb; pdb.set_trace()
