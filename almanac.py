#! /usr/bin/python3

import discord
from discord.ext import commands
import uuid
import random
import string
import os

client = discord.Client()
session_dict = {}
DEBUG_MODE = True
bot = commands.Bot(command_prefix='r.')

def debug(m):
    if DEBUG_MODE:
        print(m)

class Session:
    def __init__(self, channel_id, title, start_time, server_id):
        self.server_id = server_id
        self.channel_id = channel_id
        self.title = title
        self.start_time = start_time

        #Create directory if it doesn't exist
        if not os.path.exists('sessions/' + server_id):
            os.mkdir('sessions/' + server_id)
        self.file = open('sessions/' + server_id + '/' + title + '.txt', 'w+')

        #Write title and date
        self.file.write(self.title + '\n')
        self.file.write(self.start_time + '\n')

async def is_recording(ctx):
    return ctx.message.channel.id in session_dict

async def is_not_recording(ctx):
    return not is_recording

# START
@bot.command()
@commands.check(is_not_recording)
async def start(ctx, *, recording_name):
    channel_id = str(ctx.message.channel.id)
    server_id = str(ctx.message.channel.guild.id)
    time = str(ctx.message.created_at)

    session = Session(channel_id,arg,time,server_id)
    session_dict[channel_id] = session

    await channel.send("This channel is now being recorded.")

#START ERROR
@start.error
async def start_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a title")
    if isinstance(error, commands.CheckFailure):
        await ctx.send("The channel is already recording")

#STOP
@bot.command()
@commands.check(is_recording)
async def stop(ctx):
    channel_id = str(ctx.message.channel.id)

    session = session_dict.get(channel_id)
    session.file.close()
    session_dict.pop(channel_id)

    await channel.send("Recording saved as: " + session.title)


#STOP ERROR
@stop.error
async def stop_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("The channel is not recording")


#LIST
@bot.command()
async def list(ctx):
    server_id = str(ctx.message.channel.guild.id)

    m = ""
    file_path = 'sessions/' + server_id
    if(os.path.exists(file_path)):
        for file_name in os.listdir(file_path):
            with open('sessions/' + server_id + '/' + file_name, 'r') as f:
                first_line = f.readline()
                m = m + first_line
        await channel.send(m)
    else:
        await channel.send("Make some recordings first!")


#LIST ERROR
@list.error
async def list_error(ctx, error):
    await ctx.send("An error occured in this command.")

#CHAPTER
@bot.command()
@commands.check(is_recording)
async def chapter(ctx, *, chapter_title):
    channel_id = str(ctx.message.channel.id)

    await message.add_reaction("\U0001f44d")
    session = session_dict.get(channel_id)
    session.file.write('\n\n=-=-=-=-= **' + chapter_title + '** =-=-=-=-=\n')

#CHAPTER ERROR
@start.error
async def start_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a chapter title")
    if isinstance(error, commands.CheckFailure):
        await ctx.send("The channel is not recording")

#IS RECORDING
@bot.command()
async def is_recording(ctx):
    channel_id = str(ctx.message.channel.id)
    is_recording = session_dict.has_key(channel_id)

    if(is_recording):
        await channel.send("This channel is recording")
    else:
        await channel.send("The channel is not recording.")

#RECORDING ERROR
@is_recording.error
async def is_recording_error(ctx, error):
    await ctx.send("An error occured in this command.")

#DOWNLOAD
@bot.command()
async def download(ctx, *, download_title):
    server_id = str(ctx.message.channel.guild.id)

    file_path = 'sessions/' + server_id + '/' + arg + '.txt';
    if(os.path.exists(file_path)):
        await channel.send(file=discord.File(file_path))
    else:
        await channel.send("**Error:** No such recording. Use `r.list to view.`")

#DOWNLOAD ERROR
@download.error
async def download_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a recording to download")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    author = message.author
    content = message.clean_content
    channel = message.channel
    channel_id = str(channel.id)
    server_id = str(channel.guild.id)
    time = str(message.created_at)

    #The bot should never respond to itself!
    if message.author == client.user:
        return

    #Ignore .messages and space messages
    if content.startswith('.'):
        return

    #Default false
    is_recording = channel_id in session_dict

    #Possibly log messages
    if(is_recording):
        session = session_dict.get(channel_id)
        session.file.write('**' + author.display_name + ":** " + content + '\n\n')
    else:
        await bot.process_commands(message)



f = open("token.txt","r")
token = f.read().strip()
client.run(token)
