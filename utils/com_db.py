#coding=utf-8
import logging

from django.db import connections, connection,transaction
log = logging.getLogger(__name__)

def ExecuteSql(sql,db='default'):
    """
    功能说明：   执行SQL
    --------------------------------
    修改人        修改时间        修改原因
    --------------------------------
    方朋        2014-01-06
    """
    if sql is None or sql == "":
        return

    cursor = connections[db].cursor()
    cursor.execute(sql)
    transaction.commit_unless_managed(using=db)
    cursor.close()
    return True


def SelectAllSql(sql,db='slave'):
    """
    功能说明：       查询SQL多条数据
    --------------------------------
    修改人        修改时间        修改原因
    --------------------------------
    方朋        2014-01-06
    """
    if sql is None or sql == "":
        return

    cursor = connections[db].cursor()
    cursor.execute(sql)
    fetchall = cursor.fetchall()
    cursor.close()
    return fetchall



def SelectAllSqlByColumns(sql,columns,args=(),db='slave'):

    """
    功能说明：       查询SQL多条数据
    --------------------------------
    修改人        修改时间        修改原因
    --------------------------------
    陈龙       2014-04-11
    参数示例：
    sql = "select username ,password from user"
    columns= ["username","password"]
  returns:
        [
        {"username":"陈龙","password":"密码"},
        {"username":"徐威","password":"密码"}
        ]
    """
    if sql is None or sql == "":
        return

    cursor = connections[db].cursor()
    cursor.execute(sql, args)

    fetchall = cursor.fetchall()
    object_list = []
    if fetchall:
        for obj in fetchall:
            dict = {}
            for index,c in enumerate(columns):
                dict[c] = obj[index]
            object_list.append(dict)
    cursor.close()
    return object_list


def SelectOneSql(sql, db='slave'):
    """
    功能说明：       查询SQL单条数据
    --------------------------------
    修改人        修改时间        修改原因
    --------------------------------
    方朋        2014-01-06
    """
    if sql is None or sql == "":
        return

    cursor = connections[db].cursor()
    cursor.execute(sql)
    fetchone = cursor.fetchone()
    cursor.close()
    return fetchone


def SelectOneSqlByColumns(sql, columns, db='slave'):
    """
    功能说明：       查询SQL单条数据
    --------------------------------
    修改人        修改时间        修改原因
    --------------------------------
    陈龙       2014-04-11
    参数示例：
    sql = "select username ,password from user"
    columns= ["username","password"]
    
  returns:{"username":"陈龙","password":"密码"},
        
    """
    if sql is None or sql == "":
        return
    cursor = connections[db].cursor()
    cursor.execute(sql)
    fetchone = cursor.fetchone()
    object = {}
    if fetchone:
        for index, c in enumerate(columns):
            object[c] = fetchone[index]
    cursor.close()
    return object

def callProc(proname, params):
    """
    功能说明：                调用存储过程
    -----------------------------------------------
    修改人                   修改时间
    -----------------------------------------------
    方朋                    2014－04－17
    proname:    存储过程名字
    params:     输入参数元组或列表
    """
    cc = connections['ketang'].cursor()
    db = 'ketang'
    if proname == 'get_school_unit_class':      # 获取班级学校信息的存储过程在tbkt里面。
        cc = connection.cursor()
        db = 'default'
    try:
        cc.callproc(proname, params)
        # print u'该存储[%s]过程影响的行数：%s' % (proname, cc.rowcount)

        try:
            transaction.commit_unless_managed(using=db)     # 事务提交
        except Exception, e:
            pass

        data = cc.fetchall()
        # print '存储过程返回的数据：%s' %data
        cc.close()
        return data

    except Exception, e:
        log.info('callProc:%s' % e)
        return 'err'
    finally:
        cc.close()

def get_page(sql, columns, count_sql, page_no, page_num, db='default'):
    """
    功能说明：     获取分页（获取当前页数据,和页面属性）
    --------------------------------
    修改人        修改时间        修改原因
    --------------------------------
    方朋        2014-04-16
    说明：
    ======================================================
    sql         —— 所有数据 sql 语句
    columns     —— 页面数据属性名,与 sql 的查询结果一一对应
    count_sql   —— 数据总数 sql 语句/也可以传数字
    page_no     —— 页码
    page_num    —— 每页数据量
    =======================================================
    返回数据：
    =======================================================
    {
        "objects":[],        —— 页面数据
        "page_no":1          —— 页码
        "pages":10           —— 总页数
    }
    =======================================================
    """
    cursor = connections[db].cursor()
    if isinstance(count_sql, (int, long)):
        count = count_sql
    else:
        cursor.execute(count_sql)
        count = cursor.fetchall()[0][0]     # 数据总数
    bc = count % page_num
    if bc == 0:
        pages = count/page_num
    else:
        pages = (count/page_num)+1 if bc < page_num else 0    # 总页数
    # 页面数据
    sql += """ limit %s,%s""" % ((int(page_no)-1)*page_num, page_num)
    cursor.execute(sql)
    fetchall = cursor.fetchall()
    object_lis = []        # 页面数据
    if fetchall:
        for obj in fetchall:
            dict = {}
            for index, c in enumerate(columns):
                dict[c] = obj[index]
            object_lis.append(dict)
    cursor.close()
    return {
        'objects': object_lis,
        'pageno': page_no,
        'pages': pages
        }



def sqlFilter(sql):
    """
    功能说明：       sql注入过虑
    --------------------------------
    修改人        修改时间        修改原因
    --------------------------------
    杜祖永        2015-04-01
    """

    dirty_stuff = ["\"", "\\", "/", "*", "'", "=", "-", "#", ";", "<", ">", "+", "%","$","(",")","%","@"]
    for stuff in dirty_stuff:
        sql = sql.replace(stuff,"")
    return sql

