### v1.1：【2023.11.04】
1. mac地址：首尾用%可以实现模糊匹配。
2. 环境地址：通过填入用英文逗号分割的字符串，输入需要扫描的数据库IP地址。
3. 通过多线程并发，对IP地址进行【连通性判断】和【数据库查询】，打印满足条件的虚机名称以及所在的环境。
4. 解决开始扫描后，工具界面卡死的问题。
5. 解决开始扫描后，“开始扫描”按钮仍然生效的问题。
6. 解决“输出结果”显示框内，信息残留的问题。

### v1.2：【2023.11.06】
1. 解决代码通过 pyinstaller -w 不带窗口打包后，subprocess执行失效的问题。
2. 新增对总扫描时间的打印。

### v1.3：【2023.11.09】
1. 环境地址的格式输入增加两种：IP1-IP2，IP/mask，并对输入IP格式进行校验。
2. 环境分隔符支持中文逗号。
3. 通过增加锁，保证多线程之间不会抢占共享变量，防止输出信息丢失的情况。
4. 优化工具的标题、图标。
5. 增加版本更新日志的展示。