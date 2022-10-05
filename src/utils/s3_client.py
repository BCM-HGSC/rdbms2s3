import os
from io import StringIO
from io import BytesIO
import boto3
from boto3.s3.transfer import TransferConfig

class s3_client(object):
    def __init__(self, config):
        os.environ['aws_access_key_id'] = config.s3.access_key_id
        os.environ['aws_secret_access_key'] = config.s3.secret_access_key
        os.environ['region_name'] = config.s3.region_name

        self.region_name = config.s3.region_name
        self.aws_access_key_id = config.s3.access_key_id
        self.aws_secret_access_key = config.s3.secret_access_key
        self.bucket_name = config.s3.bucket_name
        self.folder_name = config.s3.folder_name
        self.s3_client = boto3.client("s3",
                          region_name=config.s3.region_name,
                          aws_access_key_id=config.s3.access_key_id,
                          aws_secret_access_key=config.s3.secret_access_key)

    def write_pandas_parquet_to_s3(self, pd_df, tablename):
        out_buffer = BytesIO()
        pd_df.to_parquet(out_buffer, index=False)
        out_buffer.seek(0)
        self.s3_client.put_object(Bucket=self.bucket_name,
                                  Body=out_buffer.getvalue(),
                                  Key=f'{self.folder_name}/{tablename}/{tablename}.parquet')

    def write_pandas_csv_to_s3(self, pd_df, tablename):
        out_buffer = StringIO()
        pd_df.to_csv(out_buffer, header=True, index=False)
        out_buffer.seek(0)
        self.s3_client.put_object(Bucket=self.bucket_name,
                             Body=out_buffer.getvalue(),
                             Key=f'{self.folder_name}/{tablename}/{tablename}.csv')

    def write_file_to_s3(self, filename):
        config = TransferConfig(multipart_threshold=1024*25, max_concurrency=10,
                            multipart_chunksize=1024*25, use_threads=True)
        self.s3_client.upload_file(filename, Bucket=self.bucket_name, Config = config)