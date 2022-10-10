# DavinciCan
Parse DBC file and Generate arxml file for Vector Davinci Development software

This tool is used to generate CtApCom.arxml using the DBC file released by the project.
Note: Before use, pls check the DBC and ensure that there are no errors in the DBC file and The node name in the DBC must be consistent with that in the config configuration file.

***Generate CtApCom***
1. In the SourceInput/DBC folder, delete the original DBC file and replace it with a new DBC file.
2. Run Py_ARXML/Generate_Module.py for arxml generation.
3. A new CtApCom.arxml will be generated in the Gen/Module folder. The arxml file (including BusIn/Out) can be used for the modeling of Davinci Developer.
*******************

本工具用于使用项目释放的DBC文件生成CtApCom.arxml。
注：使用前需先检查DBC并确保DBC无错误并且DBC中的节点名需与config配置文件里面的节点保持一致。

***生成CtApCom***
1. 在SourceInput/DBC文件夹中，删除原DBC文件并替换生成所需项目新的DBC文件。
2. 运行Py_ARXML/Generate_Module.py进行文件生成。
3. Gen/Module文件夹中会生成新的CtApCom.arxml文件（包括BusIn/Out），可用于Davinci Developer的建模。
*****************
