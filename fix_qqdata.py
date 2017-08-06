#-*- coding: utf-8 -*-
import os
import marshal
import datetime
import json
import multiprocessing
import re

from api_tool import FNVHash

def dump_obj(obj, file_name):
    with open(file_name, 'wb') as wf:
        marshal.dump(obj, wf)

def load_obj(file_name):
    with open(file_name, 'rb') as rf:
        return marshal.load(rf)

def get_dict_of_dir(str_dir, filter_func=None):
    str_dir = str_dir.encode('gb2312', 'ignore') if isinstance(str_dir, unicode) else str_dir
    if not os.path.isdir(str_dir):
        return {}
    filter_func = filter_func if hasattr(filter_func, '__call__') else lambda s_full_name: True
    all_files, current_files = {}, os.listdir(str_dir)
    for file_name in current_files:
        if file_name=='.' or file_name=='..':
            continue
        full_name = os.path.join(str_dir, file_name)
        if os.path.isfile(full_name):
            if filter_func(full_name):
                all_files.setdefault(full_name, file_name)
        elif os.path.isdir(full_name):
            next_files = get_dict_of_dir(full_name, filter_func)
            for n_full_name, n_file_name in next_files.items():
                all_files.setdefault(n_full_name, n_file_name)

    return all_files

def main():
    print "======== START ========="
    in_dir = r'L:\qq_info'
    out_dir = r'H:\qq_save'

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    in_file_dict = get_dict_of_dir(in_dir, lambda s: s.endswith('.txt'))
    for full_name, name in in_file_dict.items():
        ret_dict, tmp_dir = {i:{} for i in range(256)}, os.path.join(out_dir, name.split('.')[0])
        if not os.path.isdir(tmp_dir):
            os.mkdir(tmp_dir)
        print '\n', datetime.datetime.now(), ' [INFO] ', 'read file:', full_name
        with open(full_name, 'rU') as rf:
            for idx, line in enumerate(rf):
                _s = line.find(',')
                if _s:
                    qq, nick = int(line[:_s]), line[_s+1:-1]
                    h = FNVHash(nick) % 256
                    ret_dict[h].setdefault(nick, set())
                    ret_dict[h][nick].add(qq)
                if idx % 10000 == 0 and idx > 0:
                    print '.',
        while ret_dict:
            h, obj = ret_dict.popitem()
            dump_obj(obj, os.path.join(tmp_dir, '%02x.obj' % (h, )))

    print datetime.datetime.now(), ' [INFO] end'
    print "======== END ========="

if __name__ == '__main__':
    main()