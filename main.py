import os
import json
import discord
import asyncio
import subprocess

import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv
from mcstatus import JavaServer

from utilities import *


class ShulkerCommands(commands.Cog):
    def __init__(self, shulkerBot, botConfig, botFolder):
        self.colors = {'green': 0x00ff00, 'yellow': 0xffcc00, 'red': 0xff0000}
        self.usernameCsvPath = os.path.join(botFolder, 'usernames.csv')
        self.usernamesDataframe = readUsernamesCsv(self.usernameCsvPath)
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

    @commands.command(name='hello', help="Greets you back.")
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner or ctx.author.id in ctx.cog.users)
    async def hello(self, ctx):
        await ctx.send(f"Hello, {ctx.author.name}!")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot is ready. Logged in as {self.bot.user}')
        initializeUsernameCsv(self.usernameCsvPath)
        self.usernamesDataframe = readUsernamesCsv(self.usernameCsvPath)
        self.updateStatus.start()
        await self.updateStatus()
        try:
            ownerUser = await self.bot.fetch_user(self.owner)
            if ownerUser:
                await ownerUser.send(f"✅ **{self.bot.user.name}** is now online and ready.")
        except Exception as e:
            print(f"⚠️ Failed to send DM to owner: {e}")

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
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner or ctx.author.id in ctx.cog.users)
    async def ip(self, ctx):
        embed = discord.Embed(title='Server IP Address',  description=f'The server\'s IP is: `{self.serverIp}`', color=self.colors['green'])
        await ctx.send(embed=embed)

    @commands.command(name='seed', help="Gives the server's world seed.")
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner or ctx.author.id in ctx.cog.users)
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
            embed = discord.Embed(title='World Seed', description=f"The server's world seed is: `{worldSeed}`", color=self.colors['green'])
            chunkBaseLink = f'https://www.chunkbase.com/apps/seed-map#{worldSeed}'
            embed.add_field(name='ChunkBase Link', value=chunkBaseLink)
            await ctx.send(embed=embed)
        else:
            await ctx.send("⚠️ Could not find the world seed in the server properties.")

    @commands.command(name='info', aliases=['status'], help="Displays server MOTD, player count, and latency.")
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner or ctx.author.id in ctx.cog.users)
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
            embed = discord.Embed(title="🖥️ Minecraft Server Info", description=f"**{motd}** | **{online}/{max_players}** | {latency_display}", color=self.colors['green'])
            await ctx.send(embed=embed)
        except Exception as e:
            error_embed = discord.Embed(title="🖥️ Minecraft Server Info", description="❌ Server Unreachable", color=self.colors['red'])
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

    @commands.command(name='start-server', aliases=['start'], help='[OWNER ONLY] Starts the MC Server.', hidden=True)
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner)
    async def startServer(self, ctx):
        arguments = [self.serverFolder, self.serverFile, self.flashMemory]

        try:
            if await isServerOnline(self.serverIp):
                embed = discord.Embed(title='Server Status', description='🟢 Server is already running.', color=self.colors['green'])
            else:
                embed = discord.Embed(title='Server Status', description='🟡 Server is offline. Starting server...', color=self.colors['yellow'])
                startBashScript = os.path.join(self.botFolder, 'scripts/mcStart.sh')
                subprocess.Popen(['/bin/bash', startBashScript] + arguments)

        except Exception as e:
            embed = discord.Embed(title='Server Status', description=f'❌ Error: {e}', color=self.colors['red'])
        await ctx.send(embed=embed)

    @commands.command(name='stop-server', aliases=['stop'], help='[OWNER ONLY] Stops the MC Server.', hidden=True)
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner)
    async def stopServer(self, ctx):
        arguments = [self.serverFolder, self.serverFile, self.flashMemory]
        try:
            if await isServerOnline(self.serverIp):
                embed = discord.Embed(title='Server Status', description='🔻 Server is online. Shutting it down...', color=self.colors['yellow'])
                await ctx.send(embed=embed)
                stopBashScript = os.path.join(self.botFolder, 'scripts/mcStop.sh')
                subprocess.run(['/bin/bash', stopBashScript] + arguments)
            else:
                embed = discord.Embed(title='Server Status', description='🛑 Server is not running.', color=self.colors['red'])
                await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title='Server Error', description=f'❌ Exception occurred: {e}', color=self.colors['red'])
            await ctx.send(embed=embed)

    @commands.command(name='change-prefix', aliases=['prefix'], help='[OWNER ONLY] Changes the command prefix.', hidden=True)
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

    @commands.command(name='add-user', help='[OWNER ONLY] Add a user to allowed users.', hidden=True)
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
        try:
            message = await user.send(f"👋 You have been granted access to the bot!\nReact with ✅ to confirm, or ❌ to cancel.")
            await ctx.send(f"✅ User {user} notified via DM.")
            await message.add_reaction("✅")
            await message.add_reaction("❌")
            def check(awaitingReaction, awaitingUser):
                return awaitingUser.id == ctx.author.id and awaitingReaction.message.id == message.id and str(
                    awaitingReaction.emoji) in ["✅", "❌"]
            try:
                reaction, reactingUser = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                print(reactingUser)
            except asyncio.TimeoutError:
                await message.edit(content="⏳ Request timed out.")
                await ctx.send(f"✅ User {user} confirmation timed out.")
                return
            if str(reaction.emoji) == "✅":
                await user.send(f"✅ You now have access to ShulkerPi!\nUse {self.config['COMMAND_PREFIX']}whitelist to request access to the Minecraft server.")
                await ctx.send(f"✅ User {user} confirmation was accepted.")
                # ADDED USER TO ALLOWED USERS LIST
                allowedUsersList.append(userIdString)
                self.config['ALLOWED_USERS'] = ','.join(allowedUsersList)
                self.users.append(user.id)
                # UPDATING ENV FILE
                envPath = os.path.join(self.botFolder, '.env')
                editEnvFile(envPath, 'ALLOWED_USERS', self.config['ALLOWED_USERS'])
                load_dotenv(dotenv_path=envPath)
        except Exception as e:
            await ctx.send(f"⚠️ Could not send DM to {user}. They might have DMs disabled.\nError: {e}")

    @commands.command(name='add-username', aliases=['username', 'link'], help='Link your Minecraft username to your Discord account.')
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner or ctx.author.id in ctx.cog.users)
    async def linkUsername(self, ctx, mcUsername: str = None):
        if not mcUsername:
            await ctx.send("⚠️ Please provide your Minecraft username. Example: `!link-username Steve`")
            return
        try:
            response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{mcUsername}")
            if response.status_code != 200:
                await ctx.send("❌ Could not find that Minecraft username.")
                return
            data = response.json()
            uuid = data.get('id')
            self.usernamesDataframe = readUsernamesCsv(self.usernameCsvPath)
            usernamesDataframe = self.usernamesDataframe[self.usernamesDataframe['DISCORD_ID'] != ctx.author.id]
            newEntry = {'DISCORD_NAME': f"{ctx.author.name}#{ctx.author.discriminator}", 'DISCORD_ID': ctx.author.id, 'MINECRAFT_USERNAME': mcUsername, 'MINECRAFT_UUID': uuid}
            self.usernamesDataframe = pd.concat([usernamesDataframe, pd.DataFrame([newEntry])], ignore_index=True)
            saveUsernameCsv(self.usernamesDataframe, self.usernameCsvPath)
            embed = discord.Embed(title="✅ Username Linked", description=f"Minecraft username `{mcUsername}` successfully linked to {ctx.author.mention}.", color=self.colors['green'])
            embed.set_thumbnail(url=f"https://minotar.net/avatar/{uuid}/64.png")
            await ctx.send(embed=embed)
            ownerUser = await self.bot.fetch_user(self.owner)
            if ownerUser:
                await ownerUser.send(f"🔗 `{ctx.author}` linked Minecraft username `{mcUsername}` (UUID: `{uuid}`).")
        except Exception as e:
            print(e)
            await ctx.send(f"❌ An error occurred while linking your username: {e}")

    @commands.command(name='remove-username', aliases=['unlink'], help='Unlink your Minecraft username from your Discord account.')
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner or ctx.author.id in ctx.cog.users)
    async def removeUsername(self, ctx):
        try:
            if self.usernamesDataframe.empty or ctx.author.id not in self.usernamesDataframe['DISCORD_ID'].values:
                await ctx.send("⚠️ You don't have a linked Minecraft username.")
                return
            oldEntry = self.usernamesDataframe[self.usernamesDataframe['DISCORD_ID'] == ctx.author.id]
            oldUsername = oldEntry['MINECRAFT_USERNAME'].values[0] if not oldEntry.empty else "Unknown"
            self.usernamesDataframe = self.usernamesDataframe[self.usernamesDataframe['DISCORD_ID'] != ctx.author.id]
            saveUsernameCsv(self.usernamesDataframe, self.usernameCsvPath)
            embed = discord.Embed(title="✅ Username Removed", description=f"Minecraft username unlinked from {ctx.author.mention}.", color=self.colors['yellow'])
            await ctx.send(embed=embed)
            ownerUser = await self.bot.fetch_user(self.owner)
            if ownerUser:
                await ownerUser.send(f"❌ `{ctx.author}` removed their linked Minecraft username `{oldUsername}`.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred while removing your username: {e}")

    @commands.command(name='flush-usernames', aliases=['flush'], help='[OWNER ONLY] Delete all linked Minecraft usernames.')
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner)
    async def flushUsernames(self, ctx):
        try:
            self.usernamesDataframe = pd.DataFrame(columns=['DISCORD_NAME', 'DISCORD_ID', 'MINECRAFT_USERNAME', 'MINECRAFT_UUID'])
            saveUsernameCsv(self.usernamesDataframe, self.usernameCsvPath)
            await ctx.send("🧹 All linked Minecraft usernames have been flushed.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred while flushing the usernames: {e}")

    @commands.command(name='stats', help="Shows your Minecraft stats.")
    @commands.check(lambda ctx: ctx.author.id == ctx.cog.owner or ctx.author.id in ctx.cog.users)
    async def givePlayerStats(self, ctx):
        try:
            df = self.usernamesDataframe
            print(df)
            userRow = df[df['DISCORD_ID'] == ctx.author.id]
            if userRow.empty:
                await ctx.send("⚠️ You don't have a linked Minecraft username.")
                embed = discord.Embed(title='Player Stats', description="⚠️ You don't have a linked Minecraft username.", color=self.colors['yellow'])
                return await ctx.author.send(embed=embed)
            mcUsername, mcUuid = userRow.iloc[0]['MINECRAFT_USERNAME'], userRow.iloc[0]['MINECRAFT_UUID']
            worldName = next((line.split('=')[1].strip() for line in open(os.path.join(self.serverFolder, 'server.properties')) if line.startswith('level-name=')), None)
            if not worldName:
                return await ctx.author.send("❌ Could not find the level name in `server.properties`.")
            statisticsPath = os.path.join(self.serverFolder, worldName, 'stats')
            playerStatistics = retrievePlayerStats(statisticsPath, mcUuid, mcUsername)
            if not playerStatistics:
                return await ctx.author.send("🛑 You have not yet joined the server.")
            embed = discord.Embed(title=f"📊 Stats for {playerStatistics.get('NAME', mcUsername)}", color=self.colors['green'])
            fields = {'Deaths': 'DEATHS', 'Mobs Killed': 'MOB_KILLS', 'Players Killed': 'PLAYER_KILLS', 'Damage Taken': 'DAMAGE_TAKEN',
                      'Damage Dealt': 'DAMAGE_DEALT', 'Total Play Time': 'PLAY_TIME', 'World Time': 'WORLD_TIME', 'Since Last Death': 'LAST_DEATH',
                      'Walked': 'WALK_DISTANCE', 'Swum': 'SWIM_DISTANCE', 'Fallen': 'FALL_DISTANCE', 'By Boat': 'BOAT_DISTANCE', 'By Elytra': 'ELYTRA_DISTANCE',
                      'By Horse': 'HORSE_DISTANCE', 'By Minecart': 'MINECART_DISTANCE', 'Most Block Mined': 'MOST_MINED', 'Most Item Used': 'MOST_USED',
                      'Most Crafted': 'MOST_CRAFTED', 'Most Mob Killed': 'MOST_KILLED', 'Most Deaths To': 'MOST_KILLED_BY', 'Most Tool Broken': 'MOST_BROKEN',}
            for label, key in fields.items():
                value = playerStatistics.get(key, 'N/A')
                embed.add_field(name=label, value=value, inline=True)
                embed.set_thumbnail(url=f"https://minotar.net/avatar/{mcUuid}/64.png")
            return await ctx.author.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title='Server Error', description=f'❌ Exception occurred: {e}', color=self.colors['red'])
            return await ctx.send(embed=embed)

    @commands.command(name='help')
    async def customHelp(self, ctx):
        prefix = self.config['COMMAND_PREFIX']
        embed = discord.Embed(title="📜 Available Commands", color=self.colors['green'])
        embed.add_field(
            name="🧾 General Commands",
            value=(
                f"**{prefix}hello** — Greets you back.\n"
                f"**{prefix}ip** — Gives the server's IP address.\n"
                f"**{prefix}seed** — Gives the server's world seed.\n"
                f"**{prefix}info** — Displays server MOTD, player count, and latency.\n"
                f"**{prefix}request-server** — Requests the owner to start the server.\n"
                f"**{prefix}add-username** — Link your Minecraft username to your Discord.\n"
                f"**{prefix}remove-username** — Unlink your Minecraft username.\n"
                f"**{prefix}stats** — Gives your player stats on the server.\n"
            ),
            inline=False
        )
        if ctx.author.id == self.owner:
            embed.add_field(
                name="🔐 Owner-Only Commands",
                value=(
                    f"**{prefix}start-server** — Starts the MC server.\n"
                    f"**{prefix}stop-server** — Stops the MC server.\n"
                    f"**{prefix}change-prefix** — Change the bot's command prefix.\n"
                    f"**{prefix}add-user** — Add a user to allowed users.\n"
                    f"**{prefix}flush-usernames** — Delete all linked Minecraft usernames.\n"
                ),
                inline=False
            )
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