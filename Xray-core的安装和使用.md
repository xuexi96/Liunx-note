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

### tag 入站标识

路由规则通过 `inboundTag` 引用它，用来区分不同入站的流量。不设的话路由无法按入站来源分流。

### port 

监听端口

### listen

监听地址

### protocol 

 入站协议

| 协议            | 用途                      |
| --------------- | ------------------------- |
| `vless`         | 主流推荐，轻量            |
| `vmess`         | V2Ray 兼容                |
| `trojan`        | Trojan 兼容               |
| `shadowsocks`   | SS 兼容                   |
| `socks`         | 本地 SOCKS5 代理入站      |
| `http`          | 本地 HTTP 代理入站        |
| `dokodemo-door` | 任意门，透明代理/端口转发 |

### settings 

#### clients

Trojan 协议

```json
"settings": {
  "clients": [
    {
      "password": "12345678910",//用户密码，客户端连接时用
      "email": "user1", // 用户标识，用于流量统计和日志区分
      "level": 0 //用户等级，对应 policy 中的等级策略
    }
  ],
  "fallbacks": [
    { "dest": 80 }
  ]
}
```

VMess 协议

```json
"settings": {
  "clients": [
    {
      "id": "a3482e88-686a-4a58-8126-99c9df64b7bf", //UUID，相当于密码
      "alterId": 0, //额外 ID 数量，现在都填 0（启用 VMessAEAD 加密，更安全）
      "email": "user1",
      "level": 0
    }
  ]
}
```

VLESS 协议

```json
"settings": {
  "clients": [
    {
      "id": "a3482e88-686a-4a58-8126-99c9df64b7bf", //UUID
      "email": "user1",
      "level": 0,
      "flow": "xtls-rprx-vision" //flow → 流控模式，配合 REALITY 时常用 "xtls-rprx-vision"
    }
  ],
  "decryption": "none",
  "fallbacks": [
    { "dest": 80 }
  ]
}
```

Shadowsocks 协议

```json
"settings": {
  "clients": [
    {
      "password": "mypassword",  
      // 加密方式，推荐 "2022-blake3-aes-128-gcm" 或 "2022-blake3-chacha20-poly1305"
      "method": "2022-blake3-aes-128-gcm",
      "email": "user1"
    }
  ],
  "network": "tcp,udp" //支持的网络类型，"tcp,udp" 表示都支持
}
```

Dokodemo-door（任意门）

用于透明代理或端口转发

```json
"settings": {
  "address": "1.1.1.1", // 转发目标地址
  "port": 53,//转发目标端口
  "network": "tcp,udp",
  "followRedirect": true // 是否跟随系统重定向（透明代理时设 true）
}
```

Socks 入站

```json
"settings": {
  "auth": "password",// auth → "noauth" 免认证 / "password" 需要认证
  "accounts": [
    {
      "user": "admin",
      "pass": "123456"
    }
  ],
  "udp": true, //udp → 是否支持 UDP
  "ip": "127.0.0.1" //ip → UDP 回传时用的 IP
}
```

HTTP 入站

```json
"settings": {
  "accounts": [
    {
      "user": "admin",
      "pass": "123456"
    }
  ],
  "allowTransparent": false
}
```



端口转发和透明代理dokodemo-door 

```json
{
  "inbounds": [
    {
      "port": 12345,//监听本机的端口
      "protocol": "dokodemo-door",
      "settings": {
        "address": "1.2.3.4", // 转发目标地址,followRedirect:false
        "port": 443, // 转发目标端口,followRedirect:false
        "network": "tcp,udp", // 支持的网络类型
        //false:表示端口转发，结合使用address:port 。true：透明代理
        "followRedirect": false 
      }
    }
  ]
}
```



透明代理

```
局域网设备的所有流量
       ↓
   iptables 全部拦截
       ↓
   转给 Xray:12345
       ↓
   Xray 读取原始目标地址
       ↓
  routing 判断去哪
     ↙        ↘
  直连(freedom)   代理(vless/vmess)
  国内流量         国外流量
```

设置 iptables

```
# 排除 Xray 自身流量，防止回环
iptables -t nat -A OUTPUT -m mark --mark 0xff -j RETURN

# 排除内网和保留地址
iptables -t nat -A PREROUTING -d 127.0.0.0/8 -j RETURN
iptables -t nat -A PREROUTING -d 192.168.0.0/16 -j RETURN
iptables -t nat -A PREROUTING -d 10.0.0.0/8 -j RETURN

# 劫持所有 TCP 到 Xray
iptables -t nat -A PREROUTING -p tcp -j REDIRECT --to-ports 12345
```



#### fallbacks 

回落参数详解

```json
"fallbacks": [
    //路径是 /ws 的请求 → 转到 8080
   { 
       "path": "/ws", 
       "dest": 8080 
   },
    // 客户端用 HTTP/2 连接的 → 转到 8443
   { 
       "alpn": "h2", 
       "dest": 8443
   },
   // 回落到 80 端口,xver — 传不传来源 IP,
   //默认后端看到的来源 IP 是 127.0.0.1，看不到真实客户端 IP
   //0 → 不传（默认）
   //1 → PROXY Protocol v1（文本格式）
   //2 → PROXY Protocol v2（二进制格式）
  { "dest": 80, "xver": 1 }
]
```





### streamSettings 

传输层配置

TCP配置

```json
"streamSettings": {
  //传输层协议,"tcp" → 原始 TCP,"ws" → WebSocket,"grpc" → gRPC,"http" → HTTP/2,"quic" → 基于 UDP 的 QUIC
  "network": "tcp", 
  // security — 加密方式,"tls" → 标准 TLS 加密,"reality" → Xray 自研的 REALITY,"none" → 不加密
  "security": "tls",
  // TLS 的具体参数
  "tlsSettings": {
      // TLS 协商时支持哪些应用协议
      "alpn":["h2", "http/1.1"],
      // TLS 证书配置
      "certificates":[{
          "certificateFile":"", //证书文件路径
          "keyFile":"" //私钥文件路径
      }
      ]
  },
  // realitySettings 是 security 设为 "reality" 时的配置项
  "realitySettings": {
      // 当非法连接到来时（比如审查者主动探测），Xray 会把流量转发到这个目标网站
      "dest":"www.apple.com:443",
      //允许的 SNI,客户端连接时 TLS 握手中携带的域名（SNI），必须和 dest 对应
      "serverNames":["www.apple.com"],
      //服务端私钥,通过命令生成xray x25519,
      "privateKey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      // 类似密码的附加验证，服务端和客户端必须一致
      "shortIds": ["abcd1234"],
      // TLS 指纹伪装
      "fingerprint": "chrome"
  },
  //tcpSettings 是 network 设为 "tcp" 时的可选配置，主要用来给 TCP 流量加一层伪装头部，让流量看起来像普通的 HTTP 请求
  "tcpSettings": {},
  // wsSettings 是 network 设为 "ws" 时的配置，让流量通过 WebSocket 传输。最大优势是可以套 CDN（如 Cloudflare），隐藏服务器真实 IP
  "wsSettings": {},
   //grpcSettings 是 network 设为 "grpc" 时的配置 
  "grpcSettings": {},
   // httpSettings 是 network 设为 "http" 时的配置，让流量通过 HTTP/2 传输
  "httpSettings": {}
}
```

WebSocket配置

```json
"streamSettings":{
	"network": "ws", // 传输层是WebSocket
    "security": "tls", // 加密方式
    "tlsSettings":{
        "certificates":[
            {
                "certificateFile":"",//证书文件路径
                "keyFile":""//私钥文件路径
            }
        ]
    },
    "wsSettings":{
        "path":"/trojan-ws", // 路径
        // 选择设置
        "headers":{
            "Host":"your-domain.com" // 对应N2rayN里的伪装域名
        }
    }
    

}
```

grpc

```json
"streamSettings":{
	"network": "grpc", // 传输层是WebSocket
    "security": "tls", // 加密方式
    "tlsSettings":{
        "certificates":[
            {
                "certificateFile":"",//证书文件路径
                "keyFile":""//私钥文件路径
            }
        ]
    },
    "grpcSettings": {
        "serviceName": "mygrpc", // grpc的serviceName
         "multiMode": true, //  false是gun 模式，true是multi 模式
         "authority":"your-domain.com" // grpc的Authority
    }
}
```

http

```json
"streamSettings":{
	"network": "http", // 传输层是h2
    "security": "tls", // 加密方式
    "tlsSettings":{
        "certificates":[
            {
                "certificateFile":"",//证书文件路径
                "keyFile":""//私钥文件路径
            }
        ]
    },
    "httpSettings": {
      "host": ["your-domain.com"], // 域名列表
      "path": "/h2-path", //请求路径，类似 ws 的 path
      "method": "PUT" //HTTP 方法，默认 "PUT"，一般不需要改
    }
}
```

quic

```json
{
  "streamSettings": {
    "network": "quic",
    "security": "tls",
    "tlsSettings": {
        "certificates": [
            {
              "certificateFile": "/path/to/cert.pem",
              "keyFile": "/path/to/key.pem"
            }
          ]
        },
    // 设置quic
    "quicSettings": {
      "security": "none",// 密方式，可选值："none"、"aes-128-gcm"、"chacha20-poly1305"
      "key": "",// 加密密钥，当 security 不为 "none" 时需要填写，客户端服务端必须一致。
      "header": {
        "type": "none" //伪装类型,"none":不伪装,"srtp":伪装成视频通话（如 WebRTC）,"utp":伪装成 BT 下载,"wechat-video":伪装成微信视频通话,"dtls":伪装成 DTLS 1.2,"wireguard":伪装成 WireGuard
      }
    }
  }
}
```

kcp

```json
{
  "streamSettings": {
    "network": "kcp",
    "kcpSettings": {
      "mtu": 1350, // 最大传输单元，一般不需要改
      "tti": 50, // 传输时间间隔（毫秒），越小延迟越低但越耗流量
      "uplinkCapacity": 12, //上行带宽（MB/s），按实际带宽填
      "downlinkCapacity": 100, //下行带宽（MB/s），按实际带宽填
      "congestion": false, // 是否启用拥塞控制
      "readBufferSize": 2, //读取缓冲区（MB）
      "writeBufferSize": 2, //写入缓冲区（MB）
      "seed": "your-password", // 加密混淆密钥，客户端服务端必须一致
      "header": {
        "type": "none" //伪装类型,"none":不伪装,"srtp":伪装成视频通话（如 WebRTC）,"utp":伪装成 BT 下载,"wechat-video":伪装成微信视频通话,"dtls":伪装成 DTLS 1.2,"wireguard":伪装成 WireGuard
      }
    }
  }
}
```

httpupgrade

```json
"streamSettings": {
    "network": "quic",
    "security": "tls",
    "tlsSettings": {
        "certificates": [
            {
              "certificateFile": "/path/to/cert.pem",
              "keyFile": "/path/to/key.pem"
            }
          ]
        },
    "httpupgradeSettings": {
      "path": "/your-path", //请求路径，客户端服务端必须一致
      "host": "your-domain.com" //请求的域名，作用等同于 ws 的 headers.Host
    }
}
```

 XHTTP(SplitHTTP)

```json
"streamSettings": {
    "network": "quic",
    "security": "tls",
    "tlsSettings": {
        "certificates": [
            {
              "certificateFile": "/path/to/cert.pem",
              "keyFile": "/path/to/key.pem"
            }
          ]
        },
    "xhttpSettings": {
      "path": "/your-path", //请求路径，客户端服务端必须一致
      "host": "your-domain.com", //请求域名，同 ws 的 Host
      "mode": "auto" //传输模式，核心字段,"auto"自动选择（默认）,"packet-up"上行用 POST 分包，下行用流式响应,"stream-up"上下行都用流式传输（需 HTTP/2 或 HTTP/3）,"stream-one"单个 POST 请求完成上下行（类似普通 HTTP）
    }
}
```

**全部传输方式对比：**

| 传输方式    | 协议 | 支持 CDN | 支持反代 | 需要 TLS | 特点                     |
| ----------- | ---- | -------- | -------- | -------- | ------------------------ |
| WebSocket   | TCP  | ✅        | ✅        | 可选     | 兼容性最好               |
| HTTPUpgrade | TCP  | ✅        | ✅        | 可选     | 轻量版 WS                |
| gRPC        | TCP  | ✅        | ✅        | 可选     | 多路复用                 |
| XHTTP       | TCP  | ✅        | ✅        | 可选     | 伪装性最强，CDN 兼容最广 |
| HTTP/2      | TCP  | ❌        | ✅        | 必须     | 原生多路复用             |
| QUIC        | UDP  | ❌        | ❌        | 必须     | 低延迟                   |
| mKCP        | UDP  | ❌        | ❌        | 不需要   | 抗丢包，费流量           |

### sniffing

 流量嗅探

```json
"sniffing": {
  // true开启嗅探,false 关闭嗅探
  "enabled": true, 
    
  //指定“允许嗅探并识别的协议类型”
  //"http":解析 HTTP 请求头 → Host
  //"tls":解析 TLS ClientHello → SNI
  //"quic":尝试解析 QUIC (UDP) 的域名
  //"fakedns":识别 FakeDNS 记录并还原域名
  "destOverride": ["http", "tls", "quic", "fakedns"],
    
  "metadataOnly": false, //仅用元数据嗅探，不读内容
  "routeOnly": true //true:嗅探结果仅用于路由，不覆盖实际目标地址,false:覆盖实际目标地址
}
```

| 字段           | 说明                                   |
| -------------- | -------------------------------------- |
| `enabled`      | 开启嗅探                               |
| `destOverride` | 嗅探哪些协议来覆盖目标地址             |
| `metadataOnly` | 仅用元数据嗅探，不读内容               |
| `routeOnly`    | 嗅探结果仅用于路由，不覆盖实际目标地址 |

allocate — 端口分配策略

```
┌──────────────────────────┐
│        客户端请求         │
│  访问：1.2.3.4:443       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     Xray 接收到连接       │
│  (inbound: socks/tproxy) │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     Sniffing 启动         │
│  读取前几个数据包         │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│   解析协议类型            │
│  ├─ HTTP → Host           │
│  └─ TLS  → SNI            │
└────────────┬─────────────┘
             │
     ┌───────┴────────┐
     │                │
     ▼                ▼
┌──────────────┐  ┌──────────────┐
│  成功拿到域名 │  │   失败（无域名）│
│  google.com   │  │   只有 IP     │
└──────┬───────┘  └──────┬───────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│ 覆盖目标地址  │   │ 使用原始 IP   │
│ google.com    │   │ 1.2.3.4      │
└──────┬───────┘   └──────┬───────┘
       │                  │
       ▼                  ▼
┌──────────────────────────┐
│        路由匹配            │
│  geosite / geoip / rule   │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│        选择出口            │
│  ├─ direct（直连）        │
│  ├─ proxy（代理）         │
│  ├─ block（拦截）         │
│  └─ balancer（负载均衡）  │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│        发起真实连接         │
│   → 目标服务器（最终）     │
└──────────────────────────┘
```





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
  "inboundTag": [],
  "domain": [],
  "ip": [],
  "port": "",
  "sourcePort": "",
  "network": "",
  "source": [],
  "user": [],
 
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



### settings配置

#### Freedom（直连出口）

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

#### blackhole（黑洞，丢弃流量）

```json
{
      "tag": "block", 
      "protocol": "blackhole"
}
```



```json
"settings": {
  "response": {
    "type": "http" // type → "none" 直接断开 / "http" 返回一个 403 响应再断开
  }
}
```



#### SOCKS5 出站（接住宅 IP）

流量通过远端 SOCKS5 代理转发出去

```json
{
  "tag": "residential",
  "protocol": "socks",
  "settings": {
    "servers": [
      {
        "address": "69.3.215.140", // 
        "port": 7777,
        "users": [
          { "user": "xxx", "pass": "xxx" }
        ]
      }
    ]
  }
}
```

Trojan 出口

```json
{
  "tag": "trojan-out",
  "protocol": "trojan",
  "settings": {
    "servers": [
      {
        "address": "ffgy.net", // 对应远端服务器 inbound 里 clients 的密码
        "port": 443,
        "password": "123456",
        "email": "user1",
        "level": 0
      }
    ]
  },
  "streamSettings": {
    "network": "tcp",
    "security": "tls",
    "tlsSettings": {
      "serverName": "ffgy.net" // TLS 握手时的 SNI，必须和远端证书域名一致
    }
  }
}
```

VMess 出口

```json
{
  "tag": "vmess-out",
  "protocol": "vmess",
  "settings": {
    // "下一跳"节点列表
    "vnext": [
      {
        "address": "ffgy.net", 
        "port": 443,
        "users": [
          {
            "id": "a3482e88-686a-4a58-8126-99c9df64b7bf", //对应远端 inbound 的 id
            "alterId": 0, //填 0，启用 AEAD 加密
             //VMess 自身的加密方式,"auto" → 自动选择（推荐）,
             //"aes-128-gcm" → AES 加密,
             //"chacha20-poly1305" → ChaCha20 加密
             //"none" → 不加密（外层有 TLS 时可以用，减少性能开销）
             // "zero" → 完全不加密不校验（不推荐）
            "security": "auto",
            "level": 0
          }
        ]
      }
    ]
  },
  "streamSettings": {
    "network": "ws",
    "security": "tls",
    "wsSettings": {
      "path": "/mypath",
      "headers": {
        "Host": "ffgy.net"
      }
    }
  }
}
```

VLESS 出口

```json
{
  "tag": "vless-out",
  "protocol": "vless",
  "settings": {
    "vnext": [
      {
        "address": "ffgy.net",
        "port": 443,
        "users": [
          {
            "id": "a3482e88-686a-4a58-8126-99c9df64b7bf",
            "encryption": "none",//encryption → 固定填 "none"，VLESS 不做自身加密
            "flow": "xtls-rprx-vision", //flow → 流控模式，配合 REALITY 时填 "xtls-rprx-vision"
            "level": 0
          }
        ]
      }
    ]
  },
  "streamSettings": {
    "network": "tcp",
    "security": "reality",
    "realitySettings": {
      "serverName": "www.apple.com",
      "publicKey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", //publicKey → 对应服务端 privateKey 生成的公钥
      "shortId": "abcd1234", //shortId → 对应服务端 shortIds 中的一个
      "fingerprint": "chrome" //TLS 指纹伪装，和服务端一致
    }
  }
}
```

Shadowsocks 出口

```json
{
  "tag": "ss-out",
  "protocol": "shadowsocks", 
  "settings": {
    "servers": [
      {
        "address": "ffgy.net",
        "port": 8388,
        "method": "2022-blake3-aes-128-gcm", // 加密方式，和服务端一致
        "password": "base64encodedkey==", // 密钥，2022 系列加密需要 base64 编码的密钥
        "level": 0
      }
    ]
  }
}
```



# 完整的trojan协议配置

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

# 完整的shadowsocks配置

服务器配置

```json
{
  "log": {
    "loglevel": "warning",
    "access": "/var/log/xray/access.log",
    "error": "/var/log/xray/error.log"
  },
  "inbounds": [
    {
      "tag": "ss-in",
      "port": 8388,
      "listen": "0.0.0.0",
      "protocol": "shadowsocks",
      "settings": {
        "method": "2022-blake3-aes-128-gcm",
        "password": "aaaaaaaaaaaaaaaabbbbbbbbbbbbbbbb",
        "network": "tcp,udp"
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic"]
      }
    }
  ],
  "outbounds": [
    {
      "tag": "direct",
      "protocol": "freedom"
    },
    {
      "tag": "block",
      "protocol": "blackhole"
    }
  ],
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [
      {
        "type": "field",
        "outboundTag": "block",
        "protocol": ["bittorrent"]
      },
      {
        "type": "field",
        "outboundTag": "block",
        "ip": ["geoip:private"]
      }
    ]
  }
}
```

客户端

```json
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "tag": "socks-in",
      "port": 1080,
      "listen": "127.0.0.1",
      "protocol": "socks",
      "settings": {
        "udp": true
      }
    },
    {
      "tag": "http-in",
      "port": 1081,
      "listen": "127.0.0.1",
      "protocol": "http"
    }
  ],
  "outbounds": [
    {
      "tag": "proxy",
      "protocol": "shadowsocks",
      "settings": {
        "servers": [
          {
            "address": "your-server-ip",
            "port": 8388,
            "method": "2022-blake3-aes-128-gcm",
            "password": "aaaaaaaaaaaaaaaabbbbbbbbbbbbbbbb"
          }
        ]
      }
    },
    {
      "tag": "direct",
      "protocol": "freedom"
    },
    {
      "tag": "block",
      "protocol": "blackhole"
    }
  ],
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [
      {
        "type": "field",
        "outboundTag": "direct",
        "domain": ["geosite:cn"]
      },
      {
        "type": "field",
        "outboundTag": "direct",
        "ip": ["geoip:cn", "geoip:private"]
      }
    ]
  }
}
```

# VMess 协议配置

服务器端

```json
{
  "log": {
    "loglevel": "warning",
    "access": "/var/log/xray/access.log",
    "error": "/var/log/xray/error.log"
  },
  "inbounds": [
    {
      "tag": "vmess-in",
      "port": 443,
      "listen": "0.0.0.0",
      "protocol": "vmess",
      "settings": {
        "clients": [
          {
            "id": "a3482e88-686a-4a58-8126-99c9df64b7bf",
            "alterId": 0,
            "email": "user1@example.com"
          }
        ]
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls",
        "tlsSettings": {
          "certificates": [
            {
              "certificateFile": "/etc/xray/cert.pem",
              "keyFile": "/etc/xray/key.pem"
            }
          ],
          "alpn": ["h2", "http/1.1"]
        },
        "wsSettings": {
          "path": "/vmess-ws",
          "headers": {
            "Host": "your-domain.com"
          }
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic"]
      }
    }
  ],
  "outbounds": [
    {
      "tag": "direct",
      "protocol": "freedom"
    },
    {
      "tag": "block",
      "protocol": "blackhole"
    }
  ],
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [
      {
        "type": "field",
        "outboundTag": "block",
        "protocol": ["bittorrent"]
      },
      {
        "type": "field",
        "outboundTag": "block",
        "ip": ["geoip:private"]
      }
    ]
  }
}
```

客户端

```json
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "tag": "socks-in",
      "port": 1080,
      "listen": "127.0.0.1",
      "protocol": "socks",
      "settings": {
        "udp": true
      }
    },
    {
      "tag": "http-in",
      "port": 1081,
      "listen": "127.0.0.1",
      "protocol": "http"
    }
  ],
  "outbounds": [
    {
      "tag": "proxy",
      "protocol": "vmess",
      "settings": {
        "vnext": [
          {
            "address": "your-domain.com",
            "port": 443,
            "users": [
              {
                "id": "a3482e88-686a-4a58-8126-99c9df64b7bf",
                "alterId": 0,
                "security": "auto"
              }
            ]
          }
        ]
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls",
        "tlsSettings": {
          "serverName": "your-domain.com",
          "allowInsecure": false,
          "alpn": ["h2", "http/1.1"],
          "fingerprint": "chrome"
        },
        "wsSettings": {
          "path": "/vmess-ws",
          "headers": {
            "Host": "your-domain.com"
          }
        }
      }
    },
    {
      "tag": "direct",
      "protocol": "freedom"
    },
    {
      "tag": "block",
      "protocol": "blackhole"
    }
  ],
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [
      {
        "type": "field",
        "outboundTag": "direct",
        "domain": ["geosite:cn"]
      },
      {
        "type": "field",
        "outboundTag": "direct",
        "ip": ["geoip:cn", "geoip:private"]
      }
    ]
  }
}
```

# VLESS协议（VLESS + Reality）

服务器

```json
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "tag": "vless-reality-in",
      "port": 443,
      "listen": "0.0.0.0",
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "a3482e88-686a-4a58-8126-99c9df64b7bf",
            "flow": "xtls-rprx-vision",
            "email": "user1@example.com"
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "www.microsoft.com:443",
          "xver": 0,
          "serverNames": [
            "www.microsoft.com",
            "microsoft.com"
          ],
          "privateKey": "YOUR_PRIVATE_KEY",
          "shortIds": [
            "",
            "0123456789abcdef"
          ]
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic"]
      }
    }
  ],
  "outbounds": [
    {
      "tag": "direct",
      "protocol": "freedom"
    },
    {
      "tag": "block",
      "protocol": "blackhole"
    }
  ],
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [
      {
        "type": "field",
        "outboundTag": "block",
        "protocol": ["bittorrent"]
      },
      {
        "type": "field",
        "outboundTag": "block",
        "ip": ["geoip:private"]
      }
    ]
  }
}
```

客户端

```json
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "tag": "socks-in",
      "port": 1080,
      "listen": "127.0.0.1",
      "protocol": "socks",
      "settings": {
        "udp": true
      }
    },
    {
      "tag": "http-in",
      "port": 1081,
      "listen": "127.0.0.1",
      "protocol": "http"
    }
  ],
  "outbounds": [
    {
      "tag": "proxy",
      "protocol": "vless",
      "settings": {
        "vnext": [
          {
            "address": "your-server-ip",
            "port": 443,
            "users": [
              {
                "id": "a3482e88-686a-4a58-8126-99c9df64b7bf",
                "flow": "xtls-rprx-vision",
                "encryption": "none"
              }
            ]
          }
        ]
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "serverName": "www.microsoft.com",
          "publicKey": "YOUR_PUBLIC_KEY",
          "shortId": "0123456789abcdef",
          "fingerprint": "chrome"
        }
      }
    },
    {
      "tag": "direct",
      "protocol": "freedom"
    },
    {
      "tag": "block",
      "protocol": "blackhole"
    }
  ],
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [
      {
        "type": "field",
        "outboundTag": "direct",
        "domain": ["geosite:cn"]
      },
      {
        "type": "field",
        "outboundTag": "direct",
        "ip": ["geoip:cn", "geoip:private"]
      }
    ]
  }
}
```



VLESS + WebSocket + TLS

服务器

```json
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "tag": "vless-ws-in",
      "port": 443,
      "listen": "0.0.0.0",
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "a3482e88-686a-4a58-8126-99c9df64b7bf",
            "email": "user1@example.com"
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls",
        "tlsSettings": {
          "certificates": [
            {
              "certificateFile": "/etc/xray/cert.pem",
              "keyFile": "/etc/xray/key.pem"
            }
          ],
          "alpn": ["h2", "http/1.1"]
        },
        "wsSettings": {
          "path": "/vless-ws",
          "headers": {
            "Host": "your-domain.com"
          }
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic"]
      }
    }
  ],
  "outbounds": [
    {
      "tag": "direct",
      "protocol": "freedom"
    },
    {
      "tag": "block",
      "protocol": "blackhole"
    }
  ],
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [
      {
        "type": "field",
        "outboundTag": "block",
        "protocol": ["bittorrent"]
      },
      {
        "type": "field",
        "outboundTag": "block",
        "ip": ["geoip:private"]
      }
    ]
  }
}
```



客户端

```
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "tag": "socks-in",
      "port": 1080,
      "listen": "127.0.0.1",
      "protocol": "socks",
      "settings": {
        "udp": true
      }
    },
    {
      "tag": "http-in",
      "port": 1081,
      "listen": "127.0.0.1",
      "protocol": "http"
    }
  ],
  "outbounds": [
    {
      "tag": "proxy",
      "protocol": "vless",
      "settings": {
        "vnext": [
          {
            "address": "your-domain.com",
            "port": 443,
            "users": [
              {
                "id": "a3482e88-686a-4a58-8126-99c9df64b7bf",
                "encryption": "none"
              }
            ]
          }
        ]
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls",
        "tlsSettings": {
          "serverName": "your-domain.com",
          "allowInsecure": false,
          "fingerprint": "chrome",
          "alpn": ["h2", "http/1.1"]
        },
        "wsSettings": {
          "path": "/vless-ws",
          "headers": {
            "Host": "your-domain.com"
          }
        }
      }
    },
    {
      "tag": "direct",
      "protocol": "freedom"
    },
    {
      "tag": "block",
      "protocol": "blackhole"
    }
  ],
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [
      {
        "type": "field",
        "outboundTag": "direct",
        "domain": ["geosite:cn"]
      },
      {
        "type": "field",
        "outboundTag": "direct",
        "ip": ["geoip:cn", "geoip:private"]
      }
    ]
  }
}
```





客户端----->trojan------>socks5----->目标地址

```json
{
  "log": {
    "loglevel": "warning"
  },
  "dns":{
	"servers":[
    "8.8.8.8",
    "1.1.1.1"
  ]
  },
  
  "inbounds": [
    {
      "tag": "trojan-in",
      "port": 443,
      "protocol": "trojan",
      "settings": {
        "clients": [
          {
            "password": "12345678910",
            "email": "user1"
          }
        ],
        //  流量回落,当不是protocol指定的流量时，流量将进入这里
        "fallbacks": [
          {
            "dest": 80
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
              "certificateFile": "/usr/local/etc/xray/ssl/us.ffgy.top_bundle.crt",
              "keyFile": "/usr/local/etc/xray/ssl/us.ffgy.top.key"
            }
          ]
        }
      },
      // 嗅探
      "sniffing": {  
        "enabled": true, // 流量嗅探
        "destOverride": ["http", "tls"], //用嗅探到的域名替换原始目标地址
		"routeOnly": true //嗅探的域名只用于路由,不会替换真实连接地址
      }
    }
  ],
  "outbounds": [
	{
		"tag":"direct",
		"protocol":"freedom", // 直连
		"settings":{
			"domainStrategy": "AsIs"
		}
	},
    {
      "tag": "block", // 屏蔽
      "protocol": "blackhole"
    },
	{
      "tag": "ai-proxy-outbounds",
      "protocol": "socks", // 代理到住宅IP
      "settings":{
		"servers":[
		 {
			"address":"住宅ip",
            "port": 443,
            "users":[
			  { "user": "用户名", "pass": "密码" }
			]			
		 }
		]  
	  }
    }
  ],
  "routing": {
    "rules": [
      {
        "type": "field",
        "outboundTag": "block",
        "domain": ["geosite:category-ads-all"]
      },
	  {
		"type":"field",
		"outboundTag":"ai-proxy-outbounds",
		"domain":[
		  "domain:chatgpt.com",
          "domain:claude.ai"
		]
	  }
    ]
  }
}

```



CDN路径:   客户端 → CDN → Nginx(/ray 代理到) → trojan-in_ws → 无匹配规则 → freedom(直连) 

直连路径:  客户端 → trojan-in(442) → socks-out(付费SOCKS5) → 目标网站



客户端 → CDN → Nginx → trojan-in_ws → 无匹配规则 → freedom(直连) 的配置

1、在cloudflare注册域名或将域名托管的cloudflare

2、在cloudflare添加DNS解析，并打开CDN

3、在cloudflare申请ssh/tls,选择"源服务器"

4、将申请到的证书配置的nginx，配置反向代理

```

worker_processes  1;
events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;

  
    server {
		# 端口
        listen       80;
		
		# 域名
        server_name  ffgy.xx;
		
		# 当访问80端口时重定向到443端口
	    return 301 https://$host$request_uri; 
    }

    server {
		# 端口
        listen 443 ssl http2;
		
		# 域名
		server_name ffgy.xx;
		
		# cloudflare 申请的证书
		ssl_certificate     /etc/ssl/ffgy.xx/ffgy.xx.pem; 
		
		# cloudflare 申请的key
        ssl_certificate_key /etc/ssl/ffgy.xx/ffgy.xx.key; 
		
        ssl_protocols       TLSv1.2 TLSv1.3;
        ssl_ciphers         ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers on; 



	location / {
            root   html;
            index  index.html index.htm;
    	}
    
	# ws的路由时/ray时 反向代理的xray的10000 
    location /ray {
        proxy_redirect off;
        proxy_pass http://127.0.0.1:10000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    }

}

```





5、xray配置

```json
{
  "log": {
    "loglevel": "warning"
  },
  "dns": {
    "servers": ["8.8.8.8", "1.1.1.1"]
  },
  "inbounds": [
    {
      "tag": "trojan-in_ws",
      "port": 10000, // nginx 流量代理的10000端口
      "listen": "127.0.0.1",
      "protocol": "trojan",
      "settings": {
        "clients": [
          {
            "password": "123456",
            "email": "user1"
          }
        ]
      },
      "streamSettings": {
        "network": "ws", // 
        "wsSettings": {
          "path": "/ray" // 和nginx的一致
        }
      }
    },
    {
      "tag": "trojan-in",
      "port": 442,
      "protocol": "trojan",
      "settings": {
        "clients": [
          {
            "password": "123456",
            "email": "user1"
          }
        ],
        "fallbacks": [
          {
            "dest": 443
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
              "certificateFile": "/usr/local/etc/xray/ssl/ffgy.xx.crt", // 这里的证书不是从cloudflare申请的
              "keyFile": "/usr/local/etc/xray/ssl/ffgy.xx.key" // 这里的证书不是从cloudflare申请的
            }
          ]
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls"],
        "routeOnly": true
      }
    }
  ],
  "outbounds": [
    {
      "protocol": "freedom",
      "tag": "direct",
      "settings": {
        "domainStrategy": "AsIs"
      }
    },
    {
      "tag": "socks-out",
      "protocol": "socks",
      "settings": {
        "servers": [
          {
            "address": "69.13.215.144",
            "port": 443,
            "users": [
              { "user": "admin", "pass": "123456789" }
            ]
          }
        ]
      }
    },
    {
      "tag": "block",
      "protocol": "blackhole"
    }
  ],
  "routing": {
    "rules": [
      {
        "type": "field",
        "outboundTag": "socks-out",
        "inboundTag": ["trojan-in"]
      },
      {
        "type": "field",
        "outboundTag": "block",
        "domain": ["geosite:category-ads-all"]
      }
    ]
  }
}
```



clash配置

```yaml
  - name: "colocrossing-CDN"
    type: trojan
    server: ffgy.xx
    port: 443
    password: "123456"
    sni: ffgy.xx
    skip-cert-verify: false
    network: ws
    ws-opts:
      path: /ray
      headers:
        Host: ffgy.xx
    
  - name: colocrossing # https://cloud.colocrossing.com/
    type: trojan
    server: ffgy.xx
    port: 442
    password: "123456"
    udp: true
    sni: ffgy.xx
    skip-cert-verify: false # 对应你的 allowInsecure=1
    network: tcp
```



https://xtls.github.io/document/level-1/fallbacks-lv1.html

开启BBR

适用于内核 4.9+

```
echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
sysctl -p
```



转发流量

```json
{
  "log": {
    "access": "/var/log/xray/access.log",
    "error": "/var/log/xray/error.log",
    "loglevel": "debug"
  },
  "inbounds": [
    {
      "tag": "in",
      "port": 443,
      "protocol": "dokodemo-door",
      "settings": {
        "network": "tcp"
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["tls", "http"]
      }
    }
  ],
  "outbounds": [
    {
      "tag": "direct",
      "protocol": "freedom"
    },
    {
      "tag": "block",
      "protocol": "blackhole"
    }
  ],
  "routing": {
    "rules": [
      {
        "type": "field",
        "ip": ["127.0.0.1"], //防止本机换回
        "outboundTag": "block"
      }
    ]
  }
}
```

