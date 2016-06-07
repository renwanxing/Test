#coding=utf-8
import logging
import datetime, calendar
import simplejson, hashlib

from django.template import RequestContext, loader, Context
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.contrib.sessions.models import Session


log = logging.getLogger('util.common')


class Struct(dict):
    """
    - 为字典加上点语法. 例如:
    >>> o = Struct({'a':1})
    >>> o.a
    >>> 1
    >>> o.b
    >>> None
    """
    def __init__(self, dictobj={}):
        self.update(dictobj)

    def __getattr__(self, name):
        # Pickle is trying to get state from your object, and dict doesn't implement it. 
        # Your __getattr__ is being called with "__getstate__" to find that magic method, 
        # and returning None instead of raising AttributeError as it should.
        if name.startswith('__'):
            raise AttributeError
        return self.get(name)

    def __setattr__(self, name, val):
        self[name] = val
    
    def __delattr__(self, name):
        self.pop(name, None)
    
    def __hash__(self):
        return id(self)

class Redirect(Exception):
    """
    - 用异常来实现随时重定向, 需要结合中间件process_exception. 用法:
    >>> raise Redirect('/login')
    """
    def __init__(self, url):
        Exception.__init__(self, 'Redirect to: %s' % url)
        self.url = url

def get_full_path(request):
    full_path = ('http', ('', 's')[request.is_secure()], '://', request.META['HTTP_HOST'], request.path)
    return ''.join(full_path)

def render_template(request, template_path, context={}):
    t = loader.get_template(template_path)
    user = request.user
    context['user'] = user
    context['settings'] = settings
    context['now'] = datetime.datetime.now()
    s = t.render(context, request)
    return HttpResponse(s)

def get_func(string):
    module, func = string.rsplit('.', 1)
    mod = __import__(module, {}, {}, [''])
    return getattr(mod, func)

def get_func_args(func, args, kwargs, skip=None):
    import inspect
    v = inspect.getargspec(func)
    k = v[0]
    defaults = v[-1]
    if not defaults:
        defaults = ()
    k1 = k[:-1*len(defaults)]
    if skip is not None:
        k = k[skip:]
        k1 = k1[skip:]
    ks = {}
    for i, p in enumerate(k[:]):
        if p in kwargs:
            ks[p] = kwargs[p]
            del k[i]
            if p in k1:
                k1.remove(p)
    ars = args[:len(k1)]
    return ars, ks

def setting(name, defaultvalue=''):
    from django.conf import settings
    return getattr(settings, name, defaultvalue)
#if __name__ == '__main__':
#    def p(a,b,c=1,d=2):pass
#    args, kwargs = get_func_args(p, (4,5,6), {'b':'a'})
#    print p(*args, **kwargs)
#    

def format_datetime(td):
    """
    格式化时间
    """
    try:
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        seconds = td.seconds % 60
        if td.days <= 0:
            if hours <= 0:
                if minutes < 5:
                    return u' 刚刚'
                else:
                    return u'于%d分钟前' % minutes
            else:
                return u'于%d小时%d分钟前' % (hours, minutes)
        else:
            return u'于%d天%d小时前' % (td.days, hours)
    except Exception, e:
        log.error(e)
        return ""


def get_host_info(request):
    """
    获取客户端主机相关信息
    """
    import uuid, os, re, urllib2, socket
    from subprocess import Popen, PIPE
    if os.name == 'nt':
        try:
            ret = ''
            CmdLine = 'ipconfig /all'
            r = os.popen(CmdLine).read()
            if r:
                L = re.findall('Physical Address.*?([0-9,A-F]{2}-[0-9,A-F]{2}-[0-9,A-F]{2}-[0-9,A-F]{2}-[0-9,A-F]{2}-[0-9,A-F]{2})', r)
                if len(L) > 0:
                    ret = L[0]
        except:
            pass
        
    elif os.name == "posix":
        try:
            ret = ''
            CmdLine = 'ifconfig'
            r = os.popen(CmdLine).read()
            if r:
                L = re.findall('HWaddr.*?([0-9,A-F]{2}:[0-9,A-F]{2}:[0-9,A-F]{2}:[0-9,A-F]{2}:[0-9,A-F]{2}:[0-9,A-F]{2})', r)
                if len(L) > 0:
                    ret = L[0]
        except:
            pass
    else:
        pass
    
    node = uuid.getnode()
    mac = uuid.UUID(int=node)
    ret2 = mac.hex[-12:]
    
    ret3 = re.search('\d+\.\d+\.\d+\.\d+',urllib2.urlopen("http://www.whereismyip.com").read()).group(0)
    ret3 = re.search('\d+\.\d+\.\d+\.\d+',Popen('ipconfig', stdout=PIPE).stdout.read()).group(0)

    ip = socket.gethostbyname(socket.gethostname())
    ip =request.META['SERVER_NAME']
    return HttpResponse('%s|%s|%s' % (ret, ip, ret3))

def md5_encrypt(param=None):
    """
    返回md5 加密字符串
    """
    newmd = None
    try:
        import hashlib
        md = hashlib.md5()
        if not param:
            import random
            param = random.random().__str__()
        param = param + datetime.datetime.now().__str__()
        md.update(param)
        newmd = md.hexdigest()
        return newmd
    except Exception, e:
        log.error(e)
        return newmd
    
def getyearweek(date):
    year=date.year
    wd=calendar.weekday(year,1,1)
    days=(date-datetime.datetime(year,1,1)).days
    nweek=0
    if wd:
        nweek=(days+wd)/7
    else:
        nweek=days/7+1
    if( nweek==0 ):
        nweek = 52
        year -= 1
    return nweek+year*100

class SimpleAjaxException(Exception):pass



def json_response(request, data, check=False):

    uid = 0
    if request.META.get("HTTP_SESSIONID"):
        session_key = request.META.get("HTTP_SESSIONID")
        try:
            s = Session.objects.get(pk=session_key)
            uid = s.get_decoded().get('_auth_user_id')
            #custom_user = User.objects.get(pk=uid)
        except Exception, e:
            log.error('error=%s' % e)
    data["user_id"] = uid

    encode = settings.DEFAULT_CHARSET

    if check:
        if not is_ajax_data(data):
            raise SimpleAjaxException, 'Return data should be follow the Simple Ajax Data Format'
    try:
        return HttpResponse(simplejson.dumps(uni_str(data, encode)))
    except:
        return HttpResponse(simplejson.dumps(uni_str(data, "gb2312")))

def ajax_data(response_code, data=None, error=None, next=None, message=None):
    """if the response_code is true, then the data is set in 'data',
    if the response_code is false, then the data is set in 'error'
    """

    r = dict(response='ok', data='', error='', next='', message='')
    if response_code is True or response_code.lower() in ('ok', 'yes', 'true'):
        r['response'] = 'ok'
    else:
        r['response'] = 'fail'
    if data:
        r['data'] = data
    if error:
        r['error'] = error
    if next:
        r['next'] = next
    if message:
        r['message'] = message
    return r

def is_ajax_data(data):
    """Judge if a data is an Ajax data"""
    if not isinstance(data, dict): return False
    for k in data.keys():
        if not k in ('response', 'data', 'error', 'next', 'message'): return False
    if not data.has_key('response'): return False
    if not data['response'] in ('ok', 'fail'): return False
    return True

def uni_str(a, encoding=None):
    if not encoding:
        encoding = settings.DEFAULT_CHARSET

    if isinstance(a, (list, tuple)):

        s = []
        for i, k in enumerate(a):
            s.append(uni_str(k, encoding))
        return s
    elif isinstance(a, dict):

        s = {}
        for i, k in enumerate(a.items()):
            key, value = k
            s[uni_str(key, encoding)] = uni_str(value, encoding)
        return s
    elif isinstance(a, unicode):

        return a
    elif isinstance(a, (int, float)):

        return a
    elif isinstance(a, str) or (hasattr(a, '__str__') and callable(getattr(a, '__str__'))):

        if getattr(a, '__str__'):
            a = str(a)

        return unicode(a, encoding)
    else:
        return a

def get_options_data(data):
    """
    return select element's options
    """

    retval = ''
    for item in data:
        retval = retval + item.__option__() + ","

    return retval[0:-1]

def get_sms_nword(text):
    """
    功能说明：                获取短信格式字数
    -----------------------------------------------
    修改人                    修改时间
    -----------------------------------------------
    王晨光                    2015-3-31
    """
    text = unicode(text)
    return len(text)

def is_chinese_word(s, minlen=2, maxlen=5):
    """
    功能说明：           判断字符串(Unicode)是否为全中文
    -----------------------------------------------
    修改人                    修改时间
    -----------------------------------------------
    王晨光                    2015-5-18
    """
    if not s:
        return False
    for ch in s:
        if u'\u4e00' <= ch <= u'\u9fff':
            pass
        else:
            return False
    if len(s) < minlen or len(s) > maxlen:
        return False
    return True

def get_upload_key():
    """
    功能说明：获取文件上传时加密串
    ----------------------------------------------------------------------------
    修改人                修改时间                修改原因
    ----------------------------------------------------------------------------
   王晨光                2016-3-14
    """
    now_time = datetime.datetime.now()
    m = hashlib.md5()
    m.update('%s%s' % (settings.UPLOAD_FILE_KEY_VALUE, now_time.strftime("%Y%m%d")))
    return m.hexdigest()
