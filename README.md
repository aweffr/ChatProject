# ChatProject
本项目是一个网页实时聊天室

主要目的是实现SocketIO + Flask + MessageQueue + Database的集成

目前已参考Miguel书按"大型程序的结构"(chaper7)完成程序结构组织, 
并且已集成Flask-SocketIO, Sqlite, 在Eventlet提供的协程服务器下正常运行.

接下来要做的:
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