import subprocess

# データベースの削除
def delete_database(port, database_name):
    cmd = f'mysql --defaults-extra-file=./my.conf -P{port} -e "DROP DATABASE {database_name};"'
    subprocess.run(cmd, shell=True)