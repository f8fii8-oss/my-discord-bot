# -*- coding: utf-8 -*-
from flask import Flask
from threading import Thread
import os
import discord
from discord.ext import commands

app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!")

    async def setup_hook(self):
        await self.tree.sync()
        print("تم مزامنة الأوامر للبوت")

    async def on_ready(self):
        print(f"تسجيل الدخول بنجاح باسم {self.user}")

bot = MyBot()

@bot.tree.command(name="hello", description="أمر سلام")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("أهلاً بك يا خالد!")

token = os.getenv('DISCORD_TOKEN') or os.getenv('TOKEN')
bot.run(token)
