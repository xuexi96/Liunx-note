# Linux的路由
ip route 是 Linux 中用于查看、添加、修改、删除路由表的命令，属于 iproute2 工具集。
它决定 Linux 收到或发送一个 IP 数据包时，应该从哪个网卡发出去、下一跳网关是谁

ip route 常用命令

|命令|	作用|
| ---| ---| 
|ip route|	查看 IPv4 主路由表|
|ip route show|	查看路由|
|ip route add|	添加路由|
|ip route del|	删除路由|
|ip route replace|	添加或替换路由|
|ip route change|	修改已存在的路由|
|ip route get|	查询到某个目标的路由选择|
|ip route flush|	批量清除路由|
|ip route show| table all	查看所有路由表|
|ip -6 route|	查看 IPv6 路由|

## 查看路由
```bash
 ip route

 # default via 192.168.2.1 dev enp3s0 proto dhcp src 192.168.2.204 metric 100
```
|字段|	含义|
|---|---|
|default|	默认路由，等同于 0.0.0.0/0|
|via 192.168.2.1|	下一跳网关|
|dev enp3s0|	从该网卡发出去|
|proto dhcp|	由 DHCP 配置|
|metric 100|	路由优先级指标，通常越小越优先|

```bash
# 172.26.0.0/24 dev br-ce9157947bce proto kernel scope link src 172.26.0.1
```
|参数|	含义|
| ------ | ------ |
|172.26.0.0/24|	目标网段，范围 172.26.0.0～172.26.0.255|
|dev br-ce9157947bce|	数据包从这个网络接口发出|
|proto kernel|	这条路由由 Linux 内核自动生成|
|scope link|	目标网络在直接连接的链路上，不需要下一跳 |IP 网关|
|src 172.26.0.1|	本机发送数据时优先使用的源 IP|

## 添加路由：ip route add

### 添加直连路由
```bash

ip route add 172.26.0.0/24 dev br-ce9157947bce

# 访问 172.26.0.0/24，使用网卡 br-ce9157947bce
```

### 添加网关路由
```bash
sudo ip route add 172.26.0.0/24 via 192.168.2.204

# 访问 172.26.0.0/24，将数据包交给 192.168.2.204 转发
```

### 添加默认路由
```bash
sudo ip route add default via 192.168.2.1 dev enp3s0
```

## 删除路由：ip route del
### 删除指定网段路由
```bash
# 删除指定网段路由
sudo ip route del 172.26.0.0/24
# 精确地指定
sudo ip route del 172.26.0.0/24 dev br-ce9157947bce

#删除默认路由
sudo ip route del default
```

## 修改路由：ip route replace
假设已经存在
```bash
10.10.0.0/16 via 192.168.2.100 dev enp3s0
```

```bash
# 修改网关
# replace路由不存在：添加
# 路由存在：替换匹配的路由
sudo ip route replace 10.10.0.0/16 via 192.168.2.200 dev enp3s0
```


## 查询路由：ip route get
```bash
ip route get 172.26.0.2
```