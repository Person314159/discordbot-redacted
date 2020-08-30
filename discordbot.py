#!/usr/bin/python3
import asyncio
import json
import os
import random
import re
import time
import traceback
from datetime import datetime
from os.path import isfile, join

import discord
from discord.ext import commands


def prefix(bot, message):
	return bot.guild_prefix_dict[str(message.guild.id)]

bot = commands.Bot(command_prefix = prefix, help_command = None, owner_id = 226878658013298690)

def loadJSON(jsonfile):
	with open(jsonfile, "r") as f:
		b = json.load(f)
		return json.loads(b)

def writeJSON(data, jsonfile):
	b = json.dumps(data)
	with open(jsonfile, "w") as f:
		json.dump(b, f)

disable_default = []
deletesnipe_exception = []
banned_users = []

def update_data(user):
	if str(user.id) not in bot.user_data:
		if not user.bot:
			bot.user_data.update({
				str(user.id): {
					"coins": 0,
					"lastMessageTime": 0,
					"lastDailyTime": 0,
					"dailyStreak": 0,
					"fishInv": {
						"Garbage": 0,
						"Common": 0,
						"Uncommon": 0,
						"Rarefish": {
							"🦈": 0,
							"🐙": 0,
							"🐢": 0,
							"🦀": 0,
							"🐧": 0,
							"🐊": 0,
							"🐳": 0,
							"🐋": 0,
							"🦑": 0,
							"🐬": 0,
							"🦐": 0
						},
						"Rareitem": {
							"🅱": 0,
							"🎁": 0,
							"💰": 0,
							"💍": 0,
							"💎": 0
						}
					}
				}
			})

	bot.writeJSON(bot.user_data, "data/userdata.json")

	# temporary
	if user.id not in bot.status_dict:
		bot.status_dict.update({user.id: [None, str(user.activity) if user.activity and isinstance(user.activity, discord.CustomActivity) else None, int(time.time())]})

async def status_task():
	await bot.wait_until_ready()

	while not bot.is_closed():
		num_guilds = len(bot.guilds)
		online_members = []

		for guild in bot.guilds:
			for member in guild.members:
				if not member.bot and member.status != discord.Status.offline:
					if member not in online_members:
						online_members.append(member)

		play = ["with the \"help\" command", " ", "with your mind", "ƃuᴉʎɐlԀ", "...something?", "a game? Or am I?", "¯\_(ツ)_/¯", f"with {num_guilds} servers", f"with {len(online_members)} people", "with boats", "with the infinity gauntlet"]
		listen = ["smart musik", "capitalist propaganda", "... wait I can't hear anything", "rush 🅱"]
		watch = ["TV", "YouTube vids", "over you", "capitalist propaganda", "how to make a bot"]

		rng = random.randrange(0, 3)

		if rng == 0:
			await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.playing, name = random.choice(play)))
		elif rng == 1:
			await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = random.choice(listen)))
		else:
			await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = random.choice(watch)))

		startup()

		await asyncio.sleep(30)

def startup():
	bot.guild_prefix_dict = bot.loadJSON("data/guildprefix.json")
	bot.channel_deletesnipe_dict = bot.loadJSON("data/deletesnipe.json")
	bot.channel_editsnipe_dict = bot.loadJSON("data/editsnipe.json")
	bot.channel_spoil_dict = bot.loadJSON("data/spoil.json")
	bot.poll_dict = bot.loadJSON("data/poll.json")
	bot.user_data = bot.loadJSON("data/userdata.json")
	bot.command_toggle_dict = bot.loadJSON("data/commandtoggle.json")
	bot.stats_dict = bot.loadJSON("data/stats.json")

	for guild in list(bot.guild_prefix_dict):
		if not bot.get_guild(int(guild)):
			del bot.guild_prefix_dict[guild]
	bot.writeJSON(bot.guild_prefix_dict, "data/guildprefix.json")

	for channel in list(bot.channel_deletesnipe_dict):
		if not bot.get_channel(int(channel)):
			del bot.channel_deletesnipe_dict[channel]
	bot.writeJSON(bot.channel_deletesnipe_dict, "data/deletesnipe.json")

	for channel in list(bot.channel_editsnipe_dict):
		if not bot.get_channel(int(channel)):
			del bot.channel_editsnipe_dict[channel]
	bot.writeJSON(bot.channel_editsnipe_dict, "data/editsnipe.json")

	for channel in list(bot.channel_spoil_dict):
		if not bot.get_channel(int(channel)):
			del bot.channel_spoil_dict[channel]
	bot.writeJSON(bot.channel_spoil_dict, "data/spoil.json")

	for channel in list(bot.poll_dict):
		if not bot.get_channel(int(channel)):
			del bot.poll_dict[channel]
	bot.writeJSON(bot.poll_dict, "data/poll.json")

	for user in list(bot.user_data):
		if not bot.get_user(int(user)):
			del bot.user_data[user]
	bot.writeJSON(bot.user_data, "data/userdata.json")

	for command in list(bot.command_toggle_dict):
		if not bot.get_command(command):
			del bot.command_toggle_dict[command]
	bot.writeJSON(bot.command_toggle_dict, "data/commandtoggle.json")

	for command in list(bot.stats_dict):
		if not bot.get_command(command):
			del bot.stats_dict[command]
	bot.writeJSON(bot.stats_dict, "data/stats.json")

	for command in bot.commands:
		if command.name not in bot.command_toggle_dict and command.name not in ["enable", "disable"]:
			bot.command_toggle_dict[command.name] = []

			for guild in bot.guilds:
				for channel in guild.text_channels:
					if command.name in disable_default:
						bot.command_toggle_dict[command.name].append(channel.id)

			bot.writeJSON(bot.command_toggle_dict, "data/commandtoggle.json")

		if command.name not in bot.stats_dict:
			bot.stats_dict[command.name] = 0
			bot.writeJSON(bot.stats_dict, "data/stats.json")

	for guild in bot.guilds:
		if str(guild.id) not in bot.guild_prefix_dict:
			bot.guild_prefix_dict.update({str(guild.id) : bot.command_prefix})
			bot.writeJSON(bot.guild_prefix_dict, "data/guildprefix.json")

		for channel in guild.text_channels:
			if str(channel.id) not in bot.channel_deletesnipe_dict:
				bot.channel_deletesnipe_dict.update({str(channel.id) : []})
				bot.writeJSON(bot.channel_deletesnipe_dict, "data/deletesnipe.json")

			if str(channel.id) not in bot.channel_editsnipe_dict:
				bot.channel_editsnipe_dict.update({str(channel.id) : []})
				bot.writeJSON(bot.channel_editsnipe_dict, "data/editsnipe.json")

			if str(channel.id) not in bot.channel_spoil_dict:
				bot.channel_spoil_dict.update({str(channel.id) : ""})
				bot.writeJSON(bot.channel_spoil_dict, "data/spoil.json")

			if str(channel.id) not in bot.poll_dict:
				bot.poll_dict.update({str(channel.id) : ""})
				bot.writeJSON(bot.poll_dict, "data/poll.json")

		for member in guild.members:
			bot.update_data(member)

@bot.event
async def on_ready():
	bot.startup()
	print("Logged in successfully")
	bot.loop.create_task(status_task())

# temporary
@bot.event
async def on_member_update(before, after):
	if isinstance(after.activity, discord.CustomActivity):
		if str(after.activity) != bot.status_dict[after.id][1]:
			bot.status_dict[after.id] = [bot.status_dict[after.id][1], str(after.activity), int(time.time())]
	else:
		if isinstance(before.activity, discord.CustomActivity):
			bot.status_dict[after.id] = [str(before.activity), None, int(time.time())]

@bot.event
async def on_member_join(member):
	bot.update_data(member)

@bot.event
async def on_message_delete(message):
	if not message.author.bot and not isinstance(message.channel, discord.abc.PrivateChannel):
		if message.content in deletesnipe_exception:
			return

		delete_author = message.author
		content = message.content

		if not content:
			content = "Last deleted message had no content"

		bot.channel_deletesnipe_dict[str(message.channel.id)].insert(0, [delete_author.display_name, str(delete_author.avatar_url), int(datetime.timestamp(message.created_at)), content])

		if len(bot.channel_deletesnipe_dict[str(message.channel.id)]) > 10:
			del bot.channel_deletesnipe_dict[str(message.channel.id)][-1]

		bot.writeJSON(bot.channel_deletesnipe_dict, "data/deletesnipe.json")

@bot.event
async def on_message_edit(before, after):
	if not before.author.bot and not isinstance(before.channel, discord.abc.PrivateChannel) and before.content != after.content:
		edit_author = before.author
		bot.channel_editsnipe_dict[str(before.channel.id)].insert(0, [edit_author.display_name, str(edit_author.avatar_url), int(datetime.timestamp(after.edited_at)), before.content, after.content])

		if len(bot.channel_editsnipe_dict[str(before.channel.id)]) > 10:
			del bot.channel_editsnipe_dict[str(before.channel.id)][-1]

		bot.writeJSON(bot.channel_editsnipe_dict, "data/editsnipe.json")
		await bot.process_commands(after)

@bot.event
async def on_guild_join(guild):
	bot.guild_prefix_dict.update({str(guild.id) : "?"})
	bot.writeJSON(bot.guild_prefix_dict, "data/guildprefix.json")

	for channel in guild.text_channels:
		bot.channel_deletesnipe_dict.update({str(channel.id) : []})
		bot.writeJSON(bot.channel_deletesnipe_dict, "data/deletesnipe.json")
		bot.channel_editsnipe_dict.update({str(channel.id) : []})
		bot.writeJSON(bot.channel_editsnipe_dict, "data/editsnipe.json")
		bot.channel_spoil_dict.update({str(channel.id) : ""})
		bot.writeJSON(bot.channel_spoil_dict, "data/spoil.json")
		bot.poll_dict.update({str(channel.id) : ""})
		bot.writeJSON(bot.poll_dict, "data/poll.json")

		for command in disable_default:
			bot.command_toggle_dict[command].append(channel.id)

		bot.writeJSON(bot.command_toggle_dict, "data/commandtoggle.json")

	for member in guild.members:
		if not member.bot:
			bot.update_data(member)

@bot.event
async def on_guild_remove(guild):
	if str(guild.id) in bot.guild_prefix_dict:
		del bot.guild_prefix_dict[str(guild.id)]
		bot.writeJSON(bot.guild_prefix_dict, "data/guildprefix.json")

	for channel in guild.channels:
		if str(channel.id) in bot.channel_editsnipe_dict:
			del bot.channel_editsnipe_dict[str(channel.id)]
			bot.writeJSON(bot.channel_editsnipe_dict, "data/editsnipe.json")

		if str(channel.id) in bot.channel_deletesnipe_dict:
			del bot.channel_deletesnipe_dict[str(channel.id)]
			bot.writeJSON(bot.channel_deletesnipe_dict, "data/deletesnipe.json")

		if str(channel.id) in bot.channel_spoil_dict:
			del bot.channel_spoil_dict[str(channel.id)]
			bot.writeJSON(bot.channel_spoil_dict, "data/spoil.json")

		if str(channel.id) in bot.poll_dict:
			del bot.poll_dict[str(channel.id)]
			bot.writeJSON(bot.poll_dict, "data/poll.json")

		for command in bot.command_toggle_dict:
			if channel.id in bot.command_toggle_dict[command]:
				bot.command_toggle_dict[command].remove(channel.id)

		bot.writeJSON(bot.command_toggle_dict, "data/commandtoggle.json")

@bot.event
async def on_channel_create(channel):
	if isinstance(channel, discord.TextChannel):
		bot.channel_deletesnipe_dict.update({str(channel.id) : []})
		bot.writeJSON(bot.channel_deletesnipe_dict, "data/deletesnipe.json")
		bot.channel_editsnipe_dict.update({str(channel.id) : []})
		bot.writeJSON(bot.channel_editsnipe_dict, "data/editsnipe.json")
		bot.channel_spoil_dict.update({str(channel.id) : ""})
		bot.writeJSON(bot.channel_spoil_dict, "data/spoil.json")
		bot.poll_dict.update({str(channel.id) : ""})
		bot.writeJSON(bot.poll_dict, "data/poll.json")

		for command in disable_default:
			bot.command_toggle_dict[command].append(channel.id)

		bot.writeJSON(bot.command_toggle_dict, "data/commandtoggle.json")

@bot.event
async def on_channel_delete(channel):
	if str(channel.id) in bot.channel_editsnipe_dict:
		del bot.channel_editsnipe_dict[str(channel.id)]
		bot.writeJSON(bot.channel_editsnipe_dict, "data/editsnipe.json")

	if str(channel.id) in bot.channel_deletesnipe_dict:
		del bot.channel_deletesnipe_dict[str(channel.id)]
		bot.writeJSON(bot.channel_deletesnipe_dict, "data/deletesnipe.json")

	if str(channel.id) in bot.channel_spoil_dict:
		del bot.channel_spoil_dict[str(channel.id)]
		bot.writeJSON(bot.channel_spoil_dict, "data/spoil.json")

	if str(channel.id) in bot.poll_dict:
		del bot.poll_dict[str(channel.id)]
		bot.writeJSON(bot.poll_dict, "data/poll.json")

	for command in bot.command_toggle_dict:
		if channel.id in bot.command_toggle_dict[command]:
			bot.command_toggle_dict[command].remove(channel.id)

	bot.writeJSON(bot.command_toggle_dict, "data/commandtoggle.json")

@bot.event
async def on_message(message):
	if message.author.bot:
		if message.content.startswith("🅱ot#0272|") and message.author != bot.user:
			counter = 0
			ignore = False

			async for msg in message.channel.history(limit = None):
				counter += 1

				if counter == 2:
					ct = msg.content.replace("<@!", "<@").split(" ")

					if len(ct[0]) != 3 or "yu <@478791705747783702> " not in msg.content.replace("<@!", "<@") or msg.author.bot:
						ignore = True
						break
					break

			if not ignore:
				data = message.content.split("|")
				user = data[1]
				info = bot.get_user(int(user))
				userx = f"{info.name}#{info.discriminator}"

				await message.channel.send(message.content)
				whichone = ""

				def check(msg):
					nonlocal whichone
					whichone = msg.content
					return msg.channel == message.channel and msg.author.id == message.author.id and msg.content == f"CONFIRMATION|{message.author}"

				try:
					await bot.wait_for("message", check = check, timeout = 2.3)
				except:
					return

				bot.user_data[user]["coins"] += int(data[2])
				bot.writeJSON(bot.user_data, "data/userdata.json")
				await message.channel.send(f"**{userx}**, **{data[2]}** coins have been received from **{message.author.name}**. You now have **{bot.user_data[user]['coins']}** coins in 🅱ot.")
		return

	if isinstance(message.channel, discord.abc.PrivateChannel):
		if message.author.id == 226878658013298690 or message.author.id == 420069040258547712:
			if message.content.startswith("ping"):
				user = bot.get_user(int(message.content.split()[1]))
				await user.send(user.mention)
				await user.send(user.mention)
				await user.send(user.mention)
				await user.send(user.mention)
				await user.send(user.mention)
			else:
				args = eval(message.content)
				attachment = None

				if len(message.attachments) == 1:
					file_name = message.attachments[0].filename
					await message.attachments[0].save(file_name)
					attachment = discord.File(file_name)

				if len(args) == 2:
					id_ = args[0]
					msg = args[1]

					send = bot.get_user(id_)

					if not send:
						send = bot.get_channel(id_)

					if send:
						try:
							if attachment:
								await send.send(msg, file = attachment)
							else:
								await send.send(msg)
						except Exception as e:
							print(e)

				if attachment:
					os.remove(file_name)
		else:
			await bot.get_user(226878658013298690).send(f"{message.author}: \"{message.content}\"")

		return

	if message.channel.id == 356187551037390868:
		return
	elif message.channel.id == 375313745582358528 and message.attachments != []:
		await message.delete()
	else:
		if time.time() - bot.user_data[str(message.author.id)]["lastMessageTime"] > 120:
			bot.user_data[str(message.author.id)]["coins"] += random.randint(5, 15)
			bot.user_data[str(message.author.id)]["lastMessageTime"] = time.time()
			bot.update_data(message.author)

		bot.command_prefix = bot.guild_prefix_dict[str(message.guild.id)]
		# with open("messages.txt", "a") as f:
		# 	print(f"{message.guild.name}: {message.channel.name}: {message.author.name}: \"{message.content}\" @ {str(datetime.datetime.now())} \r\n", file = f)

		#print(message.content)

		if message.channel.id == 437047996203401216 and (message.attachments or message.embeds):
			await message.add_reaction(bot.get_emoji(711422281150234644))
			await message.add_reaction(bot.get_emoji(711422715558625300))

		if re.findall(r"\|\|[^|]*\|\|", message.content):
			spoil_author = message.author
			avatar_url = str(spoil_author.avatar_url)
			nick = spoil_author.display_name
			spoil_message = message.content.replace("||", "|")
			bot.channel_spoil_dict[str(message.channel.id)] = [nick, avatar_url, int(datetime.timestamp(message.created_at)), spoil_message]
			bot.writeJSON(bot.channel_spoil_dict, "data/spoil.json")

		if re.findall(r"<<@&457618814058758146>&?\d{18}>", message.content):
			new = message.content.replace("<@&457618814058758146>", "@")
			await message.channel.send(new)
		elif message.content == "current prefix":
			if not bot.guild_prefix_dict[str(message.guild.id)]:
				await message.channel.send("There is currently no prefix.", delete_after = 5)
			else:
				await message.channel.send(f"The current prefix is `{bot.guild_prefix_dict[str(message.guild.id)]}`.", delete_after = 5)
		elif message.content.startswith("prefix "):
			if message.author.guild_permissions.manage_guild or message.author.id == 226878658013298690:
				args = message.content.split(" ")[1:]

				if len(args) == 1 and args[0] == "reset":
					bot.guild_prefix_dict[str(message.guild.id)] = "?"
					bot.writeJSON(bot.guild_prefix_dict, "data/guildprefix.json")
					await message.channel.send("prefix reset.", delete_after = 5)
				elif len(args) == 2 and args[0] == "set":
					if len(args[1]) > 1:
						await message.channel.send("Please enter a one-char prefix.", delete_after = 5)
					else:
						bot.guild_prefix_dict[str(message.guild.id)] = args[1]
						bot.writeJSON(bot.guild_prefix_dict, "data/guildprefix.json")
						await message.channel.send(f"prefix changed to `{args[1]}`.", delete_after = 5)
			else:
				await message.channel.send("Oops! It looks like you're not allowed to change the prefix.", delete_after = 5)
		
		if message.author.id in banned_users:
			return

		await bot.process_commands(message)
		ctx = await bot.get_context(message)

		if ctx.valid:
			bot.stats_dict[ctx.command.name] += 1
			bot.writeJSON(bot.stats_dict, "data/stats.json")

if __name__ == "__main__":
	bot.loadJSON = loadJSON
	bot.writeJSON = writeJSON
	bot.update_data = update_data
	bot.safe_servers = []
	bot.startup = startup
	bot.status_dict = {}

	for extension in [f for f in os.listdir("cogs") if isfile(join("cogs", f))]:
		bot.load_extension(f"cogs.{extension[:-3]}")
		print(f"{extension} module loaded")

@bot.event
async def on_command_error(ctx, error):
	if ctx.channel.id in bot.get_cog("Moderation").purge_channels:
		bot.get_cog("Moderation").purge_channels.remove(ctx.channel.id)

	if isinstance(error, commands.CommandNotFound) or isinstance(error, discord.HTTPException) or isinstance(error, discord.NotFound):
		pass
	elif isinstance(error, commands.CommandOnCooldown):
		await ctx.send(f"Oops! That command is on cooldown right now. Please wait **{round(error.retry_after, 3)}** seconds before trying again.", delete_after = error.retry_after)
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f"The required argument(s) {error.param} is/are missing.", delete_after = 5)
	elif isinstance(error, commands.DisabledCommand):
		await ctx.send("This command is disabled.", delete_after = 5)
	elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.BotMissingPermissions):
		await ctx.send(error, delete_after = 5)
	else:
		etype = type(error)
		trace = error.__traceback__

		try:
			await ctx.send("```" + "".join(traceback.format_exception(etype, error, trace, 999)) + "```".replace("C:\\Users\\William\\anaconda3\\lib\\site-packages\\", "").replace("D:\\my file of stuff\\discordbot\\", ""))
		except Exception:
			print("```" + "".join(traceback.format_exception(etype, error, trace, 999)) + "```".replace("C:\\Users\\William\\anaconda3\\lib\\site-packages\\", "").replace("D:\\my file of stuff\\discordbot\\", ""))

bot.run(os.getenv("DISCORDBOT_KEY"))
