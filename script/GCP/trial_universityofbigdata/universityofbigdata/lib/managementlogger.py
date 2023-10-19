from django.utils import timezone, dateformat

from userlog.models import get_mlog_box


def get_now_time():
    return dateformat.format(timezone.localtime(timezone.now()), 'Y-m-d H:i:s ')

def set_management_log_box(message, ids):
    log_obj = get_mlog_box()
    log_text = log_obj.log_field
    now = get_now_time()
    message_dict={}
    message_dict['time'] = now
    message_dict['massage'] = message
    message_dict['ids'] = ids
    if(log_text is None):
        log_text = message
    else:
        log_text =  log_text + ', \n'+ str(message_dict)
    log_obj.log_field = log_text
    log_obj.save()

