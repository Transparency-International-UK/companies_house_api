#!/usr/bin/python3

# in Dockerfile we set the WORKDIR to /companies_house_api.
# If you don't run in Docker make sure your working (root) directory is companies_house_api/
file_name = "pg_constants.py"

# absolute path to the database config file
DB_CONFIG_ABS_PATH = __file__.rstrip(file_name) + "database.ini"

# print(DB_CONFIG_ABS_PATH)

# section in the database config file with params to connect locally.
DB_CONFIG_SECTION = "PostgreSQL"

# name of the schema to be created/connected to.
# if you want to default to public leave None. Empty string will throw error.
DB_SCHEMA = None

if __name__ == "__main__":
	print(DB_CONFIG_ABS_PATH)
