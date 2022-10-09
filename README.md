# DavinciCan
1.Parse DBC file and get some msg info

本工具用于使用项目释放的DBC文件生成CtApCom.arxml。
注：使用前需先检查DBC并确保DBC无错误；DBC中的节点名需与config配置文件里面的节点保持一致。

***生成CtApCom***
1. 在SourceInput/DBC文件夹中，删除原DBC文件并替换生成所需项目新的DBC文件。
2. 运行Py_ARXML/Generate_Module.py进行文件生成。
3. Gen/Module文件夹中会生成新的CtApCom.arxml文件（包括BusInOut），可用于Davinci Developer的建模。
*****************
