import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.getcwd())

import logging
import argparse

import cx_Oracle
import yaml
from addict import Dict

from utils import oracle
from utils import s3_client

logger = logging.getLogger("covid-19")
logger.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler(stream=sys.stderr)
log_handler.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
)
log_handler.setLevel(logging.INFO)
logger.addHandler(log_handler)

def main():
    parser = create_parser()
    args = parser.parse_args()
    propertyfile=args.propertyfile

    try:
        with open(propertyfile, "rb") as fin:
            config_bytes = fin.read()
        config = Dict(yaml.safe_load(config_bytes))
        file_format = config.s3.file_format
        logger.info('Initialize oracle client')
        cx_Oracle.init_oracle_client(lib_dir=config.oracle.instant_client)
        for table in config.database.tables:
            logger.info(f'Start to transfer data from table {table}')
            retriever = oracle.oracle_retriever(config, table)
            df = retriever.retrieve_data()
            client = s3_client.s3_client(config)
            if file_format == 'csv':
                client.write_pandas_csv_to_s3(df, table)
            else: # default: parquet
                client.write_pandas_parquet_to_s3(df, table)
            logger.info(f'End to transfer data from table {table}')
    except IOError as e1:
        logger.error(f'Cannot not open property file {propertyfile}')
        logger.error(f'{e1.args}')
    except Exception as e:
        logger.error(f'{e.args}')


def create_parser():
    parser = argparse.ArgumentParser(description='Parse the cvd json file.')
    parser.add_argument("-p", "--property", dest="propertyfile",
                        help="Yaml property file for pipeline", metavar="PROP")
    return parser

if __name__ == '__main__':
    main()


