import aiohttp
import json
import logging
from typing import Optional
from astrbot.api.all import AstrMessageEvent, CommandResult, Context, Plain
import astrbot.api.event.filter as filter
from astrbot.api.star import register, Star

logger = logging.getLogger("astrbot")

@register("unicom_query", "Soulter", "联通账户查询插件", "1.0.0")
class UnicomQuery(Star):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        
        # 内置配置信息
        self._config = {
            "mobile": "16685271920",  # 需要查询的手机号
            "cookie": (
                "ecs_cook=c0e388eed7e73d414e92b495f3806b05; a_token=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDA3Mzc5NzgsInRva2VuIjp7ImxvZ2luVXNlciI6IjE2Njg1MjcxOTIwIiwicmFuZG9tU3RyIjoieWhmMDI3ZTYxNzQwMTMzMTc4In0sImlhdCI6MTc0MDEzMzE3OH0.r6wTHMMAhH1jgFFUBkcnm1It80k0JSjRQKxjjb-4vdFgUQK_TmTBrY79ZSAjRZ6MGpchybpDuwgLxKKvDNZcHw; c_id=aa692acad0e22d4de9a1e261962ae630b1a03d7510571dd9c72c5ddc3ade0a7e; c_mobile=16685271920; c_version=iphone_c@12.0100; city=085|851|90063345|-99; cw_mutual=7064d003eb3c8934e769e430ecf3d64ad3bcd7560f77a485ee6c6bcd616d8ab3102a7c3fd97895b283d9893a93c317a50fdbdb10b784d5f28c898b13e8d3e456; d_deviceCode=15A7296C-E0C3-41A6-8961-F7DE8D35C424; ecs_acc=Snn9dv+Nyu8xC3cAkveOChPamGsTofqX5BfkR2TQzwmjmvSXeTPgqY+MamEXygK6L3YPtgrSro+aTwRQVyCstpCuvfGkAxYzi2rXmUewLyikUg160UVCGPFTprPSmkAYkMQgWYwGdzjKW7jol6T3ISnOc72jg6DFaC0JkzkcQio=; ecs_token=eyJkYXRhIjoiYjlhMmNhNzBkMmFkNWQ1ZWQ2ZDJhYTM0Y2ZjOTA1MWNmMzcyNzUwZTA4ODM1NDQ0NTBmNDYwZDlkNTc3MDk1MWIyODFlMjZlNWJjMTU3M2MxZjRkY2YzZjMzMTQ1YzhkNTVkMzk0NjUyZTM4ZmZhODA5MDU2ZmNjYjY0Mzc2NGU1NzUzNWIwOTEwY2NhOWQxYTg1MzVhOWZlYmVjNDAzMTRmZDYyMDViZmRjMDgxNjFhMjVjMTlmZWRlN2U5ODg5M2MxYjI5ZDk3MjhkYTc5ZDNkMDU2OTdlNjY4ZTY3M2Y5NGVlNTMxNmViNjI3ZGM5YzlkMTQ1OTQ2NzU5MTk2ZGQ0MjZiOWQ0NGZlNjQ0ZTViZmFiOWY5M2NkOGY0ZDkxZTEyZTRjMWNiMjJiZjgxNzFkMjQ2OTdmODA3YWEyNGQiLCJ2ZXJzaW9uIjoiMDAifQ==; enc_acc=Snn9dv+Nyu8xC3cAkveOChPamGsTofqX5BfkR2TQzwmjmvSXeTPgqY+MamEXygK6L3YPtgrSro+aTwRQVyCstpCuvfGkAxYzi2rXmUewLyikUg160UVCGPFTprPSmkAYkMQgWYwGdzjKW7jol6T3ISnOc72jg6DFaC0JkzkcQio=; invalid_at=42afc4c32f7570ac2d0bf7a336f8d5f4567a39eb3d1e280767766b81389090d6; jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtb2JpbGUiOiIxNjY4NTI3MTkyMCIsInBybyI6IjA4NSIsImNpdHkiOiI4NTEiLCJpZCI6IjgxNzM4MDFkMTNmZWEzNjA1NWZmN2U5MDk1ZDJiODk0In0.uiBfrR5-Mx7aVDsdVUh1Jf80YfL8d2z14MNWQM7OsDU; login_type=01; random_login=0; t3_token=a13af1911ad25850658eb1189e4e2d65; third_token=eyJkYXRhIjoiMTMyYzJlNGFmOTFiOWU0ZTRmMmMyMDQwOWVkNWU5NDI3ZTU4NTcwYWY5ZThhNjUzYTc1MTlkZmYyMGU3ZDNkM2E2NzIyZjBkZjI3NTE4NjMyMDA2NzU5YmU1M2M5YzFlZDA1MDg4MDRiMWRlN2M5YWUzZGMwYTkyOTUxODRiZDJkYjJlOTgxMzRlNTY0OGU1NDA1ZDA0MGVmMTViMDhiZSIsInZlcnNpb24iOiIwMCJ9; u_account=16685271920; u_areaCode=; wo_family=0; GUESS_NUM=NjAwMzIxNjA=; MUT=bdb3b3de-e22a-4fdf-94f2-89e7ad1c120f; SHOP_PROV_CITY=; TOKEN_NET=UNI; TOKEN_UID=t5vDMgJ9c30sTTUWx6g4NA==; TOKEN_UID_ALL=%7B%22userNick%22%3A%22%25E8%2581%2582%25E6%2597%25BA%22%2C%22phoneNum%22%3A%2216685271920%22%2C%22certNum%22%3A%22522401********1530%22%7D; TOKEN_UID_NAME=IAXBHoVVO42xwGRthFozjcAjJnnEqzvUnh11O7seNP2kxX5xg14RbuR2Z+VFqjY0C9I4nmFbcbBKI9zMv5q9u8M3QkDCt+5fBy198QOJmbTBHcAQ58Ce9R3mUTlLCro5Z3DS9UXoLdwJJRidpfeFQv2V5N7DXAAgH9EXRzDuZy6BlKbkd4x1Dj+fxolkJCQNBaZIZ+h3W4ltNTpZMaNmgF/Gfzs7fMrLHVernfr9xoc=; TOKEN_UID_USER_TYPE=i9l3sWUHcENwPsEMBBuIog==; TOKEN_USER_NET=1; TOKEN_USER_TYPE=i9l3sWUHcENwPsEMBBuIog==; gipgeo=85|850; mallcity=85|850; tianjin_ip=0; tianjincity=11|110; usercity=85|851; cdn_area=85|851; acw_tc=3ccdc15817401331395681160e4451954e28b26adfcb6babfe8f5c85f40aad; PvSessionId=2025022118185615A7296C-E0C3-41A6-8961-F7DE8D35C424; channel=GGPD; devicedId=15A7296C-E0C3-41A6-8961-F7DE8D35C424"  
            ),
            "api_params": {
                'showType': "0",
                'version': "android@11.0601"
            }
        }

        # 初始化请求参数
        self.api_url = "https://m.client.10010.com/mobileserviceimportant/home/queryUserInfoSeven"
        self.params = {
            'currentPhone': self._config["mobile"],
            'desmobile': self._config["mobile"],
            **self._config["api_params"]
        }
        self.headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; V2183A Build/PQ3A.190801.002);unicom{version:android@11.0601}",
            'Cookie': self._config["cookie"]
        }
        self.timeout = aiohttp.ClientTimeout(total=15)

    async def fetch_data(self) -> Optional[dict]:
        """异步获取数据（保持不变）"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                    self.api_url,
                    params=self.params,
                    headers=self.headers
                ) as resp:
                    if resp.status != 200:
                        logger.error(f"API请求失败: {resp.status}")
                        return None
                    return await resp.json()
        except Exception as e:
            logger.error(f"请求异常: {str(e)}")
            return None

    # 以下方法保持不变
    def _generate_tips(self, fee: float, flow: float) -> list:
        # ... 同之前代码 ...

    @filter.command("话费查询")
    async def query_balance(self, event: AstrMessageEvent):
        '''查询联通账户余额'''
        try:
            # 发送等待提示
            yield CommandResult().message("⏳ 正在查询账户信息...")

            data = await self.fetch_data()
            if not data:
                yield CommandResult().error("❌ 查询失败，请稍后重试")
                return

            # 解析数据
            try:
                main_data = data.get("data", {})
                fee_info = main_data.get("feeResource", {})
                flow_info = main_data.get("flowResource", {})
                voice_info = main_data.get("voiceResource", {})
                point_item = next(
                    (item for item in main_data.get("dataList", []) 
                    if item.get("type") == "point"), 
                    {}
                )

                # 获取数值
                level = main_data.get("levelNum", "未知")
                fee = float(fee_info.get("feePersent", 0))
                flow = float(flow_info.get("flowPersent", 0))
                voice = voice_info.get("voicePersent", "未知")
                points = point_item.get("number", "未知")
                update_time = main_data.get("flush_date_time", "未知时间")

            except KeyError as e:
                logger.error(f"数据解析失败: {str(e)}")
                yield CommandResult().error("❌ 数据解析异常，请联系管理员")
                return

            # 生成提示
            tips = self._generate_tips(fee, flow)

            # 构建消息
            msg = [
                "📱【联通账户信息】",
                f"🌟 用户星级：{level}星",
                f"💰 剩余话费：{fee} {fee_info.get('newUnit', '')}",
                f"📶 剩余流量：{flow} {flow_info.get('newUnit', '')}",
                f"🎙️ 剩余语音：{voice} {voice_info.get('newUnit', '')}",
                f"🎁 可用积分：{points}分",
                f"⏰ 更新时间：{update_time}",
                "\n💡 温馨提示：",
                "\n".join([f"- {tip}" for tip in tips])
            ]

            yield CommandResult().message("\n".join(msg)).use_t2i(False)

        except Exception as e:
            logger.error(f"处理异常: {str(e)}", exc_info=True)
            yield CommandResult().error("❌ 系统开小差了，请稍后再试")
