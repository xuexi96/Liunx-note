# OpenClash / Mihomo 配置逐项中文说明

```yaml
# HTTP 代理端口，客户端可使用路由器 IP:7890 连接 HTTP 代理
port: 7890

# SOCKS5 代理端口，客户端可使用路由器 IP:7891 连接 SOCKS 代理
socks-port: 7891

# 混合代理端口，同时接受 HTTP 和 SOCKS 协议连接
mixed-port: 7893

# 透明代理 REDIR 入站端口：通常配合防火墙重定向 TCP 流量
redir-port: 7892

# 透明代理 TPROXY 入站端口：通常配合策略路由与防火墙处理 TCP/UDP 流量
# 单独设置端口并不会自动建立透明代理规则
tproxy-port: 7895

# 允许局域网其他设备连接 Mihomo 代理入站端口
allow-lan: true

# 监听所有可用 IP 地址；需配合防火墙限制访问来源
bind-address: "*"

# 工作模式：rule=根据 rules 规则分流；global=全局代理；direct=直连
mode: rule

# 日志级别：warning 表示主要记录警告及错误（不含常规 info/debug）
log-level: warning

# 关闭 Mihomo 内核的 IPv6 处理（不等于关闭路由器系统的 IPv6）
ipv6: false

# 外部 REST API 控制端口，0.0.0.0 表示监听所有网卡
# 建议改为 127.0.0.1:9090，或使用防火墙严格限制来源
external-controller: 0.0.0.0:9090

# 外部控制 API 的访问密钥：请自行设置高强度随机值，不要公开
secret: "BHGZJGeP11"

# Dashboard 静态文件所在的目录
external-ui: /usr/share/openclash/ui

# 外部面板名称；与所用 Mihomo/OpenClash 版本及面板管理方式有关
external-ui-name: metacubexd

# 尽量统一节点延迟测试的计算方式，以便比较
unified-delay: true

# 允许并发尝试 TCP 连接，以提升某些情况下的连接效率
tcp-concurrent: true

# 重启后需要持久保存的运行状态
profile:
  # 保存手动选择的代理节点/策略组选择
  store-selected: true
  # 持久化 Fake-IP 映射，减少重启带来的映射变更
  store-fake-ip: true

# DNS 相关设置
dns:
  # 开启 Mihomo 内置 DNS 服务
  enable: true
  # 监听所有网络接口的 7874 端口；需限制非可信客户端访问
  listen: 0.0.0.0:7874
  # 内置 DNS 不返回 IPv6 AAAA 查询结果（具体行为依内核版本而定）
  ipv6: false
  # Fake-IP 模式：对符合条件的域名返回一个虚拟 IP，再利用映射处理连接
  enhanced-mode: fake-ip
  # Fake-IP 虚拟 IP 地址池（不是局域网真实设备地址）
  fake-ip-range: 198.18.0.1/16
  # blacklist 模式：只有命中 fake-ip-filter 的域名不使用 Fake-IP
  fake-ip-filter-mode: blacklist
  # 用于解析 DNS 上游服务器自身的域名等基础解析场景
  default-nameserver:
    - 223.5.5.5        # 阿里公共 DNS
    - 119.29.29.29    # DNSPod 公共 DNS
  # 常规域名查询使用的上游 DNS（以下均是 DNS-over-HTTPS）
  nameserver:
    - https://doh.pub/dns-query
    - https://dns.alidns.com/dns-query
  # Fake-IP 排除列表：匹配的域名使用真实 DNS 解析结果，而不是虚拟 IP
  fake-ip-filter:
    - rule-set:fakeipfilter_domain  # 常见 Fake-IP 不兼容域名
    - rule-set:cn_domain           # 国内域名
    - rule-set:private_domain      # 私有/局域网域名

# 可用的单个代理出站
proxies:
  - name: 直连         # 自定义的直连出站名称
    type: direct        # 不经过远端代理，直接连接目的地址

  - name: yinnet       # 代理节点名称，可用于代理组引用
    type: vless         # 使用 VLESS 协议
    server: 192.168.2.1  # 代理服务器地址
    port: 442           # 代理服务端口
    uuid: "<你的 VLESS UUID>" # VLESS 用户 ID，属于连接凭据
    network: ws         # 使用 WebSocket 传输
    tls: true           # 启用 TLS 加密
    udp: false          # 该代理配置不启用 UDP 转发
    servername: ffgy.top       # TLS SNI 名称，服务端证书需与之匹配
    client-fingerprint: chrome # 模拟 Chrome TLS ClientHello 指纹（需内核支持）
    ws-opts:
      path: "/ray"     # WebSocket 请求路径，必须与服务端一致
      headers:
        Host: ffgy.top  # WebSocket 握手的 HTTP Host 头

# 代理策略组
proxy-groups:
  - name: "🚀 默认代理" # 规则可以引用的组名
    type: select        # 手动选择其中一个出站
    proxies:
      - yinnet          # 可选：使用远端 VLESS 节点
      - 直连            # 可选：直接连接，不走远端节点

# 分流规则：从上到下匹配，命中后停止继续匹配
rules:
  - RULE-SET,private_ip,直连,no-resolve # 私有 IP 目标直连，不为此 IP 规则强制触发解析
  - RULE-SET,private_domain,直连        # 私有/局域网域名直连
  - RULE-SET,cn_domain,直连             # 命中国内域名规则集则直连
  - RULE-SET,cn_ip,直连                 # 命中国内 IP 规则集则直连
  - MATCH,🚀 默认代理                   # 其他所有未匹配流量交给默认代理组

# 远程规则集定义：使用 HTTP 下载 .mrs 规则文件，并定期更新
rule-providers:
  fakeipfilter_domain:
    type: http         # 通过 HTTP(S) 拉取远程文件
    interval: 86400    # 每 86400 秒（24 小时）刷新一次
    behavior: domain   # 域名类型规则
    format: mrs        # Mihomo MRS 二进制规则格式
    url: https://raw.githubusercontent.com/wwqgtxx/clash-rules/release/fakeip-filter.mrs
    path: "./rule_provider/fakeipfilter_domain" # 本地规则缓存路径

  private_domain:
    type: http
    interval: 86400
    behavior: domain
    format: mrs
    url: https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/private.mrs
    path: "./rule_provider/private_domain"

  private_ip:
    type: http
    interval: 86400
    behavior: ipcidr   # IP 地址段/CIDR 类型规则
    format: mrs
    url: https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geoip/private.mrs
    path: "./rule_provider/private_ip"

  cn_domain:
    type: http
    interval: 86400
    behavior: domain
    format: mrs
    url: https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/cn.mrs
    path: "./rule_provider/cn_domain"

  cn_ip:
    type: http
    interval: 86400
    behavior: ipcidr
    format: mrs
    url: https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geoip/cn.mrs
    path: "./rule_provider/cn_ip"
```

## 2. 不同端口的用途

| 端口 | 协议/服务 | 常见用途 |
|---|---|---|
| 7890 | HTTP | 客户端手动设置 HTTP 代理 |
| 7891 | SOCKS5 | 客户端手动设置 SOCKS 代理 |
| 7893 | HTTP + SOCKS | 统一混合代理入口 |
| 7892 | REDIR | 由路由器防火墙转发 TCP 流量的透明代理入口 |
| 7895 | TPROXY | 配合防火墙和策略路由接管 TCP/UDP 流量 |
| 7874 | DNS | Mihomo 内置 DNS 服务 |
| 9090 | REST API | 控制面板与程序控制 Mihomo 的接口 |

端口配置只是在内核中提供入口；要让 R2S 后面的设备透明代理，通常还需要 OpenClash 对应的防火墙规则、DNS 劫持/转发设置，单独填端口并不能自动接管全网流量。

## 3. 分流执行顺序

```text
客户端请求
  ↓
是否为私有 IP？ ──是──→ 直连
  ↓ 否
是否为私有/局域网域名？ ──是──→ 直连
  ↓ 否
是否命中国内域名列表？ ──是──→ 直连
  ↓ 否
是否命中国内 IP 列表？ ──是──→ 直连
  ↓ 否
MATCH → 🚀 默认代理（从 yinnet 与直连中选定一个）
```

**重要：** `🚀 默认代理` 的 `type: select` 只表示允许手动选择，不会自动找最快节点。选择 `直连` 后，`MATCH` 命中的流量也将直连。

## 4. rule-providers 规则集字段解释

| 字段 | 作用 |
|---|---|
| `type: http` | 从 URL 下载规则文件 |
| `interval: 86400` | 每隔一天检查更新 |
| `behavior: domain` | 按域名匹配的规则集 |
| `behavior: ipcidr` | 按目标 IP 网段匹配的规则集 |
| `format: mrs` | Mihomo 的 MRS 规则格式 |
| `url` | 下载规则文件的远程地址 |
| `path` | 本地缓存文件路径（相对路径由内核工作目录决定） |
| `RULE-SET,名称,策略` | 在 rules 中引用这个规则集并指定走哪个出站 |
| `no-resolve` | 该 IP 规则匹配时，不额外为匹配而触发 DNS 解析 |


