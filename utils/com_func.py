#coding=utf-8
import datetime
import time
import logging, traceback
from functools import wraps

from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from django.conf import settings

from libs.utils.common import render_template
from libs.utils import ajax

log = logging.getLogger(__name__)

#                            _ooOoo_
#                           o8888888o
#                           88" . "88
#                           (| -_- |)
#                            O\ = /O
#                        ____/`---'\____
#                      .   ' \\| |// `.
#                       / \\||| : |||// \
#                     / _||||| -:- |||||- \
#                       | | \\\ - /// | |
#                     | \_| ''\---/'' | |
#                      \ .-\__ `-` ___/-. /
#                   ___`. .' /--.--\ `. . __
#                ."" '< `.___\_<|>_/___.' >'"".
#               | | : `- \`.;`\ _ /`;.`/ - ` : | |
#                 \ \ `-. \_ __\ /__ _/ .-` / /
#         ======`-.____`-.___\_____/___.-`____.-'======
#                            `=---='
#                 佛祖保佑     永无bug     永不修改
#         .............................................
#                  佛祖镇楼                  BUG辟易



def num_to_ch(num):
    """
    功能说明：讲阿拉伯数字转换成中文数字（转换[0, 10000)之间的阿拉伯数字 ）
    ----------------------------------------------------------------------------
    修改人                修改时间                修改原因
    ----------------------------------------------------------------------------
    陈龙                2012.2.9
    """
    num = int(num)
    _MAPPING = (u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', ) 
    _P0 = (u'', u'十', u'百', u'千', ) 
    _S4= 10 ** 4  
    if 0 > num and num >= _S4:
        return None
    if num < 10: 
        return _MAPPING[num] 
    else: 
        lst = [ ] 
        while num >= 10: 
            lst.append(num % 10) 
            num = num / 10 
        lst.append(num) 
        c = len(lst) # 位数 
        result = u'' 
        for idx, val in enumerate(lst): 
            if val != 0: 
                result += _P0[idx] + _MAPPING[val] 
            if idx < c - 1 and lst[idx + 1] == 0: 
                result += u'零'
        result = result[::-1]
        if result[:2] == u"一十":
            result = result[1:]
        if result[-1:] == u"零":
            result = result[:-1]
        return result   


def choice_date(day, str_date=None):
    """
    功能说明      基于某个时间的时间函数，day为正数表示day天后；为负数表示day天前
    --------------------------------
    修改人        修改时间        修改原因
    --------------------------------
    方朋        2014-03-24
    说明：如果str_date=None，则基于当前时间；否则是基于str_date这个时间
    """
    now = datetime.datetime.now()
    hope_date_format = now+datetime.timedelta(days=day)
    hope_date = hope_date_format.strftime('%Y-%m-%d %H:%M:%S')
    if str_date:
        tem = time.mktime(time.strptime(str_date, '%Y-%m-%d %H:%M:%S'))
        x = time.localtime(tem)
        date = datetime.datetime(x.tm_year, x.tm_mon, x.tm_mday, x.tm_hour, x.tm_min, x.tm_sec)
        hope_date = date+datetime.timedelta(days=day)
    return hope_date




def meCache(name, time=60*60*3):
    """
    功能说明      缓存装饰器
    --------------------------------
    修改人        修改时间        修改原因
    --------------------------------
    方朋        2014-08-26
    默认缓存3小时
    """
    miss = object()
    def real_wrapper(fn):
        def wrapper(*args, **kwargs):
            result = cache.get(name, miss)
            if result is miss:
                result = fn(*args, **kwargs)
                cache.set(name,result, time)
            return result
        return wrapper
    return real_wrapper


def addLog(fn):
    """
    功能说明      日志装饰器
    --------------------------------
    修改人        修改时间        修改原因
    --------------------------------
    方朋        2014-08-26
    """
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception, e:
            log.error('%s:%s' %(fn.__name__, e))
            return None
    return wrapper


class httpGetOrPost(object):
    """
    功能说明      HTTP POST,GET方法装饰器
    --------------------------------
    修改人        修改时间        修改原因
    --------------------------------
    方朋        2014-08-24
    """
    def __init__(self, template='', *args, **kwargs):
        self.template = template
        self.args = args
        self.kwargs = kwargs

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            try:
                result = fn(request, *args, **kwargs)
                if isinstance(result, (HttpResponseRedirect, HttpResponse)):
                    return result
                return render_template(request, self.template, result or {}) if self.template else result
            except Exception, e:
                exc = traceback.format_exc()
                log.error(exc)
                if settings.DEBUG:
                    print exc
                if self.template:
                    return render_template(request, self.template)
                info = ajax.ajax_fail("系统错误!请联系客服")
                if request.method == 'GET':
                    info = HttpResponse(u'%s:%s' %(fn.__name__, e))
                    # info = HttpResponseRedirect('/404/')
                return info

        return wrapper
