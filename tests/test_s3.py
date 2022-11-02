from s3 import S3

s3 = S3()

def test_bucket_exists():
    bucket_name = 'webgl-lp'
    print(bucket_name)
    assert s3.check_bucket(bucket_name)
