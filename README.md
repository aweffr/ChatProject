# 推送/聊天应用

## 开发环境
- Python 3.6.1
- Flask 0.12.2
- gevent 1.2.2

其它依赖库详见`requirements.txt`.

APP的代码组织结构严格参考*Flask Web Development(Miguel Grinberg著)*

## 重要
APP所依赖的`python-engineio 1.5.4` 在接收socket报文时对含有中文的内容会报错，修复方法为python运行环境下.../site-packages/engineio/payload.py文件中, 在代码```encoded_payload = fixed_payload```
语句下增加一行:
```packet_len = len(fixed_payload)```
强制刷新包长度即可修复改bug。

**可复制本项目/patch文件夹下的payload.py覆盖对应python安装目录下文件解决。**


# 部署方法
### 安装python解释器
1. 安装python3.6.1
    1. `wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2rc1.tgz`
    2. `tar -zxf Python-3.6.2rc1.tgz`
    3. 编译安装(`make test`可跳过)
        ```
        cd Python-3.6.2rc1/
        ./configure
        make
        make test
        sudo make install
        ```
### 获取源代码
2. `git clone https://github.com/aweffr/ChatProject.git`或者解压`ChatProject.zip`
3. `cd ChatProject`

### [可选]创建并激活虚拟环境:
4. `virtualenv python3 venv`
5. `source venv/bin/activate`

### 安装python依赖
6. `pip install –r requirements.txt`
7. **修改payload.py文件(以支持中文)**

### 配置数据库和activeMQ `config.py`
#### 数据库接口:
```
SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI") or \
                          "mysql://xxx:yyy@aweffr.win/chat"
```
#### ActiveMQ通信:
```
STOMP_URL = "101.37.24.136"
STOMP_PORT = 61613`
STOMP_PUBLIC_NAMESPACE = "public"
```

#### 初始化数据库
8. `python manage.py init_db`

### 配置启动绑定端口`manage.py`
9. 可配置develop_run和production_run两种对应的端口(host和post)
    ```
    @manager.command
    def develop_run():
        """Run with debug"""
        socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    
    
    @manager.command
    def production_run():
        "Run with produciton"
        socketio.run(app, host="0.0.0.0", port=5000, debug=False)
    ```

### 启动
9. 两种启动设置:
    - (debug模式) `python manage.py develop_run`
    - (正常模式)`python manage.py production_run`

其它:

- 启动APP时会根据数据库信息生成TopicList。

- 若数据库的字段有增减改名，需更新/app/models.py中对应的对应实体对象。

- 在重置数据库后默认会有两个账户:
    - 账户: root@huami.com 密码: root
    - 账户: admin@huami.com 密码: admin
    