# Shell 脚本执行原理

## 什么是 Shebang
Shebang 本质上是告诉操作系统应该使用什么解释器

每个脚本都有
```bash
#!/bin/bash
```
当直接执行这个脚本时，应该使用哪个解释器
```bash
#!/bin/bash 
```
表示使用/bin/bash 

```bash
#!/usr/bin/env bash
```
表示由 env 根据当前的 PATH 环境变量


### Bash 执行脚本 和 直接执行脚本，source运行脚本 的区别
```bash
#!/bin/bash

NAME="Tom"

cd /tmp

echo "脚本执行完成"

```


#### bash直接运行脚本
```bash
bash hello.sh
```
1、当前 Shell 收到 bash hello.sh 命令
2、当前 Shell 启动一个新的 Bash 进程
3、新的 Bash 读取 hello.sh 文件
4、Bash 逐条解析并执行命令
5、脚本执行完成，新 Bash 进程退出

bash运行脚本，不需要给 hello.sh 设置执行权限

#### 直接执行脚本
```bash
chmod +x hello.sh

./hello.sh
```
1、当前 Shell 收到 ./hello.sh 命令
2、Shell 请求操作系统执行该文件
3、Linux 内核检查文件格式
4、内核读取 Shebang
5、启动对应的解释器
6、解释器读取脚本并执行

#### source 执行脚本
```bash
source hello.sh
```
source 会让当前 Bash 直接读取并执行这个脚本,因此,变量会保留在当前 Shell,路径会被切换，export 设置的环境变量也会保留

## Shell 脚本如何查看进程
```bash
#!/bin/bash

echo "当前进程 PID：$$"

echo "父进程 PID：$PPID"

ps -o pid,ppid,comm -p "$$,$PPID"
```
## Shell 脚本如何退出



