import boto3
from botocore.exceptions import ClientError
import os

from dotenv import load_dotenv
load_dotenv(Path(__file__).parents[1] / '.s3')

# Defining bucket from environment variables
bucket = os.environ.get('BUCKET_NAME')
region_name=os.environ.get('REGION')
use_ssl=True
aws_access_key_id=os.environ.get('ACCESS_KEY_ID')
aws_secret_access_key=os.environ.get('ACCESS_KEY')

# Create S3 client
s3 = boto3.resource(
    's3',
    region_name=region_name,
    use_ssl=True,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
import pdb; pdb.set_trace()
