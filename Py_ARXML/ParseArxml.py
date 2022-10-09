# _*_ coding:utf-8 _*_

# -------------------------------------------------------------------------------
# Name:        ParseArxml
# Purpose:     Please refer to the instruction document for details
#
# Author:      JiaXing
#
# Created:     2020/06/06
# Copyright:   (c) user 2020
# Version:     v3.0
# Last revision date: 2020/06/09
# -------------------------------------------------------------------------------


from xml.etree import ElementTree as ET
import configparser
import os
import re
from pprint import pprint
from encode2utf8 import changecode, get_encode_info
# from addrunnables import AddRunnable

# runnable = AddRunnable()

def addtodict(thedict, key_a, key_b, val):
    """
    for example
    :param thedict:Dt_RECORD_xxx
    :param key_a:Dt_name
    :param key_b:CATEGORY
    :param val:STRUCTURE
    :return:
    """
    if key_a in thedict:
        thedict[key_a].update({key_b: val})
    else:
        thedict.update({key_a: {key_b: val}})


class ArxmlInfo:
    """

    """

    def __init__(self, xmlpathitem, addrunnable_filename=None):
        """
        xmlpathitem include: aurix_path; rcar_path; appmiddleware_path
        """
        # 打开并读取配置文件
        # os.system(r'config.ini')
        config = configparser.ConfigParser()
        config.read(r'..\config.ini', encoding='utf-8')
        # get xml file
        origin_xmlfile_path = config.get('Arxml_Property', xmlpathitem)
        # 判断路径是否为目录
        if os.path.isdir(origin_xmlfile_path) is True:
            origin_xmlfile_path = origin_xmlfile_path + '\\' + addrunnable_filename
        # convert code to utf-8
        print('正在检查XML文件是否需要进行编码转换')
        res = get_encode_info(origin_xmlfile_path)
        if res != 'utf-8':
            print('正在执行XML文件编码转换...')
            changecode(r'../SourceInput/Arxml')
        # delete the name space
        with open(origin_xmlfile_path, 'r+', encoding='utf-8') as origin_xmlfile:
            for x in origin_xmlfile.readlines():
                if x.find('<AUTOSAR') == 0:
                    test = 1
                    break
                else:
                    test = 0
        if test == 1:
            with open(origin_xmlfile_path, 'r', encoding='utf-8') as origin_xmlfile:
                with open('xmlwrite.arxml', 'w+', encoding='utf-8') as xmlwrite:
                    switch = 0
                    for i in origin_xmlfile.readlines():
                        if i.find('<AUTOSAR') == 0:
                            switch = 1
                            continue
                        if i.find('</AUTOSAR') == 0:
                            switch = 0
                        if switch == 1:
                            xmlwrite.writelines(i)
                self.xmlfile_path = 'xmlwrite.arxml'
        else:
            self.xmlfile_path = origin_xmlfile_path

        tree = ET.parse(self.xmlfile_path)
        self.root = tree.getroot()

        # dict
        self.datatypes_dict = dict()
        self.swcport_dict = dict()
        self.type_reference = dict()
        self.structure_ele = dict()
        self.dataaccess = dict()
        self.Structure_Ele = dict()
        self.structure_datatype = dict()

        # 自定义测试
        self.msginitcheck = ()
        self.Data_Types = self.datatypes_dict

    def get_datatypes(self):
        """
        1. DataTypes of IMPLEMENTATION-DATA-TYPE:
            include Dt_name and the category, array_size and element or element_reference
            category include value(ENUM), structure and array

        :return:
        """
        for main_layer in self.root:
            for pack in main_layer:
                if pack.text == 'DataTypes':
                    for datatypes in main_layer.iter():
                        # 1. DataTypes of IMPLEMENTATION-DATA-TYPE
                        if datatypes.tag == 'IMPLEMENTATION-DATA-TYPE':
                            for IMPLEMENTATION_DATA_TYPE in datatypes.iter():
                                # get structure info
                                if IMPLEMENTATION_DATA_TYPE.tag == 'CATEGORY' and IMPLEMENTATION_DATA_TYPE.text == 'STRUCTURE':
                                    dename_x = list()
                                    for structureinfo in datatypes.iter():
                                        if structureinfo.tag == 'SHORT-NAME' and 'Dt_' in structureinfo.text:
                                            index = 0
                                            Dt_name = structureinfo.text
                                            addtodict(self.datatypes_dict, Dt_name, 'CATEGORY', 'STRUCTURE')
                                            self.datatypes_dict[Dt_name]['Ele'] = dict()
                                            self.Structure_Ele[Dt_name] = []
                                            self.structure_datatype[Dt_name] = dict()
                                            # find elements of dt_record
                                        if structureinfo.tag == 'IMPLEMENTATION-DATA-TYPE-ELEMENT':
                                            for x in structureinfo.iter():
                                                if x.tag == 'SHORT-NAME':
                                                    dename_x.append(x.text)
                                                    signame = x.text
                                                if x.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
                                                    sigdatatype = re.split('/', x.text)[-1]
                                            self.structure_ele.update({Dt_name: dename_x})
                                            self.structure_datatype[Dt_name].update({signame:sigdatatype})
                                        if structureinfo.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
                                            Ele_ref = re.split('/', structureinfo.text)[-1]
                                            self.Structure_Ele[Dt_name].append(Ele_ref)
                                            # self.datatypes_dict.update({Dt_name: {'Ele': {str(index): Ele_ref}}})
                                            self.datatypes_dict[Dt_name]['Ele'].update({str(index): Ele_ref})
                                            index += 1

                                # get array info
                                if IMPLEMENTATION_DATA_TYPE.tag == 'CATEGORY' and IMPLEMENTATION_DATA_TYPE.text == 'ARRAY':
                                    for arrayinfo in datatypes.iter():
                                        if arrayinfo.tag == 'SHORT-NAME' and 'Dt_' in arrayinfo.text:
                                            Dt_name = arrayinfo.text
                                            addtodict(self.datatypes_dict, Dt_name, 'CATEGORY', 'ARRAY')
                                            self.datatypes_dict[Dt_name]['Ele'] = dict()
                                        if arrayinfo.tag == 'ARRAY-SIZE':
                                            arraysize = arrayinfo.text
                                        try:
                                            if arrayinfo.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
                                                Ele_ref = re.split('/', arrayinfo.text)[-1]
                                                # self.datatypes_dict.update({Dt_name: {'Ele': {str(index): Ele_ref}}})
                                                self.datatypes_dict[Dt_name]['Ele'].update(
                                                    {'ArraySize': arraysize, 'Ele_Ref': Ele_ref})
                                        except:
                                            print('can`t find arraysize from' + Dt_name)
                                # get value info
                                if IMPLEMENTATION_DATA_TYPE.tag == 'CATEGORY' and IMPLEMENTATION_DATA_TYPE.text == 'VALUE':
                                    for valueinfo in datatypes.iter():
                                        if valueinfo.tag == 'SHORT-NAME' and 'Dt_' in valueinfo.text:
                                            Dt_name = valueinfo.text
                                            addtodict(self.datatypes_dict, Dt_name, 'CATEGORY', 'VALUE')
                                            self.datatypes_dict[Dt_name]['Ele'] = dict()
                                        if valueinfo.tag == 'BASE-TYPE-REF':
                                            Ele_ref = re.split('/', valueinfo.text)[-1]
                                            # self.datatypes_dict.update({Dt_name: {'Ele': {str(index): Ele_ref}}})
                                            self.datatypes_dict[Dt_name]['Ele'].update({'BaseType': Ele_ref})
                                # get enum info
                                if IMPLEMENTATION_DATA_TYPE.tag == 'CATEGORY' and IMPLEMENTATION_DATA_TYPE.text == 'TYPE_REFERENCE':
                                    for enuminfo in datatypes:  # 仅仅循环下一层
                                        if enuminfo.tag == 'CATEGORY' and enuminfo.text == 'TYPE_REFERENCE':
                                            for enuminfo_2 in datatypes.iter():
                                                if enuminfo_2.tag == 'SHORT-NAME':
                                                    Dt_name = enuminfo_2.text
                                                    addtodict(self.datatypes_dict, Dt_name, 'CATEGORY', 'ENUM')
                                                    self.datatypes_dict[Dt_name]['Ele'] = dict()
                                                if enuminfo_2.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
                                                    Ele_ref = re.split('/', enuminfo_2.text)[-1]
                                                    self.datatypes_dict[Dt_name]['Ele'].update({'BaseType': Ele_ref})
                # self.swcport_dict, self.dataaccess
                if pack.text == 'ComponentTypes':
                    # find model name
                    count = 0
                    for swc in main_layer.iter('SHORT-NAME'):
                        count += 1
                        if count == 2:
                            modelname = swc.text
                            self.swcport_dict[modelname] = dict()
                            self.swcport_dict[modelname]['PPORT'] = dict()
                            self.swcport_dict[modelname]['RPORT'] = dict()
                            self.dataaccess[modelname] = dict()
                            break
                    # get pport info
                    piname_list = list()  # just used by checking
                    for componenttypes in main_layer.iter():
                        if componenttypes.tag == 'P-PORT-PROTOTYPE':
                            dename_list = list()
                            for portsinfo in componenttypes.iter():
                                if 'Pp' in portsinfo.text and portsinfo.tag == 'SHORT-NAME':
                                    pportname = portsinfo.text
                                if portsinfo.tag == 'DATA-ELEMENT-REF':
                                    dename = re.split('/', portsinfo.text)[-1]
                                    dename_list.append(dename)
                                if portsinfo.tag == 'PROVIDED-INTERFACE-TREF':
                                    piname = re.split('/', portsinfo.text)[-1]
                                    piname_list.append(piname)
                            self.swcport_dict[modelname]['PPORT'].update({pportname: {'DataEleRef': dename_list, 'Piname': piname}})
                        if componenttypes.tag == 'R-PORT-PROTOTYPE':
                            dename_list = list()
                            for portsinfo in componenttypes.iter():
                                if 'Pp' in portsinfo.text and portsinfo.tag == 'SHORT-NAME':
                                    pportname = portsinfo.text
                                if portsinfo.tag == 'DATA-ELEMENT-REF':
                                    dename = re.split('/', portsinfo.text)[-1]
                                    dename_list.append(dename)
                                if portsinfo.tag == 'REQUIRED-INTERFACE-TREF':
                                    piname = re.split('/', portsinfo.text)[-1]
                                    piname_list.append(piname)
                            self.swcport_dict[modelname]['RPORT'].update({pportname: {'DataEleRef': dename_list, 'Piname': piname}})
                        # get runnable info
                        if componenttypes.tag == 'RUNNABLE-ENTITY':
                            for rname in componenttypes:
                                if rname.tag == 'SHORT-NAME':
                                    runnablename = rname.text
                                    self.dataaccess[modelname][runnablename] = dict()
                                    self.dataaccess[modelname][runnablename]['RPORT'] = dict()
                                    self.dataaccess[modelname][runnablename]['PPORT'] = dict()
                            for RUNNABLE_ENTITY in componenttypes.iter():
                                if RUNNABLE_ENTITY.tag == 'VARIABLE-ACCESS':
                                    for VARIABLE_ACCESS in RUNNABLE_ENTITY.iter():
                                        if VARIABLE_ACCESS.tag == 'SHORT-NAME':
                                            sig_name = VARIABLE_ACCESS.text
                                            sr_name = re.split('_', VARIABLE_ACCESS.text, maxsplit=1)
                                            check_sr = sr_name[0]
                                            pportname_runnable = sr_name[1]
                                        if VARIABLE_ACCESS.tag == 'PORT-PROTOTYPE-REF':
                                            piname_runnable = re.sub('Pp', 'Pi', re.split('/', VARIABLE_ACCESS.text)[-1])
                                        if VARIABLE_ACCESS.tag == 'TARGET-DATA-PROTOTYPE-REF':
                                            dename_runnable = re.split('/', VARIABLE_ACCESS.text)[-1]
                                    if check_sr == 'REC':
                                        mode = 'Read'
                                        self.dataaccess[modelname][runnablename]['RPORT'].update({pportname_runnable: {'Mode': mode, 'Dename': dename_runnable, 'Piname': piname_runnable}})
                                    elif check_sr == 'SEND':
                                        mode = 'Write'
                                        self.dataaccess[modelname][runnablename]['PPORT'].update({pportname_runnable: {'Mode': mode, 'Dename': dename_runnable, 'Piname': piname_runnable}})
                                    else:
                                        print('\033[0;31mcheck_sr error:  ' + check_sr+'\033[0m  ' + sig_name)
                # self.type_reference
                if pack.text == 'PortInterfaces':
                    for portinterfaces in main_layer.iter():
                        if portinterfaces.tag == 'SENDER-RECEIVER-INTERFACE':
                            for typeref in portinterfaces.iter():
                                if typeref.tag == 'SHORT-NAME' and 'Pi' in typeref.text:
                                    piname_typeref = typeref.text
                                    self.type_reference[piname_typeref] = dict()
                                if typeref.tag == 'VARIABLE-DATA-PROTOTYPE':
                                    for VARIABLE_DATA_PROTOTYPE in typeref.iter():
                                        if VARIABLE_DATA_PROTOTYPE.tag == 'SHORT-NAME':
                                            dename_typeref = VARIABLE_DATA_PROTOTYPE.text
                                        if VARIABLE_DATA_PROTOTYPE.tag == 'TYPE-TREF':
                                            dt_typeref = re.split('/', VARIABLE_DATA_PROTOTYPE.text)[-1]
                                            self.type_reference[piname_typeref].update({dename_typeref: dt_typeref})



        print(self.datatypes_dict)
        print(self.swcport_dict)
        print(self.type_reference)
        print(self.structure_ele)
        print(self.dataaccess)
        print(self.structure_datatype)

    def siginitcheck(self):
        """
        检查模型里面的报文初始化方式是否是reference
        :return:
        """
        print('\033[1;36mreference检查:\033[0m')

        ckres = 0
        for main_layer in self.root:
            for pack in main_layer:
                if pack.text == 'ComponentTypes':
                    for componenttypes in main_layer.iter():
                        if componenttypes.tag == 'P-PORT-PROTOTYPE':
                            for P_PORT_PROTOTYPE in componenttypes.iter():
                                if P_PORT_PROTOTYPE.tag == 'SHORT-NAME':
                                    ppname = P_PORT_PROTOTYPE.text
                                if P_PORT_PROTOTYPE.tag == 'NONQUEUED-SENDER-COM-SPEC':
                                    listr = list()
                                    for nscs in P_PORT_PROTOTYPE.iter():
                                        if nscs.tag == 'DATA-ELEMENT-REF':
                                            dename = re.split('/', nscs.text)[-1]
                                        listr.append(nscs.tag)
                                    if 'CONSTANT-REF' not in listr:
                                        ckres = 1
                                        print(ppname+'{:^10}'.format('*')+dename)
        if ckres == 0:
            print('\033[1;32mPASS\033[0m')
        else:
            print('\033[0;31m以上信号的初始化方式不是reference\033[0m')


if __name__ == '__main__':
    # 文件夹，os.listdir里面输入和test_xmlpath一样的地址
    # for i in os.listdir(r'./Arxml/fotes'):
    #     arxml = ArxmlInfo('test_xmlpath', i)
    # 非文件夹
    arxml = ArxmlInfo('test_xmlpath')

    arxml.get_datatypes()

    # arxml.siginitcheck()