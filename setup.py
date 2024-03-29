from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))
# Load the version
with open(path.join(HERE, "version.py")) as version_file:
    exec(version_file.read())

REQUIREMENTS = [
    "addict",
    "boto3",
    "pandas",
    "pyyaml",
    'pyarrow',
    'sqlalchemy',
    'cx_Oracle',
    'pymysql',
    'connectorx',
]

setup(
    name='rdbms2s3',
    version=__version__,
    description="This application imports data from RDBMS to AWS S3 bucket as CSV/parquet.",
    author="Liwen Wang",
    author_email="liwenw@bcm.edu",
    packages = find_packages(),
    python_requires="~=3.7",
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "oracle_2_s3=src.oracle_2_s3:main",
            "mysql_2_s3=src.mysql_2_s3:main",
        ],
    },
)

