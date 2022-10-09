import configparser
import re
import os
import copy
from encode2utf8 import changecode, get_encode_info
from pprint import pprint


class ParseDbc:
    """
    解析DBC文件
    """

    def __init__(self, filepath=None):
        self.dbc_filelist = list()
        self.dbcinfo = {}
        # 打开并读取配置文件
        # os.system(r'config.ini')
        config = configparser.ConfigParser()
        config.read(r'..\config.ini', encoding='utf-8')
        self.dbc_path = config.get('Dbc_Property', 'dbc_path')
        self.specialname = config.get('Dbc_Property', 'specialname')
        self.node = config.get('Dbc_Property', 'node')
        self.sendtype = config.get('Dbc_Property', 'sendtype')
        self.box = config.get('Dbc_Property', 'box')
        # get *.dbc file and ignore *.ini file in dbc_path
        if filepath:
            self.dbc_filelist = filepath
        else:
            filelist = os.listdir(self.dbc_path)
            for dbcfile in filelist:
                if '.dbc' in dbcfile.lower():
                    self.dbc_filelist.append(dbcfile)
        # 编码检查
        print('正在检查是否需要对DBC文件进行编码转换...')
        for i in self.dbc_filelist:
            res = get_encode_info(self.dbc_path+'\\'+i)
            if res != 'utf-8':
                print('正在执行DBC文件编码转换...')
                changecode(self.dbc_path)
                break
        # 定义初始输出变量
        self.txlist_msginfo = list()
        self.rxlist_msginfo = list()
        self.rxlist_msginfo_check = list()
        self.msgbox = list()
        self.allmsginfo = list()
        self.dbc_dict = dict()
        self.dbc_dict_rx = dict()

    def parseprograme(self):
        """

        :return:包含所有被解析了的dbc的信息
        """
        dbcinfo = dict()
        print('正在解析DBC...')
        for dbcfile in self.dbc_filelist:
            Check_RE = 0
            cycletime = dict()
            meslist = list()
            if len(self.dbc_filelist) == 1 and ':/' in self.dbc_filelist:
                dbcpath = dbcfile
                dbcfile = re.split('/', dbcfile)[-1]
                dbcinfo.update({dbcfile: ''})
            else:
                dbcpath = self.dbc_path + '/' + dbcfile
                dbcinfo.update({dbcfile: ''})
            with open(dbcpath, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    if line.find('BO_ ') == 0:
                        mes = dict()
                        linelist = line.split(' ')
                        mes['id'] = linelist[1]
                        mes['name'] = linelist[2].strip(':')
                        mes['size'] = linelist[3]
                        mes['node'] = linelist[4].strip('\n')
                        mes['siglist'] = []
                        meslist.append(mes)
                    elif line.find(' SG_ ') == 0:
                        sig = dict()
                        linelist = re.split(r'[ :|@()\[\],]+', line.strip())
                        receivernode = re.split('"', line.strip())
                        sig["name"] = linelist[1]
                        sig["size"] = eval(linelist[3])
                        try:
                            sig["valuetype"] = re.search('\D', linelist[4]).group()
                            sig["factor"] = eval(linelist[5])
                        except:
                            sig['valuetype'] = 'None'
                            sig['factor'] = 0
                            if mes["node"] == self.node:
                                print('valuetype & factor \033[31mError\033[0m    '+sig['name'])
                                Check_RE = 1
                        sig["offset"] = eval(linelist[6])
                        sig["min"] = linelist[7]
                        sig["max"] = linelist[8]
                        sig["unit"] = linelist[9]
                        sig["receiver"] = receivernode[2].strip()
                        # add datatype
                        sig_factor = sig['factor']
                        sig_size = sig['size']
                        sig_offset = sig['offset']
                        sig_valuetype = sig['valuetype']
                        if sig_size == 1:
                            datatype = 'boolean'
                        elif type(sig_factor) is float:
                            if sig_size <= 32:
                                datatype = 'float32'
                            else:
                                datatype = 'float64'
                        elif sig_factor == 1:
                            if sig_offset < 0 or sig_valuetype == '-':
                                if sig_size <= 8:
                                    datatype = 'sint8'
                                elif sig_size <= 16:
                                    datatype = 'sint16'
                                elif sig_size <= 32:
                                    datatype = 'sint32'
                            elif sig_offset >= 0:
                                if sig_size <= 8:
                                    datatype = 'uint8'
                                elif sig_size <= 16:
                                    datatype = 'uint16'
                                elif sig_size <= 32:
                                    datatype = 'uint32'
                                elif sig_size <= 64:
                                    datatype = 'uint64'
                        elif sig_factor > 1 and type(sig_factor) is int:
                            if sig_offset < 0 or sig_valuetype == '-':
                                if sig_size <= 16:
                                    datatype = 'sint16'
                                elif sig_size <= 32:
                                    datatype = 'sint32'
                            elif sig_offset >= 0:
                                if sig_size <= 16:
                                    datatype = 'uint16'
                                elif sig_size <= 32:
                                    datatype = 'uint32'
                        if sig['valuetype'] == '-':
                            sig['datatype_bus'] = 'sint'
                        sig['datatype'] = datatype
                        mes['siglist'].append(sig)
                    # find cycle time
                    if line.find('BA_ "GenMsgCycleTime"') == 0:
                        linelist = line.split(' ')
                        msgid = linelist[3]
                        msgtime = re.match('\d+', linelist[4]).group()
                        cycletime.update({msgid: msgtime})
                dbcinfo.update({dbcfile: meslist})
            # Check_RE:检查DBC解析是否成功
            if Check_RE == 1:
                print('\033[1;31m解析失败，程序退出，出现问题的DBC是：\033[0m')
                print(dbcfile)
                exit()
            # add cycle time into dbcinfo
            for msginfo in dbcinfo[dbcfile]:
                for msgid, msgtime in cycletime.items():
                    if msginfo['id'] == msgid:
                        msginfo.update({'cycletime': str(msgtime)+'ms'})
        # pprint(dbcinfo)
        # print(cycletime)
        self.dbcinfo = dbcinfo

        return self.dbcinfo

    def switchs(self):
        """
        筛选函数，用于提取出特定的dbc文件的信息和节点或发送方式的信息，以及是否打开box函数开关
        :param dbcfile: 选择特定dbc文件进行信息提取，默认为提取所有dbc文件
        :param node: 提取出特定节点的信息
        :param sendtype: 提取出TX或是RX的msg的信息，不选择默认为所有msg
        :param box: specialbox函数开关，默认为关闭; 一个可以装msg的盒子，用于特定提取出box里面的msg
        :return:发送列表，接收列表，特定信号列表
        """
        self.parseprograme()
        dbcinfo_all = self.dbcinfo
        # param dbcfile:
        if self.specialname != 'default' or None:
            specialname_list = re.split(',', self.specialname)
            for i in specialname_list:
                for k, v in self.dbcinfo.items():
                    if i == k:
                        special_dbc = {k: v}
                        dbcinfo_all = special_dbc
        # param node&sendtype:
        for dbc_name, dbc_values in dbcinfo_all.items():
            rxlist_msginfos = list()
            txlist_msginfo = list()
            for msg_values in dbc_values:
                if self.node == msg_values['node']:
                    txlist_msginfo.append(msg_values)
                    self.txlist_msginfo.append(msg_values)
                elif self.node != msg_values['node'] and self.node != 'VECTOR__INDEPENDENT_SIG_MSG':
                    for siginfo in msg_values['siglist']:
                        # 找到所有节点收到的msg，但是此msg包含的信号可能没有map上
                        if self.node in siginfo['receiver']:
                            self.rxlist_msginfo_check.append(msg_values)
                            rxlist_msginfos.append(msg_values)
                            break
            self.dbc_dict_rx.update({dbc_name: rxlist_msginfos})

            # 寻找节点收到的msg，仅提取已经map了的
            rxlist_msginfo = copy.deepcopy(self.rxlist_msginfo_check)
            for _ in self.rxlist_msginfo_check:
                for rx_msg_values in rxlist_msginfo:
                    for rx_siginfo in rx_msg_values['siglist']:
                        if self.node not in rx_siginfo['receiver']:
                            rx_msg_values['siglist'].remove(rx_siginfo)
            allmsginfo = txlist_msginfo + rxlist_msginfo
            self.rxlist_msginfo += rxlist_msginfo
            self.dbc_dict.update({dbc_name: allmsginfo})
            self.rxlist_msginfo_check.clear()

        # param box:
        if self.box != 'default' or None:
            all_mapped_msg = self.txlist_msginfo + self.rxlist_msginfo
            specialmsg = re.split(',', self.box)
            for msgbox in all_mapped_msg:
                if msgbox['name'] in specialmsg:
                    self.msgbox.append(msgbox)
        self.allmsginfo = self.txlist_msginfo + self.rxlist_msginfo
        print(self.dbc_dict)
        print('解析完成')

        return self.txlist_msginfo, self.rxlist_msginfo, self.msgbox


def main():
    # ParseDbc().parseprograme()
    ParseDbc().switchs()


if __name__ == '__main__':
    main()
