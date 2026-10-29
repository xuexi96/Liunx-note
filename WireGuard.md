# Ubuntu安装WireGuard
更新软件包
```bash
sudo apt update
```
安装 WireGuard
```bash
sudo apt install wireguard -y
```

# 生成公钥和私钥
创建配置目录
```bash
sudo mkdir -p /etc/wireguard
sudo chmod 700 /etc/wireguard
```
生成服务器密钥
```bash
sudo sh -c 'umask 077; wg genkey > /etc/wireguard/server.key'
```
从私钥生成公钥
```bash
sudo sh -c 'wg pubkey < /etc/wireguard/server.key > /etc/wireguard/server.pub'
```

配置 WireGuard 服务端
sudo vim /etc/wireguard/wg0.conf


公网上面的Linux
```conf
[Interface]
# 公网服务器的 VPN IP
Address = 10.10.0.1/32
ListenPort = 51820
PrivateKey = <服务器私钥>

# Windows 客户端
[Peer]
PublicKey = <Windows公钥>
AllowedIPs = 10.10.2.1/32

# Linux 客户端及其后面的 Docker 网段
[Peer]
PublicKey = <Linux公钥>
AllowedIPs = 10.10.3.1/32, 172.26.0.0/24

```
打开防火墙
```bash
sudo ufw allow 51820/udp
```

启动 WireGuard
```bash
sudo systemctl start wg-quick@wg0
```
设置开机启动
```bash
sudo systemctl enable wg-quick@wg0
```
检查运行状态
```bash
sudo systemctl status wg-quick@wg0
```
查看 WireGuard 接口
```bash
ip addr show wg0
```
查看连接信息
```bash
sudo wg show
```


内网的Windows 客户端
```conf
[Interface]
PrivateKey = <Windows私钥>
Address = 10.10.2.1/32

[Peer]
PublicKey = <服务器公钥>
Endpoint = <公网IP>:51820

# Windows 访问 Linux 及其 Docker 网络
AllowedIPs = 10.10.3.1/32, 172.26.0.0/24

# 定期发送保活包，维持 NAT 映射
PersistentKeepalive = 25
```

内网的Linxu运行(Docker地址172.26.0.1)
```conf
[Interface]
PrivateKey = <Linux私钥>
Address = 10.10.3.1/32

[Peer]
PublicKey = <服务器公钥>
Endpoint = <公网IP>:51820

# Windows 的 VPN 地址：用于返回响应数据
AllowedIPs = 10.10.2.1/32

# NAT 保活
PersistentKeepalive = 25
```

