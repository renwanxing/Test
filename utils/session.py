#coding: utf-8
import base64
import cPickle as pickle
import simplejson as json
import logging
from . import com_db

from django.contrib.auth.models import User, AnonymousUser


def get_session_data(session_key):
    sql = "select session_data from django_session where session_key='%s'" % session_key
    row = com_db.SelectOneSql(sql, db='slave')
    return row[0] if row else ''


def decode_123(encoded_data):
    "1.2.3版的session解析方式"
    pickled = encoded_data[:-32]
    return pickle.loads(pickled)


def decode_187(encoded_data):
    "1.8.7版解析方式"
    hash, serialized = encoded_data.split(b':', 1)
    return json.loads(serialized)


def decode(session_data):
    "兼容的解析方式"
    if not session_data:
        return {}
    s = base64.b64decode(session_data)
    try:
        result = decode_187(s)
    except Exception, e:
        logging.info("the session data is: " + s + ":SSSjiema")
        result = decode_123(s)
    return result
    # if s.find(':') >= 0:
    #     print "eee",decode_187(s)
    #     return decode_187(s)
    # return decode_123(s)


def get_user_id(request):
    """
    功能说明：从cookie中取user_id, 兼容新老两种session
    失败返回0
    ----------------------------------------------------------------------------
    修改人                修改时间                修改原因
    ----------------------------------------------------------------------------
    王晨光                2015-5-22
    """
    session_id = request.COOKIES.get('sessionid', '')
    if not session_id:
        return 0
    session_data = get_session_data(session_id)
    if not session_data:
        return 0
    o = decode(session_data)
    return o.get('_auth_user_id')


def get_user(request):
    """
    功能说明：取得当前session用户
    失败返回AnonymousUser
    ----------------------------------------------------------------------------
    修改人                修改时间                修改原因
    ----------------------------------------------------------------------------
    王晨光                2015-5-22
    """
    user_id = get_user_id(request)
    user = None
    if user_id:
        user = User.objects.filter(pk=user_id).first()
    return user or AnonymousUser()
