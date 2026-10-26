# 部署本地镜像仓库

在宿主机上创建用户存储镜像的目录
```bash
sudo mkdir -p /opt/docker-registry/data
```

启动 Registry 容器(宿主机ip:92.168.2.204)

```bash
docker run -d \
  --name registry \
  --restart unless-stopped \
  -p 5000:5000 \
  -e REGISTRY_STORAGE_DELETE_ENABLED=true \ # 允许删除镜像
  -v /opt/docker-registry/data:/var/lib/registry \
  registry:3
```

其他主机上面要访问这样镜像仓库需要修改
```bash
vim /etc/docker/daemon.json
```
添加
```json
{
  "insecure-registries": [
    "192.168.2.204:5000"
  ]
}
```

上传镜像到镜像仓库

给本地已有的 Docker 镜像添加一个新的名称（Tag）
```bash
docker tag agent-base:1.0 \
  192.168.2.204:5000/agent-base:1.0
```
命令结构
docker tag	给镜像添加一个新标签
agent-base:1.0	本地已有的镜像
192.168.2.204	局域网 Registry 服务器地址
5000	Registry 服务端口
/agent-base	Registry 中的镜像仓库名称
:1.0	镜像版本标签

上传镜像
```bash
docker push 192.168.2.204:5000/agent-base:1.0
```

查看所以镜像
```
http://192.168.2.204:5000/v2/_catalog
```
查看指定镜像的所有版本
```
curl http://192.168.2.204:5000/v2/ubuntu/tags/list
# ubuntu是镜像名，需要看其他镜像，修改这个
```