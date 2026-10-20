# -*- coding: utf-8 -*-
from flask import Flask
from threading import Thread
import os
import random
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
intents.guilds = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("تم مزامنة الأوامر للبوت بنجاح")

    async def on_ready(self):
        print(f"تسجيل الدخول بنجاح باسم {self.user}")

bot = MyBot()

# --- قائمة الأذكار والأدعية ---
AZKAR_LIST = [
    "لا إله إلا الله وحدَهُ لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
    "سُبْحَان اللهِ وبِحَمْدِهِ، عَدَدَ خَلْقِهِ، وَرِضَا نَفْسِهِ، وَزِنَةَ عَرْشِهِ، وَمِدَادَ كَلِمَاتِهِ.",
    "اللهم إني أسألك العفو والعافية في الدنيا والآخرة.",
    "استغفر الله العظيم الذي لا إله إلا هو الحي القيوم وأتوب إليه.",
    "اللهم صل وسلم على نبينا محمد وعلى آله وصحبه أجمعين.",
    "ربنا آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار.",
    "لا حول ولا قوة إلا بالله العلي العظيم.",
    "اللهم إني أسألك علماً نافعاً ورزقاً طيباً وعملاً متقبلاً."
]

# --- نظام اللوقات (Logs Events) ---

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    for guild in bot.guilds:
        log_channel = discord.utils.get(guild.text_channels, name="logs")
        if log_channel:
            embed = discord.Embed(title="🗑️ تم حذف رسالة", color=discord.Color.red())
            embed.add_field(name="المستخدم", value=message.author.mention, inline=True)
            embed.add_field(name="الروم", value=message.channel.mention, inline=True)
            embed.add_field(name="المحتوى", value=message.content or "محتوى فارغ (صورة/مرفق)", inline=False)
            await log_channel.send(embed=embed)
            break

@bot.event
async def on_member_join(member):
    log_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if log_channel:
        embed = discord.Embed(title="📥 دخل عضو جديد", description=f"{member.mention} انضم إلى السيرفر.", color=discord.Color.green())
        embed.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    log_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if log_channel:
        embed = discord.Embed(title="📤 غادر عضو", description=f"{member.mention} خرج من السيرفر.", color=discord.Color.orange())
        await log_channel.send(embed=embed)

# --- الأوامر الإدارية والتفاعلية (Slash Commands) ---

# 1. أمر الأذكار (يرسل ذكر عشوائي في روم azkar أو الروم الحالي)
@bot.tree.command(name="azkar", description="إرسال ذكر أو دعاء مبارك")
async def azkar(interaction: discord.Interaction):
    chosen_zikr = random.choice(AZKAR_LIST)
    
    # البحث عن روم الأذكار المخصص أو إرساله في نفس الروم
    azkar_channel = discord.utils.get(interaction.guild.text_channels, name="azkar")
    target_channel = azkar_channel if azkar_channel else interaction.channel
    
    embed = discord.Embed(title="📿 ذكر وتذكير", description=f"**{chosen_zikr}**", color=discord.Color.blue())
    embed.set_footer(text=f"بواسطة: {interaction.user.name}")
    
    if azkar_channel and interaction.channel.id != azkar_channel.id:
        await azkar_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ تم إرسال الذكر بنجاح في روم {azkar_channel.mention}", ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed)

# 2. قفل الروم
@bot.tree.command(name="lock", description="قفل الروم الحالي لمنع الأعضاء من الكتابة")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 تم قفل الروم بنجاح.")

# 3. فتح الروم
@bot.tree.command(name="unlock", description="فتح الروم الحالي للأعضاء")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 تم فتح الروم بنجاح.")

# 4. إنشاء روم جديد
@bot.tree.command(name="create_room", description="إنشاء روم كتابي جديد")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def create_room(interaction: discord.Interaction, name: str):
    guild = interaction.guild
    await guild.create_text_channel(name)
    await interaction.response.send_message(f"📁 تم إنشاء الروم باسم: **{name}**")

# 5. حذف الروم الحالي
@bot.tree.command(name="delete_room", description="حذف الروم الحالي")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def delete_room(interaction: discord.Interaction):
    await interaction.response.send_message("🗑️ جاري حذف الروم...")
    await interaction.channel.delete()

# 6. مسح الرسائل الجماعي (Clear)
@bot.tree.command(name="clear", description="مسح عدد محدد من الرسائل")
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 تم مسح {len(deleted)} رسالة بنجاح.", ephemeral=True)

# 7. إعطاء ميوت
@bot.tree.command(name="mute", description="إعطاء ميوت لعضو")
@discord.app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
    from datetime import timedelta
    duration = timedelta(minutes=10)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(f"🔇 تم اعطاء ميوت لـ {member.mention} لمدة 10 دقائق. السبب: {reason}")

# 8. حظر (باند/دفن) عضو
@bot.tree.command(name="ban", description="حظر (باند) عضو من السيرفر")
@discord.app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"⚰️ تم دفن وحظر {member.mention} من السيرفر. السبب: {reason}")

# 9. أمر عرض رابط الأغنية
@bot.tree.command(name="play", description="أرسل رابط الأغنية ليقوم البوت بعرضها للتشغيل")
async def play(interaction: discord.Interaction, url: str):
    if interaction.user.voice is None:
        await interaction.response.send_message("⚠️ يجب أن تكون متصلاً بروم صوتي أولاً!", ephemeral=True)
        return
    
    await interaction.response.send_message(f"🎵 تم استلام رابط الأغنية بنجاح بواسطة {interaction.user.mention}:\n{url}")

token = os.getenv('DISCORD_TOKEN') or os.getenv('TOKEN')
bot.run(token)
