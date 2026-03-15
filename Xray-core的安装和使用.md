# Xray-core的安装和使用

## 安装



```
bash <(curl -Ls https://github.com/XTLS/Xray-install/raw/main/install-release.sh)
或
bash <(wget -qO- https://github.com/XTLS/Xray-install/raw/main/install-release.sh)
```

## 更新

```
bash <(curl -Ls https://github.com/XTLS/Xray-install/raw/main/install-release.sh) install
```



## 卸载

```
bash <(curl -Ls https://github.com/XTLS/Xray-install/raw/main/install-release.sh) remove
```



## Xray-core的默认目录

```
/usr/local/bin/xray          # 主程序
/usr/local/etc/xray/config.json   # 配置文件
/usr/local/share/xray/geoip.dat
/usr/local/share/xray/geosite.dat
```



## systemd 管理

启动：

```
systemctl start xray
```

开机启动：

```
systemctl enable xray
```

重启：

```
systemctl restart xray
```

状态：

```
systemctl status xray
```

日志：

```
journalctl -u xray -f
```



Xray-core数据流结构

```
客户端
   │
   ▼
Inbound（入站）
   │
   ▼
Routing（路由规则）
   │
   ├──────────────► DNS
   │
   ▼
Outbound（出站）
   │
   ▼
目标服务器
```



## 配置模块

```json
{
  "log": {},
  "dns": {},
  "inbounds": [],
  "outbounds": [],
  "routing": {},
  "policy": {},
  "stats": {},
  "api": {},
  "transport": {},
  "reverse": {},
  "fakedns": {}
}
```

核心模块

```
log
dns
inbounds
outbounds
routing
```



# 入站配置

```json
{
  "inbounds": [
    {
      "tag": "标识名",
      "port": 443,
      "listen": "0.0.0.0",
      "protocol": "协议名",
      "settings": {},
      "streamSettings": {},
      "sniffing": {},
      "allocate": {}
    }
  ]
}
```

tag — 入站标识，路由规则通过 `inboundTag` 引用它，用来区分不同入站的流量。不设的话路由无法按入站来源分流。

port — 监听端口

listen — 监听地址

protocol — 入站协议

| 协议            | 用途                      |
| --------------- | ------------------------- |
| `vless`         | 主流推荐，轻量            |
| `vmess`         | V2Ray 兼容                |
| `trojan`        | Trojan 兼容               |
| `shadowsocks`   | SS 兼容                   |
| `socks`         | 本地 SOCKS5 代理入站      |
| `http`          | 本地 HTTP 代理入站        |
| `dokodemo-door` | 任意门，透明代理/端口转发 |

settings — 协议参数

​			fallbacks 回落参数详解



streamSettings — 传输层配置

```json
"streamSettings": {
  "network": "tcp",
  "security": "tls",
  "tlsSettings": {},
  "realitySettings": {},
  "tcpSettings": {},
  "wsSettings": {},
  "grpcSettings": {},
  "httpSettings": {}
}
```

sniffing — 流量嗅探

```json
"sniffing": {
  "enabled": true,
  "destOverride": ["http", "tls", "quic", "fakedns"],
  "metadataOnly": false,
  "routeOnly": true
}
```

| 字段           | 说明                                   |
| -------------- | -------------------------------------- |
| `enabled`      | 开启嗅探                               |
| `destOverride` | 嗅探哪些协议来覆盖目标地址             |
| `metadataOnly` | 仅用元数据嗅探，不读内容               |
| `routeOnly`    | 嗅探结果仅用于路由，不覆盖实际目标地址 |

allocate — 端口分配策略



# 路由配置

```json
{
  "routing": {
    "domainStrategy": "AsIs",
    "domainMatcher": "hybrid",
    "rules": [],
    "balancers": []
  }
}
```

domainStrategy — 域名解析策略

| 值             | 行为                                           |
| -------------- | ---------------------------------------------- |
| `AsIs`         | 默认，仅用域名匹配规则，不做 DNS 解析          |
| `IPIfNonMatch` | 域名规则没匹配到时，解析成 IP 再用 IP 规则匹配 |
| `IPOnDemand`   | 遇到任何 IP 规则就立刻解析域名为 IP            |

domainMatcher — 域名匹配算法

rules — 路由规则（核心）

```json
{
  "type": "field",
  "outboundTag": "出站tag",    // 匹配后走哪个出站
  // 或
  "balancerTag": "均衡器tag",  // 匹配后走负载均衡

  // 以下是匹配条件，可以组合使用（同一条规则内是 AND 关系）
  "domain": [],
  "ip": [],
  "port": "",
  "sourcePort": "",
  "network": "",
  "source": [],
  "user": [],
  "inboundTag": [],
  "protocol": [],
  "attrs": {}
}
```

### 匹配条件详解

**domain — 域名匹配**

```json
"domain": [
  "full:www.google.com",        // 精确匹配
  "domain:google.com",          // 匹配 google.com 及所有子域名
  "keyword:youtube",            // 包含 youtube 的域名
  "regexp:\\.cn$",              // 正则匹配
  "geosite:cn",                 // 预定义域名集：中国网站
  "geosite:geolocation-!cn",   // 预定义域名集：非中国网站
  "geosite:category-ads-all",  // 预定义域名集：广告
  "geosite:google",            // 预定义域名集：Google 系
  "geosite:netflix",           // Netflix
  "geosite:openai"             // OpenAI
]
```

省略前缀时的默认行为：

- 纯字母域名如 `"google.com"` → 等同于 `"domain:google.com"`
- 带 `.` 开头的 `".cn"` → 等同于 `"regexp:\\.cn$"`

**ip — IP 匹配**

```json
"ip": [
  "geoip:cn",                   // 中国 IP
  "geoip:private",              // 内网 IP（10.x / 172.x / 192.168.x）
  "geoip:us",                   // 美国 IP
  "1.2.3.4",                    // 单个 IP
  "10.0.0.0/8",                 // CIDR 段
  "::1/128"                     // IPv6
]
```

**port — 目标端口**

```json
"port": "80",                    // 单端口
"port": "443",
"port": "80,443",                // 多端口
"port": "1000-2000"             // 端口范围
```

**sourcePort — 来源端口**

```json
"sourcePort": "1234,5678"
```

**network — 网络类型**

```json
"network": "tcp"                 // 仅匹配 TCP
"network": "udp"                 // 仅匹配 UDP
"network": "tcp,udp"             // 两者都匹配
```

**source — 来源 IP**

```json
"source": [
  "10.0.0.100",                  // 特定客户端 IP
  "192.168.1.0/24"              // 特定网段
]
```

**user — 用户标识**

```json
"user": [
  "user1@example.com",           // 匹配 inbound 中设置的 email
  "user2@example.com"
]
```

可以实现不同用户走不同出站。

**inboundTag — 来源入站**

```json
"inboundTag": ["trojan-in", "vless-in"]
```

指定从哪个入站进来的流量适用这条规则。

**protocol — 流量协议类型**

```json
"protocol": ["http", "tls", "bittorrent"]
```

需要 `sniffing` 开启才能识别。常用于屏蔽 BT 下载。



## 出站配置

```json
{
  "tag": "my-outbound",
  "protocol": "协议名",
  "settings": {},
  "streamSettings": {},
  "proxySettings": {},
  "mux": {}
}
```

各字段含义：

- `tag` — 标识名，路由规则通过它指定走哪个出站
- `protocol` — 上面表格中的协议名
- `settings` — 协议相关参数（服务器地址、认证等）
- `streamSettings` — 传输层配置（TCP/WS/gRPC、TLS/REALITY）
- `proxySettings` — 链式代理，指定先经过另一个 outbound 再出去
- `mux` — 多路复用，多个连接共用一个底层连接

### protocol

**代理协议（转发到下一跳）**

| 协议          | 用途                                 |
| ------------- | ------------------------------------ |
| `vless`       | 转发到 VLESS 服务端，轻量高效，推荐  |
| `vmess`       | 转发到 VMess 服务端，兼容 V2Ray      |
| `trojan`      | 转发到 Trojan 服务端                 |
| `shadowsocks` | 转发到 SS 服务端                     |
| `socks`       | 转发到 SOCKS5 代理（住宅IP常用）     |
| `http`        | 转发到 HTTP/HTTPS 代理（住宅IP常用） |
| `wireguard`   | 通过 WireGuard 隧道出站（如接 WARP） |

**功能协议（特殊用途）**

| 协议        | 用途                                   |
| ----------- | -------------------------------------- |
| `freedom`   | 直连，VPS 本机 IP 出去                 |
| `blackhole` | 丢弃流量，用于屏蔽广告/特定域名        |
| `dns`       | 劫持 DNS 请求，转给 Xray 内置 DNS 处理 |
| `loopback`  | 回环，把流量重新送回路由模块再匹配一次 |



#### freedom 出站可选配置

```json
{
  "protocol": "freedom",
  "tag": "direct",
  "settings": {
    "domainStrategy": "AsIs",
    "redirect": "127.0.0.1:8080"
  }
}
```

`domainStrategy` 控制 DNS 解析行为：

- `"AsIs"` — 默认值，直接用原始域名连接，不做额外 DNS 解析
- `"UseIP"` — 先用 Xray 内置 DNS 解析，再用 IP 连接
- `"UseIPv4"` — 强制解析为 IPv4
- `"UseIPv6"` — 强制解析为 IPv6

`redirect` 可以把所有流量强制转发到指定地址，不常用。



#### SOCKS5 出站（接住宅 IP）

```json
{
  "tag": "residential",
  "protocol": "socks",
  "settings": {
    "servers": [
      {
        "address": "gate.provider.com",
        "port": 7777,
        "users": [
          { "user": "xxx", "pass": "xxx" }
        ]
      }
    ]
  }
}
```





配置trojan协议

```json
{
  "log": {
    "loglevel": "warning"
  },
   // 4*入站设置
  "inbounds": [
    {
      "tag": "trojan-in",
      "port": 443,
      "protocol": "trojan", //trojan协议
      "settings": {
        "clients": [
          {
            "password": "12345678910", // 密码
            "email": "user1" // 区分用户
          }
        ],
        
        "fallbacks": [
          {
            "dest": 80  // 默认回落到防探测的代理
          }
        ]
      },
      "streamSettings": {
        "network": "tcp",
        "security": "tls",
        "tlsSettings": {
          "alpn": ["h2", "http/1.1"],
          "certificates": [
            {
              "certificateFile": "/usr/local/etc/xray/ssl/trojan.crt",
              "keyFile": "/usr/local/etc/xray/ssl/trojan.key"
            }
          ]
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls"]
      }
    }
  ],
  // 5*出站设置
  "outbounds": [
    // 第一个出站是默认规则，freedom 就是对外直连（vps 已经是外网，所以直连）
    {
      "tag": "direct",
      "protocol": "freedom"
    },
    
    // 5.2 屏蔽规则，blackhole 协议就是把流量导入到黑洞里（屏蔽）
    {
      "tag": "block", 
      "protocol": "blackhole"
    }
  ],
  "routing": {
    "rules": [
      {
        "type": "field",
        "outboundTag": "block",// 分流策略：交给出站"block"处理（黑洞屏蔽）
        "domain": ["geosite:category-ads-all"]  // 分流条件：geosite 文件内，名为"category-ads-all"的规则（各种广告域名）
      }
    ]
  }
}
```



https://xtls.github.io/document/level-1/fallbacks-lv1.html

开启BBR

适用于内核 4.9+

```
echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
sysctl -p
```

