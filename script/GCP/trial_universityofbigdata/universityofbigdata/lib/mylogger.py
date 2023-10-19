from django.utils import timezone, dateformat

from userlog.models import get_log_box

def get_ip_address(request):
    # 'HTTP_X_FORWARDED_FOR'ヘッダから転送経路のIPアドレスを取得
    forwarded_addresses = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_addresses:
        # 'HTTP_X_FORWARDED_FOR'ヘッダがある場合は転送経路の先頭要素を取得
        client_ip = forwarded_addresses.split(',')[0]
        # 'HTTP_X_FORWARDED_FOR'ヘッダがある場合は転送経路の二番目を取得
        client_WAN_ip = forwarded_addresses.split(',')[1]
    else:
        # 'HTTP_X_FORWARDED_FOR'ヘッダがない場合は'REMOTE_ADDR'ヘッダを参照
        client_ip = request.META.get('REMOTE_ADDR')
        client_WAN_ip = client_ip
    return client_ip, client_WAN_ip

def get_user_name(request):
    # ユーザー名
    if(request.user.is_authenticated):
        username = request.user.username
    else:
        username = 'anonymous'
    return username

def get_team_name(request):
    if(request.user.is_authenticated):
        username = request.user.username
        team_name = request.user.selectedTeam.name if request.user.selectedTeam else 'unknown_team'
    else:
        username = 'anonymous'
        team_name = '0'
    return team_name

def get_now_time():
    return dateformat.format(timezone.localtime(timezone.now()), 'Y-m-d H:i:s ')

def set_log_box(message):
    log_obj = get_log_box()
    log_text = log_obj.log_field
    if(log_text is None):
        log_text = message
    else:
        log_text =  log_text + ', \n'+ message
    log_obj.log_field = log_text
    log_obj.save()

def set_log_box_lite(message_part, request):
    # ユーザー名
    username = get_user_name(request)
    # チーム名
    team_name = get_team_name(request)
    # アクセス者のIPアドレス取得
    client_ip, client_WAN_ip = get_ip_address(request)
    # ID
    if(request.user.is_authenticated):
        Team_id = request.user.selectedTeam.id if request.user.selectedTeam else 0
        User_id = request.user.id
    else:
        Team_id = 0
        User_id = 0

    # メッセージ作成
    mess_dict ={}
    mess_dict['time']=get_now_time()
    mess_dict['Team']=team_name
    mess_dict['Team_id']=Team_id
    mess_dict['User']=username
    mess_dict['User_id']=User_id
    mess_dict['message']=message_part
    mess_dict['from']=client_ip
    message = str(mess_dict)

    # メッセージセット
    set_log_box(message)
    return message

