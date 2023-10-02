import httpx
import logging
import uuid
from configs.setting import sms_api

async def send_sms(phone,message):
    params = {"to":phone,"message":message,"sender":"IdolBar"}
    headers = {}
    headers["Authorization"] = f'Bearer {sms_api.token}'
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(f'{sms_api.host}/v2/send', json = params,headers=headers, timeout=None)
            if r.status_code == 200:
                record = r.json()
                return record
            return None
    except httpx.RequestError as exc:
        return None
    except Exception as e:
        return None
