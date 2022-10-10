import connectorx as cx
import urllib.parse
from addict import Dict
import logging
import argparse
import yaml
import sys
from io import BytesIO
import boto3

logger = logging.getLogger("rdbms")
logger.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler(stream=sys.stderr)
log_handler.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
)
log_handler.setLevel(logging.INFO)
logger.addHandler(log_handler)

def create_parser():
    parser = argparse.ArgumentParser(description='retrieve oracle table to s3 file.')
    parser.add_argument("-p", "--property", dest="propertyfile",
                        help="Yaml property file for pipeline", metavar="PROP")
    return parser

def write_pandas_to_s3(s3_client, pd_df, bucket_name, folder_name, tablename, file_format):
    out_buffer = BytesIO()
    if file_format == 'csv':
        pd_df.to_csv(out_buffer, header=True, index=False)
        out_buffer.seek(0)
        s3_client.put_object(Bucket=bucket_name,
                             Body=out_buffer.getvalue(),
                             Key=f'{folder_name}/{tablename}/{tablename}.csv')
    else:  # default: parquet
        pd_df.to_parquet(out_buffer, index=False)
        out_buffer.seek(0)
        s3_client.put_object(Bucket=bucket_name,
                             Body=out_buffer.getvalue(),
                             Key=f'{folder_name}/{tablename}/{tablename}.parquet')

def main():
    parser = create_parser()
    args = parser.parse_args()
    propertyfile=args.propertyfile

    try:
        with open(propertyfile, "rb") as fin:
            config_bytes = fin.read()
        config = Dict(yaml.safe_load(config_bytes))
        file_format = config.s3.file_format

        conn = f"oracle://{urllib.parse.quote_plus(config.database.schema)}:{urllib.parse.quote_plus(config.database.password)}" \
                   f"@{urllib.parse.quote_plus(config.database.url)}:{config.database.port}/{config.database.service_name}"
        s3_client = boto3.client("s3",region_name=config.s3.region_name,
                                 aws_access_key_id=config.s3.access_key_id,
                                 aws_secret_access_key=config.s3.secret_access_key)

        for table in config.database.tables:
            logger.info(f'Start to retrieve data from table {table}')
            # start_time = time.time()
            query=f'SELECT * FROM {table}'
            df=cx.read_sql(conn, query)
            logger.info(f'End to retrieve data from table {table}')
            # print(f'Read_sql time for table {table}: {time.time() - start_time}')
            # start_time = time.time()
            logger.info(f'Start to transfer data to s3')
            write_pandas_to_s3(s3_client, df, config.s3.bucket_name, config.s3.folder_name, table, file_format)
            # print(f'Transfer to s3 time for table {table}: {time.time() - start_time}')
            logger.info(f'End to transfer data to s3')
    except IOError as e1:
        logger.error(f'Cannot not open property file {propertyfile}')
        logger.error(f'{e1.args}')
    except Exception as e:
        print(e)
        logger.error(f'{e.args}')

if __name__ == '__main__':
    main()
