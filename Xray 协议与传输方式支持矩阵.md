# Xray 协议与传输方式支持矩阵

## 一、传输方式 (network)

|  传输方式   | VLESS | VMess | Trojan | Shadowsocks | SOCKS | HTTP | Dokodemo-door |
| :---------: | :---: | :---: | :----: | :---------: | :---: | :--: | :-----------: |
|   TCP/RAW   |   ✓   |   ✓   |   ✓    |      ✓      |   ✓   |  ✓   |       ✓       |
|  WebSocket  |   ✓   |   ✓   |   ✓    |      ✗      |   ✗   |  ✗   |       ✗       |
|    gRPC     |   ✓   |   ✓   |   ✓    |      ✗      |   ✗   |  ✗   |       ✗       |
|    XHTTP    |   ✓   |   ✓   |   ✓    |      ✗      |   ✗   |  ✗   |       ✗       |
|    mKCP     |   ✓   |   ✓   |   ✓    |      ✗      |   ✗   |  ✗   |       ✗       |
| HTTPUpgrade |   ✓   |   ✓   |   ✓    |      ✗      |   ✗   |  ✗   |       ✗       |

> **说明：** TCP 传输方式在 v24.9.30 版本后更名为 RAW，两者互为别名。

------

## 二、安全层 (security)

| 安全层  | VLESS | VMess | Trojan | Shadowsocks | SOCKS | HTTP | Dokodemo-door |
| :-----: | :---: | :---: | :----: | :---------: | :---: | :--: | :-----------: |
|   TLS   |   ✓   |   ✓   |   ✓    |      ✓      |   ✗   |  ✗   |       ✗       |
| REALITY |   ✓   |   ✗   |   ✓    |      ✗      |   ✗   |  ✗   |       ✗       |
|  none   |   ✓   |   ✓   |   △    |      ✓      |   ✓   |  ✓   |       ✓       |

> **说明：** Trojan 设为 `none` 技术上可行但失去伪装意义，不推荐。

------

## 三、协议特性

|      特性      | VLESS | VMess | Trojan | Shadowsocks | SOCKS | HTTP | Dokodemo-door |
| :------------: | :---: | :---: | :----: | :---------: | :---: | :--: | :-----------: |
| fallbacks 回落 |   ✓   |   ✗   |   ✓    |      ✗      |   ✗   |  ✗   |       ✗       |
|   flow 流控    |   ✓   |   ✗   |   ✗    |      ✗      |   ✗   |  ✗   |       ✗       |
|  协议自带加密  |   ✗   |   ✓   |   ✗    |      ✓      |   ✗   |  ✗   |       ✗       |
|    UDP 支持    |   ✓   |   ✓   |   ✓    |      ✓      |   ✓   |  ✗   |       ✓       |
|     多用户     |   ✓   |   ✓   |   ✓    |      ✓      |   ✓   |  ✓   |       ✗       |
|     过 CDN     |   △   |   △   |   △    |      ✗      |   ✗   |  ✗   |       ✗       |

> **说明：**
>
> - 过 CDN 需搭配 WebSocket / gRPC / XHTTP 传输方式，TCP 直连无法过 CDN
> - flow (`xtls-rprx-vision`) 仅限 VLESS + TCP + TLS/REALITY 组合
> - fallbacks 要求入站为 TCP + TLS/REALITY，匹配优先级：SNI → ALPN → Path

------

## 四、认证方式

|     协议      |     认证字段      |                             示例                             |
| :-----------: | :---------------: | :----------------------------------------------------------: |
|     VLESS     |       UUID        |                     `"id": "uuid-here"`                      |
|     VMess     |  UUID + alterId   |              `"id": "uuid-here", "alterId": 0`               |
|    Trojan     |     password      |                `"password": "your-password"`                 |
|  Shadowsocks  | password + method | `"password": "base64-key", "method": "2022-blake3-aes-128-gcm"` |
|     SOCKS     |    user / pass    |               `"user": "name", "pass": "pwd"`                |
|     HTTP      |    user / pass    |               `"user": "name", "pass": "pwd"`                |
| Dokodemo-door |        无         |                          不需要认证                          |

------

## 五、settings 核心字段对比

|       字段       | VLESS | VMess | Trojan | Shadowsocks | SOCKS | HTTP |
| :--------------: | :---: | :---: | :----: | :---------: | :---: | :--: |
|     clients      |   ✓   |   ✓   |   ✓    |      ✓      |   ✗   |  ✗   |
|     accounts     |   ✗   |   ✗   |   ✗    |      ✗      |   ✓   |  ✓   |
|    decryption    |   ✓   |   ✗   |   ✗    |      ✗      |   ✗   |  ✗   |
|    fallbacks     |   ✓   |   ✗   |   ✓    |      ✗      |   ✗   |  ✗   |
|     network      |   ✗   |   ✗   |   ✗    |      ✓      |   ✗   |  ✗   |
|       udp        |   ✗   |   ✗   |   ✗    |      ✗      |   ✓   |  ✗   |
|       auth       |   ✗   |   ✗   |   ✗    |      ✗      |   ✓   |  ✗   |
| allowTransparent |   ✗   |   ✗   |   ✗    |      ✗      |   ✗   |  ✓   |

> **说明：**
>
> - `decryption` 是 VLESS 专有字段，必填 `"none"`
> - SOCKS 入站新版已默认兼容 HTTP 代理请求，一个端口可同时处理两种代理
> - Shadowsocks 的 `network` 字段指定支持的网络类型（`"tcp,udp"`）

------

## 六、推荐组合

### 性能最强（首选）



```
VLESS + TCP + REALITY + flow(xtls-rprx-vision)
```

无需域名证书，防探测最好，性能最高。

### 过 CDN（IP 被墙时）



```
VLESS / Trojan + WebSocket / gRPC / XHTTP + TLS
```

搭配 Cloudflare 等 CDN 使用，IP 被墙也能用。

### 兼容性好



```
Trojan + TCP + TLS
```

客户端支持广泛，密码认证直观。

### 传统方案



```
VMess + WebSocket + TLS
```

老牌方案，教程和客户端支持多，但性能和安全性不如 VLESS。

------

## 七、fallbacks 回落字段

仅 VLESS 和 Trojan 支持，要求入站为 TCP + TLS/REALITY。

| 字段 |           说明           |                      示例                       |
| :--: | :----------------------: | :---------------------------------------------: |
| dest |     回落目标（必填）     | `80` / `"127.0.0.1:80"` / `"/dev/shm/h2c.sock"` |
| alpn |     按 TLS ALPN 匹配     |              `"h2"` / `"http/1.1"`              |
| path |   按 HTTP 请求路径匹配   |                   `"/wspath"`                   |
| name |     按 TLS SNI 匹配      |              `"blog.example.com"`               |
| xver | 发送 PROXY protocol 版本 |              `0`(不发) / `1` / `2`              |

**匹配优先级：** `name`（SNI）→ `alpn` → `path`，无条件的作为默认兜底。