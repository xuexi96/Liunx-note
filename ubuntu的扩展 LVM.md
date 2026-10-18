# 先看当前磁盘、LVM 和文件系统情况

查看磁盘、分区以及块设备结构
```bash
lsblk
```
NAME                      MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda                         8:0    0   70G  0 disk
├─sda1                      8:1    0    1M  0 part
├─sda2                      8:2    0    2G  0 part /boot
└─sda3                      8:3    0   58G  0 part
  └─ubuntu--vg-ubuntu--lv 252:0    0   29G  0 lvm  /
sr0                        11:0    1 1024M  0 rom

物理磁盘是70G，LVM 物理卷58G

查看 LVM 物理卷
```bash
pvs
```
 PV         VG        Fmt  Attr PSize   PFree
  /dev/sda3  ubuntu-vg lvm2 a--  <58.00g 29.00g



查看 LVM 卷组(空闲空间)
```bash
vgs 
```
  VG        #PV #LV #SN Attr   VSize   VFree
  ubuntu-vg   1   1   0 wz--n- <58.00g 29.00g


查看 LVM 逻辑卷(已分配)
```bash
lvs
```
  LV        VG        Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  ubuntu-lv ubuntu-vg -wi-ao---- <29.00g


扩展磁盘分区
```bash
 sudo growpart /dev/sda 3
```

扩展 PV
```bash
sudo pvresize /dev/sda3
```

扩展 LV
```bash
sudo lvextend -r -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
```

物理磁盘 /dev/sda（70G）
│
├── /dev/sda1（1M）
├── /dev/sda2（2G）
│
└── /dev/sda3（58G） ← growpart 扩展这里
    │
    └── PV（物理卷） ← pvresize 扩展这里
        │
        └── ubuntu-vg（卷组）
            │
            └── ubuntu-lv（逻辑卷） ← lvextend
                │
                └── /（根目录）