import asyncio
import math
import os
import time
from collections import defaultdict
from datetime import date, datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


def get_moon():
    new_moon = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    days = (now - new_moon).total_seconds() / 86400
    moon_age = days % 29.530588

    illumination = (1 - math.cos(2 * math.pi * moon_age / 29.530588)) / 2

    if moon_age < 1.84566:
        phase = "新月"
    elif moon_age < 5.53699:
        phase = "三日月"
    elif moon_age < 9.22831:
        phase = "上弦の月"
    elif moon_age < 12.91963:
        phase = "十三夜"
    elif moon_age < 16.61096:
        phase = "満月"
    elif moon_age < 20.30228:
        phase = "十六夜"
    elif moon_age < 23.99361:
        phase = "下弦の月"
    else:
        phase = "二十六夜"

    return phase, int(illumination * 100)


MOON_EMOJIS = {
    "新月": "🌑",
    "三日月": "🌒",
    "上弦の月": "🌓",
    "十三夜": "🌔",
    "満月": "🌕",
    "十六夜": "🌖",
    "下弦の月": "🌗",
    "二十六夜": "🌘",
}


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("ログインしました")


@bot.tree.command(name="neko", description="にゃーん")
async def neko(interaction: discord.Interaction):
    await interaction.response.send_message("にゃーん")


@bot.tree.command(name="moon", description="今日の月の形を表示します")
async def moon(interaction: discord.Interaction):
    phase, illumination = get_moon()
    emoji = MOON_EMOJIS.get(phase, "🌙")

    if phase == "満月":
        title = "🌕🌕 満月です！ 🌕🌕"
        color = 0xFFD700
    else:
        title = f"{emoji} 今日の月"
        color = 0x2B2D31

    embed = discord.Embed(
        title=title,
        description=(f"月の形：{phase} {emoji}\n照らされている割合：{illumination}%"),
        color=color,
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="love", description="指定したユーザーに告白します")
@app_commands.describe(target="告白する相手")
async def love(interaction: discord.Interaction, target: discord.Member):
    if target.bot:
        await interaction.response.send_message(
            "🤖 Botをメンションすることはできません。", ephemeral=True
        )
        return

    await interaction.response.send_message(f"{target.mention}\n月が綺麗ですね")


@bot.tree.command(name="love_anonymous", description="匿名で告白")
@app_commands.describe(target="告白する相手")
async def love_anonymous(interaction: discord.Interaction, target: discord.Member):
    if target.bot:
        await interaction.response.send_message(
            "🤖 Botをメンションすることはできない", ephemeral=True
        )
        return

    await interaction.response.send_message("CHILL", ephemeral=True, delete_after=0.1)

    await interaction.channel.send(f"{target.mention}月が綺麗ですね")


@bot.tree.command(name="thread", description="プライベートのスレッドを作成（最大3人）")
@app_commands.describe(
    target1="招待するメンバー（必須）",
    target2="招待するメンバー（任意）",
    target3="招待するメンバー（任意）",
)
async def private(
    interaction: discord.Interaction,
    target1: discord.Member,
    target2: discord.Member | None = None,
    target3: discord.Member | None = None,
):
    targets = [target1]

    if target2 is not None:
        targets.append(target2)

    if target3 is not None:
        targets.append(target3)

    if any(t.bot for t in targets):
        await interaction.response.send_message(
            "🤖 botを招待することはできない", ephemeral=True
        )
        return

    names = ".".join(t.display_name for t in targets)
    threadname = f"🔒 {interaction.user.display_name} → {names}"

    thread = await interaction.channel.create_thread(
        name=threadname, type=discord.ChannelType.public_thread
    )

    await thread.add_user(interaction.user)

    for t in targets:
        await thread.add_user(t)

    mentions = ".".join(t.mention for t in targets)

    await thread.send(
        f"{mentions}\n"
        f"🔒 {interaction.user.display_name} が作成したプライベートスレッドです"
    )

    await interaction.response.send_message(
        "🔒 プライベートスレッドを作成しました。", ephemeral=True
    )


@bot.tree.command(name="thread_close", description="スレッドを削除")
async def thread_close(interaction: discord.Interaction):
    channel = interaction.channel
    if not isinstance(channel, discord.Thread):
        await interaction.response.send_message(
            "❌ このコマンドはスレッド内でのみ使用できます。", ephemeral=True
        )
        return
    if not channel.is_private:
        await interaction.response.send_message(
            "❌ プライベートスレッドでのみ使用できます。", ephemeral=True
        )
        return

    await interaction.response.send_message(
        "🗑️ このスレッドは削除されます", ephemeral=True
    )
    await channel.edit(archived=True)

    await asyncio.sleep(1)

    await channel.delete()


@bot.tree.command(name="name", description="ニックネームの変更・リセット")
@app_commands.describe(nickname="新しいニックネーム（resetで元に戻す）")
async def name(interaction: discord.Interaction, nickname: str):
    member = interaction.user

    try:
        if nickname.lower() == "reset":
            await member.edit(nick=None)
            msg = "ニックネームをリセットしました"
        else:
            await member.edit(nick=nickname)
            msg = f"ニックネームを {nickname} に変更しました"
        await interaction.response.send_message(msg, ephemeral=True)

    except discord.Forbidden:
        await interaction.response.send_message(
            "権限が足りなくて変更できません", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"エラー: {e}", ephemeral=True)


keep_alive()
bot.run(TOKEN)
