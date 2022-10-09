from Py_DBC import ParseDBC
import re


def comparetwodbc():
    """

    :return:
    """
    dbcpath = [r'intelligentVehicle_LEV12-C_CAN 20210507.dbc',
               r'intelligentVehicle_LEV12-C_CAN 20201023.dbc']
    if type(dbcpath) is list:
        if len(dbcpath) == 2:
            # tkinter.messagebox.showwarning('提醒', '请确保在main里面列表第一个放新版本dbc，第二个放老版本dbc')
            first_dbcname = re.split('/', dbcpath[0])[-1]
            print('\033[1;34m正在解析第一个dbc：' + first_dbcname + '\033[0m')
            parse_firstdbc = ParseDBC.ParseDbc([dbcpath[0]])
            parse_firstdbc.switchs()
            first_dbcinfo = parse_firstdbc.dbc_dict
            second_dbcname = re.split('/', dbcpath[1])[-1]
            print('\033[1;34m正在解析第二个dbc：' + second_dbcname + '\033[0m')
            parse_seconddbc = ParseDBC.ParseDbc([dbcpath[1]])
            parse_seconddbc.switchs()
            second_dbcinfo = parse_seconddbc.dbc_dict
            # compare dict
            print('以下报文在新版本dbc里面进行了修改')
            for i in second_dbcinfo[second_dbcname]:
                if i not in first_dbcinfo[first_dbcname]:
                    print(i)
            print('以下报文在老版本dbc里面存在')
            for s in first_dbcinfo[first_dbcname]:
                if s not in second_dbcinfo[second_dbcname]:
                    print(s)
            print('\033[1;31m如果两个都存在，则证明是周期或者是某个信号不一样\033[0m')
        else:
            print('需要输入两个文件')
    else:
        print('不是列表的方式输入文件')


if __name__ == '__main__':
    comparetwodbc()