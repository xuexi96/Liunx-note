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
from datetime import timedelta
from opensandbox import Sandbox
from opensandbox.config import ConnectionConfig
from opensandbox.models.execd import RunCommandOpts


async def main():
    config = ConnectionConfig(
        domain="192.168.2.204:8080",
        api_key="12345678",
        use_server_proxy=True,
    )

    sandbox = await Sandbox.connect(
        "3c780db6-49db-4692-92b1-543afca93a95",
        config,
    )

    try:
        result = await sandbox.commands.run(
            "timeout --signal=TERM --kill-after=1s 9s ping www.baidu.com",
            opts=RunCommandOpts(
                timeout=timedelta(seconds=12)
            ),
        )

        # 优先读取退出码
        exit_code = result.exit_code

        # 兼容退出码只保存在错误对象中的情况
        if exit_code is None and result.error:
            exit_code = result.error.exit_code

        print("退出码：", exit_code)

        if result.error:
            print("错误类型：", result.error.name)
            print("错误信息：", result.error.value)

        if exit_code == 124:
            print("命令执行超时")
        elif exit_code == 0:
            print("命令正常结束")
        else:
            print("命令异常退出或退出状态未知")

        print("===== 标准输出 =====")
        for item in result.logs.stdout:
            print(item.text)

        print("===== 错误输出 =====")
        for item in result.logs.stderr:
            print(item.text)

    finally:
        await sandbox.close()


if __name__ == "__main__":
    asyncio.run(main())

```

沙箱中的文件的读写
```python
import asyncio
from opensandbox import Sandbox
from opensandbox.config import ConnectionConfig
from opensandbox.models import WriteEntry

async def main():
    config = ConnectionConfig(
        domain="192.168.2.204:8080",
        api_key="12345678",
        use_server_proxy=True,
    )

    sandbox = await Sandbox.connect(
        "3c780db6-49db-4692-92b1-543afca93a95",
        config,
    )

    try:
        # 写入文件
        await sandbox.files.write_files([
            WriteEntry(
                path="/workspace/hello.py",
                data='print("Hello OpenSandbox!")',
                mode=644,
            )
        ])
        # 读取文件
        read = await sandbox.files.read_file("/workspace/hello.py")
        print(read)

    finally:
        await sandbox.close()


if __name__ == "__main__":
    asyncio.run(main())
```

下载和上传文件到沙箱环境中
```python
import asyncio
from opensandbox import Sandbox
from opensandbox.config import ConnectionConfig
from opensandbox.models import WriteEntry

from pathlib import Path

async def main():
    config = ConnectionConfig(
        domain="192.168.2.204:8080",
        api_key="12345678",
        use_server_proxy=True,
    )

    sandbox = await Sandbox.connect(
        "25c2893d-bf8f-43e0-8520-1b24e5320e63",
        config,
    )

    local_path = Path(
        r"E:\pythonproject\docker-python\test.py"
    )
    file_data = local_path.read_bytes()
    await sandbox.files.write_files([
        WriteEntry(
            path="/test.py",
            data=file_data,
            mode=644,
        )
    ])
    print("上传成功")
    
    
    content = await sandbox.files.read_file(path="/test.py")
    local_path2 = Path(
        r"E:\pythonproject\docker-python\test2.py"
    )
    local_path2.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if isinstance(content, str):
        local_path2.write_text(
            content,
            encoding="utf-8",
        )
    else:
        local_path2.write_bytes(content)

    print("下载完成：", local_path)




asyncio.run(main())
```




