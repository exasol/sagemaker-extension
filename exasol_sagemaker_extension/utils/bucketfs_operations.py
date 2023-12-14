#########################################################
# To be migrated to the script-languages-container-tool #
#########################################################
from pathlib import PurePosixPath, Path

from exasol_bucketfs_utils_python.bucket_config import BucketConfig
from exasol_bucketfs_utils_python.bucketfs_config import BucketFSConfig
from exasol_bucketfs_utils_python.bucketfs_connection_config import \
    BucketFSConnectionConfig
from exasol_bucketfs_utils_python.bucketfs_location import BucketFSLocation


def create_bucketfs_location(
        bucketfs_name: str, bucketfs_host: str, bucketfs_port: int,
        bucketfs_use_https: bool, bucketfs_user: str, bucketfs_password: str,
        bucket: str, path_in_bucket: str) -> BucketFSLocation:
    _bucketfs_connection = BucketFSConnectionConfig(
        host=bucketfs_host, port=bucketfs_port, user=bucketfs_user,
        pwd=bucketfs_password, is_https=bucketfs_use_https)
    _bucketfs_config = BucketFSConfig(
        bucketfs_name=bucketfs_name, connection_config=_bucketfs_connection)
    _bucket_config = BucketConfig(
        bucket_name=bucket, bucketfs_config=_bucketfs_config)
    return BucketFSLocation(
        bucket_config=_bucket_config,
        base_path=PurePosixPath(path_in_bucket))
