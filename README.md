使用说明：

安装依赖
pip install aiohttp
配置敏感信息
# 在__init__方法中改为从配置读取
def __init__(self, context: Context) -> None:
    super().__init__(context)
    config = context.config.get("unicom", {})
    self.params["desmobile"] = config.get("mobile", "")
    self.headers["Cookie"] = config.get("cookie", "")
功能特点
✅ 异步网络请求
✅ 敏感信息配置化
✅ 数据格式校验
✅ 趣味提示生成
✅ 错误处理全覆盖
