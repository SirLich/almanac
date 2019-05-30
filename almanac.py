#! /usr/bin/python3

import discord
import subprocess
from subprocess import check_output
import time
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    #The bot should never respond to itself!
    if message.author == client.user:
        return

    if message.guild.me in message.mentions:
        sentence = message.content.replace("<@418271589356797952>","")
        await message.channel.send(sentence)

f = open("token.txt","r")
token = f.read().strip()
client.run(token)
