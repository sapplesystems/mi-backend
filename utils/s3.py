import os
import boto3
import pathlib
import logging

s3 = boto3.client('s3')


def ensure_directory_path_for_file(filepath):
    mpath = pathlib.Path(filepath)
    parent_directory = mpath.parent
    parent_directory.mkdir(parents=True, exist_ok=True)


def upload_file(filepath, bucket_name, s3_bucket_path,delete=True):
    with open(filepath, "rb") as f:
        logging.info(f"uploading {filepath} to {s3_bucket_path}")
        s3.upload_fileobj(f, bucket_name, s3_bucket_path)
    if delete:
        os.remove(filepath)


def upload_file_stream(f, bucket_name, s3_bucket_path):
    logging.info(f"uploading file to {s3_bucket_path}")
    s3.upload_fileobj(f, bucket_name, s3_bucket_path, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/svg+xml'})


def upload_doc_stream(f, bucket_name, s3_bucket_path):
    logging.info(f"uploading file to {s3_bucket_path}")
    s3.upload_fileobj(f, bucket_name, s3_bucket_path)
