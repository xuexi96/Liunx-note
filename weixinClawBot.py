import time
from typing import Optional, List

import httpx
from httpx import AsyncClient
from  pydantic import BaseModel
import base64
import random
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

class Item(BaseModel):
    type: int
    create_time_ms: int
    update_time_ms: int
    is_completed: bool
    text_item: Optional[TextItem] = None

class Message(BaseModel):
    seq: int
    message_id: int
    from_user_id: str
    to_user_id: str
    client_id: str
    create_time_ms: int
    update_time_ms: int
    delete_time_ms: int
    session_id: str
    group_id: str
    message_type: int
    message_state: int
    item_list: List[Item]
    context_token: str

class RootModel(BaseModel):
    msgs: List[Message]
    sync_buf: str
    get_updates_buf: str



client =AsyncClient(base_url="https://ilinkai.weixin.qq.com",timeout=180)
class WeiXinClawBot():
    def __init__(self):
        # 整个会话使用同一个 UIN
        self._uin = base64.b64encode(str(random_uint32()).encode()).decode()

    async def get_bot_qrcode(self)->BotQrcode:
        response = await client.get("/ilink/bot/get_bot_qrcode?bot_type=3")
        botQrcode = response.json()
        return BotQrcode(**botQrcode)

    async def get_qrcode_status(self,qrcode:str):

        while True:
            response = await client.get("/ilink/bot/get_qrcode_status?qrcode=" + qrcode)
            if response.json()["status"] == "confirmed":
                return QrcodeStatus(**response.json())
            await asyncio.sleep(1)

    async def getupdates(self,bot_token):
        headers = {
            "Content-Type": "application/json",
            "AuthorizationType": "ilink_bot_token",
            "X-WECHAT-UIN": base64.b64encode(str(random_uint32()).encode()).decode(),
            "Authorization": f"Bearer {bot_token}"
        }
        get_updates_buf = ""
        while True:
            try:
                response = await client.post("/ilink/bot/getupdates",json={"get_updates_buf":get_updates_buf,"base_info": {"channel_version": "1.0.2"}},headers=headers)
                root_model = RootModel(**response.json())
                get_updates_buf = root_model.get_updates_buf
                yield root_model.msgs
                await asyncio.sleep(5)

            except httpx.ReadTimeout:
                # 长轮询正常现象
                print("timeout... continue")
                continue

            except Exception as e:
                print("error:", e)
                await asyncio.sleep(3)

            await asyncio.sleep(1)

    async def getconfig(self, bot_token: str, ilink_user_id: str, context_token: str):
        headers = {
            "Content-Type": "application/json",
            "AuthorizationType": "ilink_bot_token",
            "X-WECHAT-UIN": self._uin,
            "Authorization": f"Bearer {bot_token}"
        }
        response = await client.post("/ilink/bot/getconfig", json={
            "ilink_user_id": ilink_user_id,  # 用户 ID，如 "xxx@im.wechat"
            "context_token": context_token,
            "base_info": {"channel_version": "1.0.2"}
        }, headers=headers)
        return response.json()

    async def sendtyping(self, bot_token: str, ilink_user_id: str, typing_ticket: str, status: int = 1):
        """status=1 开始输入, status=2 取消输入"""
        headers = {
            "Content-Type": "application/json",
            "AuthorizationType": "ilink_bot_token",
            "X-WECHAT-UIN":  base64.b64encode(str(random_uint32()).encode()).decode(),
            "Authorization": f"Bearer {bot_token}"
        }
        response = await client.post("/ilink/bot/sendtyping", json={
            "ilink_user_id": ilink_user_id,
            "typing_ticket": typing_ticket,
            "status": status,
            "base_info": {"channel_version": "1.0.2"}
        }, headers=headers)
        print(response.json())
        return response.json()

    async def sendmessage(self,bot_token:str,message:Message,text:str):
        headers = {
            "Content-Type": "application/json",
            "AuthorizationType": "ilink_bot_token",
            "X-WECHAT-UIN": base64.b64encode(str(random_uint32()).encode()).decode(),
            "Authorization": f"Bearer {bot_token}"
        }
        print("发送消息")

        response = await client.post("/ilink/bot/sendmessage",json={
        "msg": {
            "from_user_id": "",
            "to_user_id": message.from_user_id,
            "client_id": f"py-{int(time.time()*1000)}",
            "message_type": 2,
            "message_state": 2,
            "context_token": message.context_token,
            "item_list": [
                {"type": 1, "text_item": {"text": text}}
            ]
        },
        "base_info": {
            "channel_version": "1.0.2"
        }
    },headers=headers)
        print(response.json())



weiXinClawBot = WeiXinClawBot()

async def main():
    q = await weiXinClawBot.get_bot_qrcode()
    print(q.qrcode_img_content)
    qrcode_status = await weiXinClawBot.get_qrcode_status(q.qrcode)
    print("用户扫码登录"+str(qrcode_status))
    async for msg in weiXinClawBot.getupdates(qrcode_status.bot_token):
        if len(msg) != 0:
            config = await weiXinClawBot.getconfig(qrcode_status.bot_token,msg[0].from_user_id,msg[0].context_token)
            typing_ticket = config["typing_ticket"]
            await weiXinClawBot.sendtyping(qrcode_status.bot_token,msg[0].from_user_id,typing_ticket,status=1)
            await asyncio.sleep(60)
            await weiXinClawBot.sendmessage(qrcode_status.bot_token,msg[0],"ok")
            await weiXinClawBot.sendtyping(qrcode_status.bot_token, msg[0].from_user_id, typing_ticket, status=2)
        else:
            print("没有消息")



import asyncio
if __name__ == '__main__':
    asyncio.run(main())