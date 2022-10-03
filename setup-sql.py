import os
import sys
import json
import subprocess
from dotenv import load_dotenv
load_dotenv()

# リポジトリのクローン
def clone(df):
  for pod_item in df:
    # podRepositoryのクローン
    pod_name = pod_item['podName']
    pod_repository_url = pod_item['podRepositoryUrl']
    pod_repository_branch = pod_item['branch']
    pod_repository_local_path = f'resources/pods/{pod_name}'
    cmd = f'git clone -b {pod_repository_branch} {pod_repository_url} {pod_repository_local_path}'
    subprocess.run(cmd, shell=True)

    for database_item in pod_item['databases']:
      database_name = database_item['databaseName']
      for sql_list_item in database_item['tables']:
        # sqlListRepositoryUrlのクローン
        sql_list_name = sql_list_item['sqlListName']
        sql_list_repository_url = sql_list_item['sqlListRepositoryUrl']
        sql_list_repository_branch = sql_list_item['branch']
        sql_list_repository_local_path = f'{pod_repository_local_path}/databases/{database_name}/tables/{sql_list_name}'
        cmd = f'git clone -b {sql_list_repository_branch} {sql_list_repository_url} {sql_list_repository_local_path}'
        subprocess.run(cmd, shell=True)

# データベースの作成
def create_database(df):
  sql_root_name = os.environ['SQL_ROOT_NAME']
  sql_root_password = os.environ['SQL_ROOT_PASSWORD']
  sql_host = os.environ['SQL_HOST']
  for pod_item in df:
    sql_port = pod_item['port']
    for database_item in pod_item['databases']:
      database_name = database_item['databaseName']
      cmd = f'mysql -u{sql_root_name} -p{sql_root_password} -h{sql_host} -P{sql_port} -e "CREATE DATABASE IF NOT EXISTS {database_name} default character set utf8 ;"'
      subprocess.run(cmd, shell=True)

# テーブルの作成
def create_table(df):
  sql_root_name = os.environ['SQL_ROOT_NAME']
  sql_root_password = os.environ['SQL_ROOT_PASSWORD']
  sql_host = os.environ['SQL_HOST']
  for pod_item in df:
    pod_name = pod_item['podName']
    sql_port = pod_item['port']
    for database_item in pod_item['databases']:
      database_name = database_item['databaseName']
      for sql_list_item in database_item['tables']:
        sql_list_name = sql_list_item['sqlListName']
        index_array = []
        for sql_file_item in sql_list_item['sqlFiles']:
          index_number = sql_file_item['indexNumber']
          index_array.append(index_number)
        for i in range(1, len(index_array)+1):
          sql_file_name = sql_list_item['sqlFiles'][index_array.index(i)]['sqlFileName']
          cmd = f'mysql -u{sql_root_name} -p{sql_root_password} -h{sql_host} -P{sql_port} -D {database_name} < resources/pods/{pod_name}/databases/{database_name}/tables/{sql_list_name}/{sql_file_name}'
          subprocess.run(cmd, shell=True)

# データベースの削除
def delete_database(df):
  sql_root_name = os.environ['SQL_ROOT_NAME']
  sql_root_password = os.environ['SQL_ROOT_PASSWORD']
  sql_host = os.environ['SQL_HOST']
  for pod_item in df:
    sql_port = pod_item['port']
    for database_item in pod_item['databases']:
      database_name = database_item['databaseName']
      cmd = f'mysql -u{sql_root_name} -p{sql_root_password} -h{sql_host} -P{sql_port} -e "DROP DATABASE {database_name};"'
      subprocess.run(cmd, shell=True)

# テーブルの削除
def delete_table(df):
  sql_root_name = os.environ['SQL_ROOT_NAME']
  sql_root_password = os.environ['SQL_ROOT_PASSWORD']
  sql_host = os.environ['SQL_HOST']
  for pod_item in df:
    sql_port = pod_item['port']
    for database_item in pod_item['databases']:
      database_name = database_item['databaseName']
      for sql_list_item in database_item['tables']:
        for sql_file_item in sql_list_item['sqlFiles']:
          table_name = sql_file_item['tableName']
          cmd = f'mysql -u{sql_root_name} -p{sql_root_password} -h{sql_host} -P{sql_port}-e "DROP TABLE {database_name}.{table_name};"'
          subprocess.run(cmd, shell=True)

def main():
  args = sys.argv
  with open('list.json') as f:
    df = json.load(f)
  if args[1] == 'clone':
    clone(df)
  if args[1] == 'create':
    create_database(df)
    create_table(df)
  if args[1] == 'delete':
    delete_database(df)
    delete_table(df)

if __name__ == "__main__":
  main()