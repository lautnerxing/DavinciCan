from Py_DBC import ParseDBC
import re
from collections import Counter
import configparser


class selfcheck_dbc:
    """
    dbc文件自检程序
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read(r'..\config.ini', encoding='utf-8')
        self.node = config.get('Dbc_Property', 'node')
        parsedbc = ParseDBC.ParseDbc()
        parsedbc.switchs()
        self.filelist = parsedbc.dbc_filelist
        self.dbcinfo = parsedbc.dbc_dict
        self.dbcinfo_rx = parsedbc.dbc_dict_rx  # 用于检查信号map
        if self.dbcinfo:
            print('\033[1;30m开始自检程序:  \033[1;32m绿色\033[1;30m代表通过\033[1;31m红色\033[1;30m代表不通过\033[0m')
        else:
            print('\033[1;31m解析获得的数据为空，自检程序退出\033[0m')
            exit()
        # 同发同收检查
        print('\033[1;36m★ 检查节点下面是否存在同发同收的报文\033[0m')
        for dbcname in self.dbcinfo.keys():
            msgbox = list()
            for values in self.dbcinfo[dbcname]:
                for sig in values["siglist"]:
                    if values["node"] == sig["receiver"]:
                        msgbox.append(values["name"])
                        break
            if msgbox:
                print(dbcname + ' :  \033[31m' + str(msgbox)+'\033[0m')
            else:
                print(dbcname + ' :  \033[32mPASS\033[0m')
        # 检查DBC是否存在相同信号
        print('\033[1;36m★ 检查节点下面是否存在相同信号\033[0m')
        for dbcname, dbcinfo in self.dbcinfo.items():
            siglist = list()
            sigbox = list()
            for values in dbcinfo:
                for sig in values["siglist"]:
                    siglist.append(sig['name'])
            for k, v in Counter(siglist).items():
                if v > 1:
                    sigbox.append(k)
            if sigbox:
                print(dbcname + ' :  \033[31m' + str(sigbox)+'\033[0m')
            else:
                print(dbcname + ' :  \033[32mPASS\033[0m')
        # 检查DBC是否可以更改NetWorks名字
        print('\033[1;36m★ 检查DBC是否可以更改NetWorks(DBName)名字\033[0m')
        for dbcfile in self.filelist:
            with open(r'../SourceInput/DBC/'+dbcfile, 'r', encoding='utf-8') as f:
                state1 = state2 = 0
                for line in f.readlines():
                    if 'BA_DEF_  "DBName" STRING ;' in line:
                        state1 = 1
                    if 'BA_DEF_DEF_  "DBName" "";' in line:
                        state2 = 1
                    if 'BA_ "DBName" ' in line and state1 == state2 == 1:
                        print(dbcfile+' :  \033[32m'+line.strip()+'\033[0m')
                if state1 == 0 or state2 == 0:
                    print(dbcfile+' \033[31m不能更改DBName\033[0m')
        # 检查cycle time和send method
        print('\033[1;36m★ 检查DBC是否存在0ms报文\033[0m')
        for dbcname in self.dbcinfo.keys():
            ck = 0
            mescycletime = []
            errorbox = []
            for mesinfo in self.dbcinfo[dbcname]:
                try:
                    if mesinfo['cycletime'] == '0ms':
                        mescycletime.append(mesinfo['name'])
                        ck = 1
                except:
                    errorbox.append(mesinfo['name'])
                    ck = 2
            if ck == 1:
                print(dbcname + ' :  \033[31m' + str(mescycletime) + '\033[0m')
                continue
            if ck == 2:
                print(dbcname + ' :  \033[31mError', end='  ')
                print('未找到该报文cycletime属性' + str(errorbox)+'\033[0m')
                continue
            else:
                print(dbcname + ' :  \033[32mPASS\033[0m')
        # 检查DBC基本属性
        print('\033[1;36m★ 检查DBC基本属性\033[0m')
        checklist = ['GenMsgCycleTime', 'GenMsgDelayTime', 'GenMsgStartDelayTime', 'GenSigStartValue', 'GenMsgILSupport']
        for dbcfile in self.filelist:
            dbc_basic_property = list()
            with open(r'../SourceInput/DBC/' + dbcfile, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    for basic_property in checklist:
                        if line.find('BA_DEF_ BO_') == 0 and basic_property in line:
                            dbc_basic_property.append(re.split('"', line)[1])
                            if 'FLOAT' in line:
                                print(dbcfile + ' :  \033[31m' + line.strip() + '\033[0m')
                            else:
                                print(dbcfile+' :  \033[32m'+line.strip()+'\033[0m')
                for basic_property in checklist:
                    if basic_property not in dbc_basic_property:
                        print(dbcfile+' :  \033[31mCan\'t Find BA_DEF_ BO_  "'+basic_property+'"\033[0m')
        # 信号最大最小值检查
        print('\033[1;36m★ 信号最大最小值检查\033[0m')
        for dbcname in self.dbcinfo.keys():
            result_minmaxerror = list()
            for mesinfo in self.dbcinfo[dbcname]:
                mesinfo_minmaxerror = dict()
                siglist_minmaxerror = list()
                for siginfo in mesinfo['siglist']:
                    if siginfo['min'] == siginfo['max']:
                        siglist_minmaxerror.append(siginfo['name'])
                if siglist_minmaxerror:
                    mesinfo_minmaxerror.update({mesinfo['name']: str(siglist_minmaxerror)})
                    result_minmaxerror.append(mesinfo_minmaxerror)
            if result_minmaxerror:
                print(dbcname + ' : 字典key代表报文，value列表里面是信号')
                for i in result_minmaxerror:
                    print('      \033[31m'+str(i) + '\033[0m')
            else:
                print(dbcname + ' : \033[32mPASS\033[0m')
        # 信号长度与其最大值匹配检查
        print('\033[1;36m★ 信号长度与其最大值匹配检查\033[0m')
        for dbcname in self.dbcinfo.keys():
            sig_length_notmatched = list()
            for mesinfo in self.dbcinfo[dbcname]:
                for siglist in mesinfo['siglist']:
                    sig_size = eval(str(siglist['size']))
                    sig_factor = siglist['factor']
                    sig_offset = siglist['offset']
                    sig_bit = (2**sig_size)*sig_factor+sig_offset
                    sig_maxvalue = eval(str(siglist['max']))+1
                    if sig_bit > sig_maxvalue:
                        sig_length_notmatched.append(siglist['name'])
            if sig_length_notmatched:
                print(dbcname + ' :  \033[31m' + str(sig_length_notmatched) + '\033[0m')
            else:
                print(dbcname + ' : \033[32mPASS\033[0m')
        # 信号map检查
        print('\033[1;36m★ 信号map检查\033[0m')
        for dbcname in self.dbcinfo.keys():
            sig_notmappedlist = list()
            for mesinfo in self.dbcinfo_rx[dbcname]:
                if mesinfo['node'] != self.node:
                    for siglist in mesinfo['siglist']:
                        if siglist['receiver'] != self.node:
                            sig_notmappedlist.append(siglist['name'])
            if sig_notmappedlist:
                print(dbcname + ' :  \033[31m' + str(sig_notmappedlist) + '\033[0m')
            else:
                print(dbcname + ' : \033[32mPASS\033[0m')
        # BO_TX_BU检查(主从节点检查)
        print('\033[1;36m★ BO_TX_BU检查(主从节点检查)\033[0m')
        for dbcfile in self.filelist:
            ck = 0
            with open(r'../SourceInput/DBC/' + dbcfile, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    if line.find('BO_TX_BU') == 0:
                        print(dbcfile + ' :  \033[31m存在主从节点关系 '+line.strip()+'\033[0m')
                        ck = 1
                if ck == 0:
                    print(dbcfile + ' : \033[32mPASS\033[0m')


if __name__ == '__main__':
    selfcheck_dbc()
