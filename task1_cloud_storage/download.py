
import os
import sys
import oss2
from oss2.exceptions import OssError

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 凭证改为运行时手动输入（增强安全性，不硬编码、不存文件、不依赖系统环境变量）
_credentials = {}

def get_credentials():
    """Prompt for OSS credentials once per run."""
    global _credentials
    if not _credentials:
        _credentials['id'] = input("Enter OSS Access Key ID: ").strip()
        _credentials['secret'] = input("Enter OSS Access Key Secret: ").strip()
    return _credentials['id'], _credentials['secret']

OSS_ENDPOINT = "oss-cn-beijing.aliyuncs.com"
OSS_BUCKET = "comp3041j-minigroupproject2-2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "download_data"))
DOWNLOAD_FILE_PATH = os.path.join(DOWNLOAD_DIR, "Comp3041J MiniProject 2 Dataset.csv")
CLOUD_OBJECT_NAME = "Comp3041J MiniProject 2 Dataset.csv"
SOURCE_FILE_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "Comp3041J MiniProject 2 Dataset.csv"))


def create_oss_bucket():
    access_id, access_secret = get_credentials()
    if not access_id or not access_secret:
        raise ValueError("Credentials not provided")
    return oss2.Bucket(oss2.Auth(access_id, access_secret), OSS_ENDPOINT, OSS_BUCKET)


def get_samples(path, n=2):
    with open(path, 'r', encoding='utf-8') as f:
        f.readline()
        return [f.readline().strip() for _ in range(n)]


def download_file():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    bucket = create_oss_bucket()
    bucket.get_object_to_file(CLOUD_OBJECT_NAME, DOWNLOAD_FILE_PATH)
    print(f"Downloaded: oss://{OSS_BUCKET}/{CLOUD_OBJECT_NAME} -> {DOWNLOAD_FILE_PATH}")
    return DOWNLOAD_FILE_PATH


def verify_download():
    source_size = os.path.getsize(SOURCE_FILE_PATH)
    downloaded_size = os.path.getsize(DOWNLOAD_FILE_PATH)
    source_samples = get_samples(SOURCE_FILE_PATH)
    downloaded_samples = get_samples(DOWNLOAD_FILE_PATH)

    print(f"Platform: Local Machine / Windows, Cloud: Alibaba Cloud OSS, Region: cn-beijing, Bucket: {OSS_BUCKET}")
    print(f"Size Check: source={source_size} downloaded={downloaded_size} {'PASS' if source_size == downloaded_size else 'FAIL'}")
    print(f"Sample Check 1: {'PASS' if source_samples[0] == downloaded_samples[0] else 'FAIL'}")
    print(f"Sample Check 2: {'PASS' if source_samples[1] == downloaded_samples[1] else 'FAIL'}")

    all_pass = source_size == downloaded_size and source_samples[0] == downloaded_samples[0] and source_samples[1] == downloaded_samples[1]

    if all_pass:
        print("Verification: PASSED - Task 1 complete. Data available at download_data/ for Task 2 (MapReduce) and Task 3 (Ray)")
    else:
        print("Verification: FAILED")

    return all_pass


if __name__ == "__main__":
    download_file()
    if not verify_download():
        sys.exit(1)