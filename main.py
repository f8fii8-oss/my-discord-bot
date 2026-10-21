# -*- coding: utf-8 -*-
from flask import Flask
from threading import Thread
import os
import discord
from discord.ext import commands

app = Flask('')

@app.route('/')
def home():
    return "AFK Voice Bot is alive and running!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"البوت الصوتي شغال الآن باسم {bot.user}")

@bot.tree.command(name="join", description="دخول البوت إلى الروم الصوتي الذي أنت فيه")
@discord.app_commands.checks.has_permissions(administrator=True)
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("⚠️ يجب أن تكون متصلاً بروم صوتي أولاً!", ephemeral=True)
        return
    
    # تأجيل الرد لمنع حدوث خطأ The application did not respond
    await interaction.response.defer(ephemeral=True)
    
    voice_channel = interaction.user.voice.channel
    try:
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.move_to(voice_channel)
        else:
            await voice_channel.connect()
        await interaction.followup.send(f"✅ تم الانضمام إلى روم: **{voice_channel.name}** بنجاح!")
    except Exception as e:
        await interaction.followup.send(f"❌ حدث خطأ أثناء الاتصال الصوتي: {e}")

@bot.tree.command(name="leave", description="إخراج البوت من الروم الصوتي")
@discord.app_commands.checks.has_permissions(administrator=True)
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 تم إخراج البوت من الروم الصوتي.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ البوت غير متصل بأي روم صوتي!", ephemeral=True)

token = os.getenv('DISCORD_TOKEN') or os.getenv('TOKEN')
bot.run(token)
