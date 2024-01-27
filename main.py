import csv
import os
import json
import requests
import subprocess
import re

import discord
from discord.ext import commands
from dotenv import load_dotenv

CURRENT_FOLDER = os.path.dirname(os.path.realpath(__file__))
load_dotenv(os.path.join(CURRENT_FOLDER, '.env'))
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
SERVER_IP = os.getenv('SERVER_IP')
SERVER_FOLDER = os.getenv('SERVER_FOLDER')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX')
SERVER_FILE = os.getenv('SERVER_FILE')
FLASH_MEMORY = os.getenv('FLASH_MEMORY')


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    # print(f'{bot.user} is connected to {guild.name}(id: {guild.id})')
    # print([member.name for member in guild.members])


######################## COMMANDS ########################
@bot.command(name='hello', help='Responds with a hello message')
async def hello(ctx):
    await ctx.send('Hello!')


@bot.command(name='change-prefix', help='Change the command prefix')
@commands.has_permissions(administrator=True)
async def changePrefix(ctx, newPrefix):
    if newPrefix:
        with open('.env', 'r') as env_file:
            lines = env_file.readlines()
        with open('.env', 'w') as env_file:
            for line in lines:
                if line.startswith('COMMAND_PREFIX='):
                    env_file.write(f'COMMAND_PREFIX={newPrefix}\n')
                else:
                    env_file.write(line)
        load_dotenv()
        bot.command_prefix = newPrefix
        await ctx.send(f'Command prefix changed to: `{newPrefix}`')
    else:
        await ctx.send('Please provide a new prefix.')


@bot.command(name='start-server', help='Starts the MC Server.')
@commands.has_permissions(administrator=True)
async def startMinecraftServer(ctx):
    arguments = [SERVER_FOLDER, SERVER_FILE, FLASH_MEMORY]
    statusBashScript = os.path.join(CURRENT_FOLDER, 'scripts/mcStatus.sh')
    print(os.path.exists(statusBashScript))
    returnCode = subprocess.run(['/bin/bash', statusBashScript] + arguments).returncode
    if returnCode == 0:
        embed = discord.Embed(title='Server Status', description='Server already running.', color=0x00ff00)
        await ctx.send(embed=embed)
    elif returnCode == 1:
        embed = discord.Embed(title='Server Status', description='Server starting.', color=0x00ff00)
        await ctx.send(embed=embed)
        startBashScript = os.path.join(CURRENT_FOLDER, 'scripts/mcStart.sh')
        subprocess.Popen(['/bin/bash', startBashScript] + arguments)
    else:
        embed = discord.Embed(title='Server Status', description='Status Error.', color=0x00ff00)
        await ctx.send(embed=embed)


@bot.command(name='stop-server', help='Stops the MC Server.')
@commands.has_permissions(administrator=True)
async def stopMinecraftServer(ctx):
    # Checking if server is running
    arguments = [SERVER_FOLDER, SERVER_FILE, FLASH_MEMORY]
    statusBashScript = os.path.join(CURRENT_FOLDER, 'scripts/mcStatus.sh')
    returnCode = subprocess.run(['/bin/bash', statusBashScript] + arguments).returncode
    if returnCode == 0:
        embed = discord.Embed(title='Server Status', description='Server shutting down.', color=0x00ff00)
        await ctx.send(embed=embed)
        stopBashScript = os.path.join(CURRENT_FOLDER, 'scripts/mcStop.sh')
        subprocess.run([stopBashScript] + arguments)
    elif returnCode == 1:
        embed = discord.Embed(title='Server Status', description='Server is not running.', color=0x00ff00)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title='Server Status', description='Status Error.', color=0x00ff00)
        await ctx.send(embed=embed)


@bot.command(name='reset-server', help='Resets the MC Server.')
@commands.has_permissions(administrator=True)
async def resetMinecraftServer(ctx):
    # Checking if server is running
    arguments = [SERVER_FOLDER, SERVER_FILE, FLASH_MEMORY]
    statusBashScript = os.path.join(CURRENT_FOLDER, 'scripts/mcStatus.sh')
    returnCode = subprocess.run(['/bin/bash', statusBashScript] + arguments).returncode
    if returnCode == 0:
        embed = discord.Embed(title='Server Status', description='Server Resetting.', color=0x00ff00)
        await ctx.send(embed=embed)
        stopBashScript = os.path.join(CURRENT_FOLDER, 'scripts/mcStop.sh')
        subprocess.run([stopBashScript] + arguments)
    elif returnCode == 1:
        embed = discord.Embed(title='Server Status', description='Server is not running.', color=0x00ff00)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title='Server Status', description='Status Error.', color=0x00ff00)
        await ctx.send(embed=embed)


@bot.command(name='status', help='Checks if the server is running.')
async def checkStatus(ctx):
    # Checking if server is running
    arguments = [SERVER_FOLDER, SERVER_FILE, FLASH_MEMORY]
    statusBashScript = os.path.join(CURRENT_FOLDER, 'scripts/mcStatus.sh')
    returnCode = subprocess.run(['/bin/bash', statusBashScript] + arguments).returncode
    if returnCode == 0:
        embed = discord.Embed(title='Server Status', description='Server is running.', color=0x00ff00)
        await ctx.send(embed=embed)
    elif returnCode == 1:
        embed = discord.Embed(title='Server Status', description='Server is not running.', color=0x00ff00)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title='Server Status', description='Status Error.', color=0x00ff00)
        await ctx.send(embed=embed)


@bot.command(name='ip', help='Gives the server\'s IP address.')
async def giveServerIp(ctx):
    embed = discord.Embed(title='Server IP Address', description=f'The server\'s IP is: {SERVER_IP}', color=0x00ff00)
    await ctx.send(embed=embed)


@bot.command(name='seed', help='Gives the server\'s world seed.')
async def giveWorldSeed(ctx):
    worldSeed = None
    with open(os.path.join(SERVER_FOLDER, 'server.properties'), 'r') as file:
        for line in file.readlines():
            if line.startswith('level-seed='):
                seedLine = line.replace('\n', '')
                worldSeed = seedLine.split('=')[1]
    embed = discord.Embed(title='World Seed', description=f'The server\'s world seed is: {worldSeed}', color=0x00ff00)
    if worldSeed is not None:
        chunkBaseLink = f'https://www.chunkbase.com/apps/seed-map#{worldSeed}'
        embed.add_field(name='ChunkBase Link', value=chunkBaseLink)
    await ctx.send(embed=embed)


@bot.command(name='online', help='Give the number of online players.')
async def nbOnline(ctx):
    arguments = [SERVER_FOLDER, SERVER_FILE, FLASH_MEMORY]
    statusBashScript = os.path.join(CURRENT_FOLDER, 'scripts/mcStatus.sh')
    returnCode = subprocess.run(['/bin/bash', statusBashScript] + arguments).returncode
    if returnCode == 0:
        latestLogFilePath = os.path.join(SERVER_FOLDER, 'logs/latest.log')
        nbPlayers, _ = getPlayersOnlineFromLogs(latestLogFilePath)
        maxNbPlayers = 0
        with open(os.path.join(SERVER_FOLDER, 'server.properties'), 'r') as file:
            for line in file.readlines():
                if line.startswith('max-players='):
                    maxNbPlayers = line.split('=')[1]
        embed = discord.Embed(title='Player Count', description=f'{nbPlayers}/{maxNbPlayers}', color=0x00ff00)
        await ctx.send(embed=embed)
    elif returnCode == 1:
        embed = discord.Embed(title='Player Count', description='Server is not running.', color=0x00ff00)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title='Player Count', description='Status Error.', color=0x00ff00)
        await ctx.send(embed=embed)


@bot.command(name='online-players', help='List the players currently online.')
async def onlinePlayers(ctx):
    arguments = [SERVER_FOLDER, SERVER_FILE, FLASH_MEMORY]
    statusBashScript = os.path.join(CURRENT_FOLDER, 'scripts/mcStatus.sh')
    returnCode = subprocess.run(['/bin/bash', statusBashScript] + arguments).returncode
    if returnCode == 0:
        latestLogFilePath = os.path.join(SERVER_FOLDER, 'logs/latest.log')
        _, playersOnline = getPlayersOnlineFromLogs(latestLogFilePath)
        if playersOnline:
            playersList = "\n".join(f"• {player}" for player in playersOnline)
            embed = discord.Embed(title='Players Online', description=playersList, color=0x00ff00)
        else:
            embed = discord.Embed(title='Players Online', description='No players online.', color=0x00ff00)
        await ctx.send(embed=embed)
    elif returnCode == 1:
        embed = discord.Embed(title='Players Online', description='Server is not running.', color=0x00ff00)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title='Players Online', description='Status Error.', color=0x00ff00)
        await ctx.send(embed=embed)


@bot.command(name='username', help='Lets the user give their MC username.')
async def changeUsername(ctx, userName):
    senderId, guildId = ctx.author.id, ctx.guild.id
    playerUuid = getUuidFromUsername(userName)
    if playerUuid is None:
        await ctx.send(f'{userName} is not recognized as a MC username')
        return
    dataFolder = os.path.join(CURRENT_FOLDER, 'data')
    if not os.path.exists(dataFolder):
        os.mkdir(dataFolder)
    usernamesFile = os.path.join(dataFolder, 'usernames.csv')
    if not os.path.exists(usernamesFile):
        with open(usernamesFile, 'w', newline='') as csvfile:
            fieldnames = ['user_id', 'guild_id', 'mc_uuid']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    with open(usernamesFile, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        userExists = any(row['user_id'] == str(senderId) for row in rows)
    with open(usernamesFile, 'w', newline='') as csvfile:
        fieldnames = ['user_id', 'guild_id', 'mc_uuid']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            if row['user_id'] == str(senderId):
                row['mc_uuid'] = playerUuid
            writer.writerow(row)
        if not userExists:
            writer.writerow({'user_id': str(senderId), 'guild_id': str(guildId), 'mc_uuid': playerUuid})
    await ctx.send(f'You are now registered as {userName}')


@bot.command(name='stats', help='Gives the player\'s stats.')
async def givePlayerStats(ctx):
    userIds, mcUuids = retrieveUuids()
    if ctx.author.id in userIds:
        with open(os.path.join(SERVER_FOLDER, 'server.properties'), 'r') as file:
            for line in file.readlines():
                if line.startswith('level-name='):
                    levelLine = line.replace('\n', '')
                    levelName = levelLine.split('=')[1]
        levelStatsFolderPath = os.path.join(SERVER_FOLDER, f'{levelName}/stats')
        playerStats = retrievePlayerStats(levelStatsFolderPath, mcUuids[userIds.index(ctx.author.id)])
        if playerStats is None:
            await ctx.send(f'You have not yet joined the server')
        else:
            embed = discord.Embed(title=f"Stats for {playerStats['NAME']}", color=0x00ff00)
            embed.add_field(name='Deaths', value=playerStats['DEATHS'])
            embed.add_field(name='Mobs Killed', value=playerStats['MOB_KILLS'])
            embed.add_field(name='Players Killed', value=playerStats['PLAYER_KILLS'])
            embed.add_field(name='Damage Taken', value=playerStats['DAMAGE_TAKEN'])
            embed.add_field(name='Damage Dealt', value=playerStats['DAMAGE_DEALT'])
            embed.add_field(name='Total Play Time', value=playerStats['PLAY_TIME'])
            embed.add_field(name='Total Time Opened', value=playerStats['WORLD_TIME'])
            embed.add_field(name='Total Since Last Death', value=playerStats['LAST_DEATH'])
            embed.add_field(name='Distance Walked', value=playerStats['WALK_DISTANCE'])
            embed.add_field(name='Distance Swum', value=playerStats['SWIM_DISTANCE'])
            embed.add_field(name='Distance Fallen', value=playerStats['FALL_DISTANCE'])
            embed.add_field(name='Distance by Boat', value=playerStats['BOAT_DISTANCE'])
            embed.add_field(name='Distance by Elytra', value=playerStats['ELYTRA_DISTANCE'])
            embed.add_field(name='Distance by Horse', value=playerStats['HORSE_DISTANCE'])
            embed.add_field(name='Distance by Minecart', value=playerStats['MINECART_DISTANCE'])
            await ctx.author.send(embed=embed)
    else:
        await ctx.send(f'You have not registered your MC username.')


@bot.command(name='flush-usernames', help='Destroys all usernames.')
@commands.has_permissions(administrator=True)
async def flushUsernames(ctx):
    dataFolder = os.path.join(CURRENT_FOLDER, 'data')
    usernamesFile = os.path.join(dataFolder, 'usernames.csv')
    if os.path.exists(usernamesFile):
        with open(usernamesFile, 'w', newline='') as csvfile:
            fieldnames = ['user_id', 'guild_id', 'mc_usernames']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        await ctx.send(f'Flushed all usernames in database.')
    else:
        if not os.path.exists(dataFolder):
            os.mkdir(dataFolder)
        if not os.path.exists(usernamesFile):
            with open(usernamesFile, 'w', newline='') as csvfile:
                fieldnames = ['user_id', 'guild_id', 'mc_usernames']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
        await ctx.send(f'No usernames in database.')


######################## FUNCTIONS ########################
def getPlayersOnlineFromLogs(logFilePath):
    try:
        with open(logFilePath, 'r') as log_file:
            lines = log_file.readlines()
            joinPattern = re.compile(r"\[Server thread/INFO\]: (\w+) joined the game")
            leavePattern = re.compile(r"\[Server thread/INFO\]: (\w+) left the game")
            players = set()
            for line in lines:
                joinMatch = joinPattern.search(line)
                leaveMatch = leavePattern.search(line)
                if joinMatch:
                    playerName = joinMatch.group(1)
                    players.add(playerName)
                elif leaveMatch:
                    playerName = leaveMatch.group(1)
                    if playerName in players:
                        players.remove(playerName)
            nbPlayersOnline = len(players)
            return nbPlayersOnline, players
    except FileNotFoundError:
        print(f"Log file not found: {logFilePath}")
        return None
    except Exception as e:
        print(f"Error reading log file: {e}")
        return None


def getUsernameFromUuid(playerUuid):
    playerUuid = playerUuid.replace('-', '')
    apiUrl = f'https://sessionserver.mojang.com/session/minecraft/profile/{playerUuid}'
    try:
        response = requests.get(apiUrl)
        if response.status_code == 200:
            data = response.json()
            currentUsername = data['name']
            return currentUsername
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None


def getUuidFromUsername(currentUsername):
    apiUrl = f'https://api.mojang.com/users/profiles/minecraft/{currentUsername}'
    try:
        response = requests.get(apiUrl)
        data = response.json()
        if 'id' in data:
            return data['id']
        else:
            return None
    except requests.RequestException as e:
        print(f"Error fetching UUID: {e}")
        return None


def getMinecraftMost(minecraftDict):
    if minecraftDict is not None:
        mostKey = max(minecraftDict, key=minecraftDict.get).split(':')[1]
        mostKey = mostKey.replace('_', '').capitalize()
        return mostKey
    else:
        return 'N/A'


def retrievePlayerStats(levelStatsFolderPath, mcUuid):
    playerInfo = {}
    for filename in os.listdir(levelStatsFolderPath):
        if filename[:-5].replace('-', '') == mcUuid:
            playerUsername = getUsernameFromUuid(filename[:-5])
            playerInfo['NAME'] = playerUsername
            with open(os.path.join(levelStatsFolderPath, filename), 'r') as file:
                playerStats = json.load(file)
            if playerStats['stats'].get('minecraft:custom', None) is not None:
                # DEATH STATISTICS
                playerInfo['DEATHS'] = playerStats['stats']['minecraft:custom'].get('minecraft:deaths', '0')
                playerInfo['MOB_KILLS'] = playerStats['stats']['minecraft:custom'].get('minecraft:mob_kills', '0')
                playerInfo['PLAYER_KILLS'] = playerStats['stats']['minecraft:custom'].get('minecraft:player_kills', '0')
                playerInfo['DAMAGE_TAKEN'] = playerStats['stats']['minecraft:custom'].get('minecraft:damage_taken', '0')
                playerInfo['DAMAGE_DEALT'] = playerStats['stats']['minecraft:custom'].get('minecraft:damage_dealt', '0')
                # TIME STATISTICS
                playTime = playerStats['stats']['minecraft:custom'].get('minecraft:play_time', 0)
                lastDeath = playerStats['stats']['minecraft:custom'].get('minecraft:time_since_death', 0)
                worldTime = playerStats['stats']['minecraft:custom'].get('minecraft:total_world_time', 0)
                playerInfo['PLAY_TIME'] = formatTimeDifference(int(playTime) / 20)
                playerInfo['WORLD_TIME'] = formatTimeDifference(int(worldTime) / 20)
                playerInfo['LAST_DEATH'] = formatTimeDifference(int(lastDeath) / 20)
                # MOVEMENT STATISTICS
                walkDistance = playerStats['stats']['minecraft:custom'].get('minecraft:walk_one_cm', 0)
                swimDistance = playerStats['stats']['minecraft:custom'].get('minecraft:swim_one_cm', 0)
                fallDistance = playerStats['stats']['minecraft:custom'].get('minecraft:fall_one_cm', 0)
                boatDistance = playerStats['stats']['minecraft:custom'].get('minecraft:boat_one_cm', 0)
                elytraDistance = playerStats['stats']['minecraft:custom'].get('minecraft:aviate_one_cm', 0)
                horseDistance = playerStats['stats']['minecraft:custom'].get('minecraft:horse_one_cm', 0)
                minecartDistance = playerStats['stats']['minecraft:custom'].get('minecraft:minecart_one_cm', 0)
                playerInfo['WALK_DISTANCE'] = formatDistance(int(walkDistance) / 100)
                playerInfo['SWIM_DISTANCE'] = formatDistance(int(swimDistance) / 100)
                playerInfo['FALL_DISTANCE'] = formatDistance(int(fallDistance) / 100)
                playerInfo['BOAT_DISTANCE'] = formatDistance(int(boatDistance) / 100)
                playerInfo['ELYTRA_DISTANCE'] = formatDistance(int(elytraDistance) / 100)
                playerInfo['HORSE_DISTANCE'] = formatDistance(int(horseDistance) / 100)
                playerInfo['MINECART_DISTANCE'] = formatDistance(int(minecartDistance) / 100)
                # "MOST" STATISTICS
                playerInfo['MOST_MINED'] = getMinecraftMost(playerStats['stats'].get('minecraft:mined', None))
                playerInfo['MOST_USED'] = getMinecraftMost(playerStats['stats'].get('minecraft:used', None))
                playerInfo['MOST_CRAFTED'] = getMinecraftMost(playerStats['stats'].get('minecraft:crafted', None))
                playerInfo['MOST_KILLED'] = getMinecraftMost(playerStats['stats'].get('minecraft:killed', None))
                playerInfo['MOST_KILLED_BY'] = getMinecraftMost(playerStats['stats'].get('minecraft:killed_by', None))
            return playerInfo
    return None


def retrieveUuids():
    dataFolder = os.path.join(CURRENT_FOLDER, 'data')
    if not os.path.exists(dataFolder):
        os.mkdir(dataFolder)
    usernamesFile = os.path.join(dataFolder, 'usernames.csv')
    if not os.path.exists(usernamesFile):
        with open(usernamesFile, 'w', newline='') as csvfile:
            fieldnames = ['user_id', 'guild_id', 'mc_usernames']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    with open(usernamesFile, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    return [int(row['user_id']) for row in rows], [row['mc_uuid'] for row in rows]


def formatTimeDifference(seconds):
    years, remainder = divmod(seconds, 31536000)
    months, remainder = divmod(remainder, 2592000)
    days, remainder = divmod(remainder, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    timeString = ""
    if years > 0:
        timeString += f"{int(years)}y, "
    if months > 0:
        timeString += f"{int(months)}m, "
    if days > 0:
        timeString += f"{int(days)}d, "
    if hours > 0:
        timeString += f"{int(hours)}h, "
    if minutes > 0:
        timeString += f"{int(minutes)}min, "
    timeString += f"{int(seconds)}s"
    return timeString


def formatDistance(meters):
    if meters >= 1000:
        distance_kilometers = meters / 1000
        return f"{distance_kilometers:.2f} km"
    else:
        return f"{meters} m"


def formatPlayerInfo(playerInfo):
    formattedInfo = []
    for key, value in playerInfo.items():
        formattedInfo.append(f"**{key}:** {value}")
    return '\n'.join(formattedInfo)


bot.run(TOKEN)
