# University of Big Data

**予測コンペティション型の多人数データ解析システムです。**

## 機能
- **予測コンペティションの開催**
  - Webアプリ上で予測コンペティションを開催します。
  - 参加者は訓練データを使ってモデルを作成し、テストデータに対する予測結果を投稿します。
  - 正解率等、コンペティションごとに決められた評価指標で競います。
- **チーム**
  - チームで協力して取り組むことができます。
- **議論ページ**
  - コンペティションごとに議題を作成し、議論を行うことができます。

## 要件
- [GCEのe2-micro](https://cloud.google.com/compute/vm-instance-pricing?hl=ja#e2_sharedcore_machine_types) 程度で動作します。
- WebアプリがDockerコンテナ上で動作するため、Docker Engineが使用できる環境が必要です。
- Googleアカウントで参加者登録 (ソーシャル認証)することを前提としているため、固定IPアドレスと(サブ)ドメイン名が必要です。
   - 本リポジトリのドキュメンテーションでは例として、GCEインスタンスで固定IPを取得し、DDNS Nowでサブドメイン名を取得します。

## 準備
### Linuxインスタンスの用意
Docker EngineがインストールされたLinuxインスタンスを用意してください。

[GCEのVMインスタンス操作例](doc/GCE.md)にDocker EngineがインストールされたGCEのVMインスタンスを用意する方法の一例を示しています。

### ファイアウォール設定
不正なアクセスを防ぐためには、必要に応じてファイアウォールを設定することが有効です。

GCEインスタンスを使用する場合、[ファイアウォール設定例](doc/firewall.md)を参考にしてください。

### ドメイン名取得
[Google OAuth2クライアント](#google-oauth2クライアント取得)または[Let's EncryptによるSSL接続](#lets-encryptによるtls-ssl証明書の発行)を使用する場合には(サブ)ドメイン名が必要になります。

サブドメイン名を取得する方法の一例として[ドメイン名取得](doc/get-domain-name.md)に説明があります。

### Google OAuth2クライアント取得
Googleアカウントによるユーザのログインを可能にするため、Google OAuth2クライアント設定が必要です。
[Google OAuth2クライアント設定](doc/oauth2.md)を参照してください。

## インスタンス操作手順
### ソースコードのダウンロード
本リポジトリのソースコードを次のように `git clone` でダウンロードします。

```
git clone https://github.com/UniversityOfBigData/UniversityOfBigData.git
```

以下、リポジトリのルートディレクトリ `UniversityOfBigData` で設定を行うものとします。
```
cd UniversityOfBigData
```

### 設定ファイルの作成
`.env-exaple` をコピーして `.env` という名前でテキストファイルを作成します。

```bash
cp .env-example .env
```

次のように内容を編集してください。

```
DJANGO_SECRET_KEY=<DJANGOのシークレットキー>
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=<Google OAuth2 のキー>
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=<Google OAuth2 のシークレットキー>
VERSION=latest
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.ac.jp
DJANGO_SUPERUSER_PASSWORD=admin
```

`=`右の値はクォーテーション `''` やダブルクォーテーション `""` で囲わないでください。

DJANGOのシークレットキーは適当な文字列を設定してください。
Google OAuth2 のキーおよびシークレットキーは[Google OAuth2クライアント設定](doc/oauth2.md)の手順で取得したものを使用してください。

初期状態で作成する管理者ユーザの各情報を次の変数で指定してください。
- `DJANGO_SUPERUSER_USERNAME`: 管理者ユーザ名
- `DJANGO_SUPERUSER_EMAIL`: 管理者のメールアドレス
- `DJANGO_SUPERUSER_PASSWORD`: 管理者のパスワード

### Dockerイメージの準備
必要なDockerイメージをダウンロード (pull)またはビルドします。

ダウンロード (pull)する場合、次のように実行します。

```bash
docker compose pull
```

Dockerイメージをビルドするには、次のように実行します。

```bash
docker compose build
```

### インスタンスの立ち上げ
ビルドしたイメージを使用し、Dockerコンテナによりインスタンスを立ち上げます。

```bash
docker compose up -d
```

立ち上げ後、 http://<LinuxインスタンスのIPアドレス> でアクセスできます。

### インスタンスの停止
インスタンスを停止および削除するには、次のように実行します。

```bash
docker compose down
```

### コマンドラインでの操作
起動しているコンテナでコマンドライン操作をする際には、次のようにコマンドを実行します。

```bash
docker exec -it <コンテナ名> bash
```

`<コンテナ名>` にはUniversityOfBigDataのWebサーバのコンテナ名 `universityofbigdata-django-1` を入力してください。

上記コマンドの実行により、コンテナ内のbashシェルを起動することができます。

## アプリの操作方法
[アプリの操作方法](doc/app-usage.md)を参照してください。

## 設定
### Djangoの設定
Dockerコンテナを停止した状態で、`universityofbigdata/settings/local.py`を編集し、Djangoサーバーの設定を変更することができます。
Djangoサーバーの設定については[公式のドキュメント](https://docs.djangoproject.com/ja/4.0/ref/settings/)を参照してください。

### データベースの変更
デフォルト設定ではSQLite3をデータベースとして使用します。

`universityofbigdata/settings/local.py` を編集し、変数 `DATABASES` を上書きすることでデータベースの設定を行うことができます。
例えばpostgresqlを使用する場合、次のような行を追加します。

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django',
        'USER': 'django',
        'PASSWORD': 'django',
        'HOST': 'db',
        'PORT': 5432,
    }
}
```

Docker Composeでデータベースを起動する場合は、`docker-compose.yml`の`services`下に例えば次のような行を追加します。

```yaml
  db:
    image: postgres:16.2
    restart: always
    volumes:
      - ./db:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD
      - POSTGRES_USER
      - POSTGRES_DB
```

この場合、postgresqlを`.env`で設定したパスワード `POSTGRES_PASSWORD`、ユーザ名 `POSTGRES_USER`、データベース名 `POSTGRES_DB`で初期化したpostgresのコンテナを起動します。

### Let's EncryptによるTLS (SSL)証明書の発行
Let's EncryptによるTLS (SSL)証明書の発行を行う (SSLによる通信を有効化する)場合の方法の一つとして、[https-portal](https://github.com/SteveLTN/https-portal) を使用する方法があります。

`docker-compose.yml` を編集し、`https-portal` のサービスを追加します。

```yaml
  # Let's EncryptによるTLS証明書を有効にする場合
  https-portal:
    image: steveltn/https-portal:1
    ports:
      - '80:80'
      - '443:443'
    links:
      - nginx
    restart: always
    environment:
      DOMAINS: '$DOMAIN -> http://nginx'
      STAGE: 'production' # Don't use production until staging works
      # FORCE_RENEW: 'true'
    volumes: 
      - https-portal-data:/var/lib/https-portal

volumes:
  https-portal-data:
```

インスタンスのドメイン名を `$DOMAIN` の箇所または`.env`で`DOMAIN` の値に設定してください。

次に、`nginx` の項目の `ports` の設定箇所をコメントアウトしてください。

```yaml
  nginx:
    image: nginx:1.24.0
    restart: always
    #ports:
    #  - "${PORT:-80}:80"  # Let's EncryptによるTLS証明書を有効にする場合はコメントアウト
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./uwsgi/uwsgi_params:/etc/nginx/uwsgi_params
      - ./data:/data
    depends_on:
      - django
```

Let's EncryptのACMEチャレンジを成功させるため、[ファイアウォール設定例](doc/firewall.md)のようなアクセス制限を行うファイアウォールを無効化する必要があります。[ファイアウォール設定例](doc/firewall.md)の設定の場合、default-allow-http と default-allow-https の設定を再度有効化することで、ACMEチャレンジを通すことができます (ただし、その場合アクセス制限が無効になります)。

以上のような設定を行った上で、docker compose によりインスタンスを稼動してください。

### 評価処理の拡張
[評価処理の拡張方法](doc/extend-eval.md)を参照してください。

## その他機能
### デモモード
インスタンスを立ち上げた状態で、コンテナ上で次のように管理コマンドを実行することで、デモ用のユーザを生成し、デモ用のコンペティションおよび議題を投稿する処理を起動します ([コマンドラインでの操作](#コマンドラインでの操作)の手順でコンテナ内のシェルを立ち上げてから実行します)。

```bash
python manage.py demo
```

このデモでユーザ名、コンペティション名、議題が `__demo__` で始まるものはデモにより上書き・削除されてしまうので注意してください。

次のようなコマンドラインオプションにより、デモモードで行動する一般ユーザ数 (デフォルト: 15)、スタッフ (TA)ユーザ数 (デフォルト: 2)、スーパーユーザ (管理者)数 (デフォルト: 1)を変更することができます。

```bash
python manage.py demo --num-users <一般ユーザ数> --num-staff-users <スタッフユーザ数> --num-super-users <スーパーユーザ数>
```

### サンプルコンペティションの作成
コンテナ上で次のようにコマンドラインからサンプルコンペティションを作成することができます ([コマンドラインでの操作](#コマンドラインでの操作)の手順でコンテナ内のシェルを立ち上げてから実行します)。

```bash
python manage.py launch_competition \
    --user-name <作成者ユーザ名> --dataset <データセット名> \
    --start-datetime <開始時刻> --end-datetime <終了時刻>
```

`<作成者ユーザ名>` はコンペティション作成権限のあるユーザの名前を指定してください。

`<データセット名>`は次の中から選択してください。

- `titanic`: Titanicデータセットでの分類問題 (テーブルデータ)
- `iris`: Iris Speciesデータセットでの分類問題 (テーブルデータ)
- `wine`: Wine Quality Dataでの2ラベル分類問題 (テーブルデータ)
- `auto-mpg`: Auto Miles per Gallon (MPG)データセットでの回帰問題 (テーブルデータ)
- `mnist`: MNISTデータセットでの画像分類問題 (画像データ)

`<開始時刻>` (デフォルト: `0m`、現時刻)と`<終了時刻>` (デフォルト: `10m`、10分後)はISO 8601形式での日時指定、もしくは[pytimeparse形式](https://pypi.org/project/pytimeparse/)で現在からの相対時刻で指定できます。

- ISO 8601形式の例:
   - `2024-01-26T10:33:00+09:00`
- pytimeparse形式の例:
   - `32m`
   - `2h32m`
   - `3d2h32m`
   - `1w3d2h32m`

## 謝辞
本プロジェクトの一部は、戦略的創造研究推進事業 CREST 「人とAIの協働ヒューマンコンピュテーション基盤」の支援を受けて実施されています。
