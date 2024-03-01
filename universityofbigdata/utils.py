from json_log_formatter import JSONFormatter, _json_serializable
from logging import LogRecord, getLogger
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import json
from django.conf import settings


def get_ip_address(request):
    # 'HTTP_X_FORWARDED_FOR'ヘッダから転送経路のIPアドレスを取得
    forwarded_addresses = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_addresses and (len(forwarded_addresses.split(',')) > 1):
        # 'HTTP_X_FORWARDED_FOR'ヘッダがある場合は転送経路の先頭要素を取得
        client_ip = forwarded_addresses.split(',')[0]
        # 'HTTP_X_FORWARDED_FOR'ヘッダがある場合は転送経路の二番目を取得
        client_WAN_ip = forwarded_addresses.split(',')[1]
    else:
        # 'HTTP_X_FORWARDED_FOR'ヘッダがない場合は'REMOTE_ADDR'ヘッダを参照
        client_ip = request.META.get('REMOTE_ADDR')
        client_WAN_ip = client_ip
    return client_ip, client_WAN_ip


def get_user_info(request):
    # ユーザー名
    if(request.user.is_authenticated):
        user_name = request.user.username
        user_id = request.user.id
        team_name = request.user.selectedTeam.name if request.user.selectedTeam else 'unknown'
        team_id = request.user.selectedTeam.id if request.user.selectedTeam else 0
    else:
        user_name = 'anonymous'
        user_id = 0
        team_name = 'unknown'
        team_id = 0
    return user_name, user_id, team_name, team_id


class CustomJSONFormatter(JSONFormatter):
    def json_record(self, message: str, extra: dict, record: LogRecord) -> dict:
        extra['message'] = message
        request = extra.pop('request', None)

        if request:
            extra['ip'], extra['wan_ip'] = get_ip_address(request)
            extra['user_name'], extra['user_id'], \
                extra['team_name'], extra['team_id'] = get_user_info(request)

        # Include builtins
        extra['level'] = record.levelname
        extra['name'] = record.name

        if 'time' not in extra:
            extra['time'] = timezone.now()

        if record.exc_info:
            extra['exc_info'] = self.formatException(record.exc_info)

        return extra

    def to_json(self, record):
        """Converts record dict to a JSON string.

        日本語が記録できるように `ensure_ascii=False` を追記したもの.

        """
        try:
            return self.json_lib.dumps(
                    record, default=_json_serializable, ensure_ascii=False)
        # ujson doesn't support default argument and raises TypeError.
        # "ValueError: Circular reference detected" is raised
        # when there is a reference to object inside the object itself.
        except (TypeError, ValueError, OverflowError):
            try:
                return self.json_lib.dumps(record, ensure_ascii=False)
            except (TypeError, ValueError, OverflowError):
                return '{}'



def access_recorded(logger, page_name, page_display_name):
    """ページレンダラに付けて、ログを記録する."""
    def decorator(view_func):
        def func_with_logging(request, *args, **kwargs):
            logger.info(
                f"{page_display_name} {_('にアクセス')}",
                extra={
                    'request': request,
                    'action': {
                        'name': 'access_page',
                        'page_name': page_name,
                        },
                    })
            return view_func(request, *args, **kwargs)
        return func_with_logging
    return decorator


def get_log_reader():
    for suffix in [''] + [f'.{i+1}' for i in range(settings.LOG_BACKUP_COUNT)]:
        with open(settings.LOG_FILE, 'r') as f:
            for line in f:
                yield json.loads(line)
