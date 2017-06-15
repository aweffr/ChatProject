# ChatProject
本项目是一个网页实时聊天室

主要目的是实现SocketIO + Flask + MessageQueue + Database的集成

目前已参考Miguel书按"大型程序的结构"(chaper7)完成程序结构组织, 
并且已集成Flask-SocketIO, Sqlite, 在Eventlet提供的协程服务器下正常运行.


### Development Log
- 2017.6.15
    - 今日走通了ActiveMQ的连接功能, 撸了一个简易的flask_mq, 可以用组件注册的方式在App中加载.
    - 可以通过shell进入debug, 单独测试send和subscribe功能
        - 不能用`Evenlet`启动, 以`Evenlet`启动就不能服务器主动发送消息
    - 用户进入聊天页面后可以加载最近50条聊天记录
    - 目前的版本用户发送的消息会被推送到ActiveMQ, 显示在游览器上的消息都是从ActiveMQ上订阅的.
    - **TODO**
        - 分离用户自己发送消息和接受别人消息再推送到游览器的通道
        - 增加"消息发送成功/未推送到服务器/未推送到ActiveMQ"三个状态, 并区分处理方式
        - 如何保证启动多个Flask实例和独立sqlite下消息的一致性
        - 比较Evenlet和Gevent中提供的Socket API, 看看能不能解决Evenlet中遇到的问题
        - 数据库, socketIO, MQ三者独立的**单元测试**
        - 并发性能测试
        


- 2017.6.14
    - 连接ActiveMQ
        - (Optional) 自己写一个Flask-activeMQ
        - 确定Flask和ActiveMQ的连接方式
    
    - 用户模块
        - 用户的登陆和注册
        - 用户主页
        - 用户头像(多媒体信息存储?文件上传下载和保存?)
        - 用户信息修改
    
    - 用户文件模块
        - 上传图片的接口
    
    - 确定用户信息(user's message)的结构
        - 不同的用户可以加入不同的聊天组(以及公共组)
        - 每个用户可以在自己的主页查看"聊天记录"
            - 如何组织聊天记录?
            
    - 视图部分
        -  (2017.6.15 Check) 逻辑: 用户进入视图可以加载所有说过的话(历史记录)
        -  (2017.6.15 Check) 逻辑: 用户名字键入后若存在用户则加载, 不存在则向表里加记录
        