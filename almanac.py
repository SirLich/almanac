#! /usr/bin/python3

import discord
import uuid
client = discord.Client()
session_dict = {}

class Session:
    def __init__(self, channel_id, title, start_time):
        self.channel_id = channel_id
        self.title = title
        self.start_time = start_time
        self.file = open('sessions/' + title + '.txt', 'w+')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    #The bot should never respond to itself!
    if message.author == client.user:
        return

    author = message.author
    content = message.content
    channel = message.channel
    channel_id = channel.id
    title = content.replace('!startrecording ','').replace('!stoprecording ','').replace('!isrecording ','')
    time = str(message.created_at)

    #Default false
    is_recording = False

    #Should we set to true?
    if(channel_id in session_dict):
        is_recording = True

    #Start recording
    if content.startswith('!startrecording'):
        if(is_recording):
            await channel.send("You are already recording in this channel. Use !stoprecording to stop.")
        else:
            await channel.send("You have begun recording!")
            session = Session(channel_id,title,time)
            session_dict[channel_id] = session

    #Stop recording
    elif content.startswith('!stoprecording'):
        if(is_recording):
            await channel.send("Recording stopped at:" + time)
            session = session_dict.get(channel_id)
            session.file.close()
            session_dict.pop(channel_id)
        else:
            await channel.send("The channel is not recording. Use !startrecording to start.")

    #Is currently recording
    elif content.startswith('!isrecording'):
        if(is_recording):
            await channel.send("This channel has been recording since:" + time)
        else:
            await channel.send("The channel is not recording.")

    else:
        session = session_dict.get(channel_id)
        session.file.write(content + '\n')



f = open("token.txt","r")
token = f.read().strip()
client.run(token)
