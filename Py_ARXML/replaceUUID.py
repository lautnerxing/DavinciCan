import uuid
import re
import os
import time


class ReplaceUuid:
    """
    对arxml文件里面的uuid进行重复项检查和自动去重
    """

    def __init__(self, filepath):
        self._filepath = filepath
        self._filepathdir = '\\'.join(re.split(r'\\', self._filepath)[:-1])
        self.check_uuid()

    def make_path(self):
        """
        获取用户输入路径，为替换文件并重命名oldfile做准备
        :return: usr_path
        """

    def check_uuid(self):
        """
        检查uuid是否重复，如果没有重复则打印出结果，
        如果重复则自动修改并替换文件，
        并自动打开替换后的文件
        :return:
        """
        check_box = list()
        try:
            with open(self._filepath, 'r+', encoding='utf-8') as f:
                for line in f:
                    if 'UUID=' in line:
                        s = re.split(r'"', line)
                        check_box.append(s[1])
            if len(check_box) == len(set(check_box)):
                print('\033[1;32mPass 无重复UUID\033[0m')
            else:
                print('\033[1;31mFailed 有重复UUID\033[0m')
                self.main()
                print('修改完成，对修改后文件进行检查')
                self.check_uuid()
                print('即将打开修改后的文件所在文件夹')
                time.sleep(1)
                os.startfile(self._filepathdir)
        except:
            print('文件路径或文件名输入错误')

    def main(self):
        """
        查找所有的uuid修改为新uuid(为uuid4随机生成)，并替换文档
        :return:
        """
        with open(self._filepath, 'r+', encoding='utf-8') as f:
            with open('./new_file.txt', 'w', encoding='utf-8') as f_new:
                for line in f:
                    if 'UUID=' in line:
                        # 随机生成一个uuid
                        random_uuid = str(uuid.uuid4()).upper()
                        # 提取出文本中该行uuid并生成要替换的内容
                        s = re.split(r'"', line)
                        s[1] = random_uuid
                        replace_line = '"'.join(s)
                        f_new.writelines(replace_line)
                        continue
                    # 写入新文档
                    f_new.writelines(line)
        # 以旧换新
        os.remove(self._filepath)
        os.rename('./new_file.txt', self._filepath)


if __name__ == '__main__':
    ReplaceUuid(r'C:\Users\Administrator\Desktop\Ascp\0817\CtApVMS_swc.arxml')