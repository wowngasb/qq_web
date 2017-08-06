#-*- coding: utf-8 -*-
import os
import marshal
import datetime
import json
import multiprocessing
import re
import base64
import array
import binascii
import time

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

def do_file(out_dir, full_name, name):
    ret_dict, tmp_dir = {i:{} for i in range(256)}, os.path.join(out_dir, name.split('.')[0])
    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)
    print '\n', datetime.datetime.now(), '[INFO]', 'read file:', full_name
    with open(full_name, 'rU') as rf:
        for idx, line in enumerate(rf):
            _s = line.find(',')
            if _s:
                qq, nick = int(line[:_s]), line[_s+1:-1]
                h = (binascii.crc32(nick) & 0xffffffff) % 256
                ret_dict[h].setdefault(nick, set())
                ret_dict[h][nick].add(qq)
            if idx % (10000 * 100) == 0 and idx > 0:
                print datetime.datetime.now(), '[INFO] file:', name, 'idx:', idx
    while ret_dict:
        h, obj = ret_dict.popitem()
        dump_obj(obj, os.path.join(tmp_dir, '%02x.obj' % (h, )))

def main222():
    print "======== START ========="
    in_dir = r'L:\qq_info'
    out_dir = r'H:\qq_save'

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    in_file_dict = get_dict_of_dir(in_dir, lambda s: s.endswith('.txtok'))
    for full_name, name in in_file_dict.items():
        do_file(out_dir, full_name, name)

    print datetime.datetime.now(), '[INFO] end'
    print "======== END ========="

def merge_file(in_file_dict, save_file):
    if os.path.isfile(save_file):
        return
    ret_dict = {}
    for full_name, name in in_file_dict.items():
        tmp_dict = load_obj(full_name)
        print datetime.datetime.now(), '[INFO] file:', full_name, 'len:', len(ret_dict)
        for k, v in tmp_dict.items():
            if k in ret_dict:
                ret_dict[k] = ret_dict[k].union(v)
            else:
                ret_dict[k] = v
    dump_obj(ret_dict, save_file)

def main333():
    print "======== START ========="
    in_dir = r'H:\qq_save'
    out_dir = r'F:\qq_merge'

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    pool = multiprocessing.Pool(5)

    for idx in range(256):
        file_key = '%02x' % (idx, )
        in_file_dict = get_dict_of_dir(in_dir, lambda s: s.endswith(file_key + '.obj'))
        save_file = os.path.join(out_dir, file_key + '.obj')
        pool.apply_async(merge_file, args=(in_file_dict, save_file))

    pool.close()
    pool.join()

    print datetime.datetime.now(), '[INFO] end'
    print "======== END ========="

def int_list_base64(in_list):
    arr = array.array('L')
    arr.extend(in_list)
    return base64.b64encode(arr.tostring())



def dump_mongo(in_file_dict, save_file):
    tpl_list = ['{"n":', None, ',"d":{"$binary":"', None, '","$type":"00"},"c":', None, '}']
    with open(save_file, 'w') as wf:
        for full_name, name in in_file_dict.items():
            tmp_dict = load_obj(full_name)
            print datetime.datetime.now(), '[INFO] file:', full_name, 'len:', len(tmp_dict)
            line_list = []
            while tmp_dict:
                k, v = tmp_dict.popitem()
                tpl_list[1], tpl_list[3], tpl_list[5] = json.dumps(k, ensure_ascii=False), int_list_base64(v), str(len(v))
                line = ''.join(tpl_list)
                line_list.append(line + '\n')

            wf.writelines(line_list)
            wf.flush()

def apply_async(multi_num, pool, func, args=(), kwds={}):
    if multi_num <= 1:
        return func(*args, **kwds)
    else:
        pool.apply_async(func, args=args, kwds=kwds)

def main():
    print "======== START ========="
    in_dir = r'F:\qq_merge'
    out_dir = r'L:\qq_data'

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    multi_num = 8
    pool = multiprocessing.Pool(multi_num)

    for idx in range(8):
        file_key = 'crc32_%d' % (idx, )
        test_file = lambda name: name in ['%02x' % (i, ) for i in range(256) if i % 8 == idx]
        in_file_dict = get_dict_of_dir(in_dir, lambda s: test_file(s.split('\\')[-1].split('.')[0]))
        save_file = os.path.join(out_dir, file_key + '.json')
        if idx > 0 :
            time.sleep(10)
        apply_async(multi_num, pool, dump_mongo, args=(in_file_dict, save_file))

    pool.close()
    pool.join()

    print datetime.datetime.now(), '[INFO] end'
    print "======== END ========="


if __name__ == '__main__':
    main()