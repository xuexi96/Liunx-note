# 设置用户运行Docker权限
在运行docker的主机上运行
```bash
sudo usermod -aG docker vm1
# vm1 是要运行docker的用户
```
如果提示 docker 组不存在，先执行
```bash
sudo groupadd docker
sudo usermod -aG docker vm1
```

# 配置ssh密钥
在需要连接docker的主机创建密钥
Windows 生成 SSH 密钥
```powershell
ssh-keygen -t ed25519 -C "docker-python"
```
查看公钥
```powershell
Get-Content "$HOME\.ssh\id_ed25519.pub"
```

在运行docker的主机上运行(主机地址：192.168.1.61)
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
vim ~/.ssh/authorized_keys # 将公钥复制到这个文件
```
设置权限
```bash
chmod 600 ~/.ssh/authorized_keys
```

在Windows运行
```powershell
ssh vm1@192.168.1.61
```


# 连接docker容器

需要安装

```bash
pip install paramiko
pip install docker
```
代码在Windows运行
```python
import docker

client = docker.DockerClient(
    base_url="ssh://vm1@192.168.1.61"
)

print(client.ping())

containers = client.containers.list(all=True)

for container in containers:
    print(container.name, container.status)
```

创建docker网络
```bash
docker network create \
  --driver bridge \
  --subnet 172.26.0.0/24 \
  -o com.docker.network.bridge.gateway_mode_ipv4=routed \
  agent-routed
```
对应python代码
```python

import docker
from docker.types import IPAMConfig, IPAMPool

# 连接远程 Docker
client = docker.DockerClient(
    base_url="ssh://vm1@192.168.1.61",
)

# 配置网络地址池
ipam = IPAMConfig(
    pool_configs=[
        IPAMPool(subnet="172.26.0.0/24")
    ]
)

# 创建 Docker 网络
network = client.networks.create(
    name="agent-routed",
    driver="bridge",
    ipam=ipam,
    options={
        "com.docker.network.bridge.gateway_mode_ipv4": "routed"
    }
)

print("网络 ID:", network.id)
print("网络名称:", network.name)

```

创建容器
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

使用python
```python
import docker

client = docker.DockerClient(
    base_url="ssh://vm1@192.168.2.204"
)

try:
    container = client.containers.run(
        image="ubuntu24-systemd:1.0",
        name="agent-user-001",
        hostname="agent-user-001",
        runtime="sysbox-runc",
        network="agent-routed",
        networking_config={
            "agent-routed": client.api.create_endpoint_config(
                ipv4_address="172.26.0.2"
            )
        },
        restart_policy={
            "Name": "unless-stopped"
        },
        ports={
            "9080/tcp": ("0.0.0.0", None) 
        },
        detach=True
    )

    container.reload()

    print("容器 ID:", container.id)
    print("容器名称:", container.name)
    print("容器状态:", container.status)

    print(
        "容器 IP:",
        container.attrs["NetworkSettings"]["Networks"]["agent-routed"]["IPAddress"]
    )

    print(
        "端口映射:",
        container.attrs["NetworkSettings"]["Ports"]
    )

finally:
    client.close()
```

在某个容器内运行命令
```python
import docker
import io
import tarfile
import json

client = docker.DockerClient(
    base_url="ssh://vm1@192.168.2.204",
)

try:
    container = client.containers.get("agent-user-001")

    # 创建目录
    result = container.exec_run(
        ["mkdir", "-p", "/root/config"],
        user="root"
    )
    if result.exit_code != 0:
        raise RuntimeError(result.output.decode())

    # 配置内容
    config = {}

    content = json.dumps(config, ensure_ascii=False, indent=2)
    file_data = content.encode("utf-8")

    # 在内存中创建 tar 文件
    buffer = io.BytesIO()

    with tarfile.open(fileobj=buffer, mode="w") as tar:
        info = tarfile.TarInfo("opencode.json")
        info.size = len(file_data)
        info.mode = 0o600

        tar.addfile(info, io.BytesIO(file_data))

    buffer.seek(0)

    # 上传文件到容器
    container.put_archive(
        path="/root/config",
        data=buffer.getvalue()
    )

    print("配置文件创建成功")

finally:
    client.close()

```