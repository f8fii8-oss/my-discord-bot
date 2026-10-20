# -*- coding: utf-8 -*-
from flask import Flask
from threading import Thread
import os
import random
import sqlite3
from datetime import datetime, timedelta
import discord
from discord.ext import commands

app = Flask('')

@app.route('/')
def home():
    return "I am alive and fully packed!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# --- إعداد قاعدة البيانات للستريك واللفلات ---
db = sqlite3.connect("bot_database.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    streak INTEGER DEFAULT 0,
    last_streak TEXT,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1
)
""")
db.commit()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("تمت مزامنة جميع الأوامر الخرافية بنجاح!")

    async def on_ready(self):
        print(f"البوت جاهز ويعمل باسم {self.user}")

bot = MyBot()

AZKAR_LIST = [
    "لا إله إلا الله وحدَهُ لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
    "سُبْحَان اللهِ وبِحَمْدِهِ، عَدَدَ خَلْقِهِ، وَرِضَا نَفْسِهِ، وَزِنَةَ عَرْشِهِ، وَمِدَادَ كَلِمَاتِهِ.",
    "اللهم إني أسألك العفو والعافية في الدنيا والآخرة.",
    "استغفر الله العظيم الذي لا إله إلا هو الحي القيوم وأتوب إليه.",
    "اللهم صل وسلم على نبينا محمد وعلى آله وصحبه أجمعين.",
    "ربنا آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار."
]

# --- الأحداث واللوقات والنظام التلقائي ---

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # نظام الـ XP والتلفيل التلقائي مع كل رسالة
    user_id = message.author.id
    cursor.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        cursor.execute("INSERT INTO users (user_id, xp, level) VALUES (?, ?, ?)", (user_id, 10, 1))
    else:
        xp, level = result
        xp += 10
        if xp >= level * 100:  # كل لفل يحتاج نقاط أكثر
            level += 1
            xp = 0
            try:
                await message.channel.send(f"🎉 مبروك يا {message.author.mention}! لقد صعدت إلى المستوى **{level}**!")
            except:
                pass
        cursor.execute("UPDATE users SET xp = ?, level = ? WHERE user_id = ?", (xp, level, user_id))
    db.commit()

    await bot.process_commands(message)

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
        embed = discord.Embed(title="📥 دخل عضو جديد", description=f"{member.mention} انضم إلى السيرفر منورنا!", color=discord.Color.green())
        embed.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    log_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if log_channel:
        embed = discord.Embed(title="📤 غادر عضو", description=f"{member.mention} خرج من السيرفر.", color=discord.Color.orange())
        await log_channel.send(embed=embed)

# --- الأوامر التفاعلية والـ Slash Commands الخرافية ---

# 1. نظام الستريك (Streak) اليومي
@bot.tree.command(name="streak", description="سجل حضورك اليومي للحفاظ على الستريك وتكبيره 🔥")
async def streak(interaction: discord.Interaction):
    user_id = interaction.user.id
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("SELECT streak, last_streak FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        cursor.execute("INSERT INTO users (user_id, streak, last_streak) VALUES (?, 1, ?)", (user_id, today))
        db.commit()
        await interaction.response.send_message(f"🔥 رائع يا {interaction.user.mention}! بداية ستريك جديد: **1 يوم**.")
        return

    current_streak, last_streak = result

    if last_streak == today:
        await interaction.response.send_message(f"⏳ لقد سجلت ستريك اليوم مسبقاً! ستريكك الحالي: **{current_streak} أيام** 🔥", ephemeral=True)
        return

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    if last_streak == yesterday:
        current_streak += 1
        msg = f"🔥 ممتاز! تم زيادة الستريك الخاص بك ليصبح: **{current_streak} أيام** متتالية!"
    else:
        current_streak = 1
        msg = f"⚠️ لقد انقطع ستريكك للأسف! بدأنا عداد جديد: **1 يوم**."

    cursor.execute("UPDATE users SET streak = ?, last_streak = ? WHERE user_id = ?", (current_streak, today, user_id))
    db.commit()
    await interaction.response.send_message(f"{interaction.user.mention} {msg}")

# 2. ملف الشخصي واللفل (Profile)
@bot.tree.command(name="profile", description="عرض مستواك، نقاطك، والستريك الخاص بك")
async def profile(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    cursor.execute("SELECT streak, xp, level FROM users WHERE user_id = ?", (target.id,))
    result = cursor.fetchone()

    if not result:
        streak_val, xp_val, level_val = 0, 0, 1
    else:
        streak_val, xp_val, level_val = result

    embed = discord.Embed(title=f"👤 ملف الشخصي لـ {target.name}", color=discord.Color.gold())
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="🔥 الستريك", value=f"{streak_val} يوم", inline=True)
    embed.add_field(name="⭐ المستوى (Level)", value=f"{level_val}", inline=True)
    embed.add_field(name="✨ النقاط (XP)", value=f"{xp_val} XP", inline=True)
    await interaction.response.send_message(embed=embed)

# 3. الأذكار
@bot.tree.command(name="azkar", description="إرسال ذكر أو دعاء مبارك")
async def azkar(interaction: discord.Interaction):
    chosen_zikr = random.choice(AZKAR_LIST)
    azkar_channel = discord.utils.get(interaction.guild.text_channels, name="azkar")
    
    embed = discord.Embed(title="📿 ذكر وتذكير", description=f"**{chosen_zikr}**", color=discord.Color.blue())
    embed.set_footer(text=f"بواسطة: {interaction.user.name}")
    
    if azkar_channel and interaction.channel.id != azkar_channel.id:
        await azkar_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ تم إرسال الذكر في روم {azkar_channel.mention}", ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed)

# 4. الأوامر الإدارية
@bot.tree.command(name="lock", description="قفل الروم الحالي")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 تم قفل الروم بنجاح.")

@bot.tree.command(name="unlock", description="فتح الروم الحالي")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 تم فتح الروم بنجاح.")

@bot.tree.command(name="create_room", description="إنشاء روم كتابي جديد")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def create_room(interaction: discord.Interaction, name: str):
    await interaction.guild.create_text_channel(name)
    await interaction.response.send_message(f"📁 تم إنشاء الروم باسم: **{name}**")

@bot.tree.command(name="delete_room", description="حذف الروم الحالي")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def delete_room(interaction: discord.Interaction):
    await interaction.response.send_message("🗑️ جاري حذف الروم...")
    await interaction.channel.delete()

@bot.tree.command(name="clear", description="مسح عدد محدد من الرسائل")
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 تم مسح {len(deleted)} رسالة بنجاح.", ephemeral=True)

@bot.tree.command(name="mute", description="إعطاء ميوت لعضو")
@discord.app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
    await interaction.response.defer()
    duration = timedelta(minutes=10)
    await member.timeout(duration, reason=reason)
    await interaction.followup.send(f"🔇 تم اعطاء ميوت لـ {member.mention} لمدة 10 دقائق. السبب: {reason}")

@bot.tree.command(name="ban", description="حظر (باند) عضو من السيرفر")
@discord.app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
    await interaction.response.defer()
    await member.ban(reason=reason)
    await interaction.followup.send(f"⚰️ تم دفن وحظر {member.mention} من السيرفر. السبب: {reason}")

@bot.tree.command(name="play", description="عرض رابط الأغنية")
async def play(interaction: discord.Interaction, url: str):
    if interaction.user.voice is None:
        await interaction.response.send_message("⚠️ يجب أن تكون متصلاً بروم صوتي أولاً!", ephemeral=True)
        return
    await interaction.response.send_message(f"🎵 تم استلام رابط الأغنية بواسطة {interaction.user.mention}:\n{url}")

token = os.getenv('DISCORD_TOKEN') or os.getenv('TOKEN')
bot.run(token)
