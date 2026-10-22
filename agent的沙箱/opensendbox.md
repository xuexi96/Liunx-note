# 安装opensandbox沙箱

下载沙箱
```bash
pip install opensandbox-server
或
uvx opensandbox-server init-config ~/.sandbox.toml --example docker
```

初始化配置文件
```bash
opensandbox-server init-config ~/.sandbox.toml --example docker
```
如果需要远程访问沙箱需要将.sandbox.toml 文件的`host:0.0.0.0`,配置`api_key:`
```toml
[server]
host = "0.0.0.0"
api_key="12345678"

```


创建沙箱并运行命令
```python

import os
import asyncio
from datetime import timedelta
from opensandbox import Sandbox
from opensandbox.config import ConnectionConfig


async def main():
    config = ConnectionConfig(
        domain="192.168.2.204:8080",
        api_key="12345678",
        use_server_proxy=True,

    )
    # 创建沙箱
    sandbox = await Sandbox.create(
        "agent-base:1.0",  # 镜像可以是docker容器存在的镜像
        timeout=timedelta(minutes=30), # 设置沙箱的有效期，时间到自动销毁，当是None时，是永久，手动清理
        connection_config=config,
    )

    print("沙箱 ID:", sandbox.id)

    try:
        # 执行命令
        result = await sandbox.commands.run(
            "hostname && pwd && python --version"
        )
        #
        for output in result.logs.stdout:
            print(output.text)

    finally:
        # 销毁沙箱
        await sandbox.destroy()


if __name__ == "__main__":
    asyncio.run(main())

```

查看已经存在的沙箱
```
url:http://192.168.2.204:8080/v1/sandboxes
get请求
请求头：
{
    "OPEN-SANDBOX-API-KEY":"12345678"
}

```

连接已经存在的沙箱
```python

import asyncio
import os

from opensandbox import Sandbox
from opensandbox.config import ConnectionConfig


async def main():
    config = ConnectionConfig(
        domain="192.168.2.204:8080",
        api_key="12345678",
        use_server_proxy=True,
    )

    sandbox = await Sandbox.connect(
        sandbox_id="807e99e0-ec03-440d-b1fb-a99548c7500d", # 连接沙箱id
        connection_config=config,
    )

    try:
        # 运行命令
        result = await sandbox.commands.run(
            "whoami && hostname && pwd && ls -la"
        )
        # 获取标准输出
        for item in result.logs.stdout:
            print(item.text)
    finally:
        # 关闭沙箱
        await sandbox.close()


asyncio.run(main())

```



