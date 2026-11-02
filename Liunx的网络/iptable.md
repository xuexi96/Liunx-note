# iptable的说明和使用

Linux 数据包流向
看图 iptables的数据链和表.png
```
                        外部网络
                            |
                            v
                    +----------------+
                    |  PREROUTING    |   <- 刚进机器，先过这里
                    +----------------+
                            |
                            v
                    +----------------+
                    | 路由判断        |   <- 判断目标是不是本机
                    +----------------+
                      |            |
          目标是本机   |            |   目标不是本机
                      v            v
              +-------------+   +-------------+
              |    INPUT    |   |   FORWARD   |
              +-------------+   +-------------+
                      |            |
                      v            v
                 本机进程        +----------------+
                 (ssh/nginx等)   | POSTROUTING   |
                                 +----------------+
                                          |
                                          v
                                       发出去

```

本机自己主动发包
```
                 本机进程
            (curl、ping、apt等)
                      |
                      v
               +--------------+
               |    OUTPUT    |
               +--------------+
                      |
                      v
               +--------------+
               | POSTROUTING  |
               +--------------+
                      |
                      v
                   发出去

```

三张核心表
filter 表：控制放行和拦截
包含 INPUT、FORWARD、OUTPUT。
常用动作：ACCEPT、DROP、REJECT。
```bash
# 查看filter 表的规则
sudo iptables -t filter -L -v
```


nat 表：修改源地址或目标地址
包含 PREROUTING、INPUT、OUTPUT、POSTROUTING。
常用动作：DNAT、SNAT、MASQUERADE
```bash
# 查看nat表的规则
sudo iptables -t nat -L -v
```

mangle 表：修改数据包相关属性
包含 PREROUTING、INPUT、FORWARD、OUTPUT、POSTROUTING。
常见用途：设置数据包 mark、调整 TTL、TCP MSS 等
```bash
# 查看 mangle上的规则
sudo iptables -t mangle -L -v
```

iptables 的基本语法
```bash
sudo iptables [-t 表名] 操作 链名 [匹配条件] [-j 动作]
```

常见操作参数

| 参数 | 含义 |
| --- | ------ |
|-A	|Append，追加|
|-I	|Insert，插入|
|-D	|Delete，删除|
|-R	|Replace，替换|
|-F	|Flush，清空链中的规则|
|-N	|New，创建自定义链|
|-X	|Delete Chain，删除自定义链|
|-P	|Policy，设置内置链默认策略|

常见匹配条件
|参数|	作用|	示例|
| ---| --- | --- |
|-s|	源 IP|	-s 10.10.2.1|
|-d|	目标 IP|	-d 172.26.0.2|
|-p|	协议|	-p tcp|
|--sport|	源端口|	--sport 8080|
|--dport|	目标端口|	--dport 22|
|-i|	入站网卡|	-i wg0|
|-o|	出站网卡|	-o enp3s0 |
|-m conntrack|	使用连接跟踪匹配|	-m conntrack --ctstateESTABLISHED,RELATED|
|-j| ACCEPT|	允许|	
|-j| DROP|	丢弃|	
|-j| REJECT|	拒绝并尽可能返回错误|

设置SNAT
```bash
sudo iptables -t nat -A POSTROUTING -s 172.26.0.0/24 -o enp3s0 -j SDAN --to-source 192.168.2.204

# 在POSTROUTING链的nat上匹配 源ip是172.26.0.0/24的网段，网卡是enp3s0的数据包，将数据包的源ip地址改成192.168.2.204
```

端口转发
```bash
sudo iptables -t nat -A PREROUTING -d 192.168.2.204 -p tcp --dport 8080 -j DNAT --to-destination 172.26.0.2:9080

# 在PREROUTING链的nat上面，追加一条规则，匹配目标地址是192.168.2.204 协议是tcp 目标端口是8080，将这个数据包的目标地址和端口改成172.26.0.2:9080
```

SNAT → 改源 IP → 通常在 POSTROUTING
DNAT → 改目标 IP → 通常在 PREROUTING