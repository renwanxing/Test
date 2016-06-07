#coding=utf-8
import os, sys, datetime
from django.conf import settings
from django.http  import HttpResponse

def getfilename(filename, subdir=''):
    """
    返回路径字符串
    """
    if subdir:
        return os.path.join(settings.MEDIA_ROOT, subdir, filename)
    else:
        return os.path.join(settings.MEDIA_ROOT, filename)

def del_file(path_name):
    """
    功能说明：删除指定的文件
    -------------------------------
    修改人    修改时间    修改原因
    -------------------------------
    徐威    2009-9-11
    """
    try:
        os.remove(path_name)
    except:
        return False
    else:
        return True
    
def resetfilename(filename, subdir=''):
    """
    filename : 文件名字
    subdir : 文件相对路径
    """
    fname = getfilename(filename, subdir)
    if os.path.exists(fname):
        #若存在当前文件则删除路径 
        try:
            os.remove(fname)
        except:
            pass
    #返回目录中的路径
    dirs = os.path.dirname(fname)
    if not os.path.exists(dirs):
        #创建路径
        os.makedirs(dirs)
    return fname

def rename(filename, prefix=''):
    """
    返回以日期命名的文件名
    """
    x = filename.rindex('.') + 1
    y = len(filename)
    ext_name = filename[x:y]
    now_time = datetime.datetime.now()
    retval = '%s.%s' % (now_time.strftime("%Y%m%d%H%M%S")+str(now_time.microsecond), ext_name)#filename.split('.')[1])
    if prefix:
        retval = prefix + retval
    return retval

def save_upload_file(filename, file):
    """
    保存文件
    filename：包含路径的文件名
    file : 文件
    """
    if os.path.isfile(filename):
        os.remove(filename)
    content = file.read()
    fp = open(filename, 'wb')
    fp.write(content)
    fp.close()

def download_file(file_path):
    """
    功能说明：       下载文件
    --------------------------------
    修改人          修改时间      修改原因
    --------------------------------
    孟昂          2010-9-16
    """
    try:
        f = open(file_path, "rb")
        data = f.read()
        f.close()
        response = HttpResponse(data,mimetype='application/octet-stream')
        response['Content-Disposition'] = u'attachment; filename=%s' % os.path.basename(file_path)
        return response
    except Exception,e:
        return "error"