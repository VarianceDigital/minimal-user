import psycopg2
from .db import get_db
from psycopg2.extras import RealDictCursor
import os
from werkzeug.utils import secure_filename
import boto3, botocore

def gets3():
    return boto3.client(
        "s3",
        aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )
    
def delete_file_from_s3(awskey, bucket_name):
    s3 = gets3()
    #DELETE FROM GIVEN BUCKET
    s3.delete_object(Bucket=bucket_name, Key=awskey)


def write_tile_to_s3(filename, bucket_name, svgtext):
    s3 = gets3()
    #WRITE SVG AS FILE ON S3
    s3.put_object(Body=svgtext, Bucket=bucket_name, Key=filename, ContentType='image/svg+xml')
    