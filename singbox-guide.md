**sing-box**

安装、配置与使用完整指南

适配版本：sing-box v1.12+

官方文档：https://sing-box.sagernet.org/configuration/

**一、安装**

**1.1 一键安装脚本**

适用于 Debian / Ubuntu / CentOS / ArchLinux：

> curl -fsSL https://sing-box.app/install.sh \| sh
>
> ⚠️ 安装后服务已注册为 systemd 服务，但默认不启动，需手动启用。

**1.2 仓库安装（支持自动更新）**

**Debian / Ubuntu**

> sudo mkdir -p /etc/apt/keyrings
>
> sudo curl -fsSL https://sing-box.app/gpg.key -o
> /etc/apt/keyrings/sagernet.asc
>
> sudo chmod a+r /etc/apt/keyrings/sagernet.asc
>
> echo \'Types: deb
>
> URIs: https://deb.sagernet.org/
>
> Suites: \*
>
> Components: \*
>
> Enabled: yes
>
> Signed-By: /etc/apt/keyrings/sagernet.asc\' \| sudo tee
> /etc/apt/sources.list.d/sagernet.sources
>
> sudo apt-get update && sudo apt-get install sing-box

**CentOS / Rocky / RHEL**

> sudo dnf config-manager addrepo
> \--from-repofile=https://sing-box.app/sing-box.repo
>
> sudo dnf install sing-box

**1.3 文件路径**

-----------------------------------------------------------------------------------
  **路径**                                **说明**
--------------------------------------- -------------------------------------------
  /etc/sing-box/config.json               主配置文件（核心）

  /usr/bin/sing-box                       可执行文件

  /var/lib/sing-box/                      运行时数据目录（缓存、证书）

  /etc/systemd/system/sing-box.service    单实例 systemd 服务

/etc/systemd/system/sing-box@.service   多实例模板服务

**1.4 服务管理**

> systemctl start sing-box \# 启动
>
> systemctl stop sing-box \# 停止
>
> systemctl restart sing-box \# 重启
>
> systemctl enable sing-box \# 开机自启
>
> systemctl status sing-box \# 查看状态
>
> journalctl -u sing-box -f \# 实时查看日志

检查配置语法（启动前建议先执行）：

> sing-box check -c /etc/sing-box/config.json

**二、配置文件结构**

sing-box 使用单个 JSON 文件作为配置，顶层共 9 个字段：

> {
>
> \"log\": {}, // 日志
>
> \"dns\": {}, // DNS 解析
>
> \"ntp\": {}, // 时间同步
>
> \"inbounds\": \[\], // 入站（接收流量）
>
> \"outbounds\": \[\], // 出站（发送流量）
>
> \"route\": {}, // 路由（决定走哪个出站）
>
> \"endpoints\": \[\], // 端点（WireGuard 等）
>
> \"services\": \[\], // 服务（Tor 等）
>
> \"experimental\":{}, // 实验性功能（Clash API 等）
>
> }

**数据流向**

> 外部流量
>
> │
>
> ▼
>
> inbounds（接收：监听端口，解析协议）
>
> │
>
> ▼
>
> dns（解析：域名 → IP）
>
> │
>
> ▼
>
> route（判断：匹配规则，选择出站）
>
> │
>
> ▼
>
> outbounds（发送：direct / block / 代理）
>
> │
>
> ▼
>
> 目标服务器

**三、各字段配置说明**

**3.1 log --- 日志**

控制日志输出方式和级别。

> 💡 不配置 output 时日志输出到 journalctl，用 journalctl -u sing-box -f
> 查看。 若配置 output 需确保 sing-box 用户对该文件有写权限。

-----------------------------------------------------------------------------------------
  **字段**        **类型**   **默认值**   **说明**
--------------- ---------- ------------ -------------------------------------------------
  disabled        bool       false        是否完全禁用日志

  level           string     warn         级别：trace / debug / info / warn / error / fatal

  output          string     标准输出     日志写入的文件路径，不填则输出到终端/journalctl

timestamp       bool       false        日志行首是否显示时间戳

推荐配置：

> \"log\": {
>
> \"level\": \"info\",
>
> \"timestamp\": true
>
> }

**3.2 dns --- DNS 解析**

> ⚠️ v1.12+ 重大变更： • 旧格式用 \"address\" 字段；新格式改用
> \"type\" + \"server\" 字段 • 不再支持 \"final\" 字段；改用 rules
> 末尾的兜底规则 • dns.servers 不再支持 \"detour\" 字段

**DNS 服务器 type 对照表**

-------------------------------------------------------------------------------
  **旧 address 写法**             **新 type**     **新 server**
------------------------------- --------------- -------------------------------
  \"223.5.5.5\"                   udp             \"223.5.5.5\"

  \"tcp://223.5.5.5\"             tcp             \"223.5.5.5\"

  \"tls://dns.google\"            tls             \"dns.google\"

  \"https://1.1.1.1/dns-query\"   https           \"1.1.1.1\"

  \"fakeip\"                      fakeip          不需要

  \"rcode://success\"             block           不需要

\"local\"                       local           不需要

**dns.servers\[\] 字段**

-----------------------------------------------------------------------
  **字段**           **说明**
------------------ ----------------------------------------------------
  type               协议类型（必填）：udp / tcp / tls / https / fakeip /
                     block / local

  tag                服务器标识，在 rules 中引用

  server             DNS 服务器地址（IP 或域名）

  address_resolver   解析 DoH/DoT 服务器域名时使用的 DNS
                     tag（防鸡生蛋问题）

strategy           返回结果的 IP 版本策略：prefer_ipv4 / ipv4_only 等

**dns.rules\[\] 常用匹配条件**

-----------------------------------------------------------------------
  **字段**           **说明**
------------------ ----------------------------------------------------
  domain             精确匹配域名

  domain_suffix      域名后缀匹配（子域名）

  domain_keyword     域名关键词匹配

  geosite            匹配 geosite 规则集（如 cn / gfw）

  rule_set           匹配外部规则集（.srs 文件）

  outbound           匹配出站流量触发的 DNS（any = 所有）

server             （结果字段）命中时使用的 DNS 服务器 tag

**dns 顶层字段**

------------------------------------------------------------------------
  **字段**            **说明**
------------------- ----------------------------------------------------
  strategy            IP 版本策略：prefer_ipv4 / prefer_ipv6 / ipv4_only /
                      ipv6_only

  disable_cache       禁用 DNS 缓存

  independent_cache   每个服务器使用独立缓存

  reverse_mapping     建立 IP→域名反向映射（TUN 模式用）

fakeip              fake-ip 配置（enabled / inet4_range / inet6_range）

推荐配置（v1.12+ 新格式）：

> \"dns\": {
>
> \"servers\": \[
>
> {
>
> \"type\": \"https\",
>
> \"tag\": \"default\",
>
> \"server\": \"1.1.1.1\"
>
> }
>
> \],
>
> \"rules\": \[
>
> { \"server\": \"default\" } // 兜底：所有请求走 default
>
> \]
>
> }

**3.3 ntp --- 时间同步**

保持系统时钟准确，QUIC 类协议（Hysteria2 / TUIC）时间误差超过 30s
会握手失败。

> ⚠️ v1.12+ 不支持 ntp.detour 字段，请删除。

----------------------------------------------------------------------------
  **字段**          **类型**   **默认值**   **说明**
----------------- ---------- ------------ ----------------------------------
  enabled           bool       false        是否启用 NTP

  server            string     ---          NTP 服务器地址

  server_port       int        123          NTP 端口

  interval          duration   30m          同步间隔

write_to_system   bool       false        是否写入系统时钟（需 root）

推荐配置：

> \"ntp\": {
>
> \"enabled\": true,
>
> \"server\": \"time.cloudflare.com\",
>
> \"interval\": \"30m\"
>
> }

**3.4 inbounds --- 入站**

监听端口，接收客户端流量。服务端的核心配置，每个入站是数组中的一个对象。

**公共字段（所有入站协议通用）**

-----------------------------------------------------------------------------
  **字段**                     **说明**
---------------------------- ------------------------------------------------
  type                         协议类型（必填）：vless / vmess / trojan /
                               shadowsocks / hysteria2 / tuic / tun 等

  tag                          入站标识，在路由规则中引用

  listen                       监听地址，:: = 所有网卡（IPv4+IPv6），0.0.0.0 =
                               仅 IPv4

  listen_port                  监听端口

  tcp_fast_open                启用 TCP Fast Open，降低握手延迟

  sniff                        开启流量嗅探，识别协议/域名，路由分流需要

sniff_override_destination   用嗅探到的域名覆盖目标地址（防 DNS 污染）

**TLS 配置（tls 字段）**

-----------------------------------------------------------------------
  **字段**              **说明**
--------------------- -------------------------------------------------
  enabled               是否启用 TLS

  certificate_path      证书文件路径（已有证书时用此方式）

  key_path              私钥文件路径

  acme.domain           ACME 自动申请证书的域名列表

  acme.email            ACME 注册邮箱

  acme.provider         CA 机构：letsencrypt / zerossl

  reality.enabled       启用 Reality 协议（不需要域名和证书）

  reality.private_key   Reality 服务端私钥（sing-box generate
                        reality-keypair 生成）

reality.short_id      短 ID 列表（openssl rand -hex 8 生成）

> 💡 证书路径参考：
> certbot：/etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem 和
> privkey.pem acme.sh：\~/.acme.sh/YOUR_DOMAIN/fullchain.cer 和
> YOUR_DOMAIN.key

**Transport 配置（transport 字段）**

--------------------------------------------------------------------------
  **type**      **底层**   **适用场景**
------------- ---------- -------------------------------------------------
  ws            TCP        WebSocket，CDN 中转（Cloudflare 等）最佳选择

  httpupgrade   TCP        轻量版 WS，握手更简单

  http          TCP        HTTP/2，高并发场景

  grpc          TCP        穿透企业防火墙能力强

不填          TCP/UDP    裸连，速度最快（Reality / SS 使用）

**各协议特有字段**

-------------------------------------------------------------------------
  **协议**      **重要字段**          **说明**
------------- --------------------- -------------------------------------
  VLESS         users\[\].uuid        用户 UUID

  VLESS         users\[\].flow        Reality 场景填 xtls-rprx-vision，WS
                                      不填

  VMess         users\[\].alterId     填 0 使用 AEAD 加密（推荐）

  Trojan        users\[\].password    用户密码

  Trojan        fallback              非 Trojan 流量回落目标，防主动探测

  Shadowsocks   method                推荐 2022-blake3-aes-256-gcm

  Shadowsocks   password              SS2022 需用 openssl rand -base64 32
                                      生成

  Hysteria2     users\[\].password    认证密码

  Hysteria2     masquerade            HTTP 伪装目标地址（如
                                      https://www.bing.com）

  TUIC          congestion_control    拥塞控制：bbr / cubic / new_reno

  TUN           auto_route            自动添加系统路由，接管全局流量

  TUN           stack                 网络栈：system（性能好）/
                                      gvisor（兼容好）/ mixed
  -------------------------------------------------------------------------

**3.5 outbounds --- 出站**

定义流量从哪里发出。服务端通常只需 direct 和
block，客户端还需要代理节点出站。

**基础出站类型**

-----------------------------------------------------------------------
  **type**        **说明**
--------------- -------------------------------------------------------
  direct          直连，流量直接从本机发出

  block           拦截，流量直接丢弃

  dns             将 DNS 查询送回 DNS 模块处理

  socks           SOCKS5 代理出站，支持 username / password 认证

  vless           VLESS 代理出站（客户端用）

  vmess           VMess 代理出站（客户端用）

  trojan          Trojan 代理出站（客户端用）

  shadowsocks     Shadowsocks 代理出站（客户端用）

  hysteria2       Hysteria2 代理出站（客户端用）
  -----------------------------------------------------------------------

**策略出站（Selector / URLTest）**

-----------------------------------------------------------------------
  **字段**              **说明**
--------------------- -------------------------------------------------
  type: selector        手动选择器，通过 Clash API 面板切换节点

  outbounds             可供选择的出站 tag 列表

  default               默认使用的出站 tag

  type: urltest         自动测速，选延迟最低的节点

  url                   测速 URL，推荐
                        https://www.gstatic.com/generate_204

  interval              测速间隔，如 3m

tolerance             延迟容差（ms），差值在此范围内不切换

**多路复用（multiplex）**

-----------------------------------------------------------------------
  **字段**           **说明**
------------------ ----------------------------------------------------
  enabled            是否启用多路复用

  protocol           协议：smux / yamux / h2mux

  padding            流量填充混淆

brutal.enabled     启用 Brutal 拥塞控制（类 Hysteria）

> ⚠️ VLESS + Reality + Vision flow 场景不建议开启 multiplex。

**3.6 route --- 路由**

决定每条流量走哪个出站，规则从上到下匹配，命中即停止。

**route 顶层字段**

-------------------------------------------------------------------------
  **字段**                **说明**
----------------------- -------------------------------------------------
  rules                   路由规则列表，按顺序匹配，命中即停止

  rule_set                外部规则集定义（.srs 文件），供 rules 引用

  final                   所有规则都不匹配时的默认出站

auto_detect_interface   自动检测出站网卡（Linux 直连时需要）

**route.rules\[\] 匹配条件**

-----------------------------------------------------------------------
  **字段**           **说明**
------------------ ----------------------------------------------------
  protocol           协议嗅探：dns / http / tls / bittorrent 等

  domain             精确匹配域名

  domain_suffix      域名后缀匹配

  domain_keyword     域名关键词匹配

  geosite            匹配 geosite 分类（如 cn / gfw）

  ip_cidr            匹配目标 IP 段

  ip_is_private      是否为私有 IP（局域网）

  geoip              匹配 geoip 国家代码（如 cn）

  port               匹配目标端口

  network            网络类型：tcp / udp

  process_name       匹配进程名（仅客户端，Linux/macOS）

  rule_set           引用已定义的规则集

  invert             取反，匹配不满足条件的流量

outbound           （结果字段）命中时走哪个出站 tag

**route.rule_set\[\] 规则集配置**

-----------------------------------------------------------------------
  **字段**           **说明**
------------------ ----------------------------------------------------
  tag                规则集标识，在 rules 中用 rule_set 字段引用

  type               remote（远程下载）/ local（本地文件）

  format             binary（.srs，性能好）/ source（.json 源文件）

  url                远程规则集下载地址

  download_detour    下载规则集时走哪个出站

update_interval    自动更新间隔，如 1d / 12h

**3.7 experimental --- 实验性功能**

**Clash API**

启用后可用 Yacd / MetaCubeX 等面板管理节点和查看连接状态。

-----------------------------------------------------------------------
  **字段**              **说明**
--------------------- -------------------------------------------------
  external_controller   API 监听地址，如 127.0.0.1:9090

  secret                API 访问鉴权密钥（Bearer Token）

  default_mode          默认模式：rule（规则）/ global（全局代理）/
                        direct（全局直连）

external_ui           面板静态文件目录

**Cache File**

持久化缓存 DNS 结果和选择器状态，重启后不丢失。

-----------------------------------------------------------------------
  **字段**           **说明**
------------------ ----------------------------------------------------
  enabled            是否启用缓存

  path               SQLite 缓存文件路径，如 /var/lib/sing-box/cache.db

store_fakeip       持久化 fake-ip 映射，重启后域名→fake-ip 不变

**四、服务端完整配置示例（v1.12+）**

以下为基于本指南调试验证的可用配置，VLESS + WebSocket + TLS + 上游
SOCKS5。

> {
>
> \"log\": {
>
> \"level\": \"info\",
>
> \"timestamp\": true
>
> // 不配置 output，日志走 journalctl
>
> },
>
> \"dns\": {
>
> \"servers\": \[
>
> {
>
> \"type\": \"https\", // 新格式，不用 address
>
> \"tag\": \"default\",
>
> \"server\": \"1.1.1.1\" // 不配置 detour
>
> }
>
> \],
>
> \"rules\": \[
>
> { \"server\": \"default\" } // 兜底，替代旧的 final 字段
>
> \]
>
> },
>
> \"ntp\": {
>
> \"enabled\": true,
>
> \"server\": \"time.cloudflare.com\",
>
> \"interval\": \"30m\"
>
> // 不配置 detour
>
> },
>
> \"inbounds\": \[
>
> {
>
> \"tag\": \"vless-in\",
>
> \"type\": \"vless\",
>
> \"listen\": \"::\",
>
> \"listen_port\": 443,
>
> \"sniff\": true,
>
> \"users\": \[
>
> {
>
> \"name\": \"user1\",
>
> \"uuid\": \"YOUR_UUID\"
>
> }
>
> \],
>
> \"tls\": {
>
> \"enabled\": true,
>
> \"certificate_path\": \"/path/to/fullchain.pem\",
>
> \"key_path\": \"/path/to/privkey.pem\"
>
> },
>
> \"transport\": {
>
> \"type\": \"ws\",
>
> \"path\": \"/vless-ws\",
>
> \"headers\": {
>
> \"Host\": \"YOUR_DOMAIN\"
>
> }
>
> }
>
> }
>
> \],
>
> \"outbounds\": \[
>
> { \"tag\": \"direct\", \"type\": \"direct\" },
>
> { \"tag\": \"block\", \"type\": \"block\" },
>
> {
>
> \"tag\": \"socks-proxy\",
>
> \"type\": \"socks\",
>
> \"version\": \"5\",
>
> \"server\": \"SOCKS_SERVER_IP\",
>
> \"server_port\": 443,
>
> \"username\": \"SOCKS_USER\",
>
> \"password\": \"SOCKS_PASS\"
>
> }
>
> \],
>
> \"route\": {
>
> \"rules\": \[
>
> { \"protocol\": \"bittorrent\", \"outbound\": \"block\" },
>
> { \"ip_is_private\": true, \"outbound\": \"block\" }
>
> \],
>
> \"final\": \"socks-proxy\"
>
> }
>
> }

**五、常见问题**

---------------------------------------------------------------------------------
  **错误信息**              **原因**           **解决方式**
------------------------- ------------------ ------------------------------------
  legacy DNS servers is     DNS 使用旧格式     改用 type + server 新格式
  deprecated                address 字段       

  unknown field \"final\"   dns.final 在 1.12+ 改用 rules 末尾兜底规则
  (dns)                     已移除             

  detour to an empty direct dns/ntp 配置了     删除 dns/ntp 中的 detour 字段
  outbound                  detour: direct     

  permission denied         进程无写权限       删除 log.output 字段，改用
  (/var/log/sing-box.log)                      journalctl

  unknown field \"final\"   ---                这个是合法字段，检查是否有语法错误
  (route)                                      
  ---------------------------------------------------------------------------------

**六、附录**

**6.1 常用生成命令**

> \# 生成 UUID
>
> sing-box generate uuid
>
> \# 生成 Reality 密钥对（服务端填 private，客户端填 public）
>
> sing-box generate reality-keypair
>
> \# 生成 Reality short_id（8位）
>
> openssl rand -hex 8
>
> \# 生成 SS2022 密码（32字节 base64）
>
> openssl rand -base64 32

**6.2 时间格式参考**

-----------------------------------------------------------------------
  **单位**               **示例**
---------------------- ------------------------------------------------
  毫秒                   300ms

  秒                     30s

  分钟                   5m

  小时                   1h

  天                     1d

组合                   1h30m

**6.3 端口规划建议**

--------------------------------------------------------------------------
  **协议**           **建议端口**   **传输**     **是否需要域名**
------------------ -------------- ------------ ---------------------------
  VLESS + Reality    443            TCP          否

  VLESS + WS + TLS   8443           TCP          是

  VMess + WS + TLS   8444           TCP          是

  Trojan             8445           TCP          是

  Shadowsocks 2022   8388           TCP+UDP      否

  Hysteria2          8446           UDP          是

TUIC v5            8447           UDP          是