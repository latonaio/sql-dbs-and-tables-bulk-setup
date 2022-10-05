# sql-dbs-and-tables-bulk-setup

sql-dbs-and-tables-bulk-setup は 指定したホストとポートのSQL に指定したデータベースおよびテーブルの作成、削除をまとめて処理するマイクロサービスです。


## 動作環境
- Python

## 動作手順
### ライブラリのインストール
仮想環境を作成し、必要なライブラリをインストールします。
```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

### 環境変数、jsonファイルの設定
`my.conf` を作成し、SQL のユーザー、ユーザーパスワード、ホストを設定します。

`my-root.conf` を作成し、SQL のルートユーザー、ルートユーザーパスワード、ホストを設定します。

`.env` を作成し、SQL のユーザーを設定します。

`list.json` にポート番号、データベース名、sqlファイル名、テーブル名等を設定します。

### リポジトリのクローン
#### SQL を立ち上げ得るリポジトリとsqlファイルを含むリポジトリを使用する場合
以下のコマンドで、Kubernetes 上でSQL のPod を立ち上げるリポジトリとSQL のテーブルを作成を行うリポジトリのクローンをします。
```
python setup_sql.py clone
```

- Kubernetes 上でSQL のPod を立ち上げるリポジトリの例
  - [data-platfrom-authenticator-mysql-kube](https://github.com/latonaio/data-platform-authenticator-mysql-kube)

- SQL のテーブルを作成を行うリポジトリの例
  - [data-platform-authenticator-sql](https://github.com/latonaio/data-platform-authenticator-sql)

#### sqlファイルを手動で配置する場合
以下のフォルダ構成を`[podName]`、`[databaseName]`、`[sqlListName]` および`[sqlFileName]` は`list.json` と同じ名前を指定して作成します。

また、`list.json` の`port`、`tableName` および`indexNumber` も設定します。

`indexNumber` はテーブルを作成する順番を示します。

`list.json` の残りのキーは空白でも問題ないです。
```
resources
└── pods
    ├──[podName]
    │   └── databases
    │       └── [databaseName]
    │           └── tables
    │               └── [sqlListName]
    │                   └── [sqlFileName]
    └──[podName]
        └── ...
```

### データベースとテーブルの作成
#### ユーザーにデータベースとテーブルの作成権限がある場合
以下のコマンドで、指定したデータベースとテーブルを作成します。
```
python setup_sql.py create
```

#### ユーザーにデータベースとテーブルの作成権限がない場合
以下のコマンドで、指定したユーザーに権限の付与をしてから、指定したデータベースとテーブルを作成します。
```
python setup_sql.py create --perms
```

### 権限の付与
以下のコマンドで、指定したユーザーに権限を付与します。
```
python setup_sql.py grant
```

### データベースとテーブルの削除
以下のコマンドで、指定したデータベースとテーブルを削除します。
```
python setup_sql.py delete
```