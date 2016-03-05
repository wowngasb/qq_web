# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        qq_api
# Purpose:
#
# Author:      Administrator
#
# Created:     01/01/2016
# Copyright:   (c) Administrator 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import array
import inspect
from api_tool import api_wrapper, FNVHash
from qq_config import config

MYSQL_DB = config.MYSQL_DB
MONGO_CONN = config.MONGO_CONN

SQL_IN_BLOCK_MAX_ITEM = 500
CACHE_ITEM_NUM = 1000
AW_NONE = api_wrapper( (CACHE_ITEM_NUM, lambda argsl, kwds:None), lambda args_str, web_input: None)
AW_INT = api_wrapper( (CACHE_ITEM_NUM, lambda argsl, kwds:argsl[0] if argsl else 0), lambda args_str, web_input: int(args_str) if args_str.isdigit() else None)
AW_INT_LIST = api_wrapper( (CACHE_ITEM_NUM, lambda argsl, kwds:tuple(sorted(list(argsl[0]))) ), lambda args_str, web_input: [int(si) for si in args_str.split(',') if si.isdigit()])
AW_STR = api_wrapper( (CACHE_ITEM_NUM, lambda argsl, kwds:argsl[0] if argsl else ''), lambda args_str, web_input: args_str.strip())
AW_STR_LIST = api_wrapper( (CACHE_ITEM_NUM, lambda argsl, kwds:tuple(sorted(list(argsl[0]))) ), lambda args_str, web_input: [si.strip() for si in args_str.split(',') if si])


def fix(item):
    if not isinstance(item, dict):
        return item

    item['Age'] = item['Info'] / 256
    item['Auth'] = (item['Info'] % 256)/4
    item['Gender'] = u'女' if item['Info'] % 4 == 0 else u'男'
    return item

#========================================================
#========================API FUNCS=======================
#========================================================

@AW_STR
def apihelp(args=None):
    api_dict = getattr(apihelp, 'api_dict', None)
    if api_dict is None:
        doc = lambda f:{'doc': getattr(f, '__doc__', 'no __doc__ .'),
                        'args':str(inspect.getargspec(f)),
                        'args_parser':inspect.getsource(getattr(f,'args_parser',lambda args_str, web_input:args_str)),
                        }
        api_dict = {k:doc(v) for k,v in globals().items() if hasattr(v, '__call__') and getattr(v, 'is_api', False)}
        apihelp.api_dict = api_dict

    result = {'apihelp':"use /api?func=...&args=...[&indent=4][&callback=callback]",
              'func':api_dict}
    if not isinstance(args, (str, unicode)):
        return result
    return {args:api_dict[args]} if args in api_dict else result

@AW_STR
def nickqqs(args):
    """get qq_num_list of the nick."""
    result = []
    if not args or not isinstance(args, unicode):
        return result
    unicode_nick = args
    cur = MONGO_CONN['qqnick%d_%d' % (len(unicode_nick), FNVHash(unicode_nick)%4)]['qqnick']
    mongo_ret = cur.find_one({'nick':unicode_nick})
    if not mongo_ret:
        return result
    else:
        result = array.array('L')
        result.fromstring(str(mongo_ret['num']))
        return list(result)

@AW_STR_LIST
def nickqqs_ex(args):
    result = {}
    if not args or not isinstance(args, (list, set)):
        return result
    unicode_nick_set = set(args)
    result = {unicode_nick:nickqqs(unicode_nick) for unicode_nick in unicode_nick_set}
    return result

@AW_INT
def quninfo(args):
    result = {}
    if not args or  not isinstance(args, (int, long)):
        return result
    QunNum = int(args)
    mysql_ret = MYSQL_DB.select('QUNinfo.qunlist', where='QunNum=$QunNum', vars={'QunNum':QunNum})
    if not mysql_ret:
        return result
    else:
        result = dict(mysql_ret[0])
        result['CreateDate'] = str(result['CreateDate'])
        return result

@AW_INT_LIST
def quninfo_ex(args):
    result = {}
    if not args or not isinstance(args, (list, set)):
        return result
    QunNum_set = set(args)
    if len(QunNum_set)>SQL_IN_BLOCK_MAX_ITEM:
        QunNum_set = list(QunNum_set)
        while QunNum_set:
            result.update( quninfo_ex(QunNum_set[:SQL_IN_BLOCK_MAX_ITEM]) )
            QunNum_set = []#QunNum_set[SQL_IN_BLOCK_MAX_ITEM:]
        return result

    mysql_ret = MYSQL_DB.select('QUNinfo.qunlist', where='QunNum in (%s)' % (','.join([str(QunNum) for QunNum in QunNum_set]),), vars={})
    if not mysql_ret:
        return result
    else:
        result = {i['QunNum']:dict(i) for i in mysql_ret}
        for _,item in result.items():
            item['CreateDate'] = str(item['CreateDate'])

        for QunNum in QunNum_set:
            result.setdefault(QunNum, {})
        return result

@AW_INT
def qunmembers(args):
    result = []
    if not args or not isinstance(args, (int, long)):
        return result
    QunNum = int(args)
    if QunNum/10000000+1 > 11:
        return result

    mysql_ret = MYSQL_DB.select('qqinfo%s' % (QunNum/10000000+1,) , where='QunNum=$QunNum', vars={'QunNum':QunNum})
    if not mysql_ret:
        return result
    else:
        result = [fix(dict(i)) for i in mysql_ret]
        for index, item in enumerate(result):
            item['Index'] = index + 1
        return result

@AW_INT_LIST
def qunmembers_ex(args):
    result = {}
    if not args or not isinstance(args, (list, set)):
        return result
    QunNum_set = set(args)
    result = {QunNum:qunmembers(QunNum) for QunNum in QunNum_set}
    return result

@AW_INT
def qqinfo(args):
    result = []
    if not args or not isinstance(args, (int, long)):
        return result
    QQNum = int(args)
    ret_list = []
    for qun_index in range(1, 12):
        mysql_ret = MYSQL_DB.select('qqinfo%s' % (qun_index,) , where='QQNum=$QQNum', vars={'QQNum':QQNum})
        if mysql_ret:
            ret_list.append(mysql_ret)

    for mysql_ret in ret_list:
        result.extend([fix(dict(i)) for i in mysql_ret])

    qun_set = set([item['QunNum'] for item in result if 'QunNum' in item and item['QunNum']>0])
    quninfo_dict = quninfo_ex(qun_set)
    for item in result:
        item.update(quninfo_dict.get(item['QunNum'], {}))
    return result

@AW_INT_LIST
def qqinfo_ex(args):
    result = {}
    if not args or not isinstance(args, (list, set)):
        return result
    QQNum_set = set(args)
    if len(QQNum_set)>SQL_IN_BLOCK_MAX_ITEM:
        QQNum_set = list(QQNum_set)
        while QQNum_set:
            result.update( qqinfo_ex(QQNum_set[:SQL_IN_BLOCK_MAX_ITEM]) )
            QQNum_set = []#QQNum_set[SQL_IN_BLOCK_MAX_ITEM:]
        return result

    ret_list = []
    for qun_index in range(1, 12):
        mysql_ret = MYSQL_DB.select('qqinfo%s' % (qun_index,) ,
                    where='QQNum in (%s)' % (','.join([str(QQNum) for QQNum in QQNum_set]),), vars={})
        if mysql_ret:
            ret_list.append(mysql_ret)

    result_list = []
    for mysql_ret in ret_list:
        tmp = [fix(dict(i)) for i in mysql_ret]
        result_list.extend(tmp)

    result = {QunNum:[] for QunNum in QQNum_set}
    for item in result_list:
        result[item['QQNum']].append(item)

    qun_list = []
    for _, info in result.items():
        qun_list.extend([item['QunNum'] for item in info if 'QunNum' in item and item['QunNum']>0])
    quninfo_dict = quninfo_ex(set(qun_list))
    for _, info in result.items():
        for item in info:
            item.update(quninfo_dict.get(item['QunNum'], {}))

    return result


def main():
    print apihelp()

    qqinfo._cache_set(3, {})
    print qqinfo(402493126)
    print qqinfo(402493127)
    print qqinfo(402493127)
    print qqinfo(402493128)
    print qqinfo(402493129)
    print '\n', qqinfo._cache_info()
    import json
    print '\n', json.dumps(qqinfo._cache_dict,indent=4)
    print '\n', '\n', nickqqs('赵日天'.decode('utf-8'))

if __name__ == '__main__':
    main()
