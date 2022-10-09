from Py_ARXML import ParseArxml
import re
import os
import configparser


class AddRunnable:
    """
    1. Update the Templates path
    2. Update runnable arxml path in config.ini
    """

    def __init__(self):
        # 打开并读取配置文件
        # os.system(r'config.ini')
        config = configparser.ConfigParser()
        config.read(r'..\config.ini', encoding='utf-8')
        # get xml filedir
        runnable_path = config.get('Arxml_Property', 'runnable_xmlpath')
        # Import Templates
        with open(r'..\Templates\RUNNABLES\runnable.arxml', 'r') as f:
            self.runnable_arxml = ''.join(f.readlines())
        with open(r'..\Templates\RUNNABLES\TIMING-EVENT.Template', 'r') as f:
            self.timing_event = ''.join(f.readlines())
        with open(r'..\Templates\RUNNABLES\RUNNABLE-ENTITY.Template', 'r') as f:
            self.runnable_entity = ''.join(f.readlines())
        with open(r'..\Templates\RUNNABLES\sendVALUES.Template', 'r') as f:
            self.sendvalues = ''.join(f.readlines())
        with open(r'..\Templates\RUNNABLES\recVALUES.Template', 'r') as f:
            self.recvalues = ''.join(f.readlines())
        # 判断是否为目录
        if os.path.isdir(runnable_path) is True:
            runnable_xmlnames = os.listdir(runnable_path)
            isdir = 1
        else:
            runnable_xmlnames = [runnable_path]
            isdir = 0
        # get xml filename
        # self.swcport = ParseArxml.ArxmlInfo('runnable_xmlpath')
        for runnable_xmlname in runnable_xmlnames:
            # self.filename = re.split(r'\\', runnable_dir)[-1]
            # self.filename = runnable_xmlname
            # 输入文件
            if isdir == 0:
                self.filename = re.split(r'\\', runnable_path)[-1]
                with open(runnable_path, 'r', encoding='utf-8') as f:
                    self.vms_arxml = ''.join(f.readlines())
            elif isdir == 1:
                self.filename = runnable_xmlname
                with open(runnable_path+'\\'+self.filename, 'r', encoding='utf-8') as f:
                    self.vms_arxml = ''.join(f.readlines())
            if not re.search('InternalBehavior</SHORT-NAME>', self.vms_arxml):
                print('\033[1;31m在XML文件里未找到InternalBehavior定位点')
                print('请打开DEV模型检查该模块的Package属性是否两项均设置为automaticall\033[0m')
                print('程序终止，输出文件失败')
                exit()
            if re.search('<RUNNABLES>', self.vms_arxml):
                print('\033[1;31mXML文件已经存在runnable，需要删除后再运行程序\033[0m'+'  '+self.filename)
                print('程序终止，输出文件失败')
                exit()

            self.finalfile = ''
            # 提前寻找模块包含的所有周期
            cycle_time_list = list()
            self.swcport = ParseArxml.ArxmlInfo('runnable_xmlpath', self.filename)
            self.swcport.get_datatypes()
            self.portinfo = self.swcport.swcport_dict
            # print(self.portinfo)
            for modlename, srport in self.portinfo.items():
                for sendtype, portname in srport.items():
                    for ppname, deinfo in portname.items():
                        piname = deinfo['Piname']
                        cycletime = re.split('_', piname)[-1]
                        if 'ms' in cycletime:
                            cycle_time_list.append(cycletime)
                        else:
                            print('\033[1;31m该报文程序无法添加进runnable，请检查模型：'+ppname+'\033[0m')
            self.cycle_time = list(set(cycle_time_list))
            print('找到模块里面所有cycletime的集合:')
            print(self.cycle_time)
            # 开始添加runnable
            self.addxmlrunnable()

    def getrunnable(self):
        """

        :return:
        """
        event_str = ''
        entity_str = ''
        sendvalues = ''
        recvalues = ''
        for cycle_time in self.cycle_time:
            for modlename, srport in self.portinfo.items():
                for sendtype, portname in srport.items():
                    for ppname, deinfo in portname.items():
                        piname = deinfo['Piname']
                        delist = deinfo['DataEleRef']
                        cktime = re.split('_', piname)[-1]
                        if cktime == cycle_time:
                            if sendtype == 'PPORT':
                                rstype = 'SEND'
                                for dename in delist:
                                    res = self.sendvalues.format(sendtype=rstype, piname=piname, dename=dename,
                                                                 modlename=modlename, ppname=ppname)
                                    sendvalues += res + '\n'
                            if sendtype == 'RPORT':
                                rstype = 'REC'
                                for dename in delist:
                                    res = self.recvalues.format(sendtype=rstype, piname=piname, dename=dename,
                                                                 modlename=modlename, ppname=ppname)
                                    recvalues += res + '\n'
            res_runnable = self.runnable_entity.format(modlename=modlename, cycle_time=cycle_time)
            res_runnable = res_runnable.replace('recvalues', recvalues).replace('sendvalues', sendvalues)
            entity_str += res_runnable + '\n'
            sendvalues = ''
            recvalues = ''
        for cycle_time in self.cycle_time:
            cycle_time_s = int(re.match('\d+', cycle_time).group()) / 1000
            res = self.timing_event.format(modlename=modlename, cycle_time=cycle_time, cycle_time_s=str(cycle_time_s))
            event_str += res + '\n'
        self.finalfile = self.runnable_arxml.replace('replaceEVENTS', event_str).replace('replaceRUNNABLES', entity_str)
        # with open('./fotes.arxml','w') as ff:
        #     ff.write(self.finalfile)

    def addxmlrunnable(self):
        """

        :return:
        """
        self.getrunnable()
        with open(r'..\Gen\runnable.txt', 'w+', encoding='utf-8') as f:
            b = re.sub('InternalBehavior</SHORT-NAME>', 'InternalBehavior</SHORT-NAME>'+'\n'
                                                        'IFSA', self.vms_arxml)  # 适用于大部分xml文件，用于定位文本插入点
            # with open('./fotes.arxml','w', encoding='utf-8') as ff:
            #     ff.write(b)
            b = b.replace('IFSA', self.finalfile)
            f.write(b)
        # 快速去除空行并生成带有runnable的vms文件
        switch = 0
        with open(r'..\Gen\runnable.txt', 'r', encoding='utf-8') as fr, \
                open(r'..\Gen\Runnable_module\{filename}'.format(filename=self.filename), 'w', encoding='utf-8') as fd:
            for text in fr.readlines():
                if text.split():
                    # 去除<PORT-API-OPTIONS>的影响，这会导致导入DEV失败
                    if text.find('              <PORT-API-OPTIONS>') == 0:
                        switch = 1
                    if text.find('              </PORT-API-OPTIONS>') == 0:
                        switch = 0
                        continue
                    if switch == 1:
                        continue

                    fd.write(text)
            print('输出成功....')
        print('即将打开文件所在路径')
        os.remove(r'..\Gen\runnable.txt')
        # 输出文件
        os.startfile(r'..\Gen\Runnable_module')


if __name__ == '__main__':
    # AddRunnable().getrunnable()
    AddRunnable()
