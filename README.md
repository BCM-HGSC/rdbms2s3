# RDBMS To S3

## Current applications
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

- use rdbms2s3.yaml under resources as template.


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
