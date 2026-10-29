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

查看镜像自身保存的默认配置
```bash
docker image inspect 镜像名

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
#### Dockerfile 可以设置内容

常用参数设置
| 指令 | 作用 | 示例 |
|---|---|---|
| `FROM` | 指定基础镜像 | `FROM ubuntu:24.04` |
| `CMD` | 设置容器默认启动命令 | `CMD ["python3", "app.py"]` |
| `ENTRYPOINT` | 设置容器的主要执行程序 | `ENTRYPOINT ["python3"]` |
| `RUN` | 构建镜像时执行命令 | `RUN apt-get install -y curl` |
| `COPY` | 复制文件到镜像,将宿主机的opencode.json文件复制到容器的/root/.config/opencode/目录，容器的/root/.config/opencode/不存在时，容器自动创建，opencode.json是路径是相对于运行docker build所在目录 | `COPY opencode.json /root/.config/opencode/` |
| `ADD` | 复制文件，也支持自动解压本地归档等功能 | `ADD app.tar.gz /app/` |
| `WORKDIR` | 设置工作目录，Docker 镜像内部的当前工作目录。后续的 RUN、CMD、ENTRYPOINT 等指令会以这个目录作为默认工作目录 | `WORKDIR /app` |
| `ENV` | 设置环境变量，默认在容器运行时保留 | `ENV TZ=Asia/Shanghai` |
| `EXPOSE` | 声明应用使用的端口 | `EXPOSE 9080` |
| `USER` | 指定后续构建步骤及默认进程使用的用户 | `USER appuser` |
| `STOPSIGNAL` | 设置停止容器时发送的信号 | `STOPSIGNAL SIGTERM` |


##### RUN
RUN 就是在构建镜像时，执行一条命令,
每一条 RUN 通常会形成一个镜像构建层，后面的命令可以使用前面留下来的文件和软件
Dockerfile 中，每一条 RUN 默认都会启动一个新的 Shell 进程，因此不是同一个 Shell 上下文
```Dockerfile
FROM ubuntu:24.04

RUN export NAME=Tom # 设置NAME变量
RUN echo "$NAME"  # 获取不到NAME变量

RUN cd /app  # 切换到/app目录
RUN pwd   # 不是app目录

```
可以通过
```bash 
RUN bash -c 'export NAME=Tom && cd /app && echo "$NAME" && pwd' 
# 或
RUN export NAME=Tom && \
    cd /app && \
    echo "$NAME" && \
    pwd
```
在同一个Shell环境运行多个命令




##### CMD 和 ENTRYPOINT 单独使用
只使用 CMD
```Dockerfile
FROM ubuntu:24.04

CMD ["python3", "app.py"]
```
默认启动
```bash
docker run my-image

#  运行时，实际执行 python3 app.py
```
启动时指定其他参数
```bash
docker run my-image bash
# 运行时，实际执行 bash
```
只使用 ENTRYPOINT
```Dockerfile
FROM ubuntu:24.04
ENTRYPOINT ["python3"]
```
默认启动
```bash
docker run my-image
# 运行时，实际执行 python3
```
如果启动时指定参数
```bash
docker run my-image --version
# 运行时，实际执行 python3  --version
```
CMD 和 ENTRYPOINT 结合使用
```Dockerfile
FROM ubuntu:24.04

ENTRYPOINT ["python3"]
CMD ["app.py"]
```
默认启动
```bash
docker run my-image
# ，实际执行 python3  app.py
```
如果启动时指定其他参数
```bash
docker run my-image test.py
# 实际执行  python3 test.py
```

其他参数
| 指令 | 作用 | 示例 |
|---|---|---|
| `EXPOSE` | 声明应用使用的端口 | `EXPOSE 9080` |
| `VOLUME` | 声明容器中的数据卷目录 | `VOLUME ["/data"]` |
| `LABEL` | 为镜像添加元数据 | `LABEL version="1.0"` |
| `HEALTHCHECK` | 定义容器健康检查方式 | `HEALTHCHECK CMD curl -f http://localhost:9080/` |
| `SHELL` | 修改 `RUN` 等指令使用的默认 Shell | `SHELL ["/bin/bash", "-c"]` |
| `ONBUILD` | 定义下游镜像构建时自动执行的指令 | `ONBUILD COPY . /app` |
| `ARG` | 定义构建镜像时使用的参数 | `ARG APP_VERSION=1.0` |


简单的Dockerfile的模板(错误示例)
```Dockerfile
FROM ubuntu:24.04

# 设置工作目录，启动 shell 默认所在的目录
WORKDIR /app

# 设置时区
ENV TZ=Asia/Shanghai

# 更新软件源
RUN apt update 

# 安装
# ca-certificates # 安装证书

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \ 
        curl \
        git 

# 删除 APT 下载的软件包索引缓存        
RUN rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["curl"]
CMD ["http://192.168.2.204:5000/v2/ubuntu/tags/list"]
        
```
上面示例是错误,因为每运行RUN就是一层镜像，Dockerfile 中每条 RUN 通常都会产生一个新的镜像层，因此安装软件和清理 APT 缓存最好放在同一个 RUN 中
```Dockerfile
FROM ubuntu:24.04

# 设置工作目录
WORKDIR /app

# 设置时区
ENV TZ=Asia/Shanghai

# 更新软件源、安装软件、清理缓存
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# 容器启动命令（按实际需要填写）
ENTRYPOINT ["curl"]
CMD ["http://192.168.2.204:5000/v2/ubuntu/tags/list"]

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

#### docker容器的网络
##### bridge网络
容器使用独立 IP，通过网桥通信
bridge网络的网关模式
| 网关模式 | NAT | 特点 |
|---|---|---|
| `nat` | 有 | 默认模式，端口映射 |
| `routed` | 无 | 直接通过路由访问容器 IP |
| `nat-unprotected` | 有 | 不对未发布端口实施常规端口过滤 |
| `isolated` | 无 | 与 `internal` 网络配合，实现更严格的隔离 |

###### nat 网关
默认 bridge 下，宿主机直接访问容器 IP 不需要 -p；局域网其他设备默认通过宿主机 IP + -p 映射的端口访问

###### routed
创建
```bash
docker network create \
    --driver bridge \
    --subnet 172.26.0.0/24 \
    -o com.docker.network.bridge.gateway_mode_ipv4=routed \
    agent-routed
```
routed 模式下，Docker 仍然对发布端口实施过滤。对于未发布端口，并不是一定能直接从其他主机访问,可以通过-p 0.0.0.0::80发表端口，或-p 80



##### host容器共享宿主机网络
host 网络模式时，容器没有独立的容器 IP，而是直接共享宿主机的网络命名空间
```bash
docker run -d \
    --name web \
    --network host \
    python:3.12 \
    python -m http.server 9080 --bind 0.0.0.0
```

##### container
container 网络模式表示：一个容器直接共享另一个容器的网络命名空间（Network Namespace）
假设有两个容器：
- 容器 A：container-a (172.26.0.2)
- 容器 B：container-b

容器A
```bash
docker run -d \
    --name container-a \
    python:3.12 \
    python -m http.server 8080 --bind 0.0.0.0

```
 
容器 B 使用容器 A 的网络
```bash
docker run -d \
    --name container-b \
    --network container:container-a \
    nginx
```
使用 --network container:container-a 的容器不能单独使用 -p、--publish 等网络配置。需要在容器 A 上设置相应的端口发布




### 容器相关命令
通用格式
```bash
docker run [容器配置参数] 镜像名 [启动命令或参数]
```

创建容器并运行容器
```bash
docker run -it --name agent_user_001 ubuntu24-systemd:1.0 -p 127.0.0.1:80:8080  /bin/bash
```
-i:保持容器运行
-t:为容器重新分配一个伪输入终端，与-i一起使用
-d 以守护（后台）模式运行容器
-p: 指定端口映射，格式为：主机(宿主)端口:容器端口

```bash
docker run -it \
  --name agent_user_001 \
  -v /home/agent_user_001/.config/opencode:/root/.config/opencode \
  -e OPENCODE_SERVER_PASSWORD=a123 \
  -e OPENCODE_SERVER_USERNAME
  ubuntu24-systemd:1.0
```



-v:用户于设置文件挂载，宿主机路径:容器内路径 ，挂载成功后，容器中被挂到的目录下的文件和目录将被隐藏，看到的都是宿主机的目录,指定到文件表示只挂载这个文件，宿主机文件所在的目录下的文件，容器是看不到的，可以有多个-v,注意宿主机的目录或文件要存在,-v 宿主机路径:容器内路径:挂载模式,ro:只读，rw读写(默认)
-e:用于设置容器中的环境变量

查看容器的详细信息
```bash
docker inspect agent-user-001
# 容器名称
```

查看容器的挂载情况，
```bash
docker inspect agent-user-001 --format '{{json .Mounts}}'
#  agent-user-001 是容器名称，通过 --format '{{json .Mounts}}'获取项信息
```
查看指定容器的所有环境变量
```bash
sudo docker exec agent-user-001 env
# agent-user-001是容器的名称
```


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

# 将容器转成转成镜像
```bash
sudo docker commit agent-user-001 agent-base:1.0
# agent-user-001 容器名称
# agent-base:1.0 镜像名称
```
docker commit 主要保存文件系统变化和镜像级配置，不保存容器的运行环境配置
docker commit 的 --change 参数用于在将容器提交为镜像时，修改新镜像的配置
```bash
docker commit --change 'Dockerfile指令' 容器名 新镜像名
```
示例
```bash
sudo docker commit \
  --change 'ENV NODE_ENV=production' \
  --change 'WORKDIR /app' \
  --change 'CMD ["bash"]' \
  agent-user-001 agent-base:1.0
```
--change 支持哪些指令
|指令|作用|示例|
|---|---|---|
| CMD	| 设置默认启动命令 |	CMD ["bash"] |
| ENTRYPOINT	| 设置启动入口	| ENTRYPOINT ["opencode"] |
| ENV	| 设置环境变量	| ENV NODE_ENV=production |
| WORKDIR	| 设置默认工作目录	| WORKDIR /app|
| USER	| 设置默认运行用户	| USER root |
| EXPOSE	| 声明容器端口	| EXPOSE 9080 |
| VOLUME	| 声明数据卷路径	| VOLUME /data |
| LABEL	| 设置镜像元数据	| LABEL version=1.0 |
| ONBUILD	| 设置子镜像构建触发器	| ONBUILD RUN echo hello |


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