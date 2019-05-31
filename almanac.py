#! /usr/bin/python3

import discord
import uuid
import random
import string
import os

client = discord.Client()
session_dict = {}

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


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    #The bot should never respond to itself!
    if message.author == client.user:
        return

    author = message.author
    content = message.clean_content + ' '
    channel = message.channel
    channel_id = str(channel.id)
    server_id = str(channel.guild.id)
    title = content.split(' ')[1]
    time = str(message.created_at)

    #Default false
    is_recording = False

    #Should we set to true?
    if(channel_id in session_dict):
        is_recording = True

    #Start recording
    if content.startswith('r.start'):
        if(is_recording):
            await channel.send("This channel is already being recorded. Use r.stop to end the recording.")
        else:
            if(title != ''):
                await channel.send("This channel is now being recorded.")
                session = Session(channel_id,title.strip(),time,server_id)
                session_dict[channel_id] = session
            else:
                await channel.send("**Error:** Please include a file name. `r.start <filename>`")


    #Stop recording
    elif content.startswith('r.stop'):
        if(is_recording):
            session = session_dict.get(channel_id)
            await channel.send("Recording saved as: " + session.title)
            session.file.close()
            session_dict.pop(channel_id)
        else:
            await channel.send("The channel is not recording. Use `r.start <name> to start.`")

    #List recordings
    elif content.startswith('r.list'):
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

    #Is recording
    elif content.startswith('r.is_recording'):
        if(is_recording):
            await channel.send("This channel has been recording since: " + time)
        else:
            await channel.send("The channel is not recording.")

    #Download
    elif content.startswith('r.download'):
        try:
            title = message.content.split(' ')[1]
            file_path = 'sessions/' + server_id + '/' + title + '.txt';
            if(os.path.exists(file_path)):
                await channel.send(file=discord.File(file_path))
            else:
                await channel.send("**Error:** No such recording. Use `r.list to view.`")
        except:
            await channel.send("**Error:** Use like: `r.download <name>`")

    #Help
    elif content.startswith('r.help'):
        await channel.send("`r.start <title>` to begin recording\n`r.stop` to stop recording\n`r.download <title>` to download recording\n`r.list` to see all recordings\n`r.is_recording` to test for recordings.")




    #Possibly log messages
    else:
        if(is_recording):
            session = session_dict.get(channel_id)
            session.file.write('**' + author.display_name + ":** " + content + '\n')



f = open("token.txt","r")
token = f.read().strip()
client.run(token)
