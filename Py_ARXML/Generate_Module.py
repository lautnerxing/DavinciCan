# _*_ coding:utf-8 _*_

# -------------------------------------------------------------------------------
# Name:        Generate_Module
# Purpose:     Generate Arxml for DaVinci Developer, from DBC
#              Please refer to the instruction document for details
#
# Author:      JiaXing
#
# Created:     2020/08/27
# Copyright:   (c) user 2020
# Version:     v3.0
# Last revision date: 2020/09/11
# -------------------------------------------------------------------------------

from Py_DBC import ParseDBC
import re
import os
import time
from pprint import pprint
import configparser


class GenModule(object):
    """

    """

    def __init__(self):
        # Import Templates:
        with open(r'../Templates/Gen_Module/MainFile.xml', 'r') as mainfile:
            self.mainfile = ''.join(mainfile.readlines())
        with open(r'../Templates/Gen_Module/Replace_Autosar_platform.xml', 'r') as autosar:
            self.autosar = ''.join(autosar.readlines())
        with open(r'../Templates/Gen_Module/Replace_Dt_signame.xml', 'r') as Dt_signame:
            self.Dt_signame = ''.join(Dt_signame.readlines())
        with open(r'../Templates/Gen_Module/Replace_Dt_signame_array.xml', 'r') as Dt_signame_array:
            self.Dt_signame_array = ''.join(Dt_signame_array.readlines())
        with open(r'../Templates/Gen_Module/Replace_array_CONSTANT-SPECIFICATION.xml', 'r') as array_CS:
            self.array_CS = ''.join(array_CS.readlines())
        with open(r'../Templates/Gen_Module/Replace_record_CONSTANT-SPECIFICATION.xml', 'r') as record_CS:
            self.record_CS = ''.join(record_CS.readlines())
        with open(r'../Templates/Gen_Module/Replace_busin_NONQUEUED-RECEIVER-COM-SPEC.xml', 'r') as busin_NRCS:
            self.busin_NRCS = ''.join(busin_NRCS.readlines())
        with open(r'../Templates/Gen_Module/Replace_busout_NONQUEUED-SENDER-COM-SPEC.xml', 'r') as busout_NSCS:
            self.busout_NSCS = ''.join(busout_NSCS.readlines())
        with open(r'../Templates/Gen_Module/Replace_P-PORT-PROTOTYPE.xml', 'r') as P_Port:
            self.P_Port = ''.join(P_Port.readlines())
        with open(r'../Templates/Gen_Module/Replace_R-PORT-PROTOTYPE.xml', 'r') as R_Port:
            self.R_Port = ''.join(R_Port.readlines())
        with open(r'../Templates/Gen_Module/Replace_initvalue.xml', 'r') as initvalue:
            self.initvalue = ''.join(initvalue.readlines())
        with open(r'../Templates/Gen_Module/Replace_initvalue_recordsig.xml', 'r') as init_record:
            self.init_record = ''.join(init_record.readlines())
        with open(r'../Templates/Gen_Module/Replace_busin_IP.xml', 'r') as busin_IP:
            self.busin_IP = ''.join(busin_IP.readlines())
        with open(r'../Templates/Gen_Module/Replace_busout_IP.xml', 'r') as busout_IP:
            self.busout_IP = ''.join(busout_IP.readlines())
        with open(r'../Templates/Gen_Module/Replace_Dt_record.xml', 'r') as Dt_record:
            self.Dt_record = ''.join(Dt_record.readlines())
        with open(r'../Templates/Gen_Module/Replace_Dt_record_IDTE.xml', 'r') as Dt_record_IDTE:
            self.Dt_record_IDTE = ''.join(Dt_record_IDTE.readlines())
        with open(r'../Templates/Gen_Module/Replace_busin_VARIABLE-DATA-PROTOTYPE.xml', 'r') as busin_VDP:
            self.busin_VDP = ''.join(busin_VDP.readlines())
        with open(r'../Templates/Gen_Module/Replace_busout_VARIABLE-DATA-PROTOTYPE.xml', 'r') as busout_VDP:
            self.busout_VDP = ''.join(busout_VDP.readlines())
        with open(r'../Templates/Gen_Module/Replace_Pi_SENDER-RECEIVER-INTERFACE.xml', 'r') as Pi_SRI:
            self.Pi_SRI = ''.join(Pi_SRI.readlines())
        with open(r'../Templates/Gen_Module/Replace_ApplicationHost.xml', 'r') as app:
            self.app = ''.join(app.readlines())

        # Import data from dbc:
        parsedbc = ParseDBC.ParseDbc()
        parsedbc.switchs()
        self.txlist_msginfo = parsedbc.txlist_msginfo
        self.rxlist_msginfo = parsedbc.rxlist_msginfo
        self.msginfo = parsedbc.allmsginfo
        pprint(self.txlist_msginfo)
        pprint(self.rxlist_msginfo)

        # 打开并读取配置文件
        config = configparser.ConfigParser()
        config.read(r'..\config.ini', encoding='utf-8')
        self.node = config.get('Dbc_Property', 'node')

    def creat(self):
        """

        :return:
        """
        outsig_NSCS_str = str()
        insig_NRCS_str = str()
        busin_VDP_str = ''
        busout_VDP_str = ''
        busin_IP_str = ''
        busout_IP_str = ''
        Dt_signame_str = ''
        # BusIn and BusOut
        for busmsg in self.msginfo:
            for bussig in busmsg['siglist']:
                bus_signame = bussig['name']
                bus_sigsize = bussig['size']
                bus_sigvaluetype = bussig['valuetype']
                bus_datatype = bussig['datatype']
                bus_outorin = bussig['receiver']
                if bus_sigsize == 1:
                    bus_datatype = 'boolean'
                elif bus_sigvaluetype == '-':
                    bus_datatype = re.sub('uint', 'sint', bus_datatype)
                    if bus_sigsize <= 16:
                        bus_datatype = 'sint16'
                    elif bus_sigsize <= 32:
                        bus_datatype = 'sint32'
                    elif bus_sigsize <= 64:
                        bus_datatype = 'sig_array'
                elif bus_sigvaluetype == '+':
                    if bus_sigsize <= 8:
                        bus_datatype = 'uint8'
                    elif bus_sigsize <= 16:
                        bus_datatype = 'uint16'
                    elif bus_sigsize <= 32:
                        bus_datatype = 'uint32'
                    elif bus_sigsize <= 64:
                        bus_datatype = 'sig_array'
                if bus_datatype != 'sig_array':
                    if bus_outorin == self.node:
                        insig_NRCS = self.busin_NRCS.format(signame=bus_signame, constant_ref='/DaVinci/InitValueSpec_Reserved')
                        insig_NRCS_str += insig_NRCS
                    elif bus_outorin != self.node:
                        outsig_NSCS = self.busout_NSCS.format(signame=bus_signame, constant_ref='/DaVinci/InitValueSpec_Reserved')
                        outsig_NSCS_str += outsig_NSCS
                    # Replace_Dt_signame.xml
                    Dt_signame = self.Dt_signame.format(signame=bus_signame, sigtype=bus_datatype)
                    Dt_signame_str += Dt_signame
                elif bus_datatype == 'sig_array':
                    if bus_outorin == self.node:
                        insig_NRCS = self.busin_NRCS.format(signame=bus_signame, constant_ref='/Constants/C_ARRAY_8_uint8')
                        insig_NRCS_str += insig_NRCS
                    elif bus_outorin != self.node:
                        outsig_array_NSCS = self.busout_NSCS.format(signame=bus_signame, constant_ref='/Constants/C_ARRAY_8_uint8')
                        outsig_NSCS_str += outsig_array_NSCS
                # Replace_busin_VARIABLE-DATA-PROTOTYPE.xml & Replace_busout_VARIABLE-DATA-PROTOTYPE.xml
                # Replace_busin_IP.xml & Replace_busout_IP.xml
                if bus_outorin == self.node:
                    busin_VDP = self.busin_VDP.format(signame=bus_signame)
                    busin_VDP_str += busin_VDP
                    busin_IP = self.busin_IP.format(signame=bus_signame)
                    busin_IP_str += busin_IP
                elif bus_outorin != self.node:
                    busout_VDP = self.busout_VDP.format(signame=bus_signame)
                    busout_VDP_str += busout_VDP
                    busout_IP = self.busout_IP.format(signame=bus_signame)
                    busout_IP_str += busout_IP
        # Replace_P_PORT_PROTOTYPE.xml and Replace_R_PORT_PROTOTYPE.xml
        P_Port_Prototype_str = ''
        R_Port_Prototype_str = ''
        Pi_SRI_str = ''
        for pport_msginfo in self.rxlist_msginfo:
            pport_msgname = pport_msginfo['name']
            # 2021/03/05: NoMsgSendType`s cycle time, user defend 1ms
            try:
                pport_cycletime = pport_msginfo['cycletime']
            except:
                pport_cycletime = '1ms'
                print('\033[1;33mWarning\033[0m 报文没有发送方式,cycletime暂设置为1ms  '+pport_msgname)

            P_Port_Prototype = self.P_Port.format(msgname=pport_msgname, cycletime=pport_cycletime)
            P_Port_Prototype_str += P_Port_Prototype
            # Replace_Pi_SENDER-RECEIVER-INTERFACE.xml
            Pi_SRI = self.Pi_SRI.format(module='Com', msgname=pport_msgname, cycletime=pport_cycletime)
            Pi_SRI_str += Pi_SRI
        for rport_msginfo in self.txlist_msginfo:
            rport_msgname = rport_msginfo['name']
            # 2021/03/05: NoMsgSendType`s cycle time, user defend 1ms
            try:
                rport_cycletime = rport_msginfo['cycletime']
            except:
                rport_cycletime = '1ms'
                print('\033[1;33mWarning\033[0m 报文没有发送方式,cycletime暂设置为1ms  ' + rport_cycletime)
            R_Port_Prototype = self.R_Port.format(msgname=rport_msgname, cycletime=rport_cycletime)
            R_Port_Prototype_str += R_Port_Prototype
            # Replace_Pi_SENDER-RECEIVER-INTERFACE.xml
            Pi_SRI = self.Pi_SRI.format(module='VMS', msgname=rport_msgname, cycletime=rport_cycletime)
            Pi_SRI_str += Pi_SRI
        # Replace_array_CONSTANT-SPECIFICATION.xml & Replace_record_CONSTANT-SPECIFICATION.xml
        array_CS_str = ''
        initvale_str = ''
        record_CS_str = ''
        # Replace_Dt_signame.xml
        Dt_signame_array_str = ''
        # Replace_Dt_record.xml
        Dt_record_str = ''
        for msginfo in self.msginfo:
            initvale_recordsig_str = ''
            Dt_record_IDTE_str = ''
            msgname = msginfo['name']
            check_ifarraymsg = 0
            for siginfo in msginfo['siglist']:
                signame = siginfo['name']
                sigsize = siginfo['size']
                sigtype = siginfo['datatype']
                if 32 < sigsize <= 64:
                    check_ifarraymsg = 1
                    count = int(sigsize/8)
                    for i in range(0, count):
                        initvale_str += self.initvalue
                    array_CS = self.array_CS.format(msgname=msgname, signame=signame, Replace_initvalue=initvale_str)
                    array_CS_str += array_CS
                    initvale_str = ''
                    # Replace_Dt_signame_array.xml
                    Dt_signame_array = self.Dt_signame_array.format(signame=signame)
                    Dt_signame_array_str += Dt_signame_array
                    # Replace_Dt_record_IDTE.xml
                    Dt_record_IDTE = self.Dt_record_IDTE.format(signame=signame, signame_or_sigtype='Dt_'+signame, site_package='DataTypes')
                    Dt_record_IDTE_str += Dt_record_IDTE
                else:
                    initvale_recordsig = self.init_record.format(signame=signame)
                    initvale_recordsig_str += initvale_recordsig
                    # Replace_Dt_record_IDTE.xml
                    Dt_record_IDTE = self.Dt_record_IDTE.format(signame=signame, signame_or_sigtype=sigtype, site_package='AUTOSAR_Platform/ImplementationDataTypes')
                    Dt_record_IDTE_str += Dt_record_IDTE
            # Replace_array_CONSTANT-SPECIFICATION.xml & Replace_record_CONSTANT-SPECIFICATION.xml
            if check_ifarraymsg == 0:
                record_CS = self.record_CS.format(msgname=msgname, Replace_initvalue_recordsig=initvale_recordsig_str)
                record_CS_str += record_CS
            # Replace_Dt_record.xml
            Dt_record = self.Dt_record.format(msgname=msgname, Replace_Dt_record_IDTE=Dt_record_IDTE_str)
            Dt_record_str += Dt_record

        # 生成xml文件到Gen目录下
        with open(r'../Templates/Gen_Module/MainFile.xml', 'r') as f:
            with open(r'..\Gen\Module\s.arxml', 'w') as s:
                mainxml = ''.join(f.readlines())
                xml = mainxml.format(Replace_Autosar=self.autosar,
                                    Replace_busout_NONQUEUED_SENDER_COM_SPEC=outsig_NSCS_str,
                                    Replace_P_PORT_PROTOTYPE=P_Port_Prototype_str,
                                    Replace_busin_NONQUEUED_RECEIVER_COM_SPEC=insig_NRCS_str,
                                    Replace_R_PORT_PROTOTYPE=R_Port_Prototype_str,
                                    Replace_array_CONSTANT_SPECIFICATION=array_CS_str,
                                    Replace_record_CONSTANT_SPECIFICATION=record_CS_str,
                                    Replace_Dt_signame=Dt_signame_str,
                                    Replace_Dt_signame_array=Dt_signame_array_str,
                                    Replace_Dt_record=Dt_record_str,
                                    Replace_busin_VARIABLE_DATA_PROTOTYPE=busin_VDP_str,
                                    Replace_busin_IP=busin_IP_str,
                                    Replace_busout_VARIABLE_DATA_PROTOTYPE=busout_VDP_str,
                                    Replace_busout_IP=busout_IP_str,
                                    Replace_Pi_SENDER_RECEIVER_INTERFACE=Pi_SRI_str)
                s.write(xml)
        check_ifnewproject = int(input('输入序号确认是否为新工程： 1是  2不是   '))
        with open(r'..\Gen\Module\s.arxml', 'r') as s:
            with open(r'..\Gen\Module\CtApCom.arxml', 'w') as c:
                if check_ifnewproject == 1:
                    print('\033[1;33m选择 1 生成ApplicationHost\033[0m')
                    for line in s:
                        if line.find('<!-- content -->') == 0:
                            c.write(self.app)
                        else:
                            c.write(line)
                if check_ifnewproject == 2:
                    print('\033[1;33m选择 2 不生成ApplicationHost\033[0m')
                    for line in s:
                        if line.find('<!-- content -->') == 0:
                            pass
                        else:
                            c.write(line)

        # 重新生成uuid
        print('正在重新生成随机uuid')
        with open(r'..\Gen\Module\CtApCom.arxml', 'r') as s:
            with open(r'..\Gen\Module\uuid.arxml', 'w') as tmp:
                for line in s.readlines():
                    # if 'UUID=' in line:
                    #     # 随机生成一个uuid
                    #     random_uuid = str(uuid.uuid4()).upper()
                    #     # 提取出文本中该行uuid并生成要替换的内容
                    #     s = re.split(r'"', line)
                    #     s[1] = random_uuid
                    #     replace_line = '"'.join(s)
                    #     tmp.writelines(replace_line)
                    #     continue
                    # 去掉多余的空行
                    if line == '\n':
                        line = line.strip('\n')
                    tmp.write(line)
        os.remove(r'..\Gen\Module\CtApCom.arxml')
        os.remove(r'..\Gen\Module\s.arxml')
        os.renames(r'..\Gen\Module\uuid.arxml', r'..\Gen\Module\CtApCom_(' + time.strftime("%Y_%m_%d %Hh%Mm%Ss") + ').arxml')
        print(r'文件生成完毕，文件路径为..\Gen')
        os.startfile(r'..\Gen\Module')


def main():
    gen = GenModule()
    gen.creat()


if __name__ == '__main__':
    main()
