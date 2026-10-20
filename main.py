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
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("تم مزامنة الأوامر للبوت بنجاح")

    async def on_ready(self):
        print(f"تسجيل الدخول بنجاح باسم {self.user}")

bot = MyBot()

# 1. قفل الروم
@bot.tree.command(name="lock", description="قفل الروم الحالي لمنع الأعضاء من الكتابة")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 تم قفل الروم بنجاح.")

# 2. فتح الروم
@bot.tree.command(name="unlock", description="فتح الروم الحالي للأعضاء")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 تم فتح الروم بنجاح.")

# 3. إنشاء روم جديد
@bot.tree.command(name="create_room", description="إنشاء روم كتابي جديد")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def create_room(interaction: discord.Interaction, name: str):
    guild = interaction.guild
    await guild.create_text_channel(name)
    await interaction.response.send_message(f"📁 تم إنشاء الروم باسم: **{name}**")

# 4. حذف الروم الحالي
@bot.tree.command(name="delete_room", description="حذف الروم الحالي")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def delete_room(interaction: discord.Interaction):
    await interaction.response.send_message("🗑️ جاري حذف الروم...")
    await interaction.channel.delete()

# 5. مسح الرسائل الجماعي (Clear)
@bot.tree.command(name="clear", description="مسح عدد محدد من الرسائل")
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 تم مسح {len(deleted)} رسالة بنجاح.", ephemeral=True)

# 6. إعطاء ميوت
@bot.tree.command(name="mute", description="إعطاء ميوت لعضو")
@discord.app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
    from datetime import timedelta
    duration = timedelta(minutes=10)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(f"🔇 تم اعطاء ميوت لـ {member.mention} لمدة 10 دقائق. السبب: {reason}")

# 7. حظر (باند/دفن) عضو
@bot.tree.command(name="ban", description="حظر (باند) عضو من السيرفر")
@discord.app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"⚰️ تم دفن وحظر {member.mention} من السيرفر. السبب: {reason}")

# 8. أمر تشغيل رابط الأغنية (عرض الرابط وتأكيد الطلب)
@bot.tree.command(name="play", description="أرسل رابط الأغنية ليقوم البوت بعرضها للتشغيل")
async def play(interaction: discord.Interaction, url: str):
    if interaction.user.voice is None:
        await interaction.response.send_message("⚠️ يجب أن تكون متصلاً بروم صوتي أولاً!", ephemeral=True)
        return
    
    await interaction.response.send_message(f"🎵 تم استلام رابط الأغنية بنجاح بواسطة {interaction.user.mention}:\n{url}\n*(ملاحظة: التشغيل الصوتي المباشر غير متوفر على استضافات ريندر المجانية، لكن الرابط جاهز!)*")

token = os.getenv('DISCORD_TOKEN') or os.getenv('TOKEN')
bot.run(token)
