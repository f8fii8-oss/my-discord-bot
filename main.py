import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='$', intents=intents)

    async def setup_hook(self):
        # مزامنة الأوامر مع ديسكورد لتظهر في القائمة
        await self.tree.sync()
        print(f"تم مزامنة الأوامر للبوت: {self.user}")

    async def on_ready(self):
        print(f'تم تسجيل الدخول بنجاح باسم: {self.user}')

bot = MyBot()

# تعريف أمر سلش (Slash Command) يظهر في القائمة المنسقة بالديسكورد
@bot.tree.command(name="hello", description="يرحب بك البوت")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("مرحباً بك!")

# التشغيل الآمن للبوت
token = os.getenv('DISCORD_TOKEN') or os.getenv('TOKEN')
bot.run(token)
