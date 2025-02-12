# 導入Discord.py模組
import discord
import os
from dotenv import load_dotenv

# 導入commands指令模組
from discord.ext import commands
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

# 載入環境變數
load_dotenv()

# intents是要求機器人的權限
intents = discord.Intents.all()
# command_prefix是前綴符號，可以自由選擇($, #, &...)
bot = commands.Bot(command_prefix="%", intents=intents)

# 從環境變數獲取設定
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_ZONE = os.getenv("GCP_ZONE")
GCP_INSTANCE = os.getenv("GCP_INSTANCE")


# 建立 GCP 憑證字典
def get_credentials():
    credentials_dict = {
        "type": os.getenv("GCP_TYPE"),
        "project_id": os.getenv("GCP_PROJECT_ID"),
        "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GCP_PRIVATE_KEY"),
        "client_email": os.getenv("GCP_CLIENT_EMAIL"),
        "client_id": os.getenv("GCP_CLIENT_ID"),
        "auth_uri": os.getenv("GCP_AUTH_URI"),
        "token_uri": os.getenv("GCP_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GCP_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": os.getenv("GCP_CLIENT_CERT_URL"),
    }
    return ServiceAccountCredentials.from_json_keyfile_dict(
        credentials_dict, scopes=["https://www.googleapis.com/auth/compute"]
    )


@bot.event
# 當機器人完成啟動
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")


@bot.command()
async def closemiffygiantasshole(ctx):
    await ctx.send("好可惜我做不到")


# 修改頻道檢查裝飾器
def check_channel():
    async def predicate(ctx):
        allowed_channel = int(os.getenv("ALLOWED_CHANNEL_ID"))
        if not allowed_channel:
            print("警告：未設定 ALLOWED_CHANNEL_ID")
            return True  # 如果未設定頻道ID，允許在所有頻道使用
        if ctx.channel.id != allowed_channel:
            await ctx.send(
                f"⚠️ 此指令僅能在特定頻道使用。請到 <#{allowed_channel}> 使用此指令！"
            )
            return False
        return True

    return commands.check(predicate)


# 新增錯誤處理裝飾器
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        # 檢查失敗的錯誤已經在 check_channel 中處理
        pass
    else:
        await ctx.send(f"執行指令時發生錯誤：{str(error)}")


# 修改現有的指令，加入頻道檢查
@bot.command()
@check_channel()
async def start(ctx):
    try:
        credentials = get_credentials()
        service = discovery.build("compute", "v1", credentials=credentials)

        request = service.instances().start(
            project=GCP_PROJECT_ID, zone=GCP_ZONE, instance=GCP_INSTANCE
        )
        response = request.execute()

        await ctx.send("VM啟動指令已發送！")
        print(response)
    except Exception as e:
        await ctx.send(f"啟動VM時發生錯誤：{str(e)}")


@bot.command()
@check_channel()
async def stop(ctx):
    try:
        credentials = get_credentials()
        service = discovery.build("compute", "v1", credentials=credentials)

        request = service.instances().stop(
            project=GCP_PROJECT_ID, zone=GCP_ZONE, instance=GCP_INSTANCE
        )
        response = request.execute()

        await ctx.send("VM關閉指令已發送！")
        print(response)
    except Exception as e:
        await ctx.send(f"關閉VM時發生錯誤：{str(e)}")


@bot.command()
@check_channel()
async def status(ctx):
    try:
        credentials = get_credentials()
        service = discovery.build("compute", "v1", credentials=credentials)

        request = service.instances().get(
            project=GCP_PROJECT_ID, zone=GCP_ZONE, instance=GCP_INSTANCE
        )
        response = request.execute()

        status = response["status"]
        status_message = {
            "RUNNING": "🟢 伺服器目前正在運行中",
            "TERMINATED": "🔴 伺服器目前已關閉",
            "STOPPING": "🟡 伺服器正在關閉中",
            "PROVISIONING": "🟡 伺服器正在啟動中",
        }.get(status, f"❓ 伺服器狀態：{status}")

        await ctx.send(status_message)
    except Exception as e:
        await ctx.send(f"查詢VM狀態時發生錯誤：{str(e)}")


# 使用環境變數中的 Token
bot.run(os.getenv("DISCORD_TOKEN"))
