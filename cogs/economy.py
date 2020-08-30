#!/usr/bin/python3
import asyncio
import random
import time

import discord
from discord.ext import commands

from util.disabled import disabled


class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def coins(self, ctx, *args):
		"""
		`{0}coins` __`Check balance or give credits`__

		**Usage:** {0}coins [user] [amount | check]

		**Examples:**
		`{0}coins` check your balance
		`{0}coins @user 9001` gives user 9001 coins
		`{0}coins @user check` check user's balance
		"""

		if not args:
			await ctx.send(f"You have **{self.bot.user_data[str(ctx.author.id)]['coins']}** coins.")
		elif len(args) == 2:
			if len(ctx.message.mentions) == 1:
				user_mentioned = ctx.message.mentions[0]

				if not user_mentioned.bot:
					if args[1] == "check":
						await ctx.send(f"**{user_mentioned.display_name}** has **{self.bot.user_data[str(user_mentioned.id)]['coins']}** coins.")
					else:
						try:
							transfer_amount = int(args[1])
						except ValueError:
							return await ctx.send("Please transfer a positive integer amount of coins to someone", delete_after = 5)

						if transfer_amount > 0:
							if transfer_amount > self.bot.user_data[str(ctx.author.id)]["coins"]:
								return await ctx.send("You don't have enough coins.", delete_after = 5)
							else:
								confirm_number = str(random.randint(1000, 9999))
								confirm = await ctx.send(f"do you want to transfer **{transfer_amount}** coins to **{user_mentioned.display_name}**? Type `{confirm_number}` to confirm.")

								def check(m):
									return m.channel == ctx.channel and m.author == ctx.author

								try:
									transfer_confirm = await self.bot.wait_for("message", timeout = 10, check = check)
								except asyncio.TimeoutError:
									await confirm.delete()
									return await ctx.send("Timed out. Transfer cancelled.", delete_after = 5)

								await confirm.delete()

								if transfer_confirm.content != confirm_number:
									return await ctx.send("Transfer invalid, please try again", delete_after = 5)
								else:
									self.bot.user_data[str(ctx.author.id)]["coins"] -= transfer_amount
									self.bot.user_data[str(user_mentioned.id)]["coins"] += transfer_amount
									await ctx.send(f"{transfer_amount} coins transferred. You have **{self.bot.user_data[str(ctx.author.id)]['coins']}** coins, and {user_mentioned.display_name} has **{self.bot.user_data[str(user_mentioned.id)]['coins']}** coins.")
									self.bot.update_data(ctx.author)
									self.bot.update_data(user_mentioned)
						else:
							await ctx.send("Please transfer a positive integer amount of coins to someone", delete_after = 5)
				else:
					await ctx.send("You cant use money commands on bots m8", delete_after = 5)
			else:
				await ctx.send("Please mention a user.", delete_after = 5)
		else:
			await ctx.send("Please enter the right number of arguments.", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def daily(self, ctx, *args):
		"""
		`{0}daily` __`Get daily coins or give to someone else`__

		**Usage:** {0}daily [user]

		**Examples:**
		`{0}daily` get your daily coins
		`{0}daily @user` give someone your daily coins
		"""

		user = ctx.author
		daily_cooldown = time.time() - self.bot.user_data[str(user.id)]["lastDailyTime"]

		if daily_cooldown >= 86400:
			if daily_cooldown >= 172800:
				self.bot.user_data[str(user.id)]["dailyStreak"] = 0

			if not args:
				daily_amount = 200 + 15 * self.bot.user_data[str(user.id)]["dailyStreak"]
				self.bot.user_data[str(user.id)]["coins"] += daily_amount
				self.bot.user_data[str(user.id)]["lastDailyTime"] = time.time()
				await ctx.send(f"**{daily_amount}** daily coins added.")
			elif len(args) == 1:
				if len(ctx.message.mentions) == 1:
					user_mentioned = ctx.message.mentions[0]

					if user_mentioned != ctx.author:
						daily_amount = 200 + 15 * self.bot.user_data[str(user.id)]["dailyStreak"] + random.randint(1, 100)
						self.bot.user_data[str(user_mentioned.id)]["coins"] += daily_amount
						self.bot.update_data(user_mentioned)
						self.bot.user_data[str(user.id)]["lastDailyTime"] = time.time()
						await ctx.send(f"**{daily_amount}** daily coins given to **{user_mentioned.display_name}**.")
					else:
						return await ctx.send("You can't daily yourself m8", delete_after = 5)
				else:
					return await ctx.send("Please mention a user.", delete_after = 5)

			self.bot.user_data[str(user.id)]["dailyStreak"] += 1
			self.bot.update_data(user)
		else:
			time_difference = 86400 - daily_cooldown
			m, s = divmod(time_difference, 60)
			h, m = divmod(m, 60)
			h = round(h)
			m = round(m)
			await ctx.send(f"Daily resets in **{h}** hours, **{m}** minutes, **{s}** seconds")

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def rich(self, ctx, *args):
		"""
		`{0}rich` __`Check richest people`__

		**Usage:** {0}rich [all]

		**Examples:**
		`{0}rich` richest users in server
		`{0}rich all` richest users globally
		"""

		rich_dict = {}

		if not args:
			for member in ctx.guild.members:
				if not member.bot:
					rich_dict[member] = self.bot.user_data[str(member.id)]["coins"]

			ranked = [i for i in sorted(rich_dict.items(), key = lambda x: x[1], reverse = True)[:10] if i[1]]
			desc = ""

			for j in ranked:
				if ranked.index(j) == 0:
					desc += f"🥇{j[1]} - {j[0].name}\n"
				elif ranked.index(j) == 1:
					desc += f"🥈{j[1]} - {j[0].name}\n"
				elif ranked.index(j) == 2:
					desc += f"🥉{j[1]} - {j[0].name}\n"
				else:
					desc += f"👏{j[1]} - {j[0].name}\n"

			embed = discord.Embed(title = "richest users in this server", description = desc)
			embed.set_footer(text = f"{ctx.guild.name} | add `all` to see global")
			await ctx.send(embed = embed)
		elif args[0] == "all":
			for guild in self.bot.guilds:
				for member in guild.members:
					if not member.bot:
						rich_dict[member] = self.bot.user_data[str(member.id)]["coins"]

			ranked = [i for i in sorted(rich_dict.items(), key = lambda x: x[1], reverse = True)[:10] if i[1]]
			desc = ""

			for j in ranked:
				if ranked.index(j) == 0:
					desc += f"🥇{j[1]} - {j[0].name}\n"
				elif ranked.index(j) == 1:
					desc += f"🥈{j[1]} - {j[0].name}\n"
				elif ranked.index(j) == 2:
					desc += f"🥉{j[1]} - {j[0].name}\n"
				else:
					desc += f"👏{j[1]} - {j[0].name}\n"

			embed = discord.Embed(title = "Top Global Richest Users", description = desc)
			embed.set_footer(text = f"Global Leaderboard")
			await ctx.send(embed = embed)
		else:
			await ctx.send("Please enter the right args", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def yu(self, ctx, usr, amount):
		"""
		`{0}yu` __`Transfer coins between bots using Yuniversal Electronic Exchange System`__

		**Usage:** {0}yu <bot mention> <amount>

		**Examples:**
		`{0}yu @rqBot#9160 1000` transfers 1000 🅱ot coins to rqBot
		"""

		rateconstant = 1
		taxconstant = 0

		transfer_bot = usr.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
		user = str(ctx.author.id)

		coins = self.bot.user_data[user]["coins"]

		if transfer_bot == str(self.bot.user.id):
			return await ctx.send(f"you cannot give yourself coins!", delete_after = 5)

		try:
			value = int(amount)
		except ValueError:
			if amount == "all":
				value = coins
			else:
				return await ctx.send(f"invalid coins value.", delete_after = 5)

		if value < 0 or value > 1000 and ctx.author.id not in [226878658013298690, 242403180653182978, 375445489627299851]:
			return await ctx.send(f"invalid coins value.", delete_after = 5)

		if coins < value:
			return await ctx.send(f"you do not have enough coins to do that!", delete_after = 5)

		transfer_bot = self.bot.get_user(int(transfer_bot))

		if not transfer_bot.bot:
			return await ctx.send(f"invalid destination bot.", delete_after = 5)

		if transfer_bot in ctx.guild.members:
			userx = f"{transfer_bot.name}#{transfer_bot.discriminator}"
			value -= taxconstant * value
			await ctx.send(f"{userx}|{ctx.author.id}|{value}|{rateconstant}")
			whichone = ""

			def check(msg):
				nonlocal whichone
				whichone = msg.content
				return msg.channel == ctx.message.channel and str(msg.author) == userx and (msg.content == f"{userx}|{ctx.author.id}|{value}|{rateconstant}" or msg.content == "{userx}|{ctx.author.id}|NULL")

			try:
				await self.bot.wait_for("message", check = check, timeout = 2.3)
			except:
				return await ctx.send(f"unable to contact {transfer_bot.name}", delete_after = 5)

			if whichone == f"{userx}|{ctx.author.id}|NULL":
				return

			await ctx.send(f"CONFIRMATION|{self.bot.user.name}#{self.bot.user.discriminator}")
			coins -= value
			self.bot.user_data[user]["coins"] = coins
			self.bot.update_data(ctx.author)
			return await ctx.send(f"**{value}** coins have been transferred to **{transfer_bot.name}**. You now have **{coins}** coins with 🅱ot.")
		else:
			await ctx.send(f"could not find this bot here.", delete_after = 5)

def setup(bot):
	bot.add_cog(Economy(bot))
