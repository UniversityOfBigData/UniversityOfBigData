FROM python:3.9.10-slim-bullseye

RUN mkdir -p /opt/universityofbigdata
WORKDIR /opt/universityofbigdata

# 必要なパッケージのインストール
COPY requirements.txt /opt/universityofbigdata/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update \
      && apt-get install -y patch gettext git

# 修正したdjango-log-viewerをインストール
WORKDIR /opt
RUN git clone https://github.com/agusmakmun/django-log-viewer.git
WORKDIR /opt/django-log-viewer
RUN git reset --hard 723cf807132eea75b894331489297fca906aa44e
RUN git clean -df
COPY docker/patches/django-log-viewer.patch /tmp/django-log-viewer.patch
RUN patch -p1 < /tmp/django-log-viewer.patch && rm -f /tmp/django-log-viewer.patch
RUN pip install .
WORKDIR /opt/universityofbigdata

# ファイルをコピー
COPY universityofbigdata /opt/universityofbigdata/universityofbigdata
COPY apps /opt/universityofbigdata/apps
COPY locale /opt/universityofbigdata/locale
COPY static /opt/universityofbigdata/static
COPY templates /opt/universityofbigdata/templates
COPY manage.py /opt/universityofbigdata/manage.py
COPY entrypoint.sh /opt/universityofbigdata/entrypoint.sh

# 翻訳ファイルのコンパイル
RUN mkdir -p /opt/universityofbigdata/data/log/apps
RUN python manage.py compilemessages

ENTRYPOINT ["bash", "./entrypoint.sh"]
