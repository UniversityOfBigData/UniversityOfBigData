FROM python:3.9.10-slim-bullseye

RUN mkdir -p /opt/universityofbigdata
WORKDIR /opt/universityofbigdata
COPY script/GCP/requirements.txt /opt/universityofbigdata/

# 必要なパッケージのインストール
RUN pip install -r requirements.txt
RUN pip install pyuwsgi  # TODO: requirements.txtに含める
RUN apt-get update \
      && apt-get install -y patch gettext

# デバッグ用
RUN pip install IPython
# テスト用
RUN pip install lxml cssselect parametrize

# ファイルをコピー
COPY script/GCP/trial_universityofbigdata /opt/universityofbigdata
COPY entrypoint.sh /opt/universityofbigdata/entrypoint.sh

# 翻訳ファイルのコンパイル
RUN python manage.py compilemessages

ENTRYPOINT ["bash", "./entrypoint.sh"]
