# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        api_tool
# Purpose:
#
# Author:      Administrator
#
# Created:     01/01/2016
# Copyright:   (c) Administrator 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import inspect

#========================================================
#========================API TOOL FUNCS==================
#========================================================
def singleton(cls):
    instances = {}
    def _singleton(*args, **kwds):
        if cls not in instances:
            instances[cls] = cls(*args, **kwds)
        return instances[cls]
    return _singleton

@singleton
class Config(object):
    def __init__(self, dict_in, **kwds):
        self.__dict__.update(dict_in)
        self.__dict__.update(kwds)

    def __str__(self):
        return str(self.__dict__)

def api_wrapper(cache_opt=(0, lambda argsl, kwds:0), args_parser=lambda args_str, web_input:args_str):
    if not hasattr(args_parser, '__call__') or len(inspect.getargspec(args_parser).args)!=2:
        raise TypeError('args_parser must be func(args_str, web_input).')
    cache_num, cache_hash = cache_opt
    if not isinstance(cache_num, (int, long)) or cache_num<0:
        raise TypeError('cache_num must be int|long >= 0.')
    if not hasattr(cache_hash, '__call__') or len(inspect.getargspec(cache_hash).args)!=2:
        raise TypeError('cache_hash must be func(argsl, kwds) and return hash_able obj.')

    def _wrapper(func):
        cache_dict = {}

        def _api(*args, **kwds):
            _cache_num = getattr(_api, '_cache_num', 0)
            _cache_dict = getattr(_api, '_cache_dict', None)
            if _cache_num and isinstance(_cache_dict, dict):
                key = cache_hash(args, kwds)
                if key not in _cache_dict:
                    _api._cache_misses = getattr(_api, '_cache_misses', 0) + 1
                    if len(_cache_dict) >= _cache_num:
                        _api._cache_pops = getattr(_api, '_cache_pops', 0) + 1
                        _cache_dict.popitem()
                    _cache_dict[key] = func(*args, **kwds)
                    return _cache_dict[key]
                else:
                    _api._cache_hits = getattr(_api, '_cache_hits', 0) + 1
                    return _cache_dict[key]
            else:
                return func(*args, **kwds)

        def cache_info():
            return "cache_num:%d, cache_hits:%d, cache_misses:%d, cache_pops:%d, calls_total:%d, calls_diff:<=%d" % (_api._cache_num, _api._cache_hits, _api._cache_misses, _api._cache_pops, _api._cache_hits+_api._cache_misses, _api._cache_num+_api._cache_pops, )

        def cache_set(cache_num, cache_dict):
            _api._cache_hits = _api._cache_misses = _api._cache_pops = 0
            _api._cache_num = cache_num
            _api._cache_dict = cache_dict

        _api._cache_info = cache_info
        _api._cache_set = cache_set
        _api._cache_set(cache_num, cache_dict)
        _api.is_api = True
        _api.args_parser = args_parser

        return update_wrapper(_api, func)

    return _wrapper

def update_wrapper(wrapper, wrapped):
    for attr in ('__module__', '__name__', '__doc__'):
        setattr(wrapper, attr, getattr(wrapped, attr, ''))
    for attr in ('__dict__',):
        getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
    return wrapper

def FNVHash(key):
    fnv_prime = 0x811C9DC5
    ln = len(key)
    h = 0

    if ln==0:
        return h
    elif ln==1:
        def f(x):
            return ((65537**(x%5)) ^ (65521**(x%7)) ^ (65519**(x%11)) * x + x + 1) % (2**31-1)
        h = ord(key[0])
        return int(f(h))

    for i in range(ln):
        h *= fnv_prime
        h ^= ord(key[i])
    h += ord(key[-1])
    return int(h % (2**31-1))



def main():
    test_str = 'sasadad'
    print test_str, FNVHash(test_str)
    test_str = 'sasadad'
    print test_str, FNVHash(test_str)

    @api_wrapper(cache_opt=(4, lambda argsl, kwds:argsl[0]))
    def _FNVHash(key):
        return FNVHash(key)

    test_str = 'sasadad'
    print test_str, _FNVHash(test_str)
    test_str = 'sasadad1'
    print test_str, _FNVHash(test_str)
    test_str = 'sasadad2'
    print test_str, _FNVHash(test_str)
    test_str = 'sasadad3'
    print test_str, _FNVHash(test_str)
    test_str = 'sasadad4'
    print test_str, _FNVHash(test_str)
    test_str = 'sasadad3'
    print test_str, _FNVHash(test_str)
    test_str = 'sasadad1'
    print test_str, _FNVHash(test_str)
    test_str = 'sasadad4'
    print test_str, _FNVHash(test_str)
    test_str = 'sasadad1'
    print test_str, _FNVHash(test_str)
    test_str = 'sasadad2'
    print test_str, _FNVHash(test_str)
    test_str = 'sasadad3'
    print test_str, _FNVHash(test_str)

    print _FNVHash._cache_info()
    import json
    print json.dumps(_FNVHash._cache_dict, indent=4)


if __name__ == '__main__':
    main()
