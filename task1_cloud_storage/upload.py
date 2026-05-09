# -*- coding: utf-8 -*-
# Author: dalele2002 dagujie@126.com
# Date: 2026-05-07 22:38:11
# FilePath: \Comp3041J-MiniProject2\task1_cloud_storage\upload.py
# Description: Task 1 Cloud Object Storage Upload - Alibaba Cloud OSS

import os
import sys
import tempfile
import oss2
from oss2.exceptions import OssError

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OSS_ACCESS_KEY_ID = os.environ.get("OSS_ACCESS_KEY_ID")
OSS_ACCESS_KEY_SECRET = os.environ.get("OSS_ACCESS_KEY_SECRET")
OSS_ENDPOINT = "oss-cn-beijing.aliyuncs.com"
OSS_BUCKET = "comp3041j-minigroupproject2-2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_FILE_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "Comp3041J MiniProject 2 Dataset.csv"))
CLOUD_OBJECT_NAME = "Comp3041J MiniProject 2 Dataset.csv"

RUNTIME_ENV = {
    "platform": "Local Machine / Windows",
    "cloud_provider": "Alibaba Cloud OSS",
    "region": "cn-beijing",
    "endpoint": OSS_ENDPOINT,
    "bucket": OSS_BUCKET,
}


def create_oss_bucket():
    if not OSS_ACCESS_KEY_ID or not OSS_ACCESS_KEY_SECRET:
        raise ValueError("Environment variables not set")
    return oss2.Bucket(oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET), OSS_ENDPOINT, OSS_BUCKET)


def get_samples(path, n=2):
    with open(path, 'r', encoding='utf-8') as f:
        f.readline()
        return [f.readline().strip() for _ in range(n)]


def upload_file():
    if not os.path.exists(LOCAL_FILE_PATH):
        raise FileNotFoundError(f"Local file not found: {LOCAL_FILE_PATH}")
    bucket = create_oss_bucket()
    bucket.put_object_from_file(CLOUD_OBJECT_NAME, LOCAL_FILE_PATH)
    print(f"Uploaded: {LOCAL_FILE_PATH} -> oss://{OSS_BUCKET}/{CLOUD_OBJECT_NAME}")
    return True


def verify_upload():
    bucket = create_oss_bucket()
    if not bucket.object_exists(CLOUD_OBJECT_NAME):
        print("File does not exist in OSS")
        return False

    cloud_size = bucket.head_object(CLOUD_OBJECT_NAME).content_length
    local_size = os.path.getsize(LOCAL_FILE_PATH)
    local_samples = get_samples(LOCAL_FILE_PATH)

    temp = os.path.join(tempfile.gettempdir(), "cloud_verify.csv")
    bucket.get_object_to_file(CLOUD_OBJECT_NAME, temp)
    cloud_samples = get_samples(temp)
    os.remove(temp)

    print(f"Platform: {RUNTIME_ENV['platform']}, Cloud: {RUNTIME_ENV['cloud_provider']}, Region: {RUNTIME_ENV['region']}, Bucket: {RUNTIME_ENV['bucket']}")
    print(f"Size Check: local={local_size} cloud={cloud_size} {'PASS' if local_size == cloud_size else 'FAIL'}")
    print(f"Sample Check 1: {'PASS' if local_samples[0] == cloud_samples[0] else 'FAIL'}")
    print(f"Sample Check 2: {'PASS' if local_samples[1] == cloud_samples[1] else 'FAIL'}")

    all_pass = local_size == cloud_size and local_samples[0] == cloud_samples[0] and local_samples[1] == cloud_samples[1]
    print(f"Verification: {'PASSED - Data stored in cloud object storage' if all_pass else 'FAILED'}")
    return all_pass


if __name__ == "__main__":
    upload_file()
    if not verify_upload():
        sys.exit(1)