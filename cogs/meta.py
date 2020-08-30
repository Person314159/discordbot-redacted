#!/usr/bin/python3
import asyncio
import datetime
import os
import random
from os.path import isfile, join

import discord
from discord.ext import commands


class Meta(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(hidden = True)
	@commands.is_owner()
	async def die(self, ctx):
		if ctx.author.id == 226878658013298690:
			await self.bot.logout()

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def disable(self, ctx, *arg):
		"""
		`{0}disable` __`Disable commands`__

		**Usage:** {0}disable <command> <channel | server>

		**Examples:**
		`{0}disable latex channel` disables `latex` command in current channel
		`{0}disable slot server` disables `slot` command in entire server
		"""

		await ctx.message.delete()

		if ctx.author.guild_permissions.manage_guild or ctx.author.id == 226878658013298690:
			if len(arg) == 2:
				cmd = self.bot.get_command(arg[0])

				if cmd:
					confirm_number = str(random.randint(1000, 9999))

					if arg[1] == "channel":
						if ctx.channel.id in self.bot.command_toggle_dict[cmd.name]:
							return await ctx.send(f"`{cmd.name}` is already disabled in this channel.", delete_after = 5)

						confirm = await ctx.send(f"Are you sure you want to disable `{arg[0]}` in this channel? enter `{confirm_number}` to confirm.")

						def check(m):
							return m.channel == ctx.channel and m.author == ctx.author

						try:
							conf = await self.bot.wait_for("message", timeout = 10, check = check)
						except asyncio.TimeoutError:
							return await ctx.send("Timed out. Disable cancelled.", delete_after = 5)

						await confirm.delete()
						await conf.delete()

						if conf.content != confirm_number:
							return await ctx.send("Confirm invalid, please try again.", delete_after = 5)

						self.bot.command_toggle_dict[cmd.name].append(ctx.channel.id)
						await ctx.send(f"`{cmd.name}` disabled in this channel.", delete_after = 5)
					elif arg[1] == "server":
						if all([channel.id in self.bot.command_toggle_dict[cmd.name] for channel in ctx.guild.text_channels]):
							return await ctx.send(f"`{cmd.name}` is already disabled in this server.", delete_after = 5)

						confirm = await ctx.send(f"Are you sure you want to disable `{arg[0]}` in this server? enter `{confirm_number}` to confirm.")

						def check(m):
							return m.channel == ctx.channel and m.author == ctx.author

						try:
							conf = await self.bot.wait_for("message", timeout = 10, check = check)
						except asyncio.TimeoutError:
							return await ctx.send("Timed out. Disable cancelled.", delete_after = 5)

						await confirm.delete()
						await conf.delete()

						if conf.content != confirm_number:
							return await ctx.send("Confirm invalid, please try again.", delete_after = 5)

						self.bot.command_toggle_dict[cmd.name] += [channel.id for channel in ctx.guild.text_channels]
						await ctx.send(f"`{cmd.name}` disabled in this server.", delete_after = 5)
					else:
						await ctx.send("Please enter either channel or server to disable the command.", delete_after = 5)
				else:
					await ctx.send(f"Command \"{arg[0]}\" not found.", delete_after = 5)

				self.bot.writeJSON(self.bot.command_toggle_dict, "data/commandtoggle.json")
			else:
				await ctx.send("Please enter the right arguments.", delete_after = 5)

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def enable(self, ctx, *arg):
		"""
		`{0}enable` __`Enable commands`__

		**Usage:** {0}enable <command> <channel | server>

		**Examples:**
		`{0}enable latex channel` enables `latex` command in current channel
		`{0}enable slot server` enables `slot` command in entire server
		"""

		await ctx.message.delete()

		if ctx.author.guild_permissions.manage_guild or ctx.author.id == 226878658013298690:
			if len(arg) == 2:
				cmd = self.bot.get_command(arg[0])

				if cmd:
					confirm_number = str(random.randint(1000, 9999))

					if arg[1] == "channel":
						if ctx.channel.id not in self.bot.command_toggle_dict[cmd.name]:
							return await ctx.send(f"`{cmd.name}` is already enabled in this channel.", delete_after = 5)

						confirm = await ctx.send(f"Are you sure you want to enable `{arg[0]}` in this channel? enter `{confirm_number}` to confirm.")

						def check(m):
							return m.channel == ctx.channel and m.author == ctx.author

						try:
							conf = await self.bot.wait_for("message", timeout = 10, check = check)
						except asyncio.TimeoutError:
							return await ctx.send("Timed out. Enable cancelled.", delete_after = 5)

						await confirm.delete()
						await conf.delete()

						if conf.content != confirm_number:
							return await ctx.send("Confirm invalid, please try again.", delete_after = 5)

						self.bot.command_toggle_dict[cmd.name].remove(ctx.channel.id)
						await ctx.send(f"`{cmd.name}` enabled in this channel.", delete_after = 5)
					elif arg[1] == "server":
						if all([channel.id not in self.bot.command_toggle_dict[cmd.name] for channel in ctx.guild.text_channels]):
							return await ctx.send(f"`{cmd.name}` is already enabled in this server.", delete_after = 5)

						confirm = await ctx.send(f"Are you sure you want to enable `{arg[0]}` in this server? enter `{confirm_number}` to confirm.")

						def check(m):
							return m.channel == ctx.channel and m.author == ctx.author

						try:
							conf = await self.bot.wait_for("message", timeout = 10, check = check)
						except asyncio.TimeoutError:
							return await ctx.send("Timed out. Enable cancelled.", delete_after = 5)

						await confirm.delete()
						await conf.delete()

						if conf.content != confirm_number:
							return await ctx.send("Confirm invalid, please try again.", delete_after = 5)

						for channel in ctx.guild.text_channels:
							if channel.id in self.bot.command_toggle_dict[cmd.name]:
								self.bot.command_toggle_dict[cmd.name].remove(channel.id)

						await ctx.send(f"`{cmd.name}` enabled in this server.", delete_after = 5)
					else:
						await ctx.send("Please enter either channel or server to enable the command.", delete_after = 5)
				else:
					await ctx.send(f"Command \"{arg[0]}\" not found.", delete_after = 5)

				self.bot.writeJSON(self.bot.command_toggle_dict, "data/commandtoggle.json")
			else:
				await ctx.send("Please enter the right arguments.", delete_after = 5)

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def help(self, ctx, *arg):
		"""
		`{0}help` __`Returns list of commands or usage of command`__

		**Usage:** {0}help [optional cmd]

		**Examples:**
		`{0}help` [embed]
		"""

		fun = self.bot.get_cog("Fun")
		economy = self.bot.get_cog("Economy")
		moderation = self.bot.get_cog("Moderation")
		utility = self.bot.get_cog("Utility")
		meta = self.bot.get_cog("Meta")
		comic = self.bot.get_cog("Comic")

		if not arg:
			embed = discord.Embed(title = "🅱ot", description = "Smartwise bot. Commands:", colour = random.randint(0, 0xFFFFFF), timestamp = datetime.datetime.utcnow())
			embed.add_field(name = f"❗ Current Prefix: `{self.bot.command_prefix}`", value = "\u200b", inline = False)
			embed.add_field(name = "🤣 Fun", value = " ".join(f"`{i}`" for i in fun.get_commands() if not i.hidden and ctx.channel.id not in self.bot.command_toggle_dict.get(i.name, [])), inline = False)
			embed.add_field(name = "💰 Economy", value = " ".join(f"`{i}`" for i in economy.get_commands() if not i.hidden and ctx.channel.id not in self.bot.command_toggle_dict.get(i.name, [])), inline = False)
			embed.add_field(name = "🔨 Moderation", value = " ".join(f"`{i}`" for i in moderation.get_commands() if not i.hidden and ctx.channel.id not in self.bot.command_toggle_dict.get(i.name, [])), inline = False)
			embed.add_field(name = "🛠 Utility", value = " ".join(f"`{i}`" for i in utility.get_commands() if not i.hidden and ctx.channel.id not in self.bot.command_toggle_dict.get(i.name, [])), inline = False)
			embed.add_field(name = "Ⓜ Meta", value = " ".join(f"`{i}`" for i in meta.get_commands() if not i.hidden and ctx.channel.id not in self.bot.command_toggle_dict.get(i.name, [])), inline = False)
			embed.add_field(name = "📰 Comic", value = " ".join(f"`{i}`" for i in comic.get_commands() if not i.hidden and ctx.channel.id not in self.bot.command_toggle_dict.get(i.name, [])), inline = False)
			embed.add_field(name = "❌ Prefixless", value = "`current prefix` `prefix`", inline = False)
			embed.set_thumbnail(url = self.bot.user.avatar_url)
			embed.set_footer(text = f"Requested by {ctx.author.display_name}", icon_url = str(ctx.author.avatar_url))
			await ctx.send(embed = embed)
		else:
			help_command = arg[0]

			comm = self.bot.get_command(help_command)

			if not comm or not comm.help or comm.hidden:
				return await ctx.send("That command doesn't exist.", delete_after = 5)

			await ctx.send(comm.help.replace("{0}", self.bot.command_prefix))

	@commands.command(hidden = True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def reload(self, ctx, *modules):
		if ctx.author.id == 226878658013298690 or ctx.author.id == 420069040258547712:
			await ctx.message.delete()

			if not modules:
				modules = [f[:-3] for f in os.listdir("cogs") if isfile(join("cogs", f))]
			else:
				pass

			for extension in modules:
				Reload = await ctx.send(f"Reloading the {extension} module")
				try:
					self.bot.reload_extension(f"cogs.{extension}")
					self.bot.startup()
				except Exception as exc:
					return await ctx.send(exc)
				await Reload.edit(content = f"{extension} module reloaded.")

			self.bot.reload_extension("cogs.meta")

			await ctx.send("Done")

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def stats(self, ctx, *args):
		"""`{0}stats` __`Bot Statistics`__

		**Usage:** {0}stats [command]

		**Examples:**
		`{0}stats` [embed of top ten most used commands]
		`{0}stats help` returns number of uses of the help command globally
		"""

		if not args:
			embed = discord.Embed(title = "Top Most Used Commands", colour = random.randint(0, 0xFFFFFF))
			top_commands = [i for i in sorted(self.bot.stats_dict.items(), key = lambda x: x[1], reverse = True)[:10] if i[1] and not self.bot.get_command(i[0]).hidden]

			for i in top_commands:
				embed.add_field(name = i[0], value = i[1], inline = False)

			await ctx.send(embed = embed)
		elif len(args) == 1:
			if self.bot.get_command(args[0]):
				cmd = self.bot.get_command(args[0])

				if not cmd.hidden:
					embed = discord.Embed(title = cmd.name, description = f"Aliases: {', '.join(cmd.aliases) if cmd.aliases else 'None'}", colour = random.randint(0, 0xFFFFFF))
					embed.add_field(name = "Usage Stats", value = self.bot.stats_dict[cmd.name], inline = False)
					await ctx.send(embed = embed)
				else:
					await ctx.send("The requested command was not found.", delete_after = 5)
			else:
				await ctx.send("The requested command was not found.", delete_after = 5)

def setup(bot):
	bot.add_cog(Meta(bot))
