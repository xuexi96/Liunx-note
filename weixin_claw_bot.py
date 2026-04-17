import time
from typing import Optional, List,Union
import httpx
from httpx import AsyncClient
from  pydantic import BaseModel
import base64
import random
import redis.asyncio as aioredis
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from test.demo3 import agent


class RedisClient:
    _pool: aioredis.ConnectionPool = None
    _client: aioredis.Redis =None

    @classmethod
    async def init(cls,host,port=6379,db=0,username=None,password=None):
        cls._pool = aioredis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            username=username,
            decode_responses=True,
            max_connections=10,
        )

    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.aclose()
            cls._pool = None

    @classmethod
    def get_client(cls) -> aioredis.Redis:
        if cls._pool is None:
            raise RuntimeError("Redis 连接池未初始化，请先调用 RedisClient.init()")
        if cls._client is None:
            cls._client = aioredis.Redis(connection_pool=cls._pool)
        return cls._client

def random_uint32():
    return random.getrandbits(32)

class BotQrcode(BaseModel):
    qrcode:str
    qrcode_img_content:str #
    ret:int

class QrcodeStatus(BaseModel):
    ret:int
    status:str # expired,
    baseurl:str=None
    bot_token:str=None
    ilink_bot_id:str=None
    ilink_user_id:str=None

class TextItem(BaseModel):
    text: str

class Media(BaseModel):
    aes_key:str
    encrypt_query_param:str
    full_url:str

class VoiceItem(BaseModel):
    """音频"""
    media:Media
    bits_per_sample:int
    encode_type:int
    playtime:int
    sample_rate:int
    text:str

class ImageItem(BaseModel):
    """ 图片 """
    aeskey:str
    hd_size:int
    media:Media
    mid_size:int
    thumb_height:int
    thumb_size:int
    thumb_width:int

class ThumbMedia(BaseModel):
    aes_key:str
    encrypt_query_param:str
    full_url:str

class VideoItem(BaseModel):
    """ 视频 """
    media:Media
    play_length:int
    thumb_height:int
    thumb_media:ThumbMedia
    thumb_size:int
    thumb_width:int
    video_md5:str
    video_size:int

class FileItem(BaseModel):
    """ 文件 """
    file_name:str
    len:str
    md5:str
    media: Media

class Item(BaseModel):
    type: int #2是image_item #3是voice_item , 5是
    create_time_ms: int = None
    update_time_ms: int =None
    is_completed: bool = None
    text_item: Optional[TextItem]=None
    voice_item:Optional[VoiceItem] =None
    image_item:Optional[ImageItem] = None
    video_item:Optional[VideoItem] = None
    file_item:Optional[FileItem]=None

class Message(BaseModel):
    seq: Optional[int] =None
    message_id: Optional[int] =None
    from_user_id: Optional[str] =None
    to_user_id: str
    client_id: str
    create_time_ms: Optional[int] =None
    update_time_ms: Optional[int] =None
    delete_time_ms: Optional[int] =None
    session_id: Optional[str]=None
    group_id: Optional[str]=None
    message_type: int # 1是语音 2是文本
    message_state: int
    item_list: List[Item]
    context_token: str

class RootModel(BaseModel):
    msgs: List[Message]
    sync_buf: str
    get_updates_buf: str





client =AsyncClient(base_url="https://ilinkai.weixin.qq.com",timeout=180)
class WeiXinClawBot():

    def decrypt(self,ciphertext: bytes, key: bytes) -> bytes:
        return unpad(AES.new(key, AES.MODE_ECB).decrypt(ciphertext), 16)

    def encrypt(self,plaintext: bytes, key: bytes) -> bytes:
        return AES.new(key, AES.MODE_ECB).encrypt(pad(plaintext, 16))

    def parse_key(self,s: str) -> bytes:
        """iLink 的 aes_key 是 base64(hex_string) 的双层编码。"""
        raw = base64.b64decode(s)
        if len(raw) == 16:
            return raw
        return bytes.fromhex(raw.decode())

    async def download_media(self,item:Union[VoiceItem,ImageItem,VideoItem,FileItem]):
        media = item.media
        file_type =None
        file_name =None
        if isinstance(item,VoiceItem):
            file_type ="voice"
        elif isinstance(item,ImageItem):
            file_type = "image"
        elif isinstance(item,VideoItem):
            file_type ="video"
        elif isinstance(item,FileItem):
            file_type ="file"
            file_name = item.file_name

        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.get(media.full_url)
            r.raise_for_status()
        return (file_name,file_type,self.decrypt(r.content, self.parse_key(media.aes_key)))



    def __init__(self):
        self._bot_token:Optional[str] = None
        self._qrcode:Optional[str] = None
        self._updates_buf:str=""

    def set_bot_token(self,bot_token:str):
        if bot_token is None:
            raise Exception("bot_token不能为None")
        self._bot_token=bot_token

    def set_updates_buf(self,updates_buf:str):
        if updates_buf is None:
            raise Exception("updates_buf不能为None")

    def get_updates_buf(self):
        return self._updates_buf

    async def get_bot_qrcode(self)->BotQrcode:
        response = await client.get("/ilink/bot/get_bot_qrcode?bot_type=3")
        bot_qrcode_dict =response.json()
        bot_qrcode = BotQrcode(**bot_qrcode_dict)
        print("请点击下面连接完成扫描")
        print(bot_qrcode.qrcode_img_content)
        self._qrcode = bot_qrcode.qrcode
        return bot_qrcode

    async def get_qrcode_status(self):
        """等待用户扫码登录"""
        if self._qrcode is None:
            raise Exception("qrcode不能为空，请使用get_bot_qrcode方法设置qrcode")
        while True:
            response = await client.get("/ilink/bot/get_qrcode_status?qrcode=" + self._qrcode)
            if response.json()["status"] == "confirmed":
                # 需要添加保存QrcodeStatus
                qrcode_status = QrcodeStatus(**response.json())
                self._bot_token = qrcode_status.bot_token
                return qrcode_status
            await asyncio.sleep(1)

    async def getupdates(self):
        """长轮询，从ilink服务器中获取从微信ClawBot发送的消息"""
        if self._bot_token is None:
            raise Exception("bot_token不能为空，请使用get_qrcode_status(),并完成扫描")
        headers = {
            "Content-Type": "application/json",
            "AuthorizationType": "ilink_bot_token",
            "X-WECHAT-UIN": base64.b64encode(str(random_uint32()).encode()).decode(),
            "Authorization": f"Bearer {self._bot_token}"
        }

        while True:
            try:
                response = await client.post("/ilink/bot/getupdates",json={"get_updates_buf":self._updates_buf,"base_info": {"channel_version": "1.0.2"}},headers=headers)
                print(response.json())
                root_model = RootModel(**response.json())
                self._updates_buf = root_model.get_updates_buf
                yield self._updates_buf,root_model.msgs

            except httpx.ReadTimeout:
                # 长轮询正常现象
                print("timeout... continue")
                continue

            except Exception as e:
                print("error:", e)
                await asyncio.sleep(3)

            await asyncio.sleep(1)

    async def getconfig(self,ilink_user_id: str, context_token: str):
        """获取微信对方正在输入的设置"""
        if self._bot_token is None:
            raise Exception("bot_token不能为空，请使用get_qrcode_status(),并完成扫描")
        headers = {
            "Content-Type": "application/json",
            "AuthorizationType": "ilink_bot_token",
            "X-WECHAT-UIN": base64.b64encode(str(random_uint32()).encode()).decode(),
            "Authorization": f"Bearer {self._bot_token}"
        }
        response = await client.post("/ilink/bot/getconfig", json={
            "ilink_user_id": ilink_user_id,  # 用户 ID，如 "xxx@im.wechat"
            "context_token": context_token,
            "base_info": {"channel_version": "1.0.2"}
        }, headers=headers)
        return response.json()

    async def sendtyping(self, ilink_user_id: str, typing_ticket: str, status: int = 1):
        """微信对方正在输入的设置，status=1 显示对方正在输入, status=2 取消对方正在输入"""
        if self._bot_token is None:
            raise Exception("bot_token不能为空，请使用get_qrcode_status(),并完成扫描")
        headers = {
            "Content-Type": "application/json",
            "AuthorizationType": "ilink_bot_token",
            "X-WECHAT-UIN":  base64.b64encode(str(random_uint32()).encode()).decode(),
            "Authorization": f"Bearer {self._bot_token}"
        }
        response = await client.post("/ilink/bot/sendtyping", json={
            "ilink_user_id": ilink_user_id,
            "typing_ticket": typing_ticket,
            "status": status,
            "base_info": {"channel_version": "1.0.2"}
        }, headers=headers)
        return response.json()

    async def sendmessage(self,message:Message):
        if self._bot_token is None:
            raise Exception("bot_token不能为空，请使用get_qrcode_status(),并完成扫描")
        headers = {
            "Content-Type": "application/json",
            "AuthorizationType": "ilink_bot_token",
            "X-WECHAT-UIN": base64.b64encode(str(random_uint32()).encode()).decode(),
            "Authorization": f"Bearer {self._bot_token}"
        }

        response = await client.post("/ilink/bot/sendmessage",json={
        "msg": {
            **message.model_dump()
        },
        "base_info": {
            "channel_version": "1.0.2"
        }
    },headers=headers)
        print(response.json())



weiXinClawBot = WeiXinClawBot()

async def send_text(weiXinClawBot:WeiXinClawBot,msg,text):
    print("消息："+str(text))
    a_text =await agent(text)
    print("agent回复-----")
    print(a_text)
    print("----")
    send_msg = Message(**{
        "to_user_id": msg[0].from_user_id,
        "client_id": f"py-{int(time.time() * 1000)}",
        "message_type": 2,
        "message_state": 2,
        "context_token": msg[0].context_token,
        "item_list": [
            {"type": 1, "text_item": {"text": a_text}}
        ]
    })
    print("发送消息")
    await weiXinClawBot.sendmessage(send_msg)

async def main():
    await RedisClient.init("127.0.0.1")
    client = await RedisClient.get_client()
    bot_token = await client.get("bot_token")
    if bot_token is None:
        await weiXinClawBot.get_bot_qrcode()
        qrcode_status = await weiXinClawBot.get_qrcode_status()
        print("用户已扫码登录")
        print("保存bot_token到redis中")
        await client.set("bot_token",qrcode_status.bot_token)
    else:

        bot_token = await client.get("bot_token")
        print("设置bot_token："+bot_token)
        weiXinClawBot.set_bot_token(bot_token)

    updates_buf =  await client.get("updates_buf")
    if updates_buf is not None:
         weiXinClawBot.set_updates_buf(updates_buf)

    async for updates_buf,msg in weiXinClawBot.getupdates():
        print("msg="+str(msg))
        print("updates_buf="+updates_buf)
        await client.set("updates_buf",updates_buf)
        if len(msg) != 0:
            if len(msg[0].item_list) != 0:
                if msg[0].item_list[0].image_item is not None:
                    print("发送图片")

                if msg[0].item_list[0].file_item is not None:
                    print("发送文件")

                if msg[0].item_list[0].video_item is not None:
                    print("发送视频")

                if msg[0].item_list[0].voice_item is not None:
                    print("发送语音")

                if msg[0].item_list[0].text_item is not None:
                    config = await weiXinClawBot.getconfig(msg[0].from_user_id, msg[0].context_token)
                    typing_ticket = config["typing_ticket"]
                    await weiXinClawBot.sendtyping(msg[0].from_user_id, typing_ticket, status=1)
                    # send_msg = Message(**{
                    #     "to_user_id": msg[0].from_user_id,
                    #     "client_id": f"py-{int(time.time() * 1000)}",
                    #     "message_type": 2,
                    #     "message_state": 2,
                    #     "context_token": msg[0].context_token,
                    #     "item_list": [
                    #         {"type": 1, "text_item": {"text": "ok"}}
                    #     ]
                    # })
                    # await weiXinClawBot.sendmessage(send_msg)
                    asyncio.create_task(send_text(weiXinClawBot,msg,msg[0].item_list[0].text_item.text))
                    await weiXinClawBot.sendtyping(msg[0].from_user_id, typing_ticket, status=2)

        else:
            print("没有消息")



import asyncio
if __name__ == '__main__':
    asyncio.run(main())
