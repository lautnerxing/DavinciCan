# _*_ coding:utf-8 _*_

# -------------------------------------------------------------------------------
# Name:        encode2utf8
# Purpose:     Automatically encode the .DBC files into UTF-8 format for easy parsing
#
# Author:      JiaXing
#
# Created:     2022/10/09
# Copyright:   (c) user 2022
# Version:     v3.0
# Last revision date: 2022/10/09
# -------------------------------------------------------------------------------

import chardet
import os
from chardet.universaldetector import UniversalDetector


def listDirFile(dir):
    filebox = []
    list = os.listdir(dir)
    for line in list:
        filepath = os.path.join(dir, line)
        if os.path.isdir(filepath):
            listDirFile(filepath)
        else:
            if '.dbc' or '.arxml' in filepath.lower():
                filebox.append(filepath)
    return filebox


def get_encode_info(file):
    with open(file, 'rb') as f:
        detector = UniversalDetector()
        for line in f.readlines():
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        return detector.result['encoding']


def read_file(file):
    with open(file, 'rb') as f:
        return f.read()


def write_file(content, file):
    with open(file, 'wb') as f:
        f.write(content)


def convert_encode2utf8(file, original_encode, des_encode):
    file_content = read_file(file)
    file_decode = file_content.decode(original_encode, 'ignore')
    file_encode = file_decode.encode(des_encode)
    write_file(file_encode, file)


def changecode(filepath):
    filebox = listDirFile(filepath)
    for filename in filebox:
        if '.dbc' in filename.lower() or '.arxml' in filename.lower():
            encode_info = get_encode_info(filename)
            if encode_info != 'utf-8':
                convert_encode2utf8(filename, encode_info, 'utf-8')
            # encode_info_2 = get_encode_info(filename)
            print('{:<80}   编码:{:^10}修改为:  utf-8'.format(filename, encode_info))


# if __name__ == "__main__":
#     filebox = listDirFile(r'C:\Users\Administrator\Desktop\AutoTesting3.0\AutoTesting3.0\DBC')
#     for filename in filebox:
#         file_content = read_file(filename)
#         encode_info = get_encode_info(filename)
#         if encode_info != 'utf-8':
#             convert_encode2utf8(filename, encode_info, 'utf-8')
#         encode_info_2 = get_encode_info(filename)
#         print('{:<80}   编码：{:^10}修改为：{:^10}'.format(filename, encode_info, encode_info_2))
