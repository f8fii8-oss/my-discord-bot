# -*- coding: utf-8 -*-
from flask import Flask
from threading import Thread
import os
import random
import sqlite3
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from collections import defaultdict, deque

app = Flask('')

@app.route('/')
def home():
    return "Ultimate Bot is alive and running!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# --- قاعدة البيانات ---
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

# تفعيل كافة الصلاحيات والـ Intents بقوة مطلقة
intents = discord.Intents.all()

class UltimateBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(TicketView())
        self.add_view(CloseTicketView())
        await self.tree.sync()
        print("تمت مزامنة جميع الأوامر وأنظمة الحماية والتكتات بنجاح!")

    async def on_ready(self):
        print(f"البوت المتكامل شغال الآن باسم {self.user}")

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

user_message_cache = defaultdict(lambda: deque(maxlen=5))
user_deleted_channels = defaultdict(list)

# --- نظام التكتات ---
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


# --- الأحداث والحماية ---

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
    await bot.process_commands(message)

# الحدث المحسن الجبار لحذف الرسائل
@bot.event
async def on_raw_message_delete(payload):
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    
    log_channel = get_log_channel(guild)
    if not log_channel:
        print(f"❌ لم يتم العثور على روم اللوقات بالأيدي 1562238501678878740 في السيرفر: {guild.name}")
        return

    try:
        # محاولة جلب تفاصيل الرسالة المحذوفة من الكاش أو الأرشيف
        message = payload.cached_message
        content = message.content if message else "رسالة غير مخزنة (أو تم حذفها مباشرة)"
        author = message.author.mention if message else "عضو (محتوى غير متوفر بالكاش)"

        embed = discord.Embed(title="🗑️ تم حذف رسالة", color=discord.Color.red())
        embed.add_field(name="الروم", value=f"<#{payload.channel_id}>", inline=True)
        embed.add_field(name="المحتوى / التفاصيل", value=content, inline=False)
        await log_channel.send(embed=embed)
        print("✅ تم إرسال لوق الحذف بنجاح عبر النظام المباشر (Raw)!")
    except Exception as e:
        print(f"❌ خطأ في إرسال لوق الحذف: {e}")

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

@bot.tree.command(name="setup_tickets", description="إرسال رسالة التكتات التفاعلية في الروم الحالي")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_tickets(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 نظام الدعم الفني والتكتات",
        description="إذا كانت لديك أي مشكلة أو استفسار، اضغط على الزر أدناه لفتح تكت خاص بك مع الإدارة.",
        color=discord.Color.blurple()
    )
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ تم إرسال لوحة التكتات بنجاح!", ephemeral=True)

@bot.tree.command(name="streak", description="سجل حضورك اليومي للحفاظ على الستريك 🔥")
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
        msg = f"⚠️ انقطع ستريكك! بدأنا عداد جديد: **1 يوم**."

    cursor.execute("UPDATE users SET streak = ?, last_streak = ? WHERE user_id = ?", (current_streak, today, user_id))
    db.commit()
    await interaction.response.send_message(f"{interaction.user.mention} {msg}")

@bot.tree.command(name="azkar", description="إرسال ذكر أو دعاء مبارك")
async def azkar(interaction: discord.Interaction):
    chosen_zikr = random.choice(AZKAR_LIST)
    embed = discord.Embed(title="📿 ذكر وتذكير", description=f"**{chosen_zikr}**", color=discord.Color.blue())
    embed.set_footer(text=f"بواسطة: {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clear", description="مسح عدد محدد من الرسائل")
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 تم مسح {len(deleted)} رسالة بنجاح.", ephemeral=True)

token = os.getenv('DISCORD_TOKEN') or os.getenv('TOKEN')
bot.run(token)
