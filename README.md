# RDBMS To S3

rdbms2s3 is a ETL tool which imports data from related database to AWS S3 bucket as CSV/parquet. Currently it can handle oracle and MySQl database.

##How It Works
rdbms2s3 contains a few CLI tools for each different database types. User can use a config yaml file to specify database and s3 informations.
Two tools are currently created for Oracle and MySQL database.
- oracle_2_s3
- mysql_2_s3


## How To Install

1. Create a virtual python environment.
Ex: With Conda
```
conda create -n [name-of-environment]
conda activate [name-of-environment]
conda install pip
```

2. cd into where the setup.py of rdbms2s3 is at and inall
```
cd /to/where/this/is/at/rdbms2s3
pip install .
```

## Create a Config File

rdbms2s3 currently only support yaml config file.

- rdbms2s3.yaml.
```
# database info
database:
  type: oracle   # oracle/mysql
  url: ****************
  schema: *******
  password: ********
  tables:
    - table1
    - table2
    - view1

# s3 setting
s3:
  region_name: *****
  bucket_name: ***s3-bucket**
  folder_name: ******
  access_key_id: ******
  secret_access_key: *************************

# only use for oracle database
oracle:
  instant_client: /path/to/instantclient
```


## How To Run

- [oracle_2_s3](#oracle_2_s3)
- [mysql_2_s3](#mysql_2_s3)


### oracle_2_s3

1. Install the oracle instant client (Save the location in config file)
2. Create config file. (Use `rdbms2s3.yaml` from resources for reference).
3. To run the application:
`oracle_2_s3 -p /path/to/config/file`

### mysql_2_s3

1. Create config file. (Use `rdbms2s3.yaml` from resources for reference).
2. To run the application:
`mysql_2_s3 -p /path/to/config/file`
