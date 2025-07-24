import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

훈련종목_선택지 = [
    app_commands.Choice(name="한글페이스", value="한글페이스"),
    app_commands.Choice(name="영어페이스", value="영어페이스"),
    app_commands.Choice(name="CE훈련", value="CE훈련")
]

@bot.event
async def on_ready():
    print(f"✅ 봇 로그인: {bot.user} (ID: {bot.user.id})")

    await bot.change_presence(
        activity=discord.Game(name="제 1경비단 훈련 개최")
    )

    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ {len(synced)}개의 명령어 동기화됨")
    except Exception as e:
        print(f"⚠️ 동기화 실패: {e}")

@bot.tree.command(
    name="훈련공지",
    description="훈련 공지를 웹훅으로 전송합니다.",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    organizer="훈련 주최자",
    location="훈련 장소",
    program="훈련 종목",
    time="훈련 시작 시간"
)
@app_commands.choices(program=훈련종목_선택지)
async def 훈련공지(
    interaction: discord.Interaction,
    organizer: str,
    location: str,
    program: app_commands.Choice[str],
    time: str
):
    await interaction.response.send_message("웹훅 전송 중...", ephemeral=True)

    embed = discord.Embed(title="📣 훈련 공지", color=discord.Color.blurple())
    embed.add_field(name="개최자", value=organizer, inline=False)
    embed.add_field(name="장소", value=location, inline=False)
    embed.add_field(name="훈련 종목", value=program.value, inline=False)
    embed.add_field(name="시작 시간", value=time, inline=False)
    embed.set_footer(text=f"발신자: {interaction.user.display_name}")

    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
        await webhook.send(
            content="<@&1386716916814708787>",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(roles=True),
            username="훈련 공지"
        )

    await interaction.followup.send("✅ 전송 완료!", ephemeral=True)

# Flask 서버 (UptimeRobot용)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True  # 데몬 쓰레드로 설정 (메인 종료시 같이 종료)
    t.start()

keep_alive()
bot.run(TOKEN)
