# automated testing practices


### 例1：基于Python的多语言集成自动化测试框架编写

​		在自动化代码需要调用rockermq的场景下，使用python里的库，例如rocketmq-python，因其不支持在windows下使用，具有较大的缺陷。考虑到rocketmq本身就是用Java实现( https://github.com/apache/rocketmq )，所以用Java调用rocketmq是一种兼容性较高的做法。
​		在这里，我们将调用逻辑用java编写，使用maven打成jar包，通过Python的subprocess以cmd的方式调用。

#### Python

```python
def rpc_test(addr, topic, topic_sync, tags, msg, 预期结果):
    jarpath = 当前路径 + "vpc_mq.jar"  # 生成的 jar 包路径
    msg = msg.replace(r'"', r'\"')
    bytes = subprocess.check_output(f"java -jar {jarpath} {addr} {topic} {topic_sync} {tags} {msg}", shell=True)
    result = bytes.decode("gb2312", "ignore").strip()
    dict = eval(result)
    return dict
```



#### jar包部分

```java
生产者：
package com.vpc;
import org.apache.rocketmq.client.producer.DefaultMQProducer;
import org.apache.rocketmq.common.message.Message;
public class Producer {
    public static void producer(String addr, String topic, String tags, String msg) throws Exception {
        // 实例化生产者
        DefaultMQProducer producer = new DefaultMQProducer("producer_group");
        // 设置NameServer地址
        producer.setNamesrvAddr(addr);
        // 启动生产者
        producer.start();
        // 创建消息
        Message message = new Message(topic, tags, msg.getBytes());
        // 发送消息
        producer.send(message);
        // 关闭生产者
        producer.shutdown();
    }
}


消费者：
package com.vpc;
import org.apache.rocketmq.client.consumer.DefaultMQPushConsumer;
import org.apache.rocketmq.client.consumer.listener.ConsumeConcurrentlyContext;
import org.apache.rocketmq.client.consumer.listener.ConsumeConcurrentlyStatus;
import org.apache.rocketmq.client.consumer.listener.MessageListenerConcurrently;
import org.apache.rocketmq.common.message.MessageExt;
import java.nio.charset.StandardCharsets;
import java.util.List;

/**
 * 消费者
 */
public class Consumer {
   public static String consume(String addr, String topic_sync) throws Exception {
       //1.创建消费者对象
       DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("sync_consumer_group");
       //2.设置nameServer地址
       consumer.setNamesrvAddr(addr);
       //3.订阅主题
       consumer.subscribe(topic_sync, "*");
       //4.注册消息监听
       StringBuilder res = new StringBuilder();
       consumer.registerMessageListener(new MessageListenerConcurrently() {
           @Override
           public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> list, ConsumeConcurrentlyContext consumeConcurrentlyContext) {
               //list就是接收到的所有信息
               for (MessageExt messageExt : list) {
                   //接收信息的信息体
                   byte[] body = messageExt.getBody();
                   //转化为string字符串
                   String s = new String(body, StandardCharsets.UTF_8);
                   res.append(s).append("\n");
               }
               return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
           }
       });
       //5.启动
       consumer.start();
       Thread.sleep(10000);
       //6.关闭
       consumer.shutdown();
       return res.toString();
   }
}


主函数部分，将函数逻辑封装，暴露参数
package com.vpc;
public class Main {
    public static void main(String[] args) throws Exception {
        //  addr, topic, topic_sync, tags, msg
        Producer.producer(args[0],args[1],args[3],args[4]);
        System.out.println(Consumer.consume(args[0],args[2]));
    }
}
```



#### pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>org.example</groupId>
    <artifactId>vpc_mq</artifactId>
    <version>1.0-SNAPSHOT</version>
    
    <properties>
        <maven.compiler.source>8</maven.compiler.source>
        <maven.compiler.target>8</maven.compiler.target>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.apache.rocketmq</groupId>
            <artifactId>rocketmq-client</artifactId>
            <version>4.7.1</version>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-assembly-plugin</artifactId>
                <version>3.2.0</version>
                <configuration>
                    <descriptorRefs>
                        <descriptorRef>jar-with-dependencies</descriptorRef>
                    </descriptorRefs>
                    <archive>
                        <manifest>
                            <!-- 指定主类 -->
                            <addClasspath>true</addClasspath>
                            <mainClass>com.vpc.Main</mainClass>
                        </manifest>
                    </archive>
                </configuration>
                <executions>
                    <execution>
                        <id>make-assembly</id>
                        <phase>package</phase>
                        <goals>
                            <goal>single</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>

</project>
```

然后以如下步骤打包即可：  
![image](https://github.com/yoohaythem/Automated-Testing-for-Multiple-Languages/assets/53369633/3cd117ea-aba5-456b-a807-91ffc056d042)

  
  
#### 其他场景

该方法还可以用在很多不同的场景，例如与tkinter结合，开发这样一个工具：

通过python，利用开发后端AES校验的JAVA代码，校验测试输入密码是否正确。

```python
'''
AES校验密码
'''
ssh_webinstall = paramiko.SSHClient()
ssh_webinstall.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_webinstall.connect(check_host, 22, "root", host_password_input.get())  # 获取主机连接
password = input_password_input.get()   # 获取输入密码

if "java version" in subprocess.getoutput('java -version'):
    jarpath = ExePath + "webinstall_AES.jar"  # 生成的 jar 包路径
    bytes = subprocess.check_output(f"java -jar {jarpath} {password}", shell=True)
    aes_result = bytes.strip().decode("utf-8")    # 根据输入密码查询到的密文
    host_aes_result = myssh.exec_shell(ssh_webinstall,"cat /home/zxcloudsetup/was/tomcat/webapps/ROOT/WEB-INF/classes/conf/minidb.properties|grep passWord=").strip().replace('\\', '')[9:]    # 主机上查询密文
    print("输入密码加密密文为：" + aes_result)
    print("主机上密文为：" + host_aes_result)
    if aes_result != host_aes_result:
        raise Exception
```

  
  
  

### 例2：基于类装饰器的用例自动化编写

#### 框架

​        目前接口自动化测试采用的是传统方法编写，直接通过try...except...else...代码块对接口和校验进行异常捕获处理，采用递归函数对接口多次重试，采用循环判断对校验多次重试，这样会导致代码层层嵌套，十分不易于维护。本方法使用面向切面的编程思想，通过自定义的类装饰器对异常进行捕获，引入retrying模块对接口和函数进行重试，让自动化编写人员的注意力集中在接口逻辑的处理，大大降低了编写自动化的难度和时间成本，适用性广。目前该设计方案已经应用到云平台的稳定性测试中，效果符合预期目标。

```python
# 抽象类，限制用例类内必须具有main()、check()两个函数
class Abstract(metaclass=abc.ABCMeta):
    @abc.abstractmethod   #定义抽象方法，无需实现功能
    def main(self):
        '子类必须定义写功能'
        pass
    @abc.abstractmethod   #定义抽象方法，无需实现功能
    def check(self):
        '子类必须定义写功能'
        pass
    
    
# 类装饰器函数
def decoratorTryCatch(cls):
    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        selfCls = cls()
        try:
            mainReturn = selfCls.main(*args, **kwargs)   # 返回值打包成固定格式
        except DatabaseError:
            # 异常逻辑1 
        except JSESSIONIDCannotFoundError:
            # 异常逻辑2
        except RequestNotSuccessError:
            # 异常逻辑3
        except simplejson.errors.JSONDecodeError:
            # 异常逻辑4
        except IndexError:
            # 异常逻辑5
        except BaseException as e:
            print('###--', traceback.format_exc())
            # 其他异常逻辑
        else:
            try:
                selfCls.check(mainReturn)    # 返回值传入校验函数
            except CheckNotPassedError:
                # 异常逻辑6
            except BaseException as e:
                print('###--', traceback.format_exc())
            	# 其他异常逻辑
            else:
                selfCls.write_success_log(**option_dict)
    return wrapper

```

  

#### 应用实例

```python
# 一个基于类装饰器的实例展示
# 虚拟机-批量挂起
@decoratorTryCatch
class vmBatchSuspend(Abstract, WebBaseFunc):
    @log
    @retry(retry_on_exception=retryErrorCollection, stop_max_attempt_number=MAX_RETRY_NUMBER, wait_fixed=RETRY_WAITING_TIME)    # pip install retrying，引入重试函数
    def main(self, UNIPORTAL_URL, UNIPORTAL_USERNAME, UNIPORTAL_PASSWORD, DATABASE_IP, **option_dict):
        database = DatabaseWeb(database_ip=DATABASE_IP, password='xxxxxxx')
        database.connect_db()
        url = UNIPORTAL_URL + "/iecs/vm/suspendVirtualMachine.action"
        headers = getHeaders(UNIPORTAL_URL, UNIPORTAL_USERNAME, UNIPORTAL_PASSWORD)
        task_start_time = database.get_vmc_time()
        vms = getVmList(option_dict)
        #----------------------------------------------------
        for vm in vms:
            vmid = database.get_database_records('vpdb', 'select uuid from vms where obj_type="3" and vm_name="%s"' % vm)[0][0]
            data = {
                "virtualMachine.id": vmid,
                "ajaxFlag": 'true'
            }
            response = requests.post(url=url, data=data, headers=headers, verify=False)
            responseLog(response)
        #----------------------------------------------------
        mainReturn = {}
        mainReturn["database"] = database
        mainReturn["task_start_time"] = task_start_time
        mainReturn["vms"] = vms
        return mainReturn
    @log
    @retry(retry_on_exception=retryErrorCollection, stop_max_attempt_number=MAX_RETRY_NUMBER, wait_fixed=RETRY_WAITING_TIME)
    def check(self, mainReturn):
        for vm in mainReturn["vms"]:
            result_code = mainReturn["database"].get_iecs_task_result('挂起', vm, mainReturn["task_start_time"], judge_result_max_times=6000)
            if result_code == '2':
                pass
            else:
                wrongLog(10003, "check方法数据库校验不通过!#50004")
                raise CheckNotPassedError()
        mainReturn["database"].close_connected()
```
  
  
  
### 例3：利用多线程实现tkinter控制的代码逻辑启停

#### 启动

​        在利用tkinter控制一段运行时间较长的代码运行时，若是简单的将后端代码封装成函数，并与前端tkinter一起放在主线程中运行，则会导致tkinter界面在后端函数运行之后卡死。所以需要通过如下方法，将代码单独抽出来成为一个独立子线程来运行。

```python
'''界面上点击运行之后，开始运行的函数'''
def _start():
    
    # tkinter界面上的展示变化逻辑
    view(xxx)

    # 后端代码的逻辑函数
    def run():

        func1(xxx)  # 后端执行函数1
        func2(xxx)  # 后端执行函数2
        ……
        funcN(xxx)  # 后端执行函数n

	
    task = Thread(target=run)
    task.start()
```


  
#### 停止

​        若是启动代码之后，发现需要临时停止这个线程，由于python不支持线程的直接终止，所以可以通过下面这种模式来实施。

```python
'''下面三个是线程停止逻辑'''
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


'''界面上点击停止之后，开始运行的函数'''
def _stop():
    
    view1(xxx)   # tkinter界面上的展示变化逻辑
    
    try:
        stop_thread(task)
    except BaseException:
        pass
    
   view2(xxx)   # tkinter界面上的展示变化逻辑
```
  

  
  

### 例4：深入理解Python反射机制，重构if...else...代码

​        在平时写代码的时候，经常会遇到需要根据业务，对第三方包里的方法进行加强，我们来看下面一段代码，这也是在接口测试中，出现频率最高的一段代码：

```python
def request_enhance(method:str, url, headers, data):
    '''
    在利用python里的request包做接口调用时，我们会面临方法的增强，例如接口返回值的校验，日志输出等等
    对多种类似方法的增强会涉及到大量if...else...的判断
    '''
    print("前置增强方法开始！")

    if method == 'post' or 'POST':
        print("requests.post方法被调用！")
        response = requests.post(url=url, data=data, headers=headers, verify=False)
    elif method == 'get' or 'GET':
        print("requests.get方法被调用！")
        response = requests.get(url=url, headers=headers, verify=False)
    elif method == 'put' or 'PUT':
        print("requests.put方法被调用！")
        response = requests.put(url=url, data=data, headers=headers, verify=False)
    elif method == 'delete' or 'DELETE':
        print("requests.delete方法被调用！")
        response = requests.delete(url=url, data=data, headers=headers, verify=False)
    else:
        print("方法参数有误，请重新输入！")

    print("后置增强方法开始！")
    print("校验状态码！")
    print("打印输出日志！")
```

​        这段代码展示了对第三方的requests包进行使用时，对接口调用的方法做前置和后置的增强。这里前置的增强可以是日志的打印，后置的增强可以是接口调用结果的校验，以及一些日志的打印。

​        当然，requests包里不只有这四种方法，通过按住ctrl跟进源码，可以看到这个包里一共包括了这么八种方法，也就是说如果我们需要对这个包整体进行业务逻辑上的增强，在这个函数里就需要写至少八个分支，当然如果在包含一个异常，应该是九个分支。当然，这都算是包含方法比较少的第三方包了，比如我们看numpy包，通过inspect.getmembers(numpy, inspect.isfunction)查找里面所有的方法数量，可以看到一共足足有302个。除此之外，这种写法有一个更大的问题。试想一下如果这个第三方的包做了扩展，里面新增了一百个方法，那相应的，上面的方法中也要相应的新增一百条分支，如果这其中丢了一些分支没有写，几乎是无法发现的，这就是代码的侵入性。
![image](https://github.com/yoohaythem/Automated_Testing_Practices/assets/53369633/66310d55-c555-44b0-8d06-7334151c3f30)


​        下面通过字典，来优化这些分支。

```python
methods = {
    'get': requests.get,
    'post': requests.post,
    'put': requests.put,
    'delete': requests.delete,
}

def request_enhance_2(method:str, url, headers, data):
    '''
    利用字典将方法做映射，也是一个比较常用的简化方法
    '''
    method = method.lower()
    print("前置增强方法开始！")

    print(f"requests.{method}方法被调用！")
    if method in methods:
        response = methods.get(method)(url=url, data=data, headers=headers, verify=False)
    else:
        print("方法参数有误，请重新输入！")

    print("后置增强方法开始！")
    print("校验状态码！")
    print("打印输出日志！")
```

​         通过字典，我们将if条件里的判断参数，和函数名做一一对应，就可以灵活的通过传入的方法名，从字典里取到函数方法，再去调用他们。当然，这种方法依然没有解决代码侵入性的问题，因为随着方法的扩展、修改或是删除，我还是需要去维护这个字典，只是看起来比上面的大段if...else...更清楚一些。直接传入方法名不就可以解决代码侵入性的问题了吗？当然，这个方法理论上说是可行的，但在实际应用中，函数的传入值往往以字符串或是json文本传入，所以这里我们只讨论method这个参数是一个字符串的情况。

​         其实以上代码还有一个问题，那就是函数名虽然被字典管理起来了，但是参数却是固定的。

```python
def request_enhance_3(method, **args):
    '''
    不同方法，甚至同一种方法的参数都是不同的，所以需要将参数的复制权交给函数调用者
    利用python的解包来实现
    '''
    method = method.lower()
    print("前置增强方法开始！")

    print(f"requests.{method}方法被调用！")
    if method in methods:
        response = methods.get(method)(verify=False, **args)
    else:
        print("方法参数有误，请重新输入！")

    print("后置增强方法开始！")
    print("校验状态码！")
    print("打印输出日志！")
```

​        利用Python参数的打包/解包可以解决这个问题。在函数最后一个形参前加上**，代表函数传入的所有多余参数，都会被打包到一个字典中，这个字典可以有0个及以上的键值对。

​        在函数体内调用函数时，我们传入这个字典，并在前面加上**，代表把这个字典解包，将其中的键值对，拆成一个个等式，给函数赋值。

​        这样一来，就将函数参数的赋值权，交给了外部函数的调用者，成功解决了函数入参耦合的问题。

```python
def request_enhance_4(method, **args):
    '''
    利用反射解决调用问题
    通过hasattr判断类里是否有该方法
    通过getattr调用方法
    '''
    method = method.lower()
    print("前置增强方法开始！")

    print(f"requests.{method}方法被调用！")
    if hasattr(requests, method):
        response = getattr(requests, method)(verify=False, **args)
    else:
        print("方法参数有误，请重新输入！")

    print("后置增强方法开始！")
    print("校验状态码！")
    print("打印输出日志！")
```

​        下面，利用反射机制，可以成功的解决代码侵入性。反射机制，是指基于字符串的事件驱动，利用字符串的形式去操作对象/模块中成员(方法、属性)。hasattr是查找包/类中是否具有该方法、属性，getattr是获取包/类中的方法、属性，注意获取的是方法和属性的本身，而不是他们的值或是返回值。这两个方法都接收两个参数，其中第一个是包对象或是类对象，第二个参数是方法、属性的同名字符串名称。在这个例子中，通过getattr获取到方法后，可以继续通过小括号的方式调用该函数。

```python
def request_enhance_5(method, **args):
    '''
    request的内部提供了一种request方法，它只需要传入方法的字符串参数
    通过看源码，post/get等方法，最终return的结果，也就是他的实现，就是通过这个request对象
    缺点：将method判断权交给了系统
    '''
    method = method.lower()
    print("前置增强方法开始！")

    print(f"requests.{method}方法被调用！")

    response = requests.request(method=method, verify=False, **args)

    print("后置增强方法开始！")
    print("校验状态码！")
    print("打印输出日志！")
def request(method, url, **kwargs):
    with sessions.Session() as session:
        return session.request(method=method, url=url, **kwargs)

def get(url, params=None, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('get', url, params=params, **kwargs)

def options(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('options', url, **kwargs)

def head(url, **kwargs):
    kwargs.setdefault('allow_redirects', False)
    return request('head', url, **kwargs)

def post(url, data=None, json=None, **kwargs):
    return request('post', url, data=data, json=json, **kwargs)

def put(url, data=None, **kwargs):
    return request('put', url, data=data, **kwargs)

def patch(url, data=None, **kwargs):
    return request('patch', url, data=data, **kwargs)

def delete(url, **kwargs):
    return request('delete', url, **kwargs)
```

​        当然，requests这个模块是比较特殊的，它本身就提供了一种request方法，该方法的第一个参数就是通过字符串的形式接受了函数名。

​        通过源码可以发现，其他的方法最后都是通过调用该request方法来实现自身的操作。但是在实际应用中，我们很少用这种方法，大多都是利用了上面反射的方式，这是因为例如options, head方法，还会在入参中设定一些特有的默认值。毕竟，直接调用Python包里封装好的方法总是一个更优解。

​        **下面说一个operator包中关于反射的应用---methodcaller。**

​        以字符串大写为例：

```python
s = 'yu hai xiang' 
s1 = s.upper()
s2 = s.replace(" ", "-")
print(s1)
print(s2)
```


​        上面的方法可以被写作：

```python
s = 'yu hai xiang' 
s1 = methodcaller('upper')(s) 
s2 = methodcaller('replace', ' ', '-')(s) 
print(s1)
print(s2)
```

​        下面是该类实现的代码：

```python
class methodcaller:
    """
    Return a callable object that calls the given method on its operand.
    After f = methodcaller('name'), the call f(r) returns r.name().
    After g = methodcaller('name', 'date', foo=1), the call g(r) returns
    r.name('date', foo=1).
    """
    __slots__ = ('_name', '_args', '_kwargs')

    def __init__(*args, **kwargs):
        if len(args) < 2:
            msg = "methodcaller needs at least one argument, the method name"
            raise TypeError(msg)
        self = args[0]
        self._name = args[1]
        if not isinstance(self._name, str):
            raise TypeError('method name must be a string')
        self._args = args[2:]
        self._kwargs = kwargs

    def __call__(self, obj):
        return getattr(obj, self._name)(*self._args, **self._kwargs)

    def __repr__(self):
        args = [repr(self._name)]
        args.extend(map(repr, self._args))
        args.extend('%s=%r' % (k, v) for k, v in self._kwargs.items())
        return '%s.%s(%s)' % (self.__class__.__module__,
                              self.__class__.__name__,
                              ', '.join(args))

    def __reduce__(self):
        if not self._kwargs:
            return self.__class__, (self._name,) + self._args
        else:
            from functools import partial
            return partial(self.__class__, self._name, **self._kwargs), self._args
```

从源码中可以看到，在methodcaller类在实例化的时候，至少需要传入一个参数，也就是方法的字符串名称，其余参数会被_args和_kwargs接收。接下来，该类重写了__call__方法，该方法的作用是让实例化的类可以像函数那样被直接调用，实现__call__方法内的功能，可以将其称之为仿函数。在methodcaller.__call__中，通过上面拿到的函数名称self._name，函数参数self._args, self._kwargs，以及后面调用实例化对象传入的obj进行组合，就可以通过反射的方式，调用类中的对象。

比如前面的案例中，利用methodcaller就可以写作：

```python
methodcaller(method,**args)(request)
```

显然这样写的可读性，就比直接使用反射要低一些。



**getattr源码**

最后，我们试图跟进getattr方法看其本身是如何实现的，但是不幸的是，该方法只在builtins.py中有一个类似于接口的实现，便到此为止了。出现这种情况，说明这段实现不是通过Python，而是通过其他语言来进行编写。这里我们使用的是CPython，所以我们找到CPython的代码托管地址：https://github.com/python/cpython，如果访问不上，也可以访问国内的同步地址：https://gitee.com/sync_repo/cpython?_from=gitee_search。

进入Python同名文件夹，可以发现一个和builtins.py名字很像的文件bltinmodule.c，在1130行可以找到我们想要的代码：

```c
/*[clinic input]
getattr as builtin_getattr

    object: object
    name: object
    default: object = NULL
    /

Get a named attribute from an object.

getattr(x, 'y') is equivalent to x.y
When a default argument is given, it is returned when the attribute doesn't
exist; without it, an exception is raised in that case.
[clinic start generated code]*/

static PyObject *
builtin_getattr_impl(PyObject *module, PyObject *object, PyObject *name,
                     PyObject *default_value)
/*[clinic end generated code: output=74ad0e225e3f701c input=d7562cd4c3556171]*/
{
    PyObject *result;

    if (default_value != NULL) {
        if (_PyObject_LookupAttr(object, name, &result) == 0) {
            // The Py_NewRef() function can be used to create a strong reference to an object.
            return Py_NewRef(default_value);
        }
    }
    else {
        result = PyObject_GetAttr(object, name);
    }
    return result;
}
```

可以看到这里有两个逻辑，如果对象存在，那么就创建这个对象的引用并返回。

我们这里假定是第一次创建，于是会调用PyObject_GetAttr方法，在Objects目录下的object.c中，可以找到其实现：

```C
PyObject *
PyObject_GetAttr(PyObject *v, PyObject *name)
{
    PyTypeObject *tp = Py_TYPE(v);
    if (!PyUnicode_Check(name)) {
        PyErr_Format(PyExc_TypeError,
                     "attribute name must be string, not '%.200s'",
                     Py_TYPE(name)->tp_name);
        return NULL;
    }

    PyObject* result = NULL;
    //[1]：通过tp_getattro获得属性对应对象
    if (tp->tp_getattro != NULL) {
        result = (*tp->tp_getattro)(v, name);
    }
    //[2]：通过tp_getattr获得属性对应对象
    else if (tp->tp_getattr != NULL) {
        const char *name_str = PyUnicode_AsUTF8(name);
        if (name_str == NULL) {
            return NULL;
        }
        result = (*tp->tp_getattr)(v, (char *)name_str);
    }
    //[3]：属性不存在，抛出异常
    else {
        PyErr_Format(PyExc_AttributeError,
                    "'%.50s' object has no attribute '%U'",
                    tp->tp_name, name);
    }

    if (result == NULL) {
        set_attribute_error_context(v, name);
    }
    return result;
}
```

这里可以看到PyObject_GetAttr方法又是通过调用Py_TYPE(v)里的tp_getattr，tp_getattro方法实现。

其中Py_TYPE被定义在Include目录下的object.h头文件中，作用为获取对象的类型

```c
static inline PyTypeObject* Py_TYPE(PyObject *ob) {
    return ob->ob_type;
}
```

tp_getattro和tp_getattr是在Python的class对象中，定义的两个与访问属性相关的操作。其中的tp_getattro是首选的属性访问操作，而tp_getattr在Python中已不再推荐使用，它们之间的区别主要是在属性名的使用上，tp_getattro所使用的属性名必须是一个PyStringObject对象，而tp_attr所使用的属性名必须是一个C中的原生字符串PyUnicode_AsUTF8(name)。如果某个类型同时定义了tp_getattr和tp_getattro两种属性访问操作，那么PyObject_GetAttr将优先使用tp_getattro操作。

而为什么类里会有这两个方法，是Python虚拟机创建<class>时，会从PyBaseObject_Type中继承tp_getattro方法，其返回值由PyObject_GenericGetAttr产生，该函数是通用的属性获取函数，其结果放入类型对象的 tp_getattro 槽中。在PyObject_GenericGetAttr中，有一套复杂地确定访问属性的算法。

```c
PyObject *PyObject_GenericGetAttr(PyObject *o, PyObject *name)
```

至此，就较为清楚地了解了Python是如何通过反射机制，从一个类中获取到方法和属性。








