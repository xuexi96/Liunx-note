# 检查openclash 是否安装
```bash
ls /etc/init.d/openclash
```
# 检查内核是否已经存在
```bash
ls -lh /etc/openclash/core/
```
内核不存在需要安装,下载：https://github.com/MetaCubeX/mihomo



# 设置订阅
备份 OpenClash 设置
```bash
cp /etc/config/openclash /etc/config/openclash.bak
```

设置订阅文件 Mihomo 配置
```bash
uci set openclash.config.config_path='/etc/openclash/config/myproxy.yaml'
```

启用插件
```bash
uci set openclash.config.enable='1'
```

使用规则模式
```bash
uci set openclash.config.proxy_mode='rule'
```

保存
```bash
uci commit openclash
```

启动 OpenClash
/etc/init.d/openclash enable
/etc/init.d/openclash restart

# 测试代理是否正常
```bash
curl -I --connect-timeout 10 https://www.baidu.com
```

```bash
curl -I \
  -x http://127.0.0.1:7893 \
  --connect-timeout 10 \
  --max-time 20 \
  https://www.google.com

```

## openclash的主要目录
/etc/config/openclash	OpenClash 的 UCI 设置
/etc/openclash/config/	订阅生成的 YAML 配置
/etc/openclash/core/	代理内核
/etc/openclash/custom/	自定义分流规则
/etc/init.d/openclash	OpenClash 服务控制



# 常用命令
功能	命令
启动	/etc/init.d/openclash start
停止	/etc/init.d/openclash stop
重启	/etc/init.d/openclash restart
开机启动	/etc/init.d/openclash enable
禁止开机启动	/etc/init.d/openclash disable
查看配置	uci show openclash
更新订阅	/usr/share/openclash/openclash.sh
查看进程	ps w \| grep '[m]ihomo'