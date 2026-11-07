# Docker文件挂载
Docker容器的文件挂载方式有两种，一种是直接挂载的宿主机上，一种是通过Docker volume

# 直接挂载宿主机的目录
```bash
docker run -d \
   -v /home/user1:/root/user1 \
   ubuntu:24.04

```
home/user1是宿主机的目录，注意宿主机的目录必须存在
/root/user1是容器的目录，如果容器/root/user1下面有文件，宿主机没有，容器中的文件将被隐藏

# 通过容器的数据卷挂载
创建数据卷的命令
```bash
docker volume create [OPTIONS] [VOLUME]

```
普通 Docker 常用参数
|参数	|默认值	| 作用|
| --- | --- | --- |
|-d, --driver|	local|	指定数据卷驱动|
|-o, --opt	|无	|设置驱动特定参数，可重复使用|
|--label	|无	|为数据卷添加元数据标签|

--opt参数说明
|选项|	作用|	示例|
| --- | --- | ---|
|type	|指定挂载文件|系统类型|	type=nfs|
|device	|指定挂载来源	device=/mnt/data|
|o	|指定 Linux mount 挂载选项|	o=bind|

使用宿主机指定目录
```bash
sudo mkdir -p /mnt/mydata

docker volume create \
  --driver local \
  --opt type=none \
  --opt device=/mnt/mydata \
  --opt o=bind \
  mydata

```
实际数据存储在 /mnt/mydata，但 docker volume inspect 中的 Mountpoint 仍通常是 Docker 管理的卷路径

使用 NFS 网络存储
```bash
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.2.100,rw \
  --opt device=:/data \
  nfsdata
```

使用 tmpfs 内存存储
```bash
docker volume create \
  --driver local \
  --opt type=tmpfs \
  --opt device=tmpfs \
  --opt o=size=100m,uid=1000 \
  tmpdata
```


## 创建数据卷
创建普通命名卷
```bash
 docker volume create mydata
```
挂载到容器
```bash
docker run -d \
    -v mydata:/root/user1
    ubuntu:24.04
```

Docker 数据卷的其他命令

查看卷
```bash
docker volume ls
```

查看卷详细配置
```bash
docker volume inspect mydata
```