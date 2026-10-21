# Docker安装

更新软件源
```bash
sudo apt update
sudo apt upgrade -y
```

安装docker
```bash
sudo apt install -y docker.io
```
查看docker版本
```bash
docker  -v
```

# 配置镜像源
配置镜像源地址

```bash
vim /etc/docker/daemon.json
```
daemon.json的内容
```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.m.daocloud.io",
    "https://docker.xuanyuan.me"
  ]
}

```

重启Docker服务
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

# Docker相关命令

### 镜像相关命令
查看本地镜像
```bash
docker image ls
# 或
docker images
```

查看镜像id
```bash
docker images -q
```

搜索镜像
```bash
docker search 镜像名
```

拉取镜像
```bash
docker pull 镜像名
或
docker pull 镜像名:版本号
```

删除本地镜像
注意：删除镜像前必须关闭容器
```bash
docker rmi 镜像ID
#或
docker rmi 镜像名:版本号

#强制删除镜像
docker rmi -f 镜像名:版本号 或  镜像ID

```
#### 自制镜像
创建一个目录
```
mkdir -p ~/sysbox-systemd
cd ~/sysbox-systemd
```
在目录创建Dockerfile
Dockerfile文件内容
```text

# 使用 Ubuntu 24.04 基础镜像
FROM ubuntu:24.04

# 避免安装软件时出现交互式提示
ENV DEBIAN_FRONTEND=noninteractive

# 安装 systemd 和常用工具
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        systemd \
        systemd-sysv \
        dbus \
        sudo \
        curl \
        wget \
        vim \
        nano \
        git \
        iproute2 \
        iputils-ping \
        net-tools \
        procps \
        openssh-server \
        ca-certificates \
        tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 创建 SSH 运行目录
RUN mkdir -p /run/sshd

# systemd 的停止信号
STOPSIGNAL SIGRTMIN+3

# 容器启动时运行 systemd（PID 1）
CMD ["/sbin/init"]


```

构建 Docker 镜像，在 Dockerfile 所在目录执行
```bash
sudo docker build -t ubuntu24-systemd:1.0 .
```



### 网络管理命令
查看所有 Docker 网络
```bash
docker network ls
```

创建网络
```bash
docker network create agent-net #agent-net是网络名称，自己设定
#或
docker network create --driver bridge agent-net  # 使用 Bridge（桥接）网络驱动
```

查看网络详细信息
```bash
docker network inspect agent-net
```	

将已有容器加入网络
```bash
docker network connect agent-net agent-001
```	
将容器从网络断开
```bash
docker network disconnect agent-net agent-001
```	
删除指定网络
```bash
docker network rm agent-net	
```
删除未使用的自定义网络
```bash
docker network prune	
```

查看容器的 IP 地址
```bash
sudo docker inspect \
  -f '{{(index .NetworkSettings.Networks "agent-net").IPAddress}}' \
  agent-user-001

# agent-net是创建的网络
# agent-user-001 是容器名称
```




### 容器相关命令

创建容器并运行容器
```bash
docker run -it --name c1 ubuntu24-systemd:1.0 -p 127.0.0.1:80:8080  /bin/bash
```
-i:保持容器运行
-t:为容器重新分配一个伪输入终端，与-i一起使用
-d 以守护（后台）模式运行容器
-p: 指定端口映射，格式为：主机(宿主)端口:容器端口


```bash 
sudo docker run -d \
  --runtime=sysbox-runc \
  --name agent-user-001 \
  --hostname agent-user-001 \
  --network agent-net \
  --restart unless-stopped \
  --memory 2g \
  --cpus 2 \
  ubuntu24-systemd:1.0
```
参数说明
--runtime：设置容器运行时
--name：容器的名称
--hostname：容器中的主机名称
--network: 网络
--restart：容器退出后自动重启，但手动停止后不会自动重启，直到再次手动启动
--memory：内存
 --cpus：cpu数量 




查看正在运行的容器
```bash
docker ps
```
查看所有容器(关闭和没关闭)
```bash
docker ps -a
```

进入容器
```bash
docker exec -it  容器名称或id  /bin/bash
# 退出容器，容器不会关闭
```

停止容器
```bash
docker stop 容器名称或id
```
启动容器
```bash
docker start 容器名称或id
```
删除容器
```bash
docker rm 容器名称或id
```



# 让局域网内主机可以访问到宿主机里面的Docker容器（宿主机所在的网络，网关可以设置）
1、创建Docker Bridge 网络(在宿主机上运行)
```bash
docker network create \
  --driver bridge \
  --subnet 172.26.0.0/24 \
  -o com.docker.network.bridge.gateway_mode_ipv4=routed \
  agent-routed
```
创建一个名为 agent-routed 的 Docker Bridge 网络，指定 IP 网段为 172.26.0.0/24，并启用 IPv4 Routed（路由）模式



在宿主机上添加路由(docker 默认会操作，如果docker容器网络崩了问题，按下面操作)
查看创建的网络
```bash
ip -br addr show type bridge
```
ip -br addr show type bridge
docker0          DOWN
br-87974d43e67e  UP             172.26.0.1/24 fe80::d414:ccff:fea1:a7be/64


```bash
sudo ip addr add 172.26.0.1/24 dev br-87974d43e67e
```

2、创建容器,通过--ip指定容器的ip，-p指定端口，指定端口外面只能访问指定的端口
```bash
sudo docker run -d \
  --runtime=sysbox-runc \
  --name agent-user-001 \
  --hostname agent-user-001 \
  --network agent-routed \
  --restart unless-stopped \
  --ip 172.26.0.2 \
  -p 0.0.0.0::9080 \
  ubuntu24-systemd:1.0

```

3、设置宿主机IP转发
宿主机ip地址(192.168.1.204)
检查IP 转发
```bash
sysctl net.ipv4.ip_forward
```
net.ipv4.ip_forward = 1

如果是0,通过下面的命令开启转发
```bash
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-ip-forward.conf
sudo sysctl --system
```


4、设置网关
软路由R2S 网关(192.168.2.1)
在软路由中添加临时路由，目标地址：172.26.0.0/24 在这个网段时，路由到192.168.2.204主机
```bash
ip route add 172.26.0.0/24 via 192.168.2.204
```

设置永久的路由
```bash
uci add network route
uci set network.@route[-1].interface='lan'
uci set network.@route[-1].target='172.26.0.0/24'
uci set network.@route[-1].gateway='192.168.2.204'
uci commit network
/etc/init.d/network reload
```

测试
在容器中运行启动 Python HTTP 文件服务器
```bash
python3 -m http.server 9080 --bind 0.0.0.0
```
在外面访问：http://172.26.0.2:9080


# 让局域网内主机可以访问到宿主机里面的Docker容器（宿主机所在的网络，不能网关可以设置）
1、创建Docker Bridge 网络(在宿主机上运行)
```bash
docker network create \
  --driver bridge \
  --subnet 172.26.0.0/24 \
  -o com.docker.network.bridge.gateway_mode_ipv4=routed \
  agent-routed
```
创建一个名为 agent-routed 的 Docker Bridge 网络，指定 IP 网段为 172.26.0.0/24，并启用 IPv4 Routed（路由）模式
注意：Docker 使用了 gateway_mode_ipv4=routed，不会自动进行 SNAT（源地址转换）,所以在容器中ping www.baidu.com ping不通


2、设置SNAT，解决Doker的SNAT（源地址转换）问题
在宿主机上运行，获取出口网卡
```bash
ip -4 route get 223.5.5.5
```
223.5.5.5 via 192.168.119.2 dev ens33 src 192.168.119.128 uid 1000
    cache
在宿主机上添加规则,添加 MASQUERADE 规则
```bash
# # 为容器网段添加出站 SNAT
sudo iptables -t nat -A POSTROUTING \
  -s 172.26.0.0/24 \
  -o ens33 \
  -j MASQUERADE
```
-t nat	操作 NAT 表
-A POSTROUTING	在出站路由之后处理数据包
-s 172.26.0.0/24	只匹配这个容器网段
-o ens33	匹配从 ens33 发出的流量
-j MASQUERADE	将源 IP 转换为 Ubuntu 出口 IP

3、设置宿主机IP转发
宿主机ip地址(192.168.1.204)
检查IP 转发
```bash
sysctl net.ipv4.ip_forward
```
net.ipv4.ip_forward = 1

如果是0,通过下面的命令开启转发
```bash
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-ip-forward.conf
sudo sysctl --system
```

4、创建容器,通过--ip指定容器的ip，-p指定端口，指定端口外面只能访问指定的端口
```bash
sudo docker run -d \
  --runtime=sysbox-runc \
  --name agent-user-001 \
  --hostname agent-user-001 \
  --network agent-routed \
  --restart unless-stopped \
  --ip 172.26.0.2 \
  -p 0.0.0.0::9080 \
  ubuntu24-systemd:1.0

```

5、设置访问主机的路由
```bash
ip route add 172.26.0.0/24 via 192.168.2.204
```