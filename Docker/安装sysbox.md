# sysbox使用

注意：sysbox依赖Docker,在安装sysbox前先安装Docker

# 安装

安装依赖
```bash
sudo apt update
sudo apt install -y wget curl jq
```

下载软件
https://github.com/nestybox/sysbox/releases

```bash
wget https://github.com/nestybox/sysbox/releases/download/v0.7.1/sysbox-ce_0.7.1.linux_amd64.deb 
```

安装
```bash
sudo apt install -y ./sysbox-ce_0.7.1.linux_amd64.deb
```

检查sysbox状态
```bash
sudo systemctl status sysbox
sudo systemctl status sysbox-mgr
sudo systemctl status sysbox-fs
```

检查 Docker 是否识别 Sysbox
```bash
 sudo docker info | grep -i runtime
```
输出
```text
Runtimes: io.containerd.runc.v2 runc sysbox-runc
Default Runtime: runc
```

运行 Sysbox 容器
```bash
sudo docker run \
  --runtime=sysbox-runc \
  --name sysbox-test \
  -it ubuntu:24.04 bash

```
退出容器：exit


启动 Sysbox 系统容器
```bash
mkdir -p ~/sysbox-systemd
cd ~/sysbox-systemd
```
在目录创建Dockerfile
Dockerfile文件内容
```Dockerfile


# Ubuntu 24.04 基础镜像
FROM ubuntu:24.04

# 禁止 apt 安装时弹出交互界面
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统工具、Python、Node.js、Git
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
        tzdata \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        python-is-python3 \
        nodejs \
        npm \
        build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 创建 SSH 运行目录
RUN mkdir -p /run/sshd

# systemd 停止信号
STOPSIGNAL SIGRTMIN+3

# 使用 systemd 作为 PID 1
CMD ["/sbin/init"]


```

使用dumb-init 作为 PID 1
Dockerfile
```Dockerfile
# 使用 Ubuntu 24.04 基础镜像
FROM ubuntu:24.04

# 避免安装软件时出现交互式提示
ENV DEBIAN_FRONTEND=noninteractive

# 安装 dumb-init 和常用工具
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        dumb-init \
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
        ca-certificates \
        tzdata && \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        python-is-python3 \
        nodejs \
        npm \
        build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 使用 dumb-init 作为 PID 1
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# 默认运行 bash
CMD ["sleep", "infinity"]

```

构建 Docker 镜像，在 Dockerfile 所在目录执行
```bash
sudo docker build -t ubuntu24-systemd:1.0 .
```

查看构建的镜像
```bash
sudo docker images
```

创建并运行sysbox容器
```bash
sudo docker run -d \
  --runtime=sysbox-runc \
  --name sysbox-systemd \
  --hostname sysbox-systemd \
  --restart unless-stopped \
  -p 127.0.0.1:2222:22 \
  ubuntu24-systemd:1.0

```
docker:Docker 命令行工具
run	创建并启动一个新容器
-d	后台运行容器，不占用当前终端
--runtime=sysbox-runc	使用 Sysbox 容器运行时，而不是默认的 runc
--name sysbox-systemd	设置 Docker 容器名称，方便管理
--hostname sysbox-systemd	设置容器内部的主机名
--restart unless-stopped	容器退出后自动重启，但手动停止后不会自动重启，直到再次手动启动
-p 127.0.0.1:2222:22	将宿主机本地的 2222 端口映射到容器的 22 端口
ubuntu24-systemd:1.0	指定要运行的 Docker 镜像及其版本标签

创建并使用容器，指定网络
创建网络
```bash
docker network create agent-net
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

查看容器分配到的ip地址
```bash
sudo docker inspect \
  -f '{{(index .NetworkSettings.Networks "agent-net").IPAddress}}' \
  agent-user-001
# agent-net 是网络
# agent-user-001 是容器名称
```

进入容器
```bash
docker exec -it  agent-user-001  /bin/bash

```