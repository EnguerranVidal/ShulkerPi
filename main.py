import os
import random
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
    embed = discord.Embed(title="Prefix Change", color=0x00ff00)
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
    embed = discord.Embed(title="Server Status", color=0x00ff00)
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
async def nbPlayersOnline(ctx):
    arguments = [SERVER_FOLDER, SERVER_FILE, FLASH_MEMORY]
    statusBashScript = os.path.join(CURRENT_FOLDER, 'scripts/mcStatus.sh')
    returnCode = subprocess.run(['/bin/bash', statusBashScript] + arguments).returncode
    if returnCode == 0:
        latestLogFilePath = os.path.join(SERVER_FOLDER, 'logs/latest.log')
        nbPlayers, _ = getPlayersOnlineFromLogs(latestLogFilePath)
        max_nb_players = 0
        with open(os.path.join(SERVER_FOLDER, 'server.properties'), 'r') as file:
            for line in file.readlines():
                if line.startswith('max-players='):
                    max_nb_players = line.split('=')[1]
        embed = discord.Embed(title='Server IP', description=f'{nbPlayers}/{max_nb_players}', color=0x00ff00)
        await ctx.send(embed=embed)
    elif returnCode == 1:
        embed = discord.Embed(title='Server Status', description='Server is not running.', color=0x00ff00)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title='Server Status', description='Status Error.', color=0x00ff00)
        await ctx.send(embed=embed)


######################## FUNCTIONS ########################
def getPlayersOnlineFromLogs(logFilePath):
    try:
        with open(logFilePath, 'r') as log_file:
            lines = log_file.readlines()[-50:]
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
            nbOnline = len(players)
            return nbOnline, players
    except FileNotFoundError:
        print(f"Log file not found: {logFilePath}")
        return None
    except Exception as e:
        print(f"Error reading log file: {e}")
        return None


bot.run(TOKEN)
