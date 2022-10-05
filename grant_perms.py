import subprocess

# 権限の付与
def grant_permissions(port, user_name):
    cmd = f'mysql --defaults-extra-file=./my-root.conf -P{port} -e "GRANT ALL ON *.* TO {user_name}@;"'
    subprocess.run(cmd, shell=True)