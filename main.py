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
        self.api_url = "https://m.client.10010.com/mobileserviceimportant/home/queryUserInfoSeven"
        self.params = {
            'currentPhone': "16685271920",
            'showType': "0",
            'version': "android@11.0601",
            'desmobile': "16685271920"
        }
        self.headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; V2183A Build/PQ3A.190801.002);unicom{version:android@11.0601}",
            'Cookie': "your_cookie_here"  # 建议从配置读取
        }
        self.timeout = aiohttp.ClientTimeout(total=15)

    async def fetch_data(self) -> Optional[dict]:
        """异步获取数据"""
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

    def _generate_tips(self, fee: float, flow: float) -> list:
        """生成趣味提示"""
        tips = []
        if fee < 10:
            tips.append("💸 话费余额较低，请及时充值")
        else:
            tips.append("😊 话费充足，放心使用")

        if flow < 1:
            tips.append("📉 流量告急，建议购买流量包")
        else:
            tips.append("🏄 流量充足，尽情冲浪")

        tips.append("🎁 积分可以兑换好礼，快去看看吧")
        return tips

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
