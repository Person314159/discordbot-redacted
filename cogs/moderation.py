#!/usr/bin/python3
import re

import discord
from discord.ext import commands

from util.disabled import disabled


class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.purge_channels = []

	@commands.command()
	@disabled()
	@commands.has_permissions(ban_members = True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def ban(self, ctx, member):
		"""
		`{0}ban` __`Bans a member`__

		**Usage:** {0}ban <member mention or id>

		**Examples:**
		`{0}ban @abc#1234` bans abc
		"""

		if re.fullmatch(r"\d{18}", member):
			member = ctx.guild.get_member(int(member))

			if not member:
				return await ctx.send("User not found.", delete_after = 5)
		elif len(ctx.message.mentions) == 1:
			member = ctx.message.mentions[0]
		else:
			return await ctx.send("User not found.", delete_after = 5)

		await member.ban()

	@commands.command()
	@disabled()
	@commands.has_permissions(kick_members = True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def kick(self, ctx, member):
		"""
		`{0}kick` __`Kicks a member`__

		**Usage:** {0}kick <member mention or id>

		**Examples:**
		`{0}kick @abc#1234` kicks abc
		"""

		if re.fullmatch(r"\d{18}", member):
			member = ctx.guild.get_member(int(member))

			if not member:
				return await ctx.send("User not found.", delete_after = 5)
		elif len(ctx.message.mentions) == 1:
			member = ctx.message.mentions[0]
		else:
			return await ctx.send("User not found.", delete_after = 5)

		await member.kick()

	# in development
	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def purge(self, ctx, amount, *arg):
		"""
		`{0}purge` __`purges all messages satisfying conditions from the last specified number of messages in channel.`__

		Usage: {0}purge <amount of messages to look through> [user | \"string\" | reactions | type]

		**Options:**
		`user` - Only deletes messages sent by this user (supports mention or ID)
		`\"string\"` - Will delete messages containing \"string\"
		`reactions` - Will remove all reactions from messages
		`type` - One of Valid Types

		**Valid Types:**
		`text` - Is text only? (Ignores image or embeds)
		`links` - Contains links?
		`bots` - Was send by Bots?
		`images` - Contains images?
		`embeds` - Contains embeds?
		`mentions` - Contains user, role or everyone/here mentions?
		"""

		await ctx.message.delete()

		if ctx.channel.id in self.purge_channels:
			return await ctx.send("Purge is active in this channel already.", delete_after = 5)

		if ctx.author.id != 226878658013298690 and not ctx.author.guild_permissions.manage_messages:
			return await ctx.send("Oops! It looks like you don't have the permission to purge.", delete_after = 5)

		try:
			amount = int(amount)
		except ValueError:
			return await ctx.send("Please enter a positive integer number of messages to purge.", delete_after = 5)

		if amount > 10000:
			return await ctx.send("Please enter a smaller number to purge.", delete_after = 5)

		self.purge_channels.append(ctx.channel.id)

		if not arg:
			total_messages = await ctx.channel.purge(limit = amount)

			await ctx.send(f"**{len(total_messages)}** message{'s' if len(total_messages) > 1 else ''} cleared.", delete_after = 5)
		elif arg[0] == "reactions":
			messages = await ctx.channel.history(limit = amount).flatten()

			for i in messages:
				if i.reactions != []:
					await i.clear_reactions()

			await ctx.send(f"Reactions removed from the last {'' if amount == 1 else '**' + str(amount) + '**'} message{'s' if amount > 1 else ''}.", delete_after = 5)
		elif len(ctx.message.mentions) == 1 or re.fullmatch(r"\d{18}", arg[0]):
			if len(ctx.message.mentions) == 1:
				user = ctx.message.mentions[0]
			elif re.fullmatch(r"\d{18}", arg[0]):
				user = self.bot.get_user(int(arg[0]))
			else:
				return await ctx.send("You inputted an invalid user.", delete_after = 5)

			if not user:
				return await ctx.send("User not found.", delete_after = 5)

			def check(m):
				return m.author == user

			total_messages = await ctx.channel.purge(limit = amount, check = check)

			await ctx.send(f"**{len(total_messages)}** message{'s' if len(total_messages) > 1 else ''} from {user.display_name} purged.", delete_after = 5)
		elif arg[0] == "text":
			def no_image(m):
				return not m.embeds and not m.attachments

			total_messages = await ctx.channel.purge(limit = amount, check = no_image)

			await ctx.send(f"**{len(total_messages)}** text message{'s' if len(total_messages) > 1 else ''} purged.")
		elif arg[0] == "bots":
			def is_bot(m):
				return m.author.bot

			total_messages = await ctx.channel.purge(limit = amount, check = is_bot)

			await ctx.send(f"**{len(total_messages)}** bot message{'s' if len(total_messages) > 1 else ''} purged.", delete_after = 5)
		elif arg[0] == "images":
			def has_image(m):
				return m.attachments != []

			total_messages = await ctx.channel.purge(limit = amount, check = has_image)

			await ctx.send(f"**{len(total_messages)}** image message{'s' if len(total_messages) > 1 else ''} purged.", delete_after = 5)
		elif arg[0] == "embeds":
			def has_embed(m):
				return m.embeds != []

			total_messages = await ctx.channel.purge(limit = amount, check = has_embed)

			await ctx.send(f"**{len(total_messages)}** embed message{'s' if len(total_messages) > 1 else ''} purged.", delete_after = 5)
		elif arg[0] == "mentions":
			def has_mention(m):
				return m.mentions != []

			total_messages = await ctx.channel.purge(limit = amount, check = has_mention)

			message = await ctx.send(f"**{len(total_messages)}** mention message{'s' if len(total_messages) > 1 else ''} purged.", delete_after = 5)
		elif arg[0] == "links":
			def has_link(m):
				return bool(re.search(r"https?://[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+", m.content))

			total_messages = await ctx.channel.purge(limit = amount, check = has_link)

			message = await ctx.send(f"**{len(total_messages)}** link message{'s' if len(total_messages) > 1 else ''} purged.", delete_after = 5)
		elif len(arg) == 1:
			def has_string(m):
				return arg[0] in m.content

			total_messages = await ctx.channel.purge(limit = amount, check = has_string)

			message = await ctx.send(f"**{len(total_messages)}** message{'s' if len(total_messages) > 1 else ''} containing \"{arg[0]}\" purged.")
		else:
			await ctx.send("Please enter a valid filter for purge. Use `?help purge` to see a list.", delete_after = 5)

		self.purge_channels.remove(ctx.channel.id)

	@commands.command()
	@disabled()
	@commands.has_permissions(ban_members = True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def unban(self, ctx, user):
		"""
		`{0}unban` __`Unbans a user`__

		**Usage:** {0}unban <user id>

		**Examples:**
		`{0}unban 123456789123456789` unbans user
		"""

		try:
			user = self.bot.get_user(int(user))
		except TypeError:
			return await ctx.send("Please enter a valid user id.", delete_after = 5)

		if not user:
			return await ctx.send("User not found.", delete_after = 5)

		try:
			await ctx.guild.unban(user)
		except discord.NotFound:
			await ctx.send("User not banned.", delete_after = 5)

def setup(bot):
	bot.add_cog(Moderation(bot))
