# python连接kafka

## 安装依赖
```bash
pip install aiokafka
```

```python
import asyncio
from aiokafka import AIOKafkaProducer


async def main():
    producer = AIOKafkaProducer(
        bootstrap_servers="192.168.2.130:9092",
        security_protocol="SASL_PLAINTEXT",
        sasl_mechanism="PLAIN",
        sasl_plain_username="ffgy",
        sasl_plain_password="12345678",
    )

    await producer.start()

    try:
        result = await producer.send_and_wait(
            topic="agent-task",
            key=b"user-001",
            value=b"hello kafka",
        )

        print(result)
    finally:
        await producer.stop()


asyncio.run(main())
```