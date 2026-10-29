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
curl http://192.168.2.204:5000/v2/_catalog
```
查看指定镜像的所有版本
```
curl http://192.168.2.204:5000/v2/ubuntu/tags/list
# ubuntu是镜像名，需要看其他镜像，修改这个
```

删除镜像
1.获取镜像 Digest
```bash
curl -sSI \
  -H 'Accept: application/vnd.oci.image.manifest.v1+json, application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.v2+json, application/vnd.docker.distribution.manifest.list.v2+json' \
  http://192.168.2.204:5000/v2/ubuntu/manifests/24.04

```
```text
Content-Length: 424
Content-Type: application/vnd.oci.image.manifest.v1+json
Docker-Content-Digest: sha256:a2d43bffc46670d7108bb3c0468c67c5557c4c92e83e1e34cbff1322ad1b94dc
Docker-Distribution-Api-Version: registry/2.0
Etag: "sha256:a2d43bffc46670d7108bb3c0468c67c5557c4c92e83e1e34cbff1322ad1b94dc"
Date: Sun, 25 Oct 2026 11:34:11 GMT

```
找到Docker-Content-Digest
删除镜像
```
curl -i -X DELETE \
  "http://192.168.2.204:5000/v2/ubuntu/manifests/sha256:a2d43bffc46670d7108bb3c0468c67c5557c4c92e83e1e34cbff1322ad1b94dc"
```