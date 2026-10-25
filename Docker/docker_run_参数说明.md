# Docker run 参数说明

## 一、docker run 的基本格式

```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

| 部分 | 作用 | 示例 |
|---|---|---|
| `docker run` | 创建并启动容器 | `docker run` |
| `OPTIONS` | Docker 容器的配置参数 | `-d --name myc -p 8080:80` |
| `IMAGE` | 使用的镜像 | `ubuntu:24.04` |
| `COMMAND` | 覆盖镜像的默认 CMD，或作为 ENTRYPOINT 的参数 | `/bin/bash` |
| `ARG` | 传给启动命令的参数 | `-c "echo hello"` |

## 二、常用参数完整分类

### 1. 容器基本设置

| 参数 | 作用 | 示例 |
|---|---|---|
| `--name` | 指定容器名称 | `--name myc` |
| `-d`, `--detach` | 后台运行 | `-d` |
| `-i`, `--interactive` | 保持标准输入打开 | `-i` |
| `-t`, `--tty` | 分配伪终端 | `-t` |
| `--rm` | 容器退出时自动删除 | `--rm` |
| `--hostname`, `-h` | 设置容器主机名 | `--hostname agent-001` |
| `--workdir`, `-w` | 设置容器工作目录 | `-w /app` |
| `--user`, `-u` | 指定运行用户 | `-u root` |
| `--entrypoint` | 覆盖镜像的 ENTRYPOINT | `--entrypoint /bin/bash` |
| `--pull` | 设置镜像拉取策略 | `--pull always` |
| `--init` | 在容器中运行一个轻量级 init 进程 | `--init` |
| `--stop-signal` | 指定停止信号 | `--stop-signal SIGTERM` |
| `--stop-timeout` | 指定停止等待时间 | `--stop-timeout 30` |

### 2. 网络和端口

| 参数 | 作用 | 示例 |
|---|---|---|
| `--network` | 指定 Docker 网络 | `--network agent-routed` |
| `--ip` | 指定容器 IPv4 地址 | `--ip 172.26.0.2` |
| `--ip6` | 指定容器 IPv6 地址 | `--ip6 2001:db8::10` |
| `-p`, `--publish` | 将容器端口发布到宿主机 | `-p 9080:9080` |
| `-P`, `--publish-all` | 发布镜像声明的端口 | `-P` |
| `--expose` | 在运行配置中声明容器端口 | `--expose 8080` |
| `--dns` | 指定 DNS 服务器 | `--dns 8.8.8.8` |
| `--dns-search` | 设置 DNS 搜索域 | `--dns-search example.com` |
| `--add-host` | 添加 hosts 记录 | `--add-host api.local:192.168.2.10` |
| `--network-alias` | 设置网络别名 | `--network-alias agent-api` |
| `--mac-address` | 指定 MAC 地址（受网络驱动限制） | `--mac-address 02:42:ac:11:00:02` |

**注意：** 如果 `agent-routed` 网络使用 `com.docker.network.bridge.gateway_mode_ipv4=routed`，这种模式不采用常规的宿主机端口 NAT 映射，应通过可路由的容器 IP 和容器端口访问服务。

### 3. 目录挂载和存储

| 参数 | 作用 | 示例 |
|---|---|---|
| `-v`, `--volume` | 挂载目录或命名数据卷 | `-v /host/data:/data` |
| `--mount` | 更明确地配置挂载类型和参数 | `--mount type=bind,src=/host/data,dst=/data` |
| `--volumes-from` | 使用其他容器的数据卷 | `--volumes-from myc` |
| `--read-only` | 将容器根文件系统设为只读 | `--read-only` |
| `--tmpfs` | 创建内存文件系统挂载 | `--tmpfs /tmp` |
| `--volume-driver` | 指定数据卷驱动 | `--volume-driver local` |

`-v` 可以用于两种常见情况：

```bash
# Bind Mount：挂载宿主机目录
-v /home/vm1/hermes:/opt/data

# Named Volume：挂载 Docker 命名数据卷
-v hermes-data:/opt/data
```

### 4. 环境变量和配置

| 参数 | 作用 | 示例 |
|---|---|---|
| `-e`, `--env` | 设置环境变量 | `-e TZ=Asia/Shanghai` |
| `--env-file` | 从文件加载环境变量 | `--env-file /home/vm1/app.env` |
| `--label`, `-l` | 给容器添加标签 | `--label app=hermes` |
| `--label-file` | 从文件加载标签 | `--label-file labels.txt` |

例如：

```bash
docker run -d \
  --name myc \
  --env-file /home/vm1/app.env \
  -e APP_ENV=production \
  my-image
```

### 5. CPU、内存和资源限制

| 参数 | 作用 | 示例 |
|---|---|---|
| `--memory`, `-m` | 限制内存 | `--memory 2g` |
| `--memory-swap` | 限制内存加交换空间的总量 | `--memory-swap 4g` |
| `--cpus` | 限制可使用的 CPU 计算配额 | `--cpus 2.0` |
| `--cpuset-cpus` | 限制可在哪些 CPU 核心运行 | `--cpuset-cpus 0-3` |
| `--cpu-shares` | 设置 CPU 相对权重 | `--cpu-shares 512` |
| `--pids-limit` | 限制进程数量 | `--pids-limit 256` |
| `--ulimit` | 设置进程资源限制 | `--ulimit nofile=65535:65535` |
| `--shm-size` | 设置 `/dev/shm` 容量 | `--shm-size 1g` |

例如：

```bash
docker run -d \
  --name agent-user-001 \
  --cpus 2 \
  --memory 4g \
  --pids-limit 512 \
  my-image
```

这适合多用户 Agent 容器，用于减少单个用户占用过多资源的风险。

### 6. 权限和安全

| 参数 | 作用 | 示例 |
|---|---|---|
| `--runtime` | 指定容器运行时 | `--runtime=sysbox-runc` |
| `--privileged` | 授予容器广泛的额外权限 | `--privileged` |
| `--cap-add` | 添加 Linux Capability | `--cap-add NET_ADMIN` |
| `--cap-drop` | 移除 Linux Capability | `--cap-drop NET_RAW` |
| `--security-opt` | 设置安全选项 | `--security-opt no-new-privileges:true` |
| `--device` | 将宿主机设备提供给容器 | `--device /dev/fuse` |
| `--group-add` | 添加附加用户组 | `--group-add 1000` |

**安全建议：** 不要因为 Agent 需要运行 Bash，就直接使用 `--privileged`。尤其是运行不可信代码时，应尽量保留最小权限。

### 7. 容器生命周期与健康检查

| 参数 | 作用 | 示例 |
|---|---|---|
| `--restart` | 自动重启策略 | `--restart unless-stopped` |
| `--health-cmd` | 健康检查命令 | `--health-cmd "curl -f http://localhost:8080/health"` |
| `--health-interval` | 健康检查间隔 | `--health-interval 30s` |
| `--health-timeout` | 单次健康检查超时 | `--health-timeout 5s` |
| `--health-retries` | 连续失败多少次判定不健康 | `--health-retries 3` |
| `--health-start-period` | 启动宽限期 | `--health-start-period 30s` |
| `--log-driver` | 日志驱动 | `--log-driver json-file` |
| `--log-opt` | 日志配置 | `--log-opt max-size=10m` |

**注意：** 健康检查标记为 `unhealthy` 不代表 Docker 默认会自动重启容器；重启策略主要针对容器主进程退出。
