import os
import json
import argparse
import subprocess

from dotenv import load_dotenv
from delete_dbs import delete_database
from grant_perms import grant_permissions

# 環境変数のインポート
load_dotenv()
sql_user_name = os.environ['SQL_USER_NAME']

# podRepository のクローン
def clone_pod_repository(pod_repository_branch, pod_repository_url, pod_repository_local_path):
    cmd = f'git clone -b {pod_repository_branch} {pod_repository_url} {pod_repository_local_path}'
    subprocess.run(cmd, shell=True)

# sqlListRepository のクローン
def clone_sql_list_repository(sql_list_repository_branch, sql_list_repository_url, sql_list_repository_local_path):
    cmd = f'git clone -b {sql_list_repository_branch} {sql_list_repository_url} {sql_list_repository_local_path}'
    subprocess.run(cmd, shell=True)


# データベースの作成
def create_database(port, database_name):
    cmd = f'mysql --defaults-extra-file=./my.conf -P{port} -e "CREATE DATABASE IF NOT EXISTS {database_name} default character set utf8 ;"'
    subprocess.run(cmd, shell=True)

# テーブルの作成
def create_table(pod_name, port, database_name, sql_list_name, sql_files):
    index_array = []
    for sql_file_item in sql_files:
        index_number = sql_file_item['indexNumber']
        index_array.append(index_number)
    for i in range(1, len(index_array)+1):
        sql_file_name = sql_files[index_array.index(i)]['sqlFileName']
        if sql_file_name is None:
            print("Key 'sqlListName' is null.")
            continue
        cmd = f'mysql --defaults-extra-file=./my.conf -P{port} -D {database_name} < resources/pods/{pod_name}/databases/{database_name}/tables/{sql_list_name}/{sql_file_name}'
        subprocess.run(cmd, shell=True)


def main():
    parser = argparse.ArgumentParser(description='Clone mysql-kube repository and Setup databases and tables.')
    parser.add_argument('operation', help='select "clone", "grant", "create", or "delete"')
    parser.add_argument('-p', '--perms', action='store_true', help='if you run "create" with "--perms", it will create the dbs and tables after granting permissionss')
    args = parser.parse_args()

    with open('list.json') as f:
        pod_items = json.load(f)

    if args.operation == 'clone':
        try:
            for pod_item in pod_items:
                pod_name = pod_item['podName']
                if pod_name is None:
                    print("Key 'podName' is null.")
                    continue
                pod_repository_url = pod_item['podRepositoryUrl']
                pod_repository_branch = pod_item['branch']
                pod_repository_local_path = f'resources/pods/{pod_name}'
                if pod_repository_url is None or pod_repository_branch is None:
                    print("Key 'podRepositoryUrl' or 'branch' are null.")
                    continue
                # podRepository のクローン
                clone_pod_repository(pod_repository_branch, pod_repository_url, pod_repository_local_path)
                for database_item in pod_item['databases']:
                    database_name = database_item['databaseName']
                    if database_name is None:
                        print("Key 'databaseName' is null.")
                        continue
                    for sql_list_item in database_item['tables']:
                        sql_list_name = sql_list_item['sqlListName']
                        if sql_list_name is None:
                            print("Key 'sqlListName' is null.")
                            continue
                        sql_list_repository_url = sql_list_item['sqlListRepositoryUrl']
                        sql_list_repository_branch = sql_list_item['branch']
                        sql_list_repository_local_path = f'{pod_repository_local_path}/databases/{database_name}/tables/{sql_list_name}'
                        if sql_list_repository_url is None or sql_list_repository_branch is None:
                            print("Key 'sqlListRepositoryUrl' or 'branch' are null.")
                            continue
                        # sqlListReoisitory のクローン
                        clone_sql_list_repository(sql_list_repository_branch, sql_list_repository_url, sql_list_repository_local_path)
        except KeyError as e:
            print(f'Key {e} is undefined.')
    elif args.operation == 'grant':
        try:
            for pod_item in pod_items:
                pod_name = pod_item['podName']
                port = pod_item['port']
                if pod_name is None or port is None:
                    print("Key 'podName' or 'port' are null.")
                    continue
                if sql_user_name == "":
                    print("Env 'SQL_USER_NAME' are null.")
                    return
                # 権限の付与
                grant_permissions(port, sql_user_name)
        except KeyError as e:
            print(f'Key {e} is undefined.')
    elif args.operation == 'create':
        try:
            for pod_item in pod_items:
                pod_name = pod_item['podName']
                port = pod_item['port']
                if pod_name is None or port is None:
                    print("Key 'podName' or 'port' are null.")
                    continue
                if args.perms:
                    if sql_user_name == "":
                        print("Env 'SQL_USER_NAME' are null.")
                        return
                    # 権限の付与
                    grant_permissions(port, sql_user_name)
                for database_item in pod_item['databases']:
                    database_name = database_item['databaseName']
                    if database_name is None:
                        print("Key 'databaseName' is null.")
                        continue
                    # データベースの作成
                    create_database(port, database_name)
                    for sql_list_item in database_item['tables']:
                        sql_list_name = sql_list_item['sqlListName']
                        sql_files = sql_list_item['sqlFiles']
                        if sql_list_name is None or sql_files is None:
                            print("Key 'sqlListName' or 'sqlFiles' are null.")
                            continue
                        # テーブルの作成
                        create_table(pod_name, port, database_name, sql_list_name, sql_files)
        except KeyError as e:
            print(f'Key {e} is undefined.')
    elif args.operation == 'delete':
        try:
            for pod_item in pod_items:
                port = pod_item['port']
                if port is None:
                    print("Key 'port' is null.")
                    continue
                for database_item in pod_item['databases']:
                    database_name = database_item['databaseName']
                    if database_name is None:
                        print("Key 'databaseName' is null.")
                        continue
                    # データベースの削除
                    delete_database(port, database_name)
        except KeyError as e:
            print(f'Key {e} is undefined.')
    else:
        print('The argument is incorrect.')

if __name__ == "__main__":
    main()