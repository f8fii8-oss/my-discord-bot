# -*- coding: utf-8 -*-
from flask import Flask
from threading import Thread
import os
import random
import sqlite3
from datetime import datetime, timedelta
import discord
from discord.ext import commands, tasks

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

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="تحقق / Verification 🟢", style=discord.ButtonStyle.green, custom_id="verify_button_persistent")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ⚠️ ضع اسم الرول الذي تريد إعطاءه للعضو هنا بالضبط
        ROLE_NAME = "عضو"  # يمكنك تغيير كلمة "عضو" باسم الرول لديك في السيرفر

        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=ROLE_NAME)

        if not role:
            # إذا لم يجد الرول بالاسم، يحاول إعطائه رول verified أو ينبه الأدمن
            role = discord.utils.get(guild.roles, name="Verified")

        if role:
            if role in interaction.user.roles:
                await interaction.response.send_message("⚠️ أنت متحقق بالفعل ولديك الرول مسبقاً!", ephemeral=True)
            else:
                try:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message(f"✅ تم التحقق بنجاح! تم منحك رول **{role.name}**.", ephemeral=True)
                except discord.Forbidden:
                    await interaction.response.send_message("❌ البوت لا يملك صلاحية إعطائك هذا الرول (تأكد أن رول البوت أعلى من رول الأعضاء).", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ لم يتم العثور على رول باسم **{ROLE_NAME}** في السيرفر! يرجى إنشاؤه وتعديل اسمه في الكود.", ephemeral=True)

class UltimateBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(TicketView())
        self.add_view(CloseTicketView())
        self.add_view(VerifyView())  # تثبيت زر التحقق لتحديد التفاعل دائماً
        await self.tree.sync()
        print("تمت مزامنة جميع الأوامر وأنظمة الصوت والتكتات والتحقق بنجاح!")

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

# --- أمر التحقق الجديد ---

@bot.tree.command(name="setup_verify", description="إرسال قائمة لوحة التحقق للأعضاء")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_verify(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    embed = discord.Embed(
        title="✅ نظام التحقق / Verification System",
        description="مرحباً بك في السيرفر! اضغط على الزر أدناه لإتمام التحقق والحصول على رول الدخول والتفاعل مع بقية الرومات.",
        color=discord.Color.green()
    )
    embed.set_footer(text="أهلاً وسهلاً بك في سيرفرنا 🌹")
    
    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.followup.send("✅ تم إرسال لوحة التحقق في هذا الروم بنجاح!", ephemeral=True)

# --- أوامر الصوت والأغاني والـ AFK ---

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

@bot.tree.command(name="join", description="دخول البوت إلى الروم الصوتي وتثبيته كـ AFK")
@discord.app_commands.checks.has_permissions(administrator=True)
async def join(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.voice:
        await interaction.followup.send("⚠️ يجب أن تكون متصلاً بروم صوتي أولاً!", ephemeral=True)
        return
    
    voice_channel = interaction.user.voice.channel
    try:
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.move_to(voice_channel)
        else:
            await voice_channel.connect()
        await interaction.followup.send(f"✅ تم الانضمام وثبات البوت في روم: **{voice_channel.name}**!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ خطأ صوتي: {str(e)}", ephemeral=True)

@bot.tree.command(name="play", description="تشغيل رابط صوتي مباشر (MP3 أو راديو)")
async def play(interaction: discord.Interaction, url: str):
    await interaction.response.defer(ephemeral=False)

    if not interaction.user.voice:
        await interaction.followup.send("⚠️ يجب أن تكون متصلاً بروم صوتي أولاً!", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel

    if not interaction.guild.voice_client:
        try:
            await voice_channel.connect()
        except:
            pass

    voice_client = interaction.guild.voice_client

    try:
        if voice_client.is_playing():
            voice_client.stop()

        source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
        voice_client.play(source)
        
        await interaction.followup.send(f"بدء تشغيل : **رابط صوتي مباشر**\n, بواسطة : {interaction.user.mention}.")
    except Exception as e:
        await interaction.followup.send(f"❌ حدث خطأ أثناء تشغيل الرابط: تأكد أنه رابط صوتي مباشر (MP3).")

@bot.tree.command(name="stop", description="إيقاف الصوت وإبقاء البوت بالروم كـ AFK")
@discord.app_commands.checks.has_permissions(administrator=True)
async def stop(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await interaction.followup.send("⏹️ تم إيقاف الصوت، وبقي البوت في الروم كـ AFK.", ephemeral=True)
    else:
        await interaction.followup.send("⚠️ لا يوجد شيء يتم تشغيله حالياً.",
