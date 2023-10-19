# University of Big Data

**予測コンペティション型の多人数データ解析システムです。**

## 機能
- **予測コンペティションの開催**
  - Webアプリ上で予測コンペティションを開催します。
  - 参加者は訓練データを使ってモデルを作成、テストデータに対する予測結果を投稿します。
  - 正解率等、コンペティションごとに決められた評価指標で競います。
- **チーム**
  - 参加者はチームを作成し、協力して取り組むことができます。
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
不正なアクセスを防ぐため、適切な設定でのファイアウォールの使用を推奨します。

GCEインスタンスを使用する場合、[ファイアウォール設定例](doc/firewall.md)を参考にしてください。

### ドメイン名取得
[ドメイン名取得](doc/get-domain-name.md)を参照してください。
Google OAuth2クライアントを使用する場合にはドメイン名が必要になります。

### Google OAuth2クライアント取得
[Google OAuth2クライアント設定](doc/oauth2.md)を参照してください。

### ソースコードのダウンロード
本リポジトリのソースコードを次のように `git clone` でダウンロードします。
```
git clone https://github.com/UniversityOfBigData/UniversityOfBigData.git
```

以下、リポジトリのルートディレクトリ `UniversityOfBigData` で設定を行うものとします。
```
cd UniversityOfBigData
```

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

## インスタンス操作手順
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
```

`=`右の値はクォーテーション `''` やダブルクォーテーション `""` で囲わないでください。

DJANGOのシークレットキーは適当な文字列を設定してください。
Google OAuth2 のキーおよびシークレットキーは[Google OAuth2クライアント設定](doc/oauth2.md)の手順で取得したものを使用してください。

### 初回起動時の設定
初回起動時前に、次のコマンドを実行し、初回起動時に必要な設定を行います。

`bash initialize.sh` を実行すると次のように表示されます:

```
$ bash initialize.sh
patching file competitions/urls.py
Running database migrations...
Migrations for 'accounts':
  accounts/migrations/0001_initial.py
    - Create model TeamTag
    - Create model User
No changes detected in app 'authentication'
...(中略)...
ユーザー名:
```

ここで、管理者ユーザ名を入力してください。
続けて、メールアドレス、パスワード、パスワード (再入力)の順で確認されるので、入力してください。

```
ユーザー名: admin
Gmail address: admin
Error: 有効なメールアドレスを入力してください。
Gmail address: admin@example.com
Password:
Password (again):
このパスワードは ユーザー名 と似すぎています。
このパスワードは短すぎます。最低 8 文字以上必要です。
このパスワードは一般的すぎます。
Bypass password validation and create user anyway? [y/N]: y
INFO 2023-09-26 15:56:30,636 models make useradmin a
Superuser created successfully.
```

上記のように、パスワードによっては短すぎる等の警告が出ますので、修正する場合はエンターまたは`N`、無視する場合は`y`を入力してください。

初期設定後のデータベースは `data/db.sqlite3` に保存されます。

初期設定を中断した場合は、`data/db.sqlite3` を削除または移動してから再度 `bash initialize.sh` を実行してください。
ただし、運用中の `data/db.sqlite3` を消すとデータベースが消えてしまうので注意してください。

### インスタンスの立ち上げ
ビルドしたイメージを使用し、Dockerコンテナによりインスタンスを立ち上げます。
```
docker compose up -d
```

立ち上げ後、 http://<LinuxインスタンスのIPアドレス> でアクセスできます。

### インスタンスの停止
インスタンスを停止および削除するには、次のように実行します。
```
docker compose down
```

## アプリの操作方法
[アプリの操作方法](doc/app-usage.md)を参照してください。

## 謝辞
本プロジェクトの一部は、戦略的創造研究推進事業 CREST 「人とAIの協働ヒューマンコンピュテーション基盤」の支援を受けて実施されています。
