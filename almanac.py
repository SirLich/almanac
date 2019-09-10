#! /usr/bin/python3

import discord
from discord.ext import commands
import uuid
import random
import string
import os
import shutil

session_dict = {}
DEBUG_MODE = True
TOKEN = "test_token.txt"
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
    return ctx.channel.id in session_dict

async def is_not_recording(ctx):
    return ctx.channel.id not in session_dict

# START
@bot.command()
@commands.check(is_not_recording)
async def start(ctx, *, recording_name):
    channel = ctx.channel
    channel_id = str(channel.id)
    server_id = str(ctx.message.channel.guild.id)
    time = str(ctx.message.created_at)

    session = Session(channel_id,recording_name,time,server_id)
    session_dict[channel_id] = session

    await channel.send("`Recording started...`")

#START ERROR
@start.error
async def start_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a recording title: `r.start <title>`")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("The channel is already recording")
    else:
        await ctx.send("The command ran into a problem")


#STOP
@bot.command()
@commands.check(is_not_recording)
async def stop(ctx):
    channel = ctx.channel
    channel_id = str(channel.id)

    session = session_dict.get(channel_id)
    session.file.close()
    session_dict.pop(channel_id)

    await channel.send("Recording saved as: " + session.title)


#STOP ERROR
@stop.error
async def stop_error(ctx, error):
    print(error)
    if isinstance(error, commands.CheckFailure):
        await ctx.send("The channel is not recording")
    else:
        await ctx.send("That command ran into a problem")


#LIST
@bot.command()
async def list(ctx):
    channel = ctx.channel
    server_id = str(channel.guild.id)

    m = ""
    file_path = 'sessions/' + server_id
    if(os.path.exists(file_path)):
        num = 1
        for file_name in os.listdir(file_path):
            with open('sessions/' + server_id + '/' + file_name, 'r') as f:
                first_line = f.readline()
                m = m + str(num) + ': ' + first_line
            num += 1
        await channel.send(m)
    else:
        await channel.send("Make some recordings first!")


#LIST ERROR
@list.error
async def list_error(ctx, error):
    print(error)
    await ctx.send("An error occured in this command.")

#CHAPTER
@bot.command()
@commands.check(is_not_recording)
async def chapter(ctx, *, chapter_title):
    channel_id = str(ctx.message.channel.id)

    await message.add_reaction("\U0001f44d")
    session = session_dict.get(channel_id)
    session.file.write('\n\n=-=-=-=-= **' + chapter_title + '** =-=-=-=-=\n')

#CHAPTER ERROR
@chapter.error
async def start_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a chapter title")
    if isinstance(error, commands.CheckFailure):
        await ctx.send("The channel is not recording")
    else:
        await ctx.send("That code ran into a problem")

#IS RECORDING
@bot.command()
async def is_recording(ctx):
    channel = ctx.channel
    channel_id = str(channel.id)

    is_recording = channel_id in session_dict

    if(is_recording):
        await channel.send("This channel is recording")
    else:
        await channel.send("The channel is not recording.")

#RECORDING ERROR
@is_recording.error
async def is_recording_error(ctx, error):
    print(error)
    await ctx.send("An error occured in this command.")

#DOWNLOAD
@bot.command()
async def download(ctx, *, download_title):
    channel = ctx.channel
    server_id = str(channel.guild.id)

    file_path = 'sessions/' + server_id + '/' + download_title + '.txt';
    if(os.path.exists(file_path)):
        await channel.send(file=discord.File(file_path))
    else:
        await channel.send("**Error:** No such recording. Use `r.list to view.`")

#DOWNLOAD ERROR
@download.error
async def download_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a recording to download")
    else:
        await ctx.send("An error has occured in that command")

#DOWNLOAD_ALL
@bot.command()
async def download_all(ctx):
    channel = ctx.channel
    server_name = channel.guild.name
    server_id = str(channel.guild.id)

    path_to_dir = 'sessions/' + server_id
    shutil.make_archive(server_name, 'zip', path_to_dir)

    await ctx.send(file=discord.File(server_name + '.zip'))
    os.remove(server_name + '.zip')

#Download ALL error
@download_all.error
async def download_all_error(ctx, error):
    print(error)
    await ctx.send("An error occured in this command.")

#DELETE
@bot.command()
async def delete(ctx, *, recording_title):
    channel = ctx.channel
    server_id = str(channel.guild.id)

    file_path = 'sessions/' + server_id + '/' + recording_title + '.txt'
    if os.path.exists(file_path):
        os.remove(file_path)
        await channel.send("Recording deleted")
    else:
        print(file_path)
        await channel.send("That recording doesn't exist!")

#DELETE ERROR
@delete.error
async def delete_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a recording to delete")
    else:
        await ctx.send("An error occured in this command.")

#CODE
@bot.command(aliases=['github','website'])
async def code(ctx):
    await ctx.channel.send("https://github.com/SirLich/almanac")

def roll_result():
    return random.randint(-1,1)

def get_emoji(r):
    if(r == -1):
        return ':heavy_minus_sign:'
    elif(r == 0):
        return ':black_large_square:'
    else:
        return ':heavy_plus_sign:'

#Roll!
@bot.command(aliases=['roll'])
async def draw(ctx, roll):
    m = "**" + ctx.message.author.display_name + '**: '
    print(roll)
    r = int(roll)
    total = 0
    for i in range(r):
        result = roll_result()
        total += result
        m += get_emoji(result) + " "

    m += ':small_orange_diamond: Result: ' + str(total)
    await ctx.channel.send(m)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):

    author = message.author
    content = message.clean_content
    channel = message.channel
    channel_id = str(channel.id)
    server_id = str(channel.guild.id)
    time = str(message.created_at)

    #The bot should never respond to itself!
    if message.author == bot.user:
        return

    #Ignore .messages and space messages
    if content.startswith('.'):
        return

    #Default false
    is_recording = channel_id in session_dict

    #Possibly log messages
    if(is_recording and not message.content.startswith('r.')):
        session = session_dict.get(channel_id)
        session.file.write('**' + author.display_name + ":** " + content + '\n\n')
    else:
        await bot.process_commands(message)



f = open(TOKEN,"r")
token = f.read().strip()
bot.run(token)
