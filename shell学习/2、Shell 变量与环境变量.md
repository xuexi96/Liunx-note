# Shell 变量与环境变量

## 变量的赋值和引用
```shell
#!/bin/bash
NAME="Tom" 
AGE=18
APP_ENV="production"

# 使用 $ 或 ${}
echo $NAME
echo ${NAME}
```
注意：变量赋值等号两边不能有空格
```shell
NAME="Tom"    # 正确

NAME = "Tom"  # 错误
```

## Shell 变量的类型
普通变量
```shell
NAME="Tom"
```
环境变量
```shell
export NAME="Tom"
```
只读变量
```shell
#!/bin/bash
readonly APP_NAME="agent"

APP_NAME="other"
```
局部变量
```shell
#!/bin/bash
function test() {
    local NAME="Tom"

    echo "$NAME"
}

test

echo "$NAME"

```
数组变量
```shell
#!/bin/bash
SERVICES=("redis" "magpie" "opencode")

echo "${SERVICES[0]}"
echo "${SERVICES[1]}"
echo "${SERVICES[2]}"

echo "${SERVICES[@]}" # 获取所有元素
echo "${#SERVICES[@]}" # 获取数组长度
```
## 环境变量
进程之间的环境变量传递
在 Linux 中，每个进程都有自己的运行环境。
当一个进程创建并启动另一个程序时，可以通过 execve() 系统调用向新程序传递环境变量。
```shell
execve(path, argv, envp);
# envp 就是传递给新程序的环境变量数组
```
变量传递规则
普通变量只存在于当前 Shell 的变量环境中。
环境变量会被传递给新启动的子进程。
子进程可以读取父进程传递给它的环境变量。
子进程修改环境变量，不会反向修改父进程。

parent.sh
```shell
#!/bin/bash

NAME="Tom"

export AGE=18

export APP_ENV="production"

bash child.sh
```
child.sh
```shell
#!/bin/bash

echo "NAME: ${NAME}"
echo "AGE: ${AGE}"
echo "APP_ENV: ${APP_ENV}"
```
环境变量是单向继承，不是双向同步

## 常见变量默认值语法
|语法|	含义|
| ---|---|
|${VAR:-default}	|未设置或为空时使用默认值|
|${VAR-default}	|未设置时使用默认值|
|${VAR:=default}	|未设置或为空时赋默认值|
|${VAR:?message}	|未设置或为空时输出错误|
|${VAR:+value}	|已设置且不为空时使用指定值|

## 删除变量
```shell
NAME="Tom"

unset NAME #执行 unset 后，变量被删除

echo "$NAME"
```