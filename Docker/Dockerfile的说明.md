# Docker的Dockerfile

Dcokerfile用来制作Docker的镜像

## Dockerfile 全部指令
### 基础指令

| 指令 | 作用 | 示例 |
|---|---|---|
| `FROM` | 指定基础镜像 | `FROM ubuntu:24.04` |
| `RUN` | 构建镜像时执行命令 | `RUN apt-get install -y curl` |
| `CMD` | 设置容器启动时的默认命令 | `CMD ["python3", "app.py"]` |
| `ENTRYPOINT` | 设置容器的默认执行程序 | `ENTRYPOINT ["python3"]` |
| `WORKDIR` | 设置工作目录，这个目录没有，会自动创建，Docker 镜像内部的当前工作目录。后续的 RUN、CMD、ENTRYPOINT 等指令会以这个目录作为默认工作目录 | `WORKDIR /app` |
| `COPY` | 复制文件到镜像,将宿主机的opencode.json文件复制到容器的/root/.config/opencode/目录，容器里的/root/.config/opencode/不存在时，容器自动创建，要复制的文件或目录和Dockerfile文件在同一目录 | `COPY opencode.json /root/.config/opencode/` |
| `ADD` | 复制文件，也支持自动解压本地归档等功能 | `ADD app.tar.gz /app/` |
| `ENV` | 设置环境变量，默认在容器运行时保留 | `ENV TZ=Asia/Shanghai` |
| `ARG` |	设置构建时，定义变量，与ENV的区别，ENV容器运行时设置的变量还在，ARG只在构建时存在，构建完成后不存在 | `ARG VERSION=1.0` |

### 容器配置指令
| 指令 | 作用 | 示例 |
|---|---|---|
| `EXPOSE` | 声明容器监听的端口,这里只是声明 | `EXPOSE 9080` |
| `USER` | 指定后续构建步骤及默认进程使用的用户，镜像构建阶段，器运行阶段都使用这个用户，USER只影响USER后面的命令 | `USER appuser` |
| `VOLUME` | 声明数据卷挂载点 | `VOLUME /data` |
| `HEALTHCHECK` | 设置容器健康检查 | `HEALTHCHECK CMD curl -f http://localhost:8080/ |
| `STOPSIGNAL` | 设置容器停止信号 | `STOPSIGNAL SIGTERM` |
| `LABEL` | 给镜像添加元数据 | LABEL version="1.0" |

### 高级指令
| 指令 | 作用 | 示例 |
|---|---|---|
|`SHELL`|	修改默认 Shell	| `SHELL ["/bin/bash", "-c"]`|
| `ONBUILD`|	设置子镜像构建时触发的指令	|`ONBUILD COPY . /app`|

#### RUN、CMD、ENTRYPOINT说明
|特性|RUN|CMD|ENTRYPOINT|
|---|---|---|---|
|构建镜像时执行|	是|	否|	否|
|启动容器时执行|	否|	是|	是|
|用途|	安装和配置软件	|设置默认命令或参数|	指定主程序|
|可以写多次|	可以|	可以，但只保留最后一个|	可以，但只保留最后一个|

##### RUN
RUN 就是在构建镜像时，执行一条命令,
每一条 RUN 通常会形成一个镜像构建层，后面的命令可以使用前面留下来的文件和软件
Dockerfile 中，每一条 RUN 默认都会启动一个新的 Shell 进程，因此不是同一个 Shell 上下文，在构建过程中
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

简单的Dockerfile的模板(错误示例)
```Dockerfile
FROM ubuntu:24.04

# 设置工作目录，启动 shell 默认所在的目录
WORKDIR /app

# 设置时区
ENV TZ=Asia/Shanghai

ENV DEBIAN_FRONTEND=noninteractive

# 更新软件源
RUN apt update 

# 安装
# ca-certificates # 安装证书

RUN  apt-get install -y --no-install-recommends \
        ca-certificates \ 
        curl \
        git 

# 删除 APT 下载的软件包索引缓存，这些文件已经在前面的镜像层，这里面只是隐藏，构建出来的镜像会很大        
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

ENV DEBIAN_FRONTEND=noninteractive 

# 更新软件源、安装软件、清理缓存
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# 容器启动命令（按实际需要填写）
ENTRYPOINT ["curl"]
CMD ["http://192.168.2.204:5000/v2/ubuntu/tags/list"]

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

查看镜像的信息
```bash
sudo docker inspect ubuntu24-systemd:1.0
```
