# setfacl的使用
setfacl 主要用来管理文件或目录的权限
## 安装
```bash
sudo apt update
sudo apt install acl -y
```

## setfacl 基本语法
```bash
setfacl [选项] [ACL规则] 文件或目录
```
常用选项
| 参数 | 作用 |
| --- | ---|
|-m	|添加或修改 ACL|
|-x	|删除指定 ACL|
|-b	|删除所有扩展 ACL|
|-R	|递归处理目录|
|-d	|设置默认 ACL|
|-k	|删除默认 ACL|
|-n	|不重新计算 ACL mask|
|--restore|	从备份恢复 ACL|

ACL 规则格式
```text
u:用户名:权限
g:组名:权限
o::权限
m::权限
```
其中：
- u：用户（user）
- g：用户组（group）
- o：其他用户（other）
- m：权限掩码（mask）

权限：
|权限|含义|
| --- | --- |
|r	|读取|
|w	|写入|
|x	|执行 / 目录遍历|
|rw	|读取和写入|
|rwx	|完整权限|
|-	|无权限|

使用示例
```bash
# 只读
sudo setfacl -m u:vm1:r-- /mnt

# 读写
sudo setfacl -m u:vm1:rw- /mnt

# 完整权限
sudo setfacl -m u:vm1:rwx /mnt
```

设置默认 ACL
```bash
# 使用这个设置权限后，后面如果root在/mnt下面创建文件，vm1不会继承权限
sudo setfacl -R -m u:vm1:rwx /mnt

# 所以使用
sudo setfacl -R -m d:u:vm1:rwx /mnt
```
