# Docker Compose 配置文件核心作用
把原本需要通过 docker run 命令配置的容器参数，统一写到 YAML 文件中，实现容器的创建、启动、停止和管理

## 安装
```bash
sudo apt update
sudo apt install docker-compose-v2 -y
```


# Compose YAML 的整体结构
```yaml
# ==========================================
# 第 1 层：项目名称
# ==========================================
name: my-project


# ==========================================
# 第 1 层：services（服务定义）
# ==========================================
services:

  # 第 2 层：服务名称（可以定义多个）
  app:

    # --------------------------------------
    # 第 3 层：镜像与容器基本配置
    # --------------------------------------
    image: ubuntu:24.04              # docker run IMAGE
    container_name: my-app           # --name my-app
    hostname: my-host                # --hostname my-host
    user: root                       # --user root
    working_dir: /app                # --workdir /app

    stdin_open: true                 # -i
    tty: true                        # -t
    privileged: false                # --privileged
    init: true                       # --init

    # --------------------------------------
    # 第 3 层：启动配置
    # --------------------------------------
    restart: unless-stopped          # --restart unless-stopped

    entrypoint: ["/bin/bash"]        # --entrypoint /bin/bash
    command: ["-c", "sleep infinity"] # IMAGE 后面的命令参数

    # --------------------------------------
    # 第 3 层：环境变量
    # --------------------------------------
    environment:                     # -e
      TZ: Asia/Shanghai              # -e TZ=Asia/Shanghai
      NODE_ENV: production           # -e NODE_ENV=production
      APP_PORT: "8080"               # -e APP_PORT=8080

    env_file:                        # --env-file
      - .env

    # --------------------------------------
    # 第 3 层：端口映射
    # --------------------------------------
    ports:                           # -p
      - "8080:80"                    # -p 8080:80
      - "127.0.0.1:9000:9000"        # -p 127.0.0.1:9000:9000

    expose:                          # --expose
      - "3000"                       # --expose 3000

    # --------------------------------------
    # 第 3 层：网络配置
    # --------------------------------------
    # network_mode: host             #  --network host
    networks:                        # --network
      agent-routed:                  # --network agent-routed
        ipv4_address: 172.26.0.5     # --ip 172.26.0.5

    dns:                             # --dns
      - 8.8.8.8
      - 1.1.1.1

    extra_hosts:                     # --add-host
      - "example.local:192.168.2.1"

    # --------------------------------------
    # 第 3 层：目录与数据卷挂载
    # --------------------------------------
    volumes:                         # -v
      - /home/data:/app/data         # -v /home/data:/app/data
      - app-data:/var/lib/app        # -v app-data:/var/lib/app
      - /home/config:/app/config:ro  # -v /home/config:/app/config:ro

    tmpfs:                           # --tmpfs
      - /tmp

    read_only: false                 # --read-only（true 时）

    # --------------------------------------
    # 第 3 层：CPU、内存、进程限制
    # --------------------------------------
    mem_limit: 4g                    # --memory 4g
    mem_reservation: 2g              # --memory-reservation 2g
    cpus: 2.0                        # --cpus 2
    cpu_shares: 512                  # --cpu-shares 512
    cpuset: "0-1"                    # --cpuset-cpus 0-1
    pids_limit: 200                  # --pids-limit 200
    shm_size: 1g                     # --shm-size 1g

    # --------------------------------------
    # 第 3 层：安全与权限
    # --------------------------------------
    runtime: runc                    # --runtime runc

    cap_add:                         # --cap-add
      - NET_ADMIN

    cap_drop:                        # --cap-drop
      - MKNOD

    security_opt:                    # --security-opt
      - no-new-privileges:true

    devices:                         # --device
      - /dev/null:/dev/null

    group_add:                       # --group-add
      - "1000"

    sysctls:                         # --sysctl
      net.ipv4.ip_forward: "1"

    # --------------------------------------
    # 第 3 层：日志
    # --------------------------------------
    logging:
      driver: json-file              # --log-driver json-file
      options:
        max-size: "10m"              # --log-opt max-size=10m
        max-file: "3"                # --log-opt max-file=3

    # --------------------------------------
    # 第 3 层：健康检查
    # --------------------------------------
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080"]
      interval: 30s                  # --health-interval 30s
      timeout: 10s                   # --health-timeout 10s
      retries: 3                     # --health-retries 3
      start_period: 10s              # --health-start-period 10s

    # --------------------------------------
    # 第 3 层：依赖服务
    # --------------------------------------
    depends_on:
      - redis                        # Compose 专有功能

  # 第 2 层：另一个服务
  redis:
    image: redis:7                   # docker run redis:7
    container_name: redis            # --name redis
    restart: unless-stopped          # --restart unless-stopped


# ==========================================
# 第 1 层：networks（网络声明）
# ==========================================
networks:

  agent-routed:                      # 网络名称
    external: true                   # 使用已经存在的网络

  # 自建网络示例
  app-network:
    driver: bridge                   # docker network create -d bridge
    ipam:
      config:
        - subnet: 172.28.0.0/24     # docker network create --subnet


# ==========================================
# 第 1 层：volumes（命名数据卷声明）
# ==========================================
volumes:

  app-data:
    driver: local                    # docker volume create


# ==========================================
# 第 1 层：configs（配置文件声明）
# ==========================================
configs:

  app-config:
    file: ./config.json


# ==========================================
# 第 1 层：secrets（敏感信息声明）
# ==========================================
secrets:

  app-secret:
    file: ./secret.txt
```

网络相关配置
```bash
docker network create \
  --driver bridge \
  --subnet 172.26.0.0/24 \
  -o com.docker.network.bridge.gateway_mode_ipv4=routed \
  agent-routed
```
对于的yaml
```yaml
networks:
  agent-routed:
    name: agent-routed
    driver: bridge
    driver_opts:
      com.docker.network.bridge.gateway_mode_ipv4: routed
    ipam:
      config:
        - subnet: 172.26.0.0/24
```


示例
```bash
docker run -d \
   --name magpie-server \
   --restart unless-stopped \
  --network agent-routed \
  --ip 172.26.0.2 \
  -p 0.0.0.0::3425 \
  -p 0.0.0.0::3430 \
  -e MAGPIE_WEB_KEY="5bd653a5a051471d0f1dc837050221b0" \
  -v /home/ffgy/magpie-config:/config \
  ghcr.io/yetone/magpie:latest \
  web --addr 0.0.0.0:3430 --no-open
```
magpie.yaml
```yaml
name: magpie
services:
   magpie-server:
      image: ghcr.io/yetone/magpie:latest
      container_name: magpie-server
      restart: unless-stopped 
      command: ["web","--addr","0.0.0.0:3430","--no-open"]
      environment:
         MAGPIE_WEB_KEY: "${MAGPIE_WEB_KEY}"
      ports:
         - "0.0.0.0::3425"
         - "0.0.0.0::3430"
      volumes:
         - /home/ffgy/magpie-config:/config
      networks: 
         agent-routed:
            ipv4_address: 172.26.0.2

networks:
  agent-routed:                    
    external: true                   
````
在同后面先通过.env 设置MAGPIE_WEB_KEY的值
.env的内容
```ENV
MAGPIE_WEB_KEY=5bd653a5a051471d0f1dc837050221b0
```

查看配置
```bash
docker compose -f magpie.yaml config
```

启动容器
```bash
docker compose -f magpie.yaml up -d
```

查看容器
```bash
docker compose -f magpie.yaml ps
```
查看日志
```bash
docker compose -f magpie.yaml logs -f
```

停止并删除容器
```bash
docker compose -f magpie.yaml down
```

拉取镜像
```bash
docker compose -f magpie.yaml pull
```
更新容器
```bash
docker compose -f magpie.yaml up -d
```

```bash
docker compose -f magpie.yaml up -d --pull always
```

# 通过Dockerfile与Docker Compose结合的方式创建容器
目录结构
docker-compose-project/
└── octop/
    ├── Dockerfile
    └── octop.yaml

Dockerfile的内容
```Dockerfile
FROM ghcr.nju.edu.cn/tencentcloud/octop:latest

# 安装基础依赖
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        ca-certificates \
        curl \
        gnupg && \
    rm -rf /var/lib/apt/lists/*

# 安装 Node.js 24
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

```
octop.yaml的内容
```yaml
name: octop

services:
  octop-server:

    # 镜像构建配置
    build:
      context: .
      dockerfile: Dockerfile
    
    # 构建后的镜像名称
    image: octop-node24:latest
    container_name: octop-server
    restart: unless-stopped
    environment:
      TZ: Asia/Shanghai
      HOME: /data

    volumes:
        - "/home/ffgy/octop-data:/data/.octop"

    ports:
        - "0.0.0.0::8088"


    # 网络配置
    networks:
      agent-routed:
        ipv4_address: 172.26.0.5

networks:
  agent-routed: # 已经之前通过命令创建，直接
    external: true

```