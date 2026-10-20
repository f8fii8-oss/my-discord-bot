import os
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask

app = Flask('')


@app.route('/')
def home():
  return 'I am alive!'


def run():
  app.run(host='0.0.0.0', port=8080)


def keep_alive():
  t = Thread(target=run)
  t.start()


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
  print(f'Logged in as {bot.user.name}')


@bot.command()
async def hello(ctx):
  await ctx.send('Hello!')


keep_alive()

bot.run('MTU2MjExOTkyMDQ5MjIyMDUxOA.GdYjG-.NS1Pu1Xjdv9Jv9KWbsvOBa6G7HfD5HCtlWnRa8')
