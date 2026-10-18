# 安装

安装基础工具
```bash
sudo apt update

sudo apt install -y \
  curl \
  ca-certificates \
  gnupg \
  lsb-release

```
添加 Kong 官方 APT 仓库
https://developer.konghq.com/gateway/install
导入官方签名密钥
```bash
curl -1sLf \
  "https://packages.konghq.com/public/gateway-39/gpg.B9DCD032B1696A89.key" \
  | gpg --dearmor \
  | sudo tee /usr/share/keyrings/kong-gateway-39-archive-keyring.gpg > /dev/null
```
添加软件源
```bash
curl -1sLf \
  "https://packages.konghq.com/public/gateway-39/config.deb.txt?distro=ubuntu&codename=noble&component=main" \
  | sudo tee /etc/apt/sources.list.d/kong-gateway-39.list > /dev/null
```

更新软件包索引
```bash
sudo apt update
```

查看可安装的 Kong 版本
```bash
apt-cache policy kong
```

安装 Kong
```bash
sudo apt install -y kong=3.9.3
```

安装完成后检查
```bash
kong version
```

创建配置文件
```bash
sudo cp /etc/kong/kong.conf.default /etc/kong/kong.conf
```
编辑配置文件
```bash
vim /etc/kong/kong.conf
```
kong.conf内容
```conf
# PostgreSQL 配置
database = postgres # 指定使用PostgreSQL数据库
pg_host = 127.0.0.1 # 数据库的ip
pg_port = 5432 # 数据库的ip
pg_user = kong  #  连接数据库的用户名
pg_password = ChangeMe_Strong_2026 #  连接数据库的密码
pg_database = kong # 使用的使用库，提前在数据创建数据库

# HTTP 代理监听端口
proxy_listen = 0.0.0.0:8000

# 管理 API，仅允许本机访问
admin_listen = 127.0.0.1:8001

# 日志
log_level = notice

```

设置文件权限
```bash
sudo chown root:kong /etc/kong/kong.conf
sudo chmod 640 /etc/kong/kong.conf
```

初始化及启动 Kong
```bash
sudo kong check /etc/kong/kong.conf
```
如果正确，会返回类似:configuration at /etc/kong/kong.conf is valid

初始化数据库
只需要初始化一次
```bash
sudo kong migrations bootstrap
```

启动 Kong
```bash
sudo kong start
```
2026/10/18 15:09:20 [warn] ulimit is currently set to "1024". For better performance set it to at least "4096" using "ulimit -n"
2026/10/18 15:09:20 [warn] ulimit is currently set to "1024". For better performance set it to at least "4096" using "ulimit -n"
Kong started


查看状态
```bash
sudo kong health
```
nginx.......running

Kong is healthy at /usr/local/kong


检查监听端口
```bash
sudo ss -lntp | grep -E '8000|8001'
```
LISTEN 0      511          0.0.0.0:8001       0.0.0.0:*    users:(("nginx",pid=208719,fd=19),("nginx",pid=208718,fd=19),("nginx",pid=208717,fd=19),("nginx",pid=208716,fd=19),("nginx",pid=208715,fd=19))
LISTEN 0      511          0.0.0.0:8000       0.0.0.0:*    users:(("nginx",pid=208719,fd=18),("nginx",pid=208718,fd=18),("nginx",pid=208717,fd=18),("nginx",pid=208716,fd=18),("nginx",pid=208715,fd=18))

# 实际使用 Kong

创建 Kong Service
```bash
curl -i -X POST http://127.0.0.1:8001/services \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo-service",
    "url": "http://127.0.0.1:9080"
  }'
```

创建 Kong Route
```bash
curl -i -X POST \
  http://127.0.0.1:8001/services/demo-service/routes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo-route",
    "paths": ["/demo"],
    "strip_path": true
  }'
```
name：路由名称。
paths：需要匹配的 URL 路径。
strip_path：是否移除匹配到的路径前缀。

测试代理
```bash
curl -i http://127.0.0.1:8000/demo/
```



