import os
import json
import discord
import asyncio
import subprocess
from discord.ext import commands, tasks
from dotenv import load_dotenv
from mcstatus import JavaServer

from utilities import *


class ShulkerCommands(commands.Cog):
    def __init__(self, shulkerBot, botConfig, botFolder):
        self.bot = shulkerBot
        self.config = botConfig
        self.botFolder = botFolder
        self.serverIsRunning = False
        self.token = botConfig['DISCORD_TOKEN']
        self.owner = botConfig['BOT_OWNER']
        self.users = [int(uid.strip()) for uid in os.getenv('ALLOWED_USERS', '').split(',') if uid.strip().isdigit()]
        self.serverIp = botConfig['SERVER_IP']
        self.serverFolder = botConfig['SERVER_FOLDER']
        self.serverFile = botConfig['SERVER_FILE']
        self.flashMemory = botConfig['FLASH_MEMORY']

    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f"Hello, {ctx.author.name}!")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot is ready. Logged in as {self.bot.user}')
        self.updateStatus.start()
        await self.updateStatus()
        try:
            ownerUser = await self.bot.fetch_user(self.owner)
            if ownerUser:
                await ownerUser.send(f"✅ **{self.bot.user.name}** is now online and ready.")
        except Exception as e:
            print(f"⚠️ Failed to send DM to owner: {e}")

    def isBotOwnerOrAllowed(self):
        def predicate(ctx):
            return ctx.author.id == self.owner or ctx.author.id in self.users
        return commands.check(predicate)

    def isBotOwner(self):
        def predicate(ctx):
            return ctx.author.id == self.owner
        return commands.check(predicate)

    @tasks.loop(seconds=10)
    async def updateStatus(self):
        try:
            server = JavaServer.lookup(self.serverIp)
            _ = await server.async_status()
            activity = discord.Game(name='SERVER 🟢')
        except Exception:
            activity = discord.Game(name='SERVER 🔴')
        await self.bot.change_presence(activity=activity)

    @commands.command(name='ip', help="Gives the server's IP address.")
    async def ip(self, ctx):
        embed = discord.Embed(title='Server IP Address',  description=f'The server\'s IP is: `{self.serverIp}`', color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(name='seed', help="Gives the server's world seed.")
    async def seed(self, ctx):
        worldSeed = None
        propertiesPath = os.path.join(self.serverFolder, 'server.properties')
        print(os.path.exists(propertiesPath), propertiesPath)
        try:
            with open(propertiesPath, 'r') as file:
                for line in file:
                    if line.startswith('level-seed='):
                        worldSeed = line.strip().split('=', 1)[1]
                        break
        except FileNotFoundError:
            await ctx.send(f"⚠️ server.properties file not found in `{self.serverFolder}`.")
            return
        if worldSeed:
            embed = discord.Embed(title='World Seed', description=f"The server's world seed is: `{worldSeed}`", color=0x00ff00)
            chunkBaseLink = f'https://www.chunkbase.com/apps/seed-map#{worldSeed}'
            embed.add_field(name='ChunkBase Link', value=chunkBaseLink)
            await ctx.send(embed=embed)
        else:
            await ctx.send("⚠️ Could not find the world seed in the server properties.")

    @commands.command(name='info', help="Displays server MOTD, player count, and latency.")
    async def info(self, ctx):
        try:
            server = JavaServer.lookup(self.serverIp)
            status = server.status()
            motd = status.description.strip() if isinstance(status.description, str) else status.description.get("text", "Unknown MOTD")
            online = status.players.online
            max_players = status.players.max
            latency = round(status.latency)
            if latency <= 100:
                latency_display = f"🟢 **{latency} ms**"
            elif latency <= 250:
                latency_display = f"🟡 **{latency} ms**"
            else:
                latency_display = f"🔴 **{latency} ms**"
            embed = discord.Embed(title="🖥️ Minecraft Server Info", description=f"**{motd}** | **{online}/{max_players}** | {latency_display}", color=0x00ff00)
            await ctx.send(embed=embed)
        except Exception as e:
            error_embed = discord.Embed(title="🖥️ Minecraft Server Info", description="❌ Server Unreachable", color=0xff0000)
            await ctx.send(embed=error_embed)

    @commands.command(name='request-server', help='Requests the owner to start the server.')
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner or ctx.author.id in ctx.cog.users)
    async def requestServer(self, ctx):
        requester = ctx.author
        if requester.id == self.owner:
            await ctx.send("🔧 You're the owner—you can start the server yourself.")
            return
        try:
            owner_user = await self.bot.fetch_user(self.owner)
            if not owner_user:
                await ctx.send("⚠️ Could not find the bot owner.")
                return
            dm_embed = discord.Embed(title="🔔 Server Start Request", description=f"{requester.mention} (`{requester.name}#{requester.discriminator}`) is requesting to start the Minecraft server.", color=0xffcc00)
            dm_embed.set_footer(text=f"User ID: {requester.id}")
            await owner_user.send(embed=dm_embed)
            await ctx.send("📩 Your request has been sent to the owner.")
        except discord.Forbidden:
            await ctx.send("⚠️ I couldn't DM the owner. They might have DMs disabled.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command(name='start-server', help='Starts the MC Server.', hidden=True)
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner)
    async def startServer(self, ctx):
        arguments = [self.serverFolder, self.serverFile, self.flashMemory]
        statusBashScript = os.path.join(self.botFolder, 'scripts/mcStatus.sh')
        try:
            returnCode = subprocess.run(['/bin/bash', statusBashScript] + arguments).returncode
            if returnCode == 0:
                embed = discord.Embed(title='Server Status', description='🟢 Server is already running.', color=0x00ff00)
            elif returnCode == 1:
                embed = discord.Embed(title='Server Status', description='🟡 Starting server...', color=0xffcc00)
                startBashScript = os.path.join(self.botFolder, 'scripts/mcStart.sh')
                subprocess.Popen(['/bin/bash', startBashScript] + arguments)
            else:
                embed = discord.Embed(title='Server Status', description='🔴 Could not determine server status.', color=0xff0000)
        except Exception as e:
            embed = discord.Embed(title='Server Status', description=f'❌ Error: {e}', color=0xff0000)
        await ctx.send(embed=embed)

    @commands.command(name='stop-server', help='Stops the MC Server.', hidden=True)
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner)
    async def stop_server(self, ctx):
        arguments = [self.serverFolder, self.serverFile, self.flashMemory]
        statusBashScript = os.path.join(self.botFolder, 'scripts/mcStatus.sh')
        try:
            returnCode = subprocess.run(['/bin/bash', statusBashScript] + arguments).returncode
            if returnCode == 0:
                embed = discord.Embed(title='Server Status', description='🔻 Server shutting down...', color=0xffcc00)
                await ctx.send(embed=embed)

                stopBashScript = os.path.join(self.botFolder, 'scripts/mcStop.sh')
                subprocess.run(['/bin/bash', stopBashScript] + arguments)
            elif returnCode == 1:
                embed = discord.Embed(title='Server Status', description='🛑 Server is not running.', color=0xff0000)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title='Server Status', description='❓ Unknown status returned by status check.',
                                      color=0xff0000)
                await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title='Server Error', description=f'❌ Exception occurred: {e}', color=0xff0000)
            await ctx.send(embed=embed)


    @commands.command(name='change-prefix', help='Changes the command prefix', hidden=True)
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner)
    async def changePrefix(self, ctx, newPrefix: str = None):
        if not newPrefix:
            await ctx.send('⚠️ Please provide a new prefix.')
            return
        envPath = os.path.join(self.botFolder, '.env')
        with open(envPath, 'r') as env_file:
            lines = env_file.readlines()
        with open(envPath, 'w') as env_file:
            for line in lines:
                if line.startswith('COMMAND_PREFIX='):
                    env_file.write(f'COMMAND_PREFIX={newPrefix}\n')
                else:
                    env_file.write(line)
        load_dotenv(dotenv_path=envPath)
        self.config['COMMAND_PREFIX'] = newPrefix
        self.bot.command_prefix = newPrefix
        await ctx.send(f'✅ Command prefix changed to: `{newPrefix}`')

    @commands.command(name='add-user', help='Add a user to allowed users (owner only)', hidden=True)
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner)
    async def addUser(self, ctx, user: discord.User = None):
        if user is None:
            await ctx.send("⚠️ Please mention a user or provide a user ID.")
            return
        userIdString = str(user.id)
        allowedUsersRaw = self.config['ALLOWED_USERS'] or ''
        allowedUsersList = [uid.strip() for uid in allowedUsersRaw.split(',') if uid.strip()]
        if userIdString in allowedUsersList:
            await ctx.send(f"ℹ️ User {user} is already in the allowed users list.")
            return
        # SEND DM TO NEW USER
        try:
            await user.send(
                f"👋 You have been granted access to the bot!\n"
                f"Server IP: `{self.serverIp}`\n"
                f"To get help from the bot, use the `{self.config['COMMAND_PREFIX']}help` command."
            )
            await ctx.send(f"✅ User {user} added and notified via DM.")
        except Exception as e:
            await ctx.send(f"⚠️ Could not send DM to {user}. They might have DMs disabled.\nError: {e}")
        finally:
            # ADDED USER TO ALLOWED USERS LIST
            allowedUsersList.append(userIdString)
            self.config['ALLOWED_USERS'] = ','.join(allowedUsersList)
            self.users.append(user.id)
            # UPDATING ENV FILE
            envPath = os.path.join(self.botFolder, '.env')
            editEnvFile(envPath, 'ALLOWED_USERS', self.config['ALLOWED_USERS'])
            load_dotenv(dotenv_path=envPath)

    @commands.command(name='help')
    async def customHelp(self, ctx):
        prefix = self.config['COMMAND_PREFIX']
        embed = discord.Embed(title="Available Commands", color=0x00ff00)
        for command in self.bot.commands:
            if command.hidden:
                continue
            if command.name == "change-prefix" and ctx.author.id != self.owner:
                continue
            if command.name == "adduser" and ctx.author.id != self.owner:
                continue
            embed.add_field(name=f"{prefix}{command.name}", value=command.help or "No description", inline=False)
        await ctx.send(embed=embed)


class ShulkerBot(commands.Bot):
    def __init__(self, botConfig, folder):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix=botConfig['COMMAND_PREFIX'], intents=intents, help_command=None)
        self.botConfig = botConfig
        self.folder = folder

    async def setup_hook(self):
        await self.add_cog(ShulkerCommands(self, self.botConfig, self.folder))

    def run_bot(self):
        super().run(self.botConfig['DISCORD_TOKEN'])


if __name__ == '__main__':
    current_folder = os.path.dirname(os.path.realpath(__file__))
    load_dotenv(os.path.join(current_folder, '.env'))
    config = {
        'DISCORD_TOKEN': os.getenv('DISCORD_TOKEN'),
        'BOT_OWNER': int(os.getenv('BOT_OWNER')),
        'ALLOWED_USERS': os.getenv('ALLOWED_USERS'),
        'SERVER_IP': os.getenv('SERVER_IP'),
        'SERVER_FOLDER': os.getenv('SERVER_FOLDER'),
        'SERVER_FILE': os.getenv('SERVER_FILE'),
        'FLASH_MEMORY': os.getenv('FLASH_MEMORY'),
        'COMMAND_PREFIX': os.getenv('COMMAND_PREFIX', '!')
    }
    bot = ShulkerBot(config, current_folder)
    bot.run_bot()