# 使用Docker容器部署kafka

## 创建目录
```bash
mkdir -p ~/docker-compose-project/kafka
cd ~/docker-compose-project/kafka
```
在目录下编辑
compose.yaml
```yaml
services:
  kafka:
    image: apache/kafka:4.4.0
    container_name: kafka
    hostname: kafka
    restart: unless-stopped

    ports:
      - "9092:9092"

    environment:
      # Kafka 节点 ID
      KAFKA_NODE_ID: 1

      # KRaft 模式
      KAFKA_PROCESS_ROLES: broker,controller

      # Controller 配置
      KAFKA_CONTROLLER_QUORUM_VOTERS: "1@kafka:9093"
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER

      # 监听地址
      KAFKA_LISTENERS: INTERNAL://:19092,EXTERNAL://:9092,CONTROLLER://:9093

      # 公布地址,192.168.2.130修改成实际的
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka:19092,EXTERNAL://192.168.2.130:9092

      # 外部监听器开启 SASL_SSL
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:SASL_SSL,CONTROLLER:PLAINTEXT

      # Broker 内部通信
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL

      # ==========================
      # SASL 用户名密码认证
      # ==========================

      KAFKA_SASL_ENABLED_MECHANISMS: PLAIN

      KAFKA_LISTENER_NAME_EXTERNAL_PLAIN_SASL_JAAS_CONFIG: >-
        org.apache.kafka.common.security.plain.PlainLoginModule required
        user_admin="${KAFKA_PASSWORD}";

      # ==========================
      # SSL/TLS 加密配置
      # ==========================

      KAFKA_SSL_KEYSTORE_TYPE: PKCS12

      KAFKA_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/kafka.keystore.p12

      KAFKA_SSL_KEYSTORE_PASSWORD: "${KAFKA_SSL_PASSWORD}"

      KAFKA_SSL_KEY_PASSWORD: "${KAFKA_SSL_PASSWORD}"

      # 不要求客户端提供客户端证书
      KAFKA_SSL_CLIENT_AUTH: none

      # TLS 协议版本
      KAFKA_SSL_ENABLED_PROTOCOLS: TLSv1.2,TLSv1.3

      # ==========================
      # 单节点配置
      # ==========================

      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0

      KAFKA_SHARE_COORDINATOR_STATE_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_SHARE_COORDINATOR_STATE_TOPIC_MIN_ISR: 1

      # 数据目录
      KAFKA_LOG_DIRS: /var/lib/kafka/data

      # JVM 内存
      KAFKA_HEAP_OPTS: "-Xms512m -Xmx512m"

      # 集群 ID
      CLUSTER_ID: "4L6g3nShT-eMCtK--X86sw"

    volumes:
      - kafka-data:/var/lib/kafka/data
      - ./ssl/kafka.keystore.p12:/etc/kafka/secrets/kafka.keystore.p12:ro

volumes:
  kafka-data:
```
在compose.yaml同级目录下运行
```bash
mkdir -p ssl
cd ssl

umask 077
```

在ssl目录下运行
创建 CA 私钥和证书
```bash
openssl genrsa -out ca.key 4096
```

```bash
openssl req -new -x509 \
  -key ca.key \
  -out ca.crt \
  -days 3650 \
  -sha256 \
  -subj "/CN=Kafka-CA"
```
创建 Kafka 服务端私钥
```bash
openssl genrsa -out kafka.key 2048
```

创建证书签名请求
```bash
openssl req -new \
  -key kafka.key \
  -out kafka.csr \
  -subj "/CN=kafka"
```

配置证书 SAN
注意修改192.168.2.130你自己kafka地址
```bash
cat > kafka.ext <<'EOF'
basicConstraints=critical,CA:FALSE
subjectAltName=IP:192.168.2.130,DNS:kafka,DNS:localhost,IP:127.0.0.1
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
EOF
```

使用 CA 签发 Kafka 证书
```bash
openssl x509 -req \
  -in kafka.csr \
  -CA ca.crt \
  -CAkey ca.key \
  -CAcreateserial \
  -out kafka.crt \
  -days 825 \
  -sha256 \
  -extfile kafka.ext
```

创建 PKCS12 密钥库
运行命令需要设置密码，后面的.env 的KAFKA_SSL_PASSWORD就是设置的密码
```bash
openssl pkcs12 -export \
  -in kafka.crt \
  -inkey kafka.key \
  -certfile ca.crt \
  -name kafka \
  -out kafka.keystore.p12
```

设置文件权限
```bash
chmod 600 ca.key kafka.key
chmod 644 ca.crt

sudo chown 1000:1000 kafka.keystore.p12
sudo chmod 600 kafka.keystore.p12

cd ..
```

创建.env 环境变量配置kafka的用户名
```ENV
KAFKA_PASSWORD=12345678
KAFKA_SSL_PASSWORD=12345678
```
设置文件权限
```bash
chmod 600 .env
```

```bash
# 拉取镜像
docker compose pull

# 启动
docker compose up -d

# 查看容器
docker compose ps

# 查看日志
docker logs -f kafka
```