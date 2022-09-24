import boto3
from botocore.exceptions import ClientError
import os
import pathlib
import glob


class S3:
    def __init__(
            self,
            aws_access_key_id=None,
            aws_secret_access_key=None,
            region_name=None,
            endpoint=None):
        """
        Create S3 Connector (with en vars of params)

        Parameters
        ----------
        aws_access_key_id : str, optional
            access key, by default None
        aws_secret_access_key : str, optional
            secret key, by default None
        region_name : str, optional
            region, by default None
        endpoint : str, optional
            endpoint, by default None
        """
        self.bucket = None if os.getenv(
            'BUCKET_NAME') is None else os.getenv('BUCKET_NAME')
        self.region_name = region_name if os.getenv(
            'REGION') is None else os.getenv('REGION')
        self.endpoint = endpoint if os.getenv(
            'ENDPOINT') is None else os.getenv('ENDPOINT')
        aws_access_key_id = aws_access_key_id if os.getenv(
            'ACCESS_KEY_ID') is None else os.getenv('ACCESS_KEY_ID')
        aws_secret_access_key = aws_secret_access_key if os.getenv(
            'ACCESS_KEY') is None else os.getenv('ACCESS_KEY')

        self.client = boto3.client(
            's3',
            region_name=region_name,
            endpoint_url=endpoint,
            use_ssl=True,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def set_bucket(self, bucket_name):
        self.bucket_name = bucket_name

    @staticmethod
    def _check_type(path, recursive=False):
        """
        Check type of path: one file, dir or list of files
        """
        if not isinstance(path, (list, str)):
            return None
        elif isinstance(path, list):
            return path
        elif isinstance(path, str):
            if os.path.isdir(path):
                if recursive:
                    return [f for f in glob.glob('f{path}/**/*', recursive=True) if pathlib.Path(f).is_file()]
                else:
                    return [os.path.join(path, i) for i in os.listdir(path) if pathlib.Path(i).is_file()]
            return [path]

    def upload(self, objet, recursive=False):
        filename = self._check_type(objet, recursive=recursive)
        for f in filename:
            self.client.upload_file(Bucket=self.bucket,  Key=f,  Filename=f)
