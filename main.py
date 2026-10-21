# -*- coding: utf-8 -*-
from flask import Flask
from threading import Thread
import os
import random
import sqlite3
from datetime import datetime, timedelta
import discord
from discord.ext import commands, tasks
from collections import defaultdict, deque

app = Flask('')

@app.route('/')
def home():
    return "Ultimate AFK Bot is alive and running!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

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

intents = discord.Intents.all()

class UltimateBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(TicketView())
        self.add_view(CloseTicketView())
        await self.tree.sync()
        print("تمت مزامنة جميع الأوامر وأنظمة الحماية والتكتات والصوت بنجاح!")

    async def on_ready(self):
        print(f"البوت المتكامل شغال الآن باسم {self.user}")
        if not auto_azkar_loop.is_running():
            auto_azkar_loop.start()

bot = UltimateBot()

AZKAR_LIST = [
    "لا إله إلا الله وحدَهُ لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
    "سُبْحَان اللهِ وبِحَمْدِهِ، عَدَدَ خَلْقِهِ، وَرِضَا نَفْسِهِ، وَزِنَةَ عَرْشِهِ، وَمِدَادَ كَلِمَاتِهِ.",
    "اللهم إني أسألك العفو والعافية في الدنيا والآخرة.",
    "استغفر الله العظيم الذي لا إله إلا هو الحي القيوم وأتوب إليه.",
    "اللهم صل وسلم على نبينا محمد وعلى آله وصحبه أجمعين.",
    "ربنا آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار."
]

def get_log_channel(guild):
    LOG_CHANNEL_ID = 1562238501678878740
    return guild.get_channel(LOG_CHANNEL_ID)

@tasks.loop(hours=2)
async def auto_azkar_loop():
    TARGET_CHANNEL_ID = 1562238501678878740
    for guild in bot.guilds:
        channel = guild.get_channel(TARGET_CHANNEL_ID)
        if channel:
            try:
                chosen_zikr = random.choice(AZKAR_LIST)
                embed = discord.Embed(title="📿 ذكر وتذكير تلقائي", description=f"**{chosen_zikr}**", color=discord.Color.blue())
                embed.set_footer(text="سبحان الله وبحمده سبحان الله العظيم")
                await channel.send(embed=embed)
            except:
                pass

class CloseTicketConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="تأكيد الإغلاق 🔒", style=discord.ButtonStyle.danger, custom_id="confirm_close_ticket")
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🗑️ جاري حذف تكت الدعم الفني خلال ثوانٍ...", ephemeral=True)
        await interaction.channel.delete()

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التكت 🔒", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = CloseTicketConfirmView()
        await interaction.response.send_message("⚠️ هل أنت متأكد من إغلاق هذا التكت؟", view=view, ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="فتح تكت 🎫", style=discord.ButtonStyle.green, custom_id="open_ticket_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="التكتات")
        if not category:
            try:
                category = await guild.create_category("التكتات")
            except:
                category = None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        channel_name = f"ticket-{interaction.user.name}"
        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        embed = discord.Embed(
            title="🎫 تكت الدعم الفني",
            description=f"مرحباً بك {interaction.user.mention}!\nيرجى كتابة مشكلتك أو استفسارك هنا، وسيقوم فريق الإدارة بالرد عليك قريباً.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ تم فتح التكت بنجاح: {ticket_channel.mention}", ephemeral=True)

@bot.event
async def on_member_join(member):
    log_channel = get_log_channel(member.guild)
    if member.bot:
        try:
            await member.kick(reason="حماية السيرفر: ممنوع دخول بوتات غير مصرح بها.")
            if log_channel:
                await log_channel.send(f"🚨 **تم طرد بوت مشبوه:** {member.mention} محاولة دخول غير مصرح بها.")
        except:
            pass
        return

    if log_channel:
        try:
            embed = discord.Embed(title="📥 دخل عضو جديد", description=f"{member.mention} انضم إلى السيرفر منورنا!", color=discord.Color.green())
            embed.set_thumbnail(url=member.display_avatar.url)
            await log_channel.send(embed=embed)
        except:
            pass

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    user_id = message.author.id
    cursor.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        cursor.execute("INSERT INTO users (user_id, xp, level) VALUES (?, ?, ?)", (user_id, 10, 1))
    else:
        xp, level = result
        xp += 10
        if xp >= level * 100:
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
async def on_raw_message_delete(payload):
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    log_channel = get_log_channel(guild)
    if not log_channel:
        return
    try:
        message = payload.cached_message
        content = message.content if message else "رسالة غير مخزنة"
        embed = discord.Embed(title="🗑️ تم حذف رسالة", color=discord.Color.red())
        embed.add_field(name="الروم", value=f"<#{payload.channel_id}>", inline=True)
        embed.add_field(name="المحتوى", value=content, inline=False)
        await log_channel.send(embed=embed)
    except:
        pass

@bot.event
async def on_member_remove(member):
    log_channel = get_log_channel(member.guild)
    if log_channel:
        try:
            embed = discord.Embed(title="📤 غادر عضو", description=f"{member.mention} خرج من السيرفر.", color=discord.Color.orange())
            await log_channel.send(embed=embed)
        except:
            pass

# --- الأوامر ---

@bot.tree.command(name="join", description="دخول البوت إلى الروم الصوتي الذي أنت فيه")
@discord.app_commands.checks.has_permissions(administrator=True)
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("⚠️ يجب أن تكون متصلاً بروم صوتي أولاً!", ephemeral=True)
        return
    
    # رد فوري لمنع أي خطأ تعليق أو مهلة من ديسكورد
    await interaction.response.send_message("🔄 جاري الاتصال بالروم الصوتي...", ephemeral=True)
    
    voice_channel = interaction.user.voice.channel
    try:
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.move_to(voice_channel)
        else:
            await voice_channel.connect()
        await interaction.edit_original_response(content=f"✅ تم الانضمام بنجاح إلى روم: **{voice_channel.name}**!")
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ خطأ صوتي: {str(e)}")

@bot.tree.command(name="leave", description="إخراج البوت من الروم الصوتي")
@discord.app_commands.checks.has_permissions(administrator=True)
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 تم إخراج البوت من الروم الصوتي.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ البوت غير متصل بأي روم صوتي!", ephemeral=True)

@bot.event
async def on_voice_state_update(member, before, after):
    # حماية تضمن بقاء البوت في الروم الصوتي وعدم خروجه تلقائياً عند خروج الآخرين
    if member.id == bot.user.id:
        if after.channel is None:
            pass

@bot.tree.command(name="setup_tickets", description="إرسال لوحة التكتات")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_tickets(interaction: discord.Interaction):
    embed = discord.Embed(title="🎫 نظام الدعم الفني والتكتات", description="اضغط الزر أدناه لفتح تكت خاص بك.", color=discord.Color.blurple())
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ تم الإرسال!", ephemeral=True)

@bot.tree.command(name="streak", description="سجل حضورك اليومي للحفاظ على الستريك 🔥")
async def streak(interaction: discord.Interaction):
    user_id = interaction.user.id
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT streak, last_streak FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if not result:
        cursor.execute("INSERT INTO users (user_id, streak, last_streak) VALUES (?, 1, ?)", (user_id, today))
        db.commit()
        await interaction.response.send_message(f"🔥 بداية ستريك جديد: **1 يوم**.")
        return
    current_streak, last_streak = result
    if last_streak == today:
        await interaction.response.send_message(f"⏳ لقد سجلت ستريك اليوم مسبقاً! ستريكك: **{current_streak} أيام**", ephemeral=True)
        return
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if last_streak == yesterday:
        current_streak += 1
    else:
        current_streak = 1
    cursor.execute("UPDATE users SET streak = ?, last_streak = ? WHERE user_id = ?", (current_streak, today, user_id))
    db.commit()
    await interaction.response.send_message(f"🔥 ستريكك الحالي: **{current_streak} أيام** متتالية!")

@bot.tree.command(name="profile", description="عرض مستواك ونقاطك")
async def profile(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    cursor.execute("SELECT streak, xp, level FROM users WHERE user_id = ?", (target.id,))
    result = cursor.fetchone()
    streak_val, xp_val, level_val = result if result else (0, 0, 1)
    embed = discord.Embed(title=f"👤 ملف {target.name}", color=discord.Color.gold())
    embed.add_field(name="🔥 الستريك", value=f"{streak_val} يوم", inline=True)
    embed.add_field(name="⭐ المستوى", value=f"{level_val}", inline=True)
    embed.add_field(name="✨ النقاط", value=f"{xp_val} XP", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="azkar", description="إرسال ذكر مبارك")
async def azkar(interaction: discord.Interaction):
    chosen_zikr = random.choice(AZKAR_LIST)
    embed = discord.Embed(title="📿 ذكر وتذكير", description=f"**{chosen_zikr}**", color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clear", description="مسح الرسائل")
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 تم مسح {len(deleted)} رسالة.", ephemeral=True)

token = os.getenv('DISCORD_TOKEN') or os.getenv('TOKEN')
bot.run(token)
