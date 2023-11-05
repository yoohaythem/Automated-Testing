import concurrent.futures
import copy
import subprocess
import pymysql
import time

result_str = ""


def measure_time(func):
    def wrapper(*args, **kwargs):
        global result_str
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"运行时间为 {execution_time:.2f} 秒")
        result_str += f"运行时间为 {execution_time:.2f} 秒\n"
        return result_str

    return wrapper


# 定义查询函数，处理异常
def query_database(db_config, query):
    try:
        # 连接数据库
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        # 执行查询操作
        cursor.execute(query)
        result = cursor.fetchall()
        # 关闭数据库连接
        cursor.close()
        conn.close()
        # 返回查询结果
        return list(res[0] for res in result)
    except:
        return ""


# 定义主函数
@measure_time
def main(host_ips, port, username, password, database, vm_mac, check_con_flag=1):
    global result_str
    result_str = ""
    # 有的环境上没有管理员权限，无法执行ping -c, 把check_con_flag置为0就行
    if check_con_flag:
        def check_connectivity(ip):
            # 执行ping命令检查连通性
            global result_str
            # 在创建进程时，加上startupinfo参数，否则pyinstaller -F -w时，subprocess会报错
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(["ping", "-c", "1", ip], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, startupinfo=si)
            # 检查ping命令的返回码，0表示连通，其他值表示不连通
            if result.returncode:
                print(f"{ip} 不可达，请检查网络！")
                result_str += f"{ip} 不可达，请检查网络！\n"
                host_ips.remove(ip)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 提交任务并获取结果
            executor.map(check_connectivity, copy.copy(host_ips))

    # 定义数据库连接配置信息
    db_configs = []
    for host_ip in host_ips:
        db_configs.append({'host': host_ip, 'port': port, 'user': username, 'password': password, 'database': database})
    # 计数
    count = 0
    # 定义查询语句，用于在云桌面数据库里查看符合条件的桌面名称
    query = f"SELECT vm.vm_name FROM xxx.vms vm LEFT JOIN yyy.nics nic on vm.uuid=nic.vm_uuid WHERE nic.mac like (LOWER(\"{vm_mac}\"));"
    # 创建线程池
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(db_configs)) as executor:
            # 并行执行查询操作
            results = list(executor.map(query_database, db_configs, [query] * len(db_configs)))
            # 处理结果
            for i in range(len(results)):
                # 输出查询结果
                if len(results[i]):
                    count += 1
                    print(f"{count}. 环境 [{host_ips[i]}] 上MAC地址为 [{vm_mac}] 的虚机为：{results[i]}")
                    result_str += f"{count}. 环境 [{host_ips[i]}] 上MAC地址为 [{vm_mac}] 的虚机为：{results[i]}\n"
    except ValueError:
        print(f"有效IP列表为空异常")
        result_str += f"有效IP列表为空异常\n"
    print(f"===> 已扫描 {len(host_ips)} 个环境，共 {count} 个环境上存在符合条件的虚机")
    result_str += f"===> 已扫描 {len(host_ips)} 个环境，共 {count} 个环境上存在符合条件的虚机\n"
    return result_str


if __name__ == '__main__':
    # 定义主机IP地址、用户名、密码、数据库名和表名等参数
    str_input = "192.168.1.100,192.168.1.101,192.168.1.102"  # 用英文逗号分割
    host_ips = [] if str_input == "" else [item.strip().strip("'") for item in str_input.split(",")]
    port = 3306
    username = 'admin'
    password = 'admin'
    database = 'xxx'
    vm_mac = 'DC:21:5C:84:9B:26'

    # 调用主函数
    main(host_ips, port, username, password, database, vm_mac)
