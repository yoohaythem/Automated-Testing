# Automated-Testing-for-Multiple-Languages
基于Python的多语言集成自动化测试框架编写

### 例1：

​		在需要自动化调用rockermq的场景下，由于rocketmq-python库不支持在windows下使用，会有如下异常：rocketmq-python does not support Windows，所以用java去调用这个本身就是用java写的消息队列是一种兼容性较高的做法。
​		在这里，我们将调用逻辑用java编写，并通过maven打成jar包，并通过Python的subprocess，通过cmd调用。

#### Python：

```python
def rpc_test(addr, topic, topic_sync, tags, msg, 预期结果):
    jarpath = 当前路径 + "vpc_mq.jar"  # 生成的 jar 包路径
    msg = msg.replace(r'"', r'\"')
    bytes = subprocess.check_output(f"java -jar {jarpath} {addr} {topic} {topic_sync} {tags} {msg}", shell=True)
    result = bytes.decode("gb2312", "ignore").strip()
    dict = eval(result)
    return dict
```



#### jar包部分：

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



#### pom.xml:

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

![image](https://github.com/yoohaythem/Automated-Testing-for-Multiple-Languages/assets/53369633/ddd05c7a-dce0-4620-9f1f-8a98c5d02f1b)
