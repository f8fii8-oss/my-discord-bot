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

class UltimateBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(TicketView())
        self.add_view(CloseTicketView())
        self.add_view(VerifyView())
        await self.tree.sync()
        print("تمت مزامنة جميع الأوامر والتحقق بنجاح!")

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

# --- نظام التحقق (Verification System) ---

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="تحقق 🟢", style=discord.ButtonStyle.green, custom_id="verify_member_btn")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name="عضو")
        
        if not role:
            await interaction.followup.send("⚠️ لم يتم العثور على رول باسم **عضو** في السيرفر! تأكد من إنشائها بضبط الرتب.", ephemeral=True)
            return

        try:
            if role in interaction.user.roles:
                await interaction.followup.send("✅ أنت موثق ومستلم للرتبة بالأساس!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.followup.send(f"🎉 تم التحقق بنجاح! وتم منحك رتبة **{role.name}**.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ حدث خطأ أثناء إعطاء الرتبة: تأكد أن رتبة البوت أعلا من رتبة **عضو** في إعدادات السيرفر.", ephemeral=True)

@bot.tree.command(name="setup_verify", description="إرسال لوحة التحقق إدارياً")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_verify(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="🔒 نظام التحقق",
        description="مرحباً بك في السيرفر! يرجى الضغط على زر التحقق أدناه للحصول على الرول والدخول إلى باقي رومات السيرفر.\n\nنتمنى لك وقتاً ممتعاً معنا!",
        color=discord.Color.green()
    )
    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.followup.send("✅ تم إرسال لوحة التحقق في هذا الروم بنجاح!", ephemeral=True)

# أمر إضافي بالبادئة العادية لتجربة مضمونة وبديلة
@bot.command(name="setup_verify")
@commands.has_permissions(administrator=True)
async def setup_verify_prefix(ctx):
    embed = discord.Embed(
        title="🔒 نظام التحقق",
        description="مرحباً بك في السيرفر! يرجى الضغط على زر التحقق أدناه للحصول على الرول والدخول إلى باقي رومات السيرفر.\n\nنتمنى لك وقتاً ممتعاً معنا!",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=VerifyView())
    try:
        await ctx.message.delete()
    except:
        pass

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
