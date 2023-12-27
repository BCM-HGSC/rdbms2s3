# -*- coding:utf-8 -*-
# Created by liwenw at 12/15/23

import os
import sys
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.getcwd())

import json
from io import BytesIO
import boto3
from botocore.exceptions import ClientError
import sqlalchemy
import pandas as pd
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

tables = ['hgsccl_tracking_metrics', 'hgsccl_sample_tracking', 'hgsccl_sample_tracking_metric',  'hgsccl_sample_tracking_view']
bucket_name = os.environ.get('BUCKET_NAME')
folder_name = os.environ.get('FOLDER_NAME')
database = os.environ.get('MYSQL_DB')


def get_secret():
    region_name = os.environ.get('REGION')
    secret_name = os.environ.get('SECRET_NAME')

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return secret


def retrieve_data(user, password, url, table_name):
    conn_str = f'mysql+pymysql://{user}:{password}@{url}'
    conn = sqlalchemy.create_engine(conn_str)
    sql_str = f"SELECT * FROM {database}.{table_name};"
    logger.info(sql_str)
    ref = pd.read_sql_query(sql_str, con=conn, chunksize=100000)
    df_list = [i for i in ref]
    return df_list


def write_pandas_parquet_to_s3(pd_df, tablename, bucket_name, folder_name, count):
    out_buffer = BytesIO()
    pd_df.to_parquet(out_buffer, index=False)
    out_buffer.seek(0)
    client = boto3.client('s3')
    client.put_object(Bucket=bucket_name,
                  Body=out_buffer.getvalue(),
                  Key=f'{folder_name}/{tablename.upper()}/{tablename.upper()}_{count}.parquet')

def lambda_handler(event, context):
    logger.info('event: {}'.format(event))
    try:
        secret = get_secret()
        secret_dict = json.loads(secret)

        for table_name in tables:
            logger.info(f'Start to retrieve data from table {table_name}')
            pd_df_list = retrieve_data(
                user=secret_dict['username'],
                password=secret_dict['password'],
                url=secret_dict['host'],
                table_name=table_name)
            logger.info(f'Finish retrieving data from table {table_name}')
            logger.info(f'Start to send data from table {table_name} to s3')
            count=0
            for pd_df in pd_df_list:
                write_pandas_parquet_to_s3(pd_df, table_name, bucket_name, folder_name, count)
                count = count + 1
            logger.info(f'Completed table {table_name}')
        logger.info('completed ...')
    except Exception as e:
        logger.error(e)
        logger.error(f'Error getting data from RDS {str(e)}')
