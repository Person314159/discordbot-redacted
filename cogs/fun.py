#!/usr/bin/python3
import asyncio
import bisect
import datetime
import html
import mimetypes
import random
import re
from fractions import Fraction
from io import BytesIO
from itertools import product
from math import *

import discord
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import requests
from discord.ext import commands
from googletrans import Translator, constants
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Point, Polygon

from util.disabled import disabled
from util.geography import *
from util.hungergames_data import *
from util.sum_of_three_palindromes import sum_of_three_palindromes


class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.channels_playing_hungergames = []
		self.channels_playing_mathrace = []
		self.ship_list = {tuple(i[0]): 1 for i in ships}
		self.seen_reddit_memes = []

		self.trash_list = ["👞", "🔋", "📎", "🗞", "🛒", "🔧", "👕", "👖", "🕶", "🎓"]
		self.common_list = ["🐟"]
		self.uncommon_list = ["🐠", "🐡", "🎣"]
		self.cash_list = ["💵", "💴", "💶", "💷", "💸", "💳"]
		self.fish_list = ["🦈", "🐙", "🐢", "🦀", "🐧", "🐊", "🐳", "🐋", "🦑", "🐬", "🦐"]
		self.rare_list = ["🅱", "🎁", "💰", "💍", "💎"]
		self.fish_dict = [("Garbage", self.trash_list), ("Common", self.common_list), ("Uncommon", self.uncommon_list), ("Cash", self.cash_list), ("Rarefish", self.fish_list), ("Rareitem", self.rare_list)]
		self.all_fish = [self.trash_list, self.common_list, self.uncommon_list, self.cash_list, self.fish_list, self.rare_list]

		self.cash_low = 1
		self.cash_high = 100
		self.fish_values = [6, 12, 20, 100, 500]
		self.rare_values = [1000, 2000, 10000, 50000, 250000]

		self.fish_dist = [0, 1, 2, 10, 50, 250, 1000]
		self.fish_total = self.fish_dist[-1]
		self.distributions = [a / self.fish_total for a in self.fish_dist[:-1]]
		self.rare_dist = [0, 1, 5, 25, 125, 250]
		self.rare_total = self.rare_dist[-1]
		self.rare_distributions = [b / self.rare_total for b in self.rare_dist[:-1]]

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def bing(self, ctx):
		"""
		`{0}bing` __`Pings a random person in server. May trigger`__

		**Usage:** {0}bing

		**Examples:**
		`{0}bing` @some_bub#1234
		"""

		if ctx.author.id == 226878658013298690 or ctx.author.permissions_in(ctx.channel).administrator:
			user = random.choice(ctx.guild.members)
			await ctx.message.delete()
			await ctx.send(user.mention, delete_after = 1)

	@commands.command(name = "8ball")
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def eightball(self, ctx):
		"""
		`{0}8ball` __`Asks the 8ball a question`__

		**Usage:** {0}8ball <question>

		**Examples:**
		`{0}8ball Is 🅱ot dumb?` Definitely.
		"""

		eightball_list = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Maybe.", "🅱oi I wouldn't know.", "Use your own brain...if you have one.", "Go outside instead.", "Certainly not.", "Decidedly not.", "Very doubtful.", "Definitely not.", "Don't rely on it.", "As I see it, no.", "Most likely not.", "Outlook not so good.", "No.", "Signs point to no."]
		reply = random.choice(eightball_list)
		await ctx.send(f"🎱 🤔 | {reply}")

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def deletesnipe(self, ctx, *number):
		"""
		`{0}deletesnipe` __`Returns deleted message in channel`__

		**Usage:** {0}deletesnipe [int]

		**Examples:**
		`{0}deletesnipe` [most recent deleted message]
		`{0}deletesnipe 2` [2nd most recent deleted message]
		"""

		if not number:
			number = 0
		else:
			try:
				number = int(number[0]) - 1
			except ValueError:
				return await ctx.send(f"Please enter an integer between 1 and {len(self.bot.channel_deletesnipe_dict[str(ctx.channel.id)])}", delete_after = 5)

		if not self.bot.channel_deletesnipe_dict[str(ctx.channel.id)]:
			return await ctx.send("There's nothing to deletesnipe!")
		elif number not in range(len(self.bot.channel_deletesnipe_dict[str(ctx.channel.id)])):
			return await ctx.send(f"Please enter an integer between 1 and {len(self.bot.channel_deletesnipe_dict[str(ctx.channel.id)])}", delete_after = 5)
		else:
			channel_deletesnipe_info = self.bot.channel_deletesnipe_dict[str(ctx.channel.id)][number]
			author = channel_deletesnipe_info[0]
			avatar_url = channel_deletesnipe_info[1]
			timestamp = datetime.datetime.fromtimestamp(channel_deletesnipe_info[2])
			deleted_message = channel_deletesnipe_info[3]
			embed = discord.Embed(title = "Deleted Message:", description = deleted_message, colour = random.randint(0, 0xFFFFFF), timestamp = timestamp)
			embed.set_author(name = author, icon_url = avatar_url)

			await ctx.send(embed = embed)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def editsnipe(self, ctx, *number):
		"""
		`{0}editsnipe` __`Returns original of edited message in channel`__

		**Usage:** {0}editsnipe [int]

		**Examples:**
		`{0}editsnipe` [edited and original message of most recent edit]
		`{0}editsnipe 2` [edited and original message of second most recent edit]
		"""

		if not number:
			number = 0
		else:
			try:
				number = int(number[0]) - 1
			except ValueError:
				return await ctx.send(f"Please enter an integer between 1 and {len(self.bot.channel_editsnipe_dict[str(ctx.channel.id)])}", delete_after = 5)

		if not self.bot.channel_editsnipe_dict[str(ctx.channel.id)]:
			return await ctx.send("There's nothing to editsnipe!")
		elif number not in range(len(self.bot.channel_editsnipe_dict[str(ctx.channel.id)])):
			return await ctx.send(f"Please enter an integer between 1 and {len(self.bot.channel_editsnipe_dict[str(ctx.channel.id)])}.", delete_after = 5)
		else:
			channel_editsnipe_info = self.bot.channel_editsnipe_dict[str(ctx.channel.id)][number]
			author = channel_editsnipe_info[0]
			avatar_url = channel_editsnipe_info[1]
			timestamp = datetime.datetime.fromtimestamp(channel_editsnipe_info[2])
			original_message = channel_editsnipe_info[3]
			new_message = channel_editsnipe_info[4]
			embed = discord.Embed(title = "Original Message", description = original_message, colour = random.randint(0, 0xFFFFFF), timestamp = timestamp)
			embed.add_field(name = "New Message", value = new_message, inline = False)
			embed.set_author(name = author, icon_url = avatar_url)
			await ctx.send(embed = embed)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def egyptian(self, ctx):
		"""
		`{0}egyptian` __`Returns a fraction as a sum of unit fractions`__

		**Usage:** {0}egyptian <fraction>

		**Examples:**
		`{0}egyptian 5/121` 5/121 = 1/25 + 1/1225 + 1/3577 + 1/7081 + 1/11737
		"""

		arg = ctx.message.content[len(self.bot.command_prefix) + 9:].replace(" ", "")

		try:
			fraction = Fraction(arg)
		except ValueError:
			return await ctx.send("Please input a valid fraction.", delete_after = 5)

		p = fraction.numerator
		q = fraction.denominator
		egyptian_fraction = f"{arg} ="

		def golomb(nr, dr):
			ef = []

			def egcd(a, b):
				if not a:
					return (b, 0, 1)
				else:
					g, y, x = egcd(b % a, a)
					return (g, x - (b // a) * y, y)

			def modinv(a, m):
				g, x, y = egcd(a, m)
				return x % m

			while nr != 1:
				p_1 = modinv(nr, dr)
				ef.append(p_1 * dr)
				nr = (nr * p_1 - 1) // dr
				dr = p_1

				if gcd(nr, dr) != 1:
					nr /= gcd(nr, dr)
					dr /= gcd(nr, dr)

			ef.append(dr)
			ef.reverse()
			return ef

		try:
			if p < 0 or not q:
				return await ctx.send("Please input a valid fraction.", delete_after = 5)
			elif p >= q:
				go = []
				egyptian_fraction += f" {p // q} + "

				if p % q:
					p -= q * (p // q)

					go = golomb(p, q)
				else:
					return await ctx.send(f"{arg} = {round(eval(arg))}")
			else:
				go = golomb(p, q)
		except Exception as error:
			return await ctx.send(error, delete_after = 5)

		egyptian_fraction += " + ".join(f"1/{go[i]}" for i in range(len(go)))

		if len(egyptian_fraction) > 2000:
			if len(egyptian_fraction) > 10000:
				await ctx.send("result too large")
				with open("egyptian.txt", "w") as f:
					f.write(egyptian_fraction)
			else:
				while len(egyptian_fraction) > 2000:
					await ctx.send(egyptian_fraction[:2000].rsplit(" + ", 1)[0])
					egyptian_fraction = egyptian_fraction[:2000].rsplit(" + ", 1)[1] + egyptian_fraction[2000:]

				await ctx.send(egyptian_fraction)
		else:
			await ctx.send(egyptian_fraction)

	@commands.command()
	@disabled()
	@commands.has_permissions(administrator = True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def everyoneping(self, ctx):
		"""
		`{0}everyoneping` __`Pings everyone in the server. Limited to admins only.`__

		**Usage:** {0}everyoneping

		**Examples:**
		`{0}everyoneping` [list of pings]
		"""

		msg = ""

		for user in ctx.guild.members:
			if not user.bot:
				msg += f"{user.mention} "

		if len(msg) > 2000:
			if len(msg) > 10000:
				await ctx.send("result too large")
			else:
				while len(msg) > 2000:
					await ctx.send(msg[:2000].rsplit(1)[0])
					msg = msg[:2000].rsplit(1)[1] + msg[2000:]

				await ctx.send(msg)
		else:
			await ctx.send(msg)


	@commands.group()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def fish(self, ctx):
		"""
		`{0}fish` __`Fish commands`__

		**Usage:** {0}fish [(inv)entory | rarefish | rareitems | redeem <rare> [amount] | sell (<type> [amount] | all) | odds]

		**Examples:**
		`{0}fish` fishes
		`{0}fish inv` checks your inventory
		`{0}fish redeem 🐙` redeems an octopus for **500** coins
		`{0}fish rarefish/rareitems` checks your collections of rare things
		`{0}fish sell garbage` sells all your garbage for **6** coins per item
		`{0}fish sell all` sells everything in your inventory (not including rares)
		`{0}fish odds` returns list of current fish probabilities
		"""

		user = ctx.author
		cost = 10

		if not ctx.subcommand_passed:
			if self.bot.user_data[str(user.id)]["coins"] >= cost:
				self.bot.user_data[str(user.id)]["coins"] -= cost
				msg = f"🎣 | **{ctx.author.name}#{ctx.author.discriminator}, you caught: "
				x = random.uniform(0, 1)
				index = len(self.all_fish) - bisect.bisect_left(self.distributions, x)

				if self.fish_dict[index][0] != "Rareitem":
					fish = random.choice(self.all_fish[index])
					msg += f"{fish}!**"

					if self.fish_dict[index][0] != "Rarefish":
						if self.fish_dict[index][0] == "Cash":
							value = self.fish_values[3]
							if fish == "💳":
								value += 500
							self.bot.user_data[str(user.id)]["coins"] += value
							msg += f" You gained **{value}** coins!"
						else:
							self.bot.user_data[str(user.id)]["fishInv"][self.fish_dict[index][0]] += 1
					else:
						self.bot.user_data[str(user.id)]["fishInv"]["Rarefish"][fish] += 1

					self.bot.update_data(user)
				else:
					y = random.uniform(0, 1)
					fish = self.rare_list[len(self.rare_list) - bisect.bisect_left(self.rare_distributions, y)]
					self.bot.user_data[str(user.id)]["fishInv"]["Rareitem"][fish] += 1
					self.bot.update_data(user)

				msg += f" You paid **{cost}** coins for casting."
				await ctx.send(msg)
			else:
				await ctx.send("Oops! It looks like you don't have enough coins.", delete_after = 5)
		elif not ctx.invoked_subcommand:
			await ctx.send("Please input a valid fish command.", delete_after = 5)

	@fish.command(aliases = ["inv"])
	async def inventory(self, ctx):
		user = ctx.author
		nick = user.display_name
		embed = discord.Embed(title = f"{nick}'s fish inventory")
		embed.add_field(name = "Garbage", value = str(self.bot.user_data[str(user.id)]["fishInv"]["Garbage"]), inline = False)
		embed.add_field(name = "Common", value = str(self.bot.user_data[str(user.id)]["fishInv"]["Common"]), inline = False)
		embed.add_field(name = "Uncommon", value = str(self.bot.user_data[str(user.id)]["fishInv"]["Uncommon"]), inline = False)
		await ctx.send(embed = embed)

	@fish.command()
	async def rarefish(self, ctx):
		user = ctx.author
		nick = user.display_name
		embed = discord.Embed(title = f"{nick}'s rarefish inventory")

		for i in self.bot.user_data[str(user.id)]["fishInv"]["Rarefish"].keys():
			if self.bot.user_data[str(user.id)]["fishInv"]["Rarefish"][i]:
				embed.add_field(name = i, value = str(self.bot.user_data[str(user.id)]["fishInv"]["Rarefish"][i]), inline = False)

		await ctx.send(embed = embed)

	@fish.command()
	async def rareitems(self, ctx):
		user = ctx.author
		nick = user.display_name
		embed = discord.Embed(title = f"{nick}'s rareitem inventory")

		for i in self.bot.user_data[str(user.id)]["fishInv"]["Rareitem"].keys():
			if self.bot.user_data[str(user.id)]["fishInv"]["Rareitem"][i]:
				embed.add_field(name = i, value = str(self.bot.user_data[str(user.id)]["fishInv"]["Rareitem"][i]), inline = False)

		await ctx.send(embed = embed)

	@fish.command()
	async def odds(self, ctx):
		await ctx.send(f"current odds and values:\n" +
						"\n".join(f"**{self.fish_dict[i][0]}** ({' '.join(self.fish_dict[i][1])}): {Fraction(self.fish_dist[6 - i] - self.fish_dist[6 - i - 1], self.fish_total)}, {self.fish_values[i]} coins" for i in [0, 1, 2, 4]) +
						f"\n**Cash** ({' '.join(self.cash_list)}): {Fraction(self.fish_dist[3] - self.fish_dist[2], self.fish_total)}, {self.cash_low}-{self.cash_high + 500} coins\n" +
						"\n".join(f"{self.rare_list[i]}: {Fraction(self.rare_dist[5 - i] - self.rare_dist[5 - i - 1], self.rare_total) * (self.fish_dist[1] - self.fish_dist[0]) / self.fish_total}, {self.rare_values[i]} coins" for i in range(len(self.rare_list))))

	@fish.command()
	async def sell(self, ctx, *args):
		user = ctx.author

		if not args:
			return await ctx.send("Please input something to sell.", delete_after = 5)
		elif len(args) == 1:
			if args[0] == "garbage" or args[0] == "trash":
				amount = self.bot.user_data[str(user.id)]["fishInv"]["Garbage"]

				if amount:
					profit = self.fish_values[0] * amount
					self.bot.user_data[str(user.id)]["fishInv"]["Garbage"] = 0
					await ctx.send(f"🎣 | **{ctx.author.name}#{ctx.author.discriminator}**, sold **{amount}** trash for **{profit}** coins.")
				else:
					return await ctx.send("You do not have any of this item in your inventory.", delete_after = 5)
			elif args[0] == "common":
				amount = self.bot.user_data[str(user.id)]["fishInv"]["Common"]

				if amount:
					profit = self.fish_values[1] * amount
					self.bot.user_data[str(user.id)]["fishInv"]["Common"] = 0
					await ctx.send(f"🎣 | **{ctx.author.name}#{ctx.author.discriminator}**, sold **{amount}** common fish for **{profit}** coins.")
				else:
					return await ctx.send("You do not have any of this item in your inventory.", delete_after = 5)
			elif args[0] == "uncommon":
				amount = self.bot.user_data[str(user.id)]["fishInv"]["Uncommon"]

				if amount:
					profit = self.fish_values[2] * amount
					self.bot.user_data[str(user.id)]["fishInv"]["Uncommon"] = 0
					await ctx.send(f"🎣 | **{ctx.author.name}#{ctx.author.discriminator}**, sold **{amount}** uncommon fish for **{profit}** coins.")
				else:
					return await ctx.send("You do not have any of this item in your inventory.", delete_after = 5)
			elif args[0] == "all":
				profit = 0
				garbage = self.bot.user_data[str(user.id)]["fishInv"]["Garbage"]
				common = self.bot.user_data[str(user.id)]["fishInv"]["Common"]
				uncommon = self.bot.user_data[str(user.id)]["fishInv"]["Uncommon"]

				if garbage + common + uncommon:
					if garbage:
						profit += self.fish_values[0] * garbage
						self.bot.user_data[str(user.id)]["fishInv"]["Garbage"] = 0

					if common:
						profit += self.fish_values[1] * common
						self.bot.user_data[str(user.id)]["fishInv"]["Common"] = 0

					if uncommon:
						profit += self.fish_values[2] * uncommon
						self.bot.user_data[str(user.id)]["fishInv"]["Uncommon"] = 0

					await ctx.send(f"🎣 | **{ctx.author.name}#{ctx.author.discriminator}**, sold all your stuff for **{profit}** coins.")
				else:
					return await ctx.send("You do not have anything in your inventory.", delete_after = 5)
			else:
				return await ctx.send("Oops! It looks like you entered wrong arguments.", delete_after = 5)
		elif len(args) == 2:
			try:
				amount = int(args[1])
			except ValueError:
				return await ctx.send("Please enter a positive integer number of items to sell.", delete_after = 5)

			if amount:
				if args[0] == "garbage" or args[0] == "trash":
					if self.bot.user_data[str(user.id)]["fishInv"]["Garbage"] >= amount:
						profit = 6 * amount
						self.bot.user_data[str(user.id)]["fishInv"]["Garbage"] -= amount
						await ctx.send(f"🎣 | **{ctx.author.name}#{ctx.author.discriminator}**, sold **{amount}** trash for **{profit}** coins.")
					else:
						return await ctx.send("You can't sell that many of this item.", delete_after = 5)
				elif args[0] == "common":
					if self.bot.user_data[str(user.id)]["fishInv"]["Common"] >= amount:
						profit = 12 * amount
						self.bot.user_data[str(user.id)]["fishInv"]["Common"] -= amount
						await ctx.send(f"🎣 | **{ctx.author.name}#{ctx.author.discriminator}**, sold **{amount}** common fish for **{profit}** coins.")
					else:
						return await ctx.send("You can't sell that many of this item.", delete_after = 5)
				elif args[0] == "uncommon":
					if self.bot.user_data[str(user.id)]["fishInv"]["Uncommon"] >= amount:
						profit = 20 * amount
						self.bot.user_data[str(user.id)]["fishInv"]["Uncommon"] -= amount
						await ctx.send(f"🎣 | **{ctx.author.name}#{ctx.author.discriminator}**, sold **{amount}** uncommon fish for **{profit}** coins.")
					else:
						return await ctx.send("You can't sell that many of this item.", delete_after = 5)
				else:
					return await ctx.send("Oops! It looks like you entered wrong arguments.", delete_after = 5)
			else:
				return await ctx.send("Please enter a positive integer number of items to sell.", delete_after = 5)

		self.bot.user_data[str(user.id)]["coins"] += profit
		self.bot.update_data(user)

	@fish.command()
	async def redeem(self, ctx, *args):
		user = ctx.author

		if not args:
			return await ctx.send("Please input something to redeem.", delete_after = 5)
		elif len(args) == 1:
			if args[0] in self.fish_list:
				amount = self.bot.user_data[str(user.id)]["fishInv"]["Rarefish"][args[0]]

				if amount:
					profit = self.fish_values[-1]
					self.bot.user_data[str(user.id)]["fishInv"]["Rarefish"][args[0]] -= 1
					await ctx.send(f"🎣 | **{ctx.author.name}#{ctx.author.discriminator}**, redeemed {args[0]} for **{profit}** coins.")
				else:
					return await ctx.send("You do not have any of this item in your inventory.", delete_after = 5)
			elif args[0] in self.rare_list:
				amount = self.bot.user_data[str(user.id)]["fishInv"]["Rareitem"][args[0]]

				if amount:
					profit = self.rare_values[self.rare_list.index(args[0])]
					self.bot.user_data[str(user.id)]["fishInv"]["Rareitem"][args[0]] -= 1
					await ctx.send(f"🎣 | **{ctx.author.name}#{ctx.author.discriminator}**, redeemed {args[0]} for **{profit}** coins.")
				else:
					return await ctx.send("You do not have any of this item in your inventory.", delete_after = 5)
			else:
				return await ctx.send("Oops! It looks like you entered wrong arguments.", delete_after = 5)
		elif len(args) == 2:
			try:
				amount = int(args[1])
			except ValueError:
				return await ctx.send("Please enter a positive integer number of items to redeem.", delete_after = 5)

			if amount:
				if args[0] in self.fish_list:
					if self.bot.user_data[str(user.id)]["fishInv"]["Rarefish"][args[0]] >= amount:
						profit = self.fish_values[-1] * amount
						self.bot.user_data[str(user.id)]["fishInv"]["Rarefish"][args[0]] -= amount
						await ctx.send(f"🎣 | **{ctx.author.name}#{ctx.author.discriminator}**, redeemed **{amount}** {args[0]} for **{profit}** coins.")
					else:
						return await ctx.send("You can't redeem that many of this item.", delete_after = 5)
				elif args[0] in self.rare_list:
					if self.bot.user_data[str(user.id)]["fishInv"]["Rareitem"][args[0]] >= amount:
						profit = self.rare_values[self.rare_list.index(args[0])] * amount
						self.bot.user_data[str(user.id)]["fishInv"]["Rareitem"][args[0]] -= amount
						await ctx.send(f"🎣 | **{ctx.author.name}#{ctx.author.discriminator}**, redeemed **{amount}** {args[0]} for **{profit}** coins.")
					else:
						return await ctx.send("You can't redeem that many of this item.", delete_after = 5)
				else:
					return await ctx.send("Oops! It looks like you entered wrong arguments.", delete_after = 5)
			else:
				return await ctx.send("Please enter a positive integer number of items to redeem.", delete_after = 5)

		self.bot.user_data[str(user.id)]["coins"] += profit
		self.bot.update_data(user)


	@commands.command()
	@disabled()
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def geography(self, ctx, *args):
		"""
		`{0}geography` __`Geography trivia`__

		**Usage:** {0}geography [category] [difficulty]

		**Categories:** endonym, capital, languages, currency, peak, flag

		**Examples:**
		`{0}geography` any category and difficulty
		`{0}geography flag` any difficulty from flags
		`{0}geography hard` any category in hard
		`{0}geography flag hard` self explanatory
		note: args are exchangeable
		"""

		categories = ["Endonym", "Capital", "Area", "Borders", "Languages", "Currency", "Peak", "Flag"]
		difficulties = ["Easy", "Medium", "Hard"]

		async def ask(category, difficulty):
			user = ctx.author
			question = ""
			answers = "*You have 10 seconds to answer.*\n\n"

			if category == 0:
				if difficulty == "Easy":
					country = random.choice(easy_name)
					rest = list(country_dict.keys())
					rest.remove(country)
					choices = random.sample(rest, 3) + [country]
				elif difficulty == "Medium":
					country = random.choice(medium_name)
					hard_list = []

					for sublist in hard_name:
						if isinstance(sublist, list):
							for item in sublist:
								hard_list.append(item)
						else:
							hard_list.append(sublist)

					rest = medium_name + hard_list
					rest.remove(country)
					choices = random.sample(rest, 3) + [country]
				else:
					hard_list = []

					for sublist in hard_name:
						if isinstance(sublist, list):
							for item in sublist:
								hard_list.append(item)
						else:
							hard_list.append(sublist)

					country = random.choice(hard_list)
					rest = hard_list
					rest.remove(country)

					for sublist in hard_name:
						if isinstance(sublist, list):
							if country in sublist:
								rest = []

								for i in sublist:
									rest.append(i)

								rest.remove(country)

					if len(rest) >= 3:
						choices = random.sample(rest, 3) + [country]
					else:
						choices = [country] + rest + random.sample(list(set(hard_list) - set([country] + rest)), 3 - len(rest))

				question = f"Which country's citizens call their country **{country_dict[country][category]}**?"
				random.shuffle(choices)
				answers += f"1) *{choices[0]}*\n2) *{choices[1]}*\n3) *{choices[2]}*\n4) *{choices[3]}*"
			elif category == 1:
				if difficulty == "Easy":
					country = random.choice(easy_capital)
					rest = list(country_dict.keys())
				elif difficulty == "Medium":
					country = random.choice(medium_capital)
					rest = medium_capital + hard_capital
				else:
					country = random.choice(hard_capital)
					rest = hard_capital[:]

				rest.remove(country)
				question = f"Which country's capital is **{country_dict[country][category]}**?"
				choices = random.sample(rest, 3) + [country]
				random.shuffle(choices)
				answers += f"1) *{choices[0]}*\n2) *{choices[1]}*\n3) *{choices[2]}*\n4) *{choices[3]}*"
			elif category == 2:
				return

				#if difficulty == "Easy":
				#elif difficulty == "Medium":
				#else:
			elif category == 3:
				return

				#if difficulty == "Easy":
				#elif difficulty == "Medium":
				#else:
			elif category == 4:
				if difficulty == "Easy":
					country = random.choice(easy_language)
					rest = list(country_dict.keys())
				elif difficulty == "Medium":
					country = random.choice(medium_language)
					rest = medium_language + hard_language
				else:
					country = random.choice(hard_language)
					rest = hard_language[:]

				for i in rest:
					if country_dict[i][category] == country_dict[country][category]:
						rest.remove(i)

				question = f"Which country's official language(s) is/are **{country_dict[country][category]}**?"
				choices = random.sample(rest, 3) + [country]
				random.shuffle(choices)
				answers += f"1) *{choices[0]}*\n2) *{choices[1]}*\n3) *{choices[2]}*\n4) *{choices[3]}*"
			elif category == 5:
				if difficulty == "Easy":
					country = random.choice(easy_currency)
					rest = list(country_dict.keys())
				elif difficulty == "Medium":
					country = random.choice(medium_currency)
					rest = medium_currency + hard_currency
				else:
					country = random.choice(hard_currency)
					rest = hard_currency[:]

				for i in rest:
					if country_dict[i][category] == country_dict[country][category]:
						rest.remove(i)

				question = f"Which country's currency(ies) is/are **{country_dict[country][category]}**?"
				choices = random.sample(rest, 3) + [country]
				random.shuffle(choices)
				answers += f"1) *{choices[0]}*\n2) *{choices[1]}*\n3) *{choices[2]}*\n4) *{choices[3]}*"
			elif category == 6:
				if difficulty == "Easy":
					country = random.choice(easy_peak)
					rest = list(country_dict.keys())
				elif difficulty == "Medium":
					country = random.choice(medium_peak)
					rest = medium_peak + hard_peak
				else:
					country = random.choice(hard_peak)
					rest = hard_peak[:]

				for i in rest:
					if country_dict[i][category] == country_dict[country][category]:
						rest.remove(i)

				question = f"Which country's highest point is **{country_dict[country][category]}**?"
				choices = random.sample(rest, 3) + [country]
				random.shuffle(choices)
				answers += f"1) *{choices[0]}*\n2) *{choices[1]}*\n3) *{choices[2]}*\n4) *{choices[3]}*"
			elif category == 7:
				if difficulty == "Easy":
					country = random.choice(easy_flag)
					rest = list(country_dict.keys())
					rest.remove(country)
					choices = random.sample(rest, 3) + [country]
				elif difficulty == "Medium":
					country = random.choice(medium_flag)
					hard_list = []

					for sublist in hard_name:
						if isinstance(sublist, list):
							for item in sublist:
								hard_list.append(item)
						else:
							hard_list.append(sublist)

					rest = medium_flag + hard_list
					rest.remove(country)
					choices = random.sample(rest, 3) + [country]
				else:
					hard_list = []

					for sublist in hard_flag:
						if isinstance(sublist, list):
							for item in sublist:
								hard_list.append(item)
						else:
							hard_list.append(sublist)

					country = random.choice(hard_list)
					rest = hard_list
					rest.remove(country)

					for sublist in hard_flag:
						if isinstance(sublist, list):
							if country in sublist:
								rest = []

								for i in sublist:
									rest.append(i)

								rest.remove(country)

					if len(rest) >= 3:
						choices = random.sample(rest, 3) + [country]
					else:
						choices = [country] + rest + random.sample(list(set(hard_list) - set([country] + rest)), 3 - len(rest))

				question = f"Which country's flag is this?"
				random.shuffle(choices)
				answers += f"1) *{choices[0]}*\n2) *{choices[1]}*\n3) *{choices[2]}*\n4) *{choices[3]}*"

			if difficulty == "Easy":
				earned = 5
			elif difficulty == "Medium":
				earned = 10
			else:
				earned = 15

			embed = discord.Embed(title = question, description = answers)
			embed.add_field(name = "Difficulty", value = f"`{difficulty}`", inline = True)
			embed.add_field(name = "Category", value = f"`{categories[category]}`", inline = True)
			embed.add_field(name = "Value", value = str(earned), inline = True)

			if category == 7:
				embed.set_thumbnail(url = country_dict[country][category])

			await ctx.send(embed = embed)

			def check(m):
				return m.channel == ctx.channel and m.author == ctx.author

			try:
				answer = await self.bot.wait_for("message", timeout = 10, check = check)
			except asyncio.TimeoutError:
				await ctx.send("Timed out.", delete_after = 5)
				return await ctx.send(f"Incorrect. The correct answer is {country}.")

			try:
				index = int(answer.content) - 1
			except ValueError:
				return await ctx.send(f"Incorrect. The correct answer is {country}.")

			if index == choices.index(country):
				await ctx.send(f"Correct! You earned **{earned}** coins.")
				self.bot.user_data[str(user.id)]["coins"] += earned
				self.bot.update_data(user)
			else:
				await ctx.send(f"Incorrect. The correct answer is {country}.")

		if not args:
			category = random.choice([0, 1, 4, 5, 6, 7]) #to be fixed once we get all data
			difficulty = random.choice(difficulties)
			await ask(category, difficulty)
		elif len(args) == 1:
			arg = args[0].lower().capitalize()

			if arg in categories:
				difficulty = random.choice(difficulties)
				await ask(categories.index(arg), difficulty)
			elif arg in difficulties:
				category = random.choice([0, 1, 4, 5, 6, 7])
				await ask(category, arg)
			else:
				return await ctx.send("Please input a valid geography category.", delete_after = 5)
		elif len(args) == 2:
			arg1 = args[0].lower().capitalize()
			arg2 = args[1].lower().capitalize()

			if arg1 in difficulties and arg2 in categories or arg2 in difficulties and arg1 in categories:
				if arg1 in difficulties:
					await ask(categories.index(arg2), arg1)
				else:
					await ask(categories.index(arg1), arg2)
			else:
				return await ctx.send("You inputted a wrong argument.", delete_after = 5)
		else:
			return await ctx.send("You inputted too many arguments.", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def gtcycle(self, ctx, *args):
		"""
		`{0}gtcycle` __`Google Translate Cycler`__

		**Usage:** {0}gtcycle <number of languages | all> <text>

		**Examples:**
		`{0}gtcycle all hello!` cycles through all languages with input text "hello!"
		`{0}gtcycle 12 hello!` cycles through 12 languages with input text "hello!"
		"""

		lang_list = list(constants.LANGUAGES)
		random.shuffle(lang_list)

		if len(args) < 2:
			return await ctx.send("Please enter the correct number of arguments.", delete_after = 5)

		limit = args[0]
		txt = " ".join(args[1:])

		if limit != "all":
			try:
				limit = int(limit)

				if limit < 1 or limit > len(constants.LANGUAGES):
					raise ValueError
			except ValueError:
				return await ctx.send(f"Please send a positive integer number of languages less than {len(constants.LANGUAGES)} to cycle.", delete_after = 5)
		else:
			limit = len(lang_list)

		lang_list = ["en"] + lang_list[:limit] + ["en"]
		translator = Translator()

		for i in range(len(lang_list) - 1):
			translation = translator.translate(txt, src = lang_list[i], dest = lang_list[i + 1])
			txt = translation.text

		if len(txt) > 2000:
			if len(txt) > 10000:
				await ctx.send("Result too large.")
			else:
				while len(txt) > 2000:
					await ctx.send(txt[:2000])
					txt = txt[2000:]

				await ctx.send(txt)
		else:
			await ctx.send(txt)
		return

	@commands.command(aliases = ["hg"])
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def hungergames(self, ctx):
		"""
		`{0}hungergames` __`Hunger Games generator`__
		**Aliases**: hg

		**Usage:** {0}hungergames <person 1 | person 2 | etc.>

		**Examples:**
		`{0}hungergames a | b | c` generate Hunger Games scenario
		"""

		if ctx.channel.id in self.channels_playing_hungergames:
			return await ctx.send("There's already an active game on this channel.", delete_after = 5)

		self.channels_playing_hungergames.append(ctx.channel.id)
		args = ctx.message.content[len(self.bot.command_prefix) + len(ctx.invoked_with) + 1:].split(" | ")

		if len(args) == 1:
			if args[0].lower() == "server":
				args = [user.display_name for user in ctx.guild.members] if len(ctx.guild.members) <= 50 else [user.display_name for user in random.sample(ctx.guild.members, 50)]
			else:
				self.channels_playing_hungergames.remove(ctx.channel.id)
				return await ctx.send("You need at least two people to play hunger games.", delete_after = 5)
		elif len(args) > 50:
			self.channels_playing_hungergames.remove(ctx.channel.id)
			return await ctx.send("Too many people.", delete_after = 5)

		players = set(Player(i) for i in args)
		dead = []
		alive = set(players)
		placements = ["**Placements:**"]
		kills = ["**Kills:**"]
		counter = 1

		def round(event_type, counter):
			msgs = []

			def pick_events(event_list, fatal_event_list, msgs = msgs):
				died = []
				current_players = set(alive)

				while current_players:
					rng = random.uniform(0, 1)

					if rng > 0.75:
						event = random.choice(fatal_event_list)
					else:
						event = random.choice(event_list)

					if event.num_players <= len(current_players):
						chosen = random.sample(current_players, event.num_players)
						msg, d = event.action(chosen)
						died += d
						msgs += msg

						for i in chosen:
							current_players.remove(i)

				return msgs, died

			if event_type == EventType.Bloodbath:
				msgs.append("**BLOODBATH**:")
				msgs, died = pick_events(bloodbath, fatal_bloodbath)
			elif event_type == EventType.Day:
				msgs.append(f"**DAY {counter}**:")
				msgs, died = pick_events(day, fatal_day)
			elif event_type == EventType.Night:
				msgs.append(f"**NIGHT {counter}**:")
				msgs, died = pick_events(night, fatal_night)
			elif event_type == EventType.Feast:
				msgs.append(f"**FEAST**:")
				msgs, died = pick_events(feast, fatal_feast)
			elif event_type == EventType.Arena:
				arena_choice = random.choice(arena)
				msgs.append(f"**ARENA: {arena_choice.name}**")
				msgs, died = pick_events(arena_choice.events, arena_choice.events)

			return msgs, died

		async def game(state, counter):
			msgs, died = round(state, counter)
			send_message = "\n".join(msgs)

			if len(send_message) > 2048:
				send_message_1 = "\n".join(send_message.split("\n")[:len(send_message.split("\n")) // 2])
				send_message_2 = "\n".join(send_message.split("\n")[len(send_message.split("\n")) // 2:])
				await ctx.send(embed = discord.Embed(title = "Hunger Games", description = send_message_1, colour = random.randint(0, 0xffffff)))
				await ctx.send(embed = discord.Embed(title = "Hunger Games", description = send_message_2, colour = random.randint(0, 0xffffff)))
			else:
				await ctx.send(embed = discord.Embed(title = "Hunger Games", description = send_message, colour = random.randint(0, 0xffffff)))

			return died

		async def status():
			send_message = []
			temp = sorted(alive, key = lambda x: x.kills, reverse = True)

			for i in temp:
				send_message.append(f"**{i.name}** HP: {i.health}, Status: Alive, Kills: {i.kills}, XP: {i.xp}")

			for i in reversed(dead):
				send_message.append(f"~~**{i.name}** Status: Dead, Kills: {i.kills}, XP: {i.xp}~~")

			if len("\n".join(send_message)) > 2048:
				send_message_1 = "\n".join(send_message[:len(send_message) // 2])
				send_message_2 = "\n".join(send_message[len(send_message) // 2:])

				if len(send_message_1) <= 2048:
					await ctx.send(embed = discord.Embed(title = "Status", description = send_message_1, colour = random.randint(0, 0xffffff)))
					await ctx.send(embed = discord.Embed(title = "Status", description = send_message_2, colour = random.randint(0, 0xffffff)))
				else:
					send_message_1 = "\n".join(send_message[:len(send_message) // 3])
					send_message_2 = "\n".join(send_message[len(send_message) // 3:len(send_message) * 2 // 3])
					send_message_3 = "\n".join(send_message[len(send_message) * 2 // 3:])
					await ctx.send(embed = discord.Embed(title = "Status", description = send_message_1, colour = random.randint(0, 0xffffff)))
					await ctx.send(embed = discord.Embed(title = "Status", description = send_message_2, colour = random.randint(0, 0xffffff)))
					await ctx.send(embed = discord.Embed(title = "Status", description = send_message_3, colour = random.randint(0, 0xffffff)))
			else:
				await ctx.send(embed = discord.Embed(title = "Status", description = "\n".join(send_message), colour = random.randint(0, 0xffffff)))

			await asyncio.sleep(10)

		died = await game(EventType.Bloodbath, 1)
		alive -= set(died)
		dead += died

		while len(alive) > 1:
			cont = await ctx.send("Continue? Type \"EXIT\" to stop game.")

			def check(m):
				return m.channel == ctx.channel and m.author == ctx.author

			try:
				confirm = await self.bot.wait_for("message", timeout = 180, check = check)
			except asyncio.TimeoutError:
				return await ctx.send("No confirm. Hunger Games ends.", delete_after = 5)

			await cont.delete()

			if confirm.content.upper() == "EXIT":
				self.channels_playing_hungergames.remove(ctx.channel.id)
				return await ctx.send("Exited game.", delete_after = 5)

			rng = random.uniform(0, 1)

			if rng > 0.95:
				d = await game(EventType.Feast, counter)
				died += d
				alive -= set(d)
				dead += d

				if len(alive) <= 1:
					break

				cont1 = await ctx.send("Continue? Type \"EXIT\" to stop game.")

				confirm1 = await self.bot.wait_for("message", timeout = 180, check = check)

				if confirm1:
					await cont1.delete()

					if confirm1.content.upper() == "EXIT":
						self.channels_playing_hungergames.remove(ctx.channel.id)
						return await ctx.send("Exited game.", delete_after = 5)
				else:
					return await ctx.send("No confirm. Hunger Games ends.", delete_after = 5)
			elif 0.95 >= rng and rng > 0.85:
				d = await game(EventType.Arena, counter)
				died += d
				alive -= set(d)
				dead += d

				if len(alive) <= 1:
					break

				cont1 = await ctx.send("Continue? Type \"EXIT\" to stop game.")

				confirm1 = await self.bot.wait_for("message", timeout = 180, check = check)

				if confirm1:
					await cont1.delete()

					if confirm1.content.upper() == "EXIT":
						self.channels_playing_hungergames.remove(ctx.channel.id)
						return await ctx.send("Exited game.", delete_after = 5)
				else:
					self.channels_playing_hungergames.remove(ctx.channel.id)
					return await ctx.send("No confirm. Hunger Games ends.", delete_after = 5)

			d = await game(EventType.Day, counter)
			died += d
			alive -= set(d)
			dead += d

			if len(alive) <= 1:
				break

			if not died:
				await ctx.send(embed = discord.Embed(description = "No cannon shots can be heard in the distance.", colour = random.randint(0, 0xffffff)))
			else:
				await ctx.send(embed = discord.Embed(description = f"{len(died)} cannon {'shot' if len(died) == 1 else 'shots'} can be heard in the distance for {', '.join([i.name for i in died])}.", colour = random.randint(0, 0xffffff)))

			stat = await ctx.send("Do you want to see the status of everyone? Answer \"YES\" or \"NO\".")

			def check(m):
				return m.channel == ctx.channel and m.author == ctx.author

			try:
				status_confirm = await self.bot.wait_for("message", timeout = 180, check = check)
			except asyncio.TimeoutError:
				return await ctx.send("No confirm. Hunger Games continues.", delete_after = 5)

			await stat.delete()

			if status_confirm.content.upper() == "YES":
				await status()
			elif status_confirm.content.upper() == "EXIT":
				self.channels_playing_hungergames.remove(ctx.channel.id)
				return await ctx.send("Exited game.", delete_after = 5)

			died = await game(EventType.Night, counter)
			alive -= set(died)
			dead += died

			if len(alive) <= 1:
				break

			counter += 1

		if len(alive) == 1:
			dead.append(list(alive)[0])
			await ctx.send(embed = discord.Embed(description = f"**{list(alive)[0].name}** is the winner!", colour = random.randint(0, 0xffffff)))
			await asyncio.sleep(1)
		else:
			await ctx.send(embed = discord.Embed(description = "Nobody won! They all died!", colour = random.randint(0, 0xffffff)))

		dead.reverse()

		await asyncio.sleep(1)

		for i in dead:
			if dead.index(i) == 10:
				placements.append(f"11th: **{i.name} ({i.xp} XP)**")
			elif dead.index(i) == 11:
				placements.append(f"12th: **{i.name} ({i.xp} XP)**")
			elif dead.index(i) == 12:
				placements.append(f"13th: **{i.name} ({i.xp} XP)**")
			elif dead.index(i) % 10 == 0:
				placements.append(f"{dead.index(i) + 1}st: **{i.name} ({i.xp} XP)**")
			elif dead.index(i) % 10 == 1:
				placements.append(f"{dead.index(i) + 1}nd: **{i.name} ({i.xp} XP)**")
			elif dead.index(i) % 10 == 2:
				placements.append(f"{dead.index(i) + 1}rd: **{i.name} ({i.xp} XP)**")
			else:
				placements.append(f"{dead.index(i) + 1}th: **{i.name} ({i.xp} XP)**")

		if len("\n".join(placements)) > 2048:
			placements_1 = "\n".join(placements[:len(placements) // 2])
			placements_2 = "\n".join(placements[len(placements) // 2:])
			await ctx.send(embed = discord.Embed(title = "Placements", description = placements_1, colour = random.randint(0, 0xffffff)))
			await ctx.send(embed = discord.Embed(title = "Placements", description = placements_2, colour = random.randint(0, 0xffffff)))
		else:
			await ctx.send(embed = discord.Embed(title = "Placements", description = "\n".join(placements), colour = random.randint(0, 0xffffff)))

		await asyncio.sleep(1)
		kills_list = sorted(dead, key = lambda x: x.kills, reverse = True)

		for i in kills_list:
			if i.kills:
				kills.append(f"{i.kills}: **{i.name}**")

		if len("\n".join(kills)) > 2048:
			kills_1 = "\n".join(kills[:len(kills) // 2])
			kills_2 = "\n".join(kills[len(kills) // 2:])
			await ctx.send(embed = discord.Embed(title = "Kills", description = kills_1, colour = random.randint(0, 0xffffff)))
			await ctx.send(embed = discord.Embed(title = "Kills", description = kills_2, colour = random.randint(0, 0xffffff)))
		else:
			await ctx.send(embed = discord.Embed(title = "Kills", description = "\n".join(kills), colour = random.randint(0, 0xffffff)))

		self.channels_playing_hungergames.remove(ctx.channel.id)

	@commands.command(hidden = True)
	@disabled()
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def life(self, ctx):
		args = [x.strip() for x in ctx.message.content[len(self.bot.command_prefix) + 5:].split(",")]
		retfood = False

		if args:
			font = ImageFont.truetype("boxfont_round.ttf", 20)

			if args[-1].lower() == "anti":
				del args[-1]
				retfood = True

			if not args:
				args = [None] * random.randint(10, 50)
			elif len(args) == 1:
				if args[0].lower() == "server":
					args = [user.display_name for user in ctx.guild.members]

		await ctx.send("Ok here we go.")
		img = Image.new("RGBA", (1000, 1000), (255, 255, 255, 255))
		d = ImageDraw.Draw(img)

		r = 10
		people = []

		for i in range(len(args)):
			x = random.randrange(10, 990)
			y = random.randrange(10, 990)
			d.ellipse([(x - r, y - r), (x + r, y + r)], fill = (0, 0, 0, 255), outline = (0, 0, 0, 255))
			name = args[i]

			people.append([x, y, 10, name, 0])

		curfood = []
		opens = [img.copy()]
		stext = ""

		while True:
			if len(people) == 1:
				break

			d.rectangle((0, 0, 1000, 1000), outline = (255, 255, 255, 255), fill = (255, 255, 255, 255))
			food = random.randrange(0, 5)

			for i in range(food):
				x = random.randrange(10, 990)
				y = random.randrange(10, 990)
				curfood.append([x, y])

			if retfood:
				choice = random.randrange(0, 5)

				if choice == 3:
					x = random.randrange(10, 990)
					y = random.randrange(10, 990)
					curfood.append([x, y, True])

			for person in people:
				left = Polygon([(0, person[1] - 9), (person[0], person[1] - 9), (0, person[1] + 9), (person[0], person[1] + 9)])
				right = Polygon([(1000, person[1] - 9), (person[0], person[1] - 9), (1000, person[1] + 9), (person[0], person[1] + 9)])
				up = Polygon([(person[0] - 9, 0), (person[0] - 9, person[1]), (person[0] + 9, 0), (person[0] + 9, person[1])])
				down = Polygon([(person[0] - 9, 1000), (person[0] - 9, person[1]), (person[0] + 9, 1000), (person[0] + 9, person[1])])
				shortdist = inf
				shortfood = None

				for food in curfood:
					xfood = Point(food[0], food[1]).buffer(10)
					dist = (person[1] - food[1]) ** 2 + (person[0] - food[0]) ** 2
		
					try:
						if (xfood.intersects(up) or xfood.intersects(down) or xfood.intersects(left) or xfood.intersects(right)) and dist < shortdist and len(food) != 3:
							shortdist = dist
							shortfood = food
					except:
						continue

				try:
					if shortfood:
						xfood = Point(shortfood[0], shortfood[1]).buffer(10)

						if xfood.intersects(up):
							xdir = (0, -10)
						elif xfood.intersects(down):
							xdir = (0, 10)
						elif xfood.intersects(left):
							xdir = (-10, 0)
						elif xfood.intersects(right):
							xdir = (10, 0)
					else:
						xdir = random.choice([(10, 0), (0, 10), (0, -10), (-10, 0)])
				except:
					xdir = random.choice([(10, 0), (0, 10), (0, -10), (-10, 0)])

				xperson = Point(person[0], person[1]).buffer(person[2])
				person[0] += xdir[0]
				person[1] += xdir[1]

				if (person[0] < 0 or person[0] > 1000 or person[1] < 0 or person[1] > 1000) and person in people:
					stext += f"**{person[3]}** fell off the world.\n"
					people.remove(person)

				for food in curfood:
					xfood = Point(food[0], food[1]).buffer(10)

					if xperson.intersects(xfood):
						curfood.remove(food)

						if retfood and len(food) == 3:
							person[2] = max(10, person[2] - 5)
						else:
							person[2] += 5

				for yperson in people:
					xyperson = Point(yperson[0], yperson[1]).buffer(yperson[2])

					if xyperson.intersects(xperson) and yperson in people and person != yperson:
						if yperson[2] > person[2]:
							if person in people:
								yperson[2] = sqrt(person[2] ** 2 + yperson[2] ** 2)
								stext += f"**{yperson[3]}** ate **{person[3]}**.\n"
								people.remove(person)
						else:
							person[2] = sqrt(person[2] ** 2 + yperson[2] ** 2)
							people.remove(yperson)
							stext += f"**{person[3]}** ate **{yperson[3]}**.\n"

			for f in curfood:
				x = f[0]
				y = f[1]
				cb = (0, 0, 255, 255)

				if len(f) == 3:
					cb = (255, 0, 0, 255)

				d.ellipse([(x - 10, y - 10), (x + 10, y + 10)], fill = cb, outline = cb)

			for p in people:
				x = p[0]
				y = p[1]
				r = p[2]
				d.ellipse([(x - r, y - r), (x + r, y + r)], fill = (p[4] * 51, 0, 0, 255), outline = (p[4] * 51, 0, 0, 255))

				if p[3]:
					d.text((x - (5 * len(p[3])), y - 10), p[3], fill = (0, 255, 0, 255), font = font)

			opens.append(img.copy())

		imgb, *imgs = opens
		filex = BytesIO()
		imgb.save(fp = filex, format = "GIF", append_images = imgs, save_all = True, duration = 10, loop = 0)

		while filex.getbuffer().nbytes > 8000000:
			toremove = []

			for i in range(len(opens)):
				if i % 2 == 0:
					toremove.append(opens[i])

			for o in toremove:
				opens.remove(o)

			imgb, *imgs = opens
			filex = BytesIO()
			imgb.save(fp = filex, format = "GIF", append_images = imgs, save_all = True, duration = 10, loop = 0)

		filex.seek(0)

		await ctx.send(file = discord.File(filex, "temp.gif"))

		if any(i for i in args):
			msg = "**KEKS:**\n\n" + stext

			if len(msg) > 2000:
				while len(msg) > 2000:
					await ctx.send(msg[:2000].rsplit("\n", 1)[0])
					msg = msg[:2000].rsplit("\n", 1)[1] + msg[2000:]

				await ctx.send(msg)
			else:
				await ctx.send(msg)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def mathrace(self, ctx, rounds):
		"""
		`{0}mathrace` __`Mathrace Game`__

		**Usage:** {0}mathrace <rounds>

		**Examples:**
		`{0}mathrace 10` generates a game of mathrace with 10 rounds
		"""

		if ctx.channel.id in self.channels_playing_mathrace:
			return await ctx.send("Mathrace already active in this channel.", delete_after = 5)

		try:
			rounds = int(rounds)
		except ValueError:
			return await ctx.send("Please enter a positive number of rounds to play.", delete_after = 5)

		if rounds < 3 or rounds > 30:
			return await ctx.send("Please enter between 3 and 30 rounds.", delete_after = 5)

		self.channels_playing_mathrace.append(ctx.channel.id)
		await ctx.send(f"Welcome to Mathrace, a competitive game to improve your math skills. Answer the arithmetic problems as fast as you can. There will be **{rounds}** rounds.")
		await asyncio.sleep(3)
		counter = 1
		competitors = {}

		while counter <= rounds:
			await ctx.send(f"Round **{counter}**:")
			await asyncio.sleep(0.5)
			rand = random.random()

			if rand < 0.25:
				n1 = random.randint(-1000, 1000)
				n2 = random.randint(-1000, 1000)
				correct = n1 + n2
				await ctx.send(f"What is **{n1} + {n2}**?")
			elif 0.25 <= rand and rand < 0.50:
				n1 = random.randint(-1000, 1000)
				n2 = random.randint(-1000, 1000)
				correct = n1 - n2
				await ctx.send(f"What is **{n1} - {n2}**?")
			elif 0.50 <= rand and rand < 0.75:
				n1 = random.randint(-30, 30)
				n2 = random.randint(-30, 30)
				correct = n1 * n2
				await ctx.send(f"What is **{n1} * {n2}**?")
			else:
				n1 = random.randint(-10, 10)
				n2 = random.randint(0, 4)
				correct = n1 ** n2
				await ctx.send(f"What is **{n1} ^ {n2}**?")

			correct_answer = False

			def check(m):
				return not m.author.bot and m.channel == ctx.channel and re.fullmatch(r"-?\d+|end", m.content)

			while not correct_answer:
				try:
					answer = await self.bot.wait_for("message", timeout = 10, check = check)
				except asyncio.TimeoutError:
					await ctx.send(f"timed out. The correct answer is **{correct}**.")
					break

				if answer.content == "end" and answer.author == ctx.author:
					self.channels_playing_mathrace.remove(ctx.channel.id)
					return await ctx.send("Game stopped.", delete_after = 5)
				elif int(answer.content) == correct:
					correct_answer = True
					author = answer.author

					if author.display_name in competitors.keys():
						competitors[author.display_name] += 1
					else:
						competitors[author.display_name] = 1

					break
				else:
					await ctx.send("Incorrect. Try again.", delete_after = 1)

			if correct_answer:
				await ctx.send(f"Correct, **{author.display_name}**.")
				await asyncio.sleep(2)

			counter += 1

		result = ""
		ranks = sorted(competitors.items(), key = lambda x: x[1], reverse = True)

		for j in ranks:
			result += f"{ranks.index(j) + 1}: **{j[0]}** - {j[1]} points\n"

		await ctx.send(f"The game has ended. Here are your results:")
		await asyncio.sleep(0.3)
		await ctx.send(result)
		self.channels_playing_mathrace.remove(ctx.channel.id)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def minesweeper(self, ctx, rows, cols, mines):
		"""
		`{0}minesweeper` __`Minesweeper generator`__

		**Usage:** {0}minsweeper <rows> <cols> <num mines>

		**Examples:**
		`{0}minesweeper 10 10 10` generates easy minesweeper game
		"""

		try:
			rows = int(rows)
			cols = int(cols)
			mines = int(mines)
		except ValueError:
			return await ctx.send("Please enter positive integer board size and number of mines.", delete_after = 5)

		if mines > rows * cols:
			return await ctx.send("Please enter a smaller number of mines for this board size.", delete_after = 5)

		if rows * cols > 198:
			return await ctx.send("Please enter a smaller board size.", delete_after = 5)

		count_dict = {0: "||0️⃣||", 1: "||1️⃣||", 2: "||2️⃣||", 3: "||3️⃣||", 4: "||4️⃣||", 5: "||5️⃣||", 6: "||6️⃣||", 7: "||7️⃣||", 8: "||8️⃣||"}

		def create_board(rows, cols, mines):
			board = [[0 for i in range(cols)] for j in range(rows)]
			num_mines = 0
			mines_list = []

			while num_mines < mines:
				y = random.randrange(rows)
				x = random.randrange(cols)

				if not board[y][x]:
					board[y][x] = "||💣||"
					mines_list.append([x, y])
					num_mines += 1

			return board, mines_list

		def count_mines(a, b, mines_list):
			c = 0

			if [a - 1, b - 1] in mines_list: c += 1
			if [a + 0, b - 1] in mines_list: c += 1
			if [a + 1, b - 1] in mines_list: c += 1
			if [a - 1, b + 0] in mines_list: c += 1
			if [a + 1, b + 0] in mines_list: c += 1
			if [a - 1, b + 1] in mines_list: c += 1
			if [a + 0, b + 1] in mines_list: c += 1
			if [a + 1, b + 1] in mines_list: c += 1

			return c

		board, mines_list = create_board(rows, cols, mines)
		msg = ""

		for y in range(len(board)):
			for x in range(len(board[0])):
				if board[y][x] != "||💣||":
					c = count_mines(x, y, mines_list)
					board[y][x] = count_dict[c]

				msg += board[y][x]

				if x == len(board[0]) - 1:
					msg += "\n"

		if len(msg) <= 2000:
			await ctx.send(msg)
		else:
			await ctx.send("Board too large. Please enter a smaller board size.", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def palindromes(self, ctx, n, base):
		"""
		`{0}palindromes` __`Sum of three palindromes`__

		**Usage:** {0}palindromes <integer> <base>

		**Examples:**
		`{0}palindromes 201 10` 201 = 101 + 99 + 1
		`{0}palindromes 80347BACD 16` 80347BACD = 701111107 + FB3003BF + 706A607
		"""

		try:
			g = int(base)
			n_ = int(n, g)

			if n_ <= 0:
				raise ValueError
		except ValueError:
			return await ctx.send("Please input a positive integer and an integer base between 2 and 36.", delete_after = 5)

		lst = sum_of_three_palindromes(n, g)

		if "0" in lst:
			lst.remove("0")

		msg = f"{n} = {' + '.join(lst)}"

		if len(msg) > 2000:
			if len(msg) > 10000:
				await ctx.send("result too large")
			else:
				while len(msg) > 2000:
					await ctx.send(msg[:2000])
					msg = msg[2000:]

				await ctx.send(msg)
		else:
			await ctx.send(msg)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def rate(self, ctx):
		"""
		`{0}rate` __`Rates a thing`__

		**Usage:** {0}rate <thing>

		**Examples:**
		`{0}rate ABCD` I rate ABCD a 100%.
		"""

		if len(ctx.message.content) == len(self.bot.command_prefix) + 8:
			return await ctx.send("Please enter a thing to rate.")

		new_message = ctx.message.content[len(self.bot.command_prefix) + 9:]
		parsed_numbers = []

		for a in new_message:
			parsed_numbers.append(ord(a))

		for b in range(len(parsed_numbers)):
			parsed_numbers[b] = ((parsed_numbers[b] + 1) ** (b + 1)) % 3386993

		for c in range(len(parsed_numbers)):
			parsed_numbers[c] = int(ldexp(parsed_numbers[c] + 1, ceil(log(c + 1)))) % 4949891

		for d in range(len(parsed_numbers)):
			parsed_numbers[d] = (parsed_numbers[d] % 731327 * 19801) ** (parsed_numbers[d] % 967)

		product = 1

		for g in parsed_numbers:
			product *= (g % 114706718444035163140155397601185673289995823253605101230230970384224541194847383396291679933008201847996701574011301703969577417314490672015112420895129196404171598865628390849414234320820856780096870512158236299318122764704155136571378525214249566170442778746497155064952736934991273237592071341861053465591)

		result = (product // 21496454303943569233832695919) % 101
		msg = f"I rate {new_message} a {result}%."

		if len(msg) > 2000:
			await ctx.send("I rate")
			await ctx.send(new_message)
			await ctx.send(f"a {result}%.")
		else:
			await ctx.send(msg)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def reddit(self, ctx, sub, category = "hot"):
		"""
		`{0}reddit` __`Reddit posts`__

		**Usage:** {0}reddit <subreddit> [category]

		**Categories:** hot, new, controversial, top, rising, defaults to hot if none provided

		**Examples:**
		`{0}reddit funny hot` returns a random post from the hot list in r/funny.
		"""

		data = requests.get(f"https://www.reddit.com/r/{sub}/{category}/.json?limit=1000", headers = {"User-agent": "Bot"}).json()

		if "message" in data.keys():
			await ctx.send(data["message"], delete_after = 5)
		elif not data["data"]["children"]:
			await ctx.send("That's not a valid subreddit.", delete_after = 5)
		else:
			post = random.choice(data["data"]["children"])

			if not post["data"]["over_18"]:
				while post["data"]["permalink"] in self.seen_reddit_memes:
					post = random.choice(data["data"]["children"])

				embed = discord.Embed(title = post["data"]["title"], url = f"https://www.reddit.com{post['data']['permalink']}", description = post["data"]["selftext"], colour = random.randint(0, 0xFFFFFF))

				m = mimetypes.guess_type(post["data"]["url"])

				if m[0].startswith("image"):
					embed.set_image(url = post["data"]["url"])

				embed.set_footer(text = f"👍 {post['data']['ups']} | 💬 {post['data']['num_comments']}")
				await ctx.send(embed = embed)

				self.seen_reddit_memes.append(post["data"]["permalink"])
			else:
				await ctx.send("The post was deemed 18+ by Reddit, thus I will not send it here.", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def rps(self, ctx, shape):
		"""
		`{0}rps` __`Rock paper scissors`__

		**Usage:** {0}rps <✊ | 🖐 | ✌>

		**Examples:**
		`{0}rps ✊` You win with ✊.
		"""

		rps_list = ["✊", "🖐", "✌"]

		if shape.lower() not in rps_list:
			return await ctx.send("Please enter one of ✊, 🖐, or ✌.", delete_after = 5)

		user_choice = shape.lower()
		bot_choice = random.choice(rps_list)
		bot_win = f"🅱ot wins with {bot_choice}"
		bot_lose = f"you win with {user_choice}"

		if user_choice == bot_choice:
			await ctx.send(f"It's a tie {user_choice} {bot_choice}")
		elif user_choice == "✊":
			if bot_choice == "🖐":
				await ctx.send(f"{bot_win}")
			else:
				await ctx.send(f"{bot_lose}")
		elif user_choice == "🖐":
			if bot_choice == "✊":
				await ctx.send(f"{bot_lose}")
			else:
				await ctx.send(f"{bot_win}")
		else:
			if bot_choice == "✊":
				await ctx.send(f"{bot_win}")
			else:
				await ctx.send(f"{bot_lose}")

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def rr(self, ctx):
		"""
		`{0}rr` __`Russian Roulette`__

		**Usage:** {0}rr <arg1> | <arg2> | ...

		**Examples:**
		`{0}rr nou | no | u` nou is killed
		"""

		args = ctx.message.content[len(self.bot.command_prefix) + 3:].split(" | ")

		if not args:
			return await ctx.send("You didn't pick things to rr.", delete_after = 5)

		if len(args) > 50:
			return await ctx.send("Too many args m8", delete_after = 5)

		msg = ""
		rng = random.randrange(0, len(args))

		for i in range(len(args)):
			if i == rng:
				msg += (f"{args[i]} 💥 🔫\n")
			else:
				msg += (f"{args[i]} 〰 🔫\n")

		await ctx.send(msg)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def slot(self, ctx, *args):
		"""
		`{0}slot` __`Play slots`__

		**Usage:** {0}slot [bet | chart]

		**Examples:**
		`{0}slot 23` plays slots with 23 credit.
		`{0}slot chart` shows win chart.
		"""

		user = ctx.author
		amount = 1

		if args:
			if args[0] == "chart":
				return await ctx.send("win chart for 🅱ot slots:\n\n💩 * 3 **->** 1\n🅱 * 2 **->** 1\n🅱 * 3 **->** 3\n🤔 * 2 **->** 2\n🤔 * 3 **->** 5\n💯 * 2 **->** 3\n💯 * 3 **->** 10\n🔔 * 2 **->** 5\n🔔 * 3 **->** 15\n💰 * 2 **->** 10\n💰 * 3 **->** 30\n🇱🇻 * 2 **->** 10\n🇱🇻 * 3 **->** 30\n:seven: * 2 **->** 25\n:seven: * 3 **->** 75\n💎 * 2 **->** 30\n💎 * 3 **->** 100")
			else:
				try:
					amount = int(re.match(r"\d+", args[0]).group(0))
				except:
					if args[0] == "inf":
						amount = inf
					elif args[0] == "all":
						amount = self.bot.user_data[str(user.id)]["coins"]

				if not amount:
					amount = 1

		if self.bot.user_data[str(user.id)]["coins"] >= amount:
			self.bot.user_data[str(user.id)]["coins"] -= amount
			profit = 0
			slot_items = ["💩", "🅱", "🤔", "💯", "🔔", "💰", "🇱🇻", ":seven:", "💎"]

			def recurse():
				a = random.choice(slot_items)
				b = random.choice(slot_items)
				c = random.choice(slot_items)
				slot_items_A = [A for A in slot_items if A != a]
				slot_items_B = [B for B in slot_items if B != b]
				slot_items_C = [C for C in slot_items if C != c]
				d = random.choice(slot_items_A)
				e = random.choice(slot_items_B)
				f = random.choice(slot_items_C)
				slot_items_D = [D for D in slot_items_A if D != d]
				slot_items_E = [E for E in slot_items_B if E != e]
				slot_items_F = [F for F in slot_items_C if F != f]
				g = random.choice(slot_items_D)
				h = random.choice(slot_items_E)
				i = random.choice(slot_items_F)
				return f"**🎰 🅱ot Slots**\n------------------\n{a} : {b} : {c}\n\n{d} : {e} : {f} **<**\n\n{g} : {h} : {i}\n------------------"

			slots1 = await ctx.send(recurse())
			await asyncio.sleep(1)
			await slots1.edit(content = recurse())
			await asyncio.sleep(1)

			def final():
				rand = random.uniform(0, 1)
				slot_dist = [x / 108 for x in [0, 1, 3, 6, 9, 15, 27, 45, 72]]
				n = slot_items[len(slot_items) - bisect.bisect_left(slot_dist, rand)]
				return n

			a = final()
			b = final()
			c = final()
			slot_items_A = [A for A in slot_items if A != a]
			slot_items_B = [B for B in slot_items if B != b]
			slot_items_C = [C for C in slot_items if C != c]
			d = random.choice(slot_items_A)
			e = random.choice(slot_items_B)
			f = random.choice(slot_items_C)
			slot_items_D = [D for D in slot_items_A if D != d]
			slot_items_E = [E for E in slot_items_B if E != e]
			slot_items_F = [F for F in slot_items_C if F != f]
			g = random.choice(slot_items_D)
			h = random.choice(slot_items_E)
			i = random.choice(slot_items_F)
			s = f"**🎰 🅱ot Slots**\n------------------\n{d} : {e} : {f}\n\n{a} : {b} : {c} **<**\n\n{g} : {h} : {i}"
			win = f"\n------------------\n| : : : : **WIN** : : : : |\n\n{user.name} used **{amount}** coin{'s' if amount > 1 else ''} and won "
			lose = f"\n------------------\n| : : :  **LOST**  : : : |\n\n{user.name} used **{amount}** coin{'s' if amount > 1 else ''} and lost everything."

			if [a, b, c].count("💩") == 3:
				profit = amount
			elif [a, b, c].count("🅱") >= 2:
				if [a, b, c].count("🅱") == 3:
					profit = 3 * amount
				else:
					profit = amount
			elif [a, b, c].count("🤔") >= 2:
				if [a, b, c].count("🤔") == 3:
					profit = 5 * amount
				else:
					profit = 2 * amount
			elif [a, b, c].count("💯") >= 2:
				if [a, b, c].count("💯") == 3:
					profit = 10 * amount
				else:
					profit = 3 * amount
			elif [a, b, c].count("🔔") >= 2:
				if [a, b, c].count("🔔") == 3:
					profit = 15 * amount
				else:
					profit = 5 * amount
			elif [a, b, c].count("💰") >= 2:
				if [a, b, c].count("💰") == 3:
					profit = 30 * amount
				else:
					profit = 10 * amount
			elif [a, b, c].count("🇱🇻") >= 2:
				if [a, b, c].count("🇱🇻") == 3:
					profit = 30 * amount
				else:
					profit = 10 * amount
			elif [a, b, c].count(":seven:") >= 2:
				if [a, b, c].count(":seven:") == 3:
					profit = 75 * amount
				else:
					profit = 25 * amount
			elif [a, b, c].count("💎") >= 2:
				if [a, b, c].count("💎") == 3:
					profit = 100 * amount
				else:
					profit = 30 * amount
			else:
				s += lose

			if profit:
				s += f"{win}**{profit}** coins!"

			await slots1.edit(content = s)
			self.bot.update_data(user)
		else:
			await ctx.send("You don't have enough coins to slot this much.", delete_after = 5)

	@commands.command(aliases = ["sm"])
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def spessmuhrine(self, ctx, phrase):
		"""
		`{0}spessmuhrine` __`Spess Muhrine Name Generator`__
		**Aliases**: sm

		**Usage:** {0}spessmuhrine <phrase>

		**Examples:**
		`{0}spessmuhrine nou` Generates 10 names containing the phrase "nou"
		"""

		nm1 = ["Abdaziel","Abdiel","Abrariel","Adnachiel","Adonael","Adriel","Afriel","Akhazriel","Akriel","Ambriel","Amitiel","Amriel","Anael","Anaiel","Anaphiel","Anapiel","Anauel","Anpiel","Ansiel","Aphael","Aradiel","Arael","Araqiel","Araquiel","Arariel","Azrael","Azriel","Barachiel","Baradiel","Barakiel","Baraqiel","Barattiel","Barbiel","Barchiel","Bariel","Barquiel","Barrattiel","Baruchiel","Bethuel","Boamiel","Cadriel","Camael","Camiel","Caphriel","Cassiel","Castiel","Cerviel","Chamuel","Chayliel","Dabriel","Dagiel","Dalquiel","Daniel","Dardariel","Diniel","Domiel","Dubbiel","Emmanuel","Eremiel","Ezekiel","Ezequiel","Gabriel","Gadiel","Gadreel","Gadriel","Gagiel","Galgaliel","Gazardiel","Geburatiel","Germael","Habriel","Hadariel","Hadramiel","Hadraniel","Hadriel","Hakael","Hamael","Hamaliel","Hasdiel","Hayliel","Hermesiel","Hochmael","Hofniel","Humatiel","Humiel","Incarael","Ishmael","Israfel","Israfiel","Israfil","Ithuriel","Jehudiel","Jeremiel","Kabshiel","Kadmiel","Kafziel","Kalaziel","Karael","Kasbiel","Kemuel","Kerubiel","Khamael","Labbiel","Lahabiel","Machidiel","Malchediel","Mazrael","Michael","Mihael","Morael","Mordigael","Mydaiel","Naaririel","Nahaliel","Nanael","Narcariel","Nasargiel","Nathanael","Nathaniel","Nelchael","Omael","Omniel","Onafiel","Ophaniel","Ophiel","Orphamiel","Osmadiel","Pathiel","Peliel","Peniel","Perpetiel","Phanuel","Pyriel","Qaphsiel","Qaspiel","Quabriel","Rachmiel","Radfael","Radueriel","Raduriel","Rahatiel","Rahmiel","Ramiel","Raphael","Rasiel","Rathanael","Razael","Raziel","Rehael","Remiel","Remliel","Rhamiel","Rikbiel","Rogziel","Rufeal","Ruhiel","Sabathiel","Sabrael","Sachael","Sachiel","Salathiel","Samael","Samandiriel","Samandriel","Samkiel","Sammael","Saniel","Sarandiel","Sariel","Satqiel","Sealtiel","Seraphiel","Shamsiel","Simiel","Stadiel","Suriel","Tadhiel","Tamiel","Tatrasiel","Theliel","Turiel","Turmiel","Uriel","Usiel","Uzziel","Vretiel","Yerachmiel","Yeshamiel","Zacharael","Zachariel","Zachriel","Zadkiel","Zahariel","Zaphiel","Zazriel","Zophiel","Zuriel"]
		nm2 = ["Abra","Ale","Alge","Alle","Alva","Ama","Apo","Arca","Archa","Are","Arge","Arte","Ata","Atana","Athi","Augu","Auto","Avi","Avu","Axa","Ba","Be","Belle","Bo","Borea","Ca","Cae","Caele","Caldi","Cassia","Cassio","Cassiu","Ce","Centu","Cleu","Co","Consta","Consu","Corio","Corne","Corvu","Cra","Cy","Cyru","Da","Dae","Damo","Dariu","Deme","Desti","Dio","Do","Domi","Ela","Ely","Eno","Epheu","Epi","Era","Eume","Fa","Fabiu","Fennia","Fenniu","Ferru","Fi","Firlu","Go","Gordia","Gothcha","Grae","Gre","Gri","Grima","Ha","Hadrio","Hea","Heli","Helve","Ho","Holo","Hono","Hy","Hype","Ica","Igna","Ikti","Invi","Ja","Janu","Ju","Juliu","Kae","Ko","Lae","Lame","Laza","Leo","Leode","Leona","Liciu","Lu","Luctu","Ludo","Ly","Lysi","Ma","Mandu","Maneu","Mariu","Marte","Maxi","Me","Mephi","Mero","Mettiu","Mi","Mike","Milu","Mora","Myki","Ne","Nele","No","Ome","Ore","Oria","Pa","Palla","Pe","Pella","Pera","Petiu","Pra","Prae","Qui","Ra","Rammiu","Re","Remu","Rena","Rheto","Rui","Sa","Sangui","Se","Sera","Seve","Sica","Soli","Tae","Tha","Theo","Tho","Thra","Tire","Titu","Tole","Toria","Try","Tybe","Va","Valle","Vite"]
		nm3 = ["beros","bius","canus","carius","ccimius","ceus","cius","ctus","ddeus","des","deus","dia","dis","dius","dosios","drios","garius","goras","gris","gus","kelus","kilus","lanus","lcus","ldimus","ldus","lestis","leus","licanus","linus","lis","lius","lixus","llas","llenus","llian","llios","llius","llo","llus","lochus","los","ltus","lus","machus","maldus","medes","menes","metheus","mion","mis","mmius","mos","mus","natos","natus","nduls","ndus","nes","neus","nicus","nius","nnias","nnius","nnus","ntinus","ntis","ntius","ntos","nus","pheus","phicus","phis","ptus","ras","ratos","rbus","rdian","reas","rex","rias","rion","rius","rlus","rnon","ron","ros","rpheus","rpus","rrus","rtes","rthus","rus","rvus","scios","sias","sios","sius","ssian","ssios","ssius","ssos","ssus","stin","stis","ston","sus","theus","thios","thos","ticus","tin","tinos","tio","tios","tius","tor","trios","trius","ttius","tus","tutus","verus","vius","vus","ximus","xis","xus","zarus"]
		nm4 = ["Akio","Andro","Aqui","Avi","Be","Beru","Ca","Cassiu","Ce","Co","Cora","Corda","Cy","Cybu","Dio","Dra","Fa","Fabri","Gie","Invi","Isso","Ky","Kyra","Ma","Manu","Me","Mede","Mo","Morre","Nu","Octa","Orio","Orty","Pho","Po","Polu","Sca","Si","Sica","So","Sola","Stro","Ta","Tari","Te","Telio","Ti","Tibe","Tigu","Titu","Tra","Tri","Trisme","Ty","Venta","Vi","Vibiu"]
		nm5 = ["bius","bus","cles","cos","ctus","cus","des","dexus","don","gistus","gus","kios","kus","la","laris","lion","lis","llis","lux","medes","meon","ncus","nos","ntanus","nus","ras","rax","rdatus","rian","ricus","rikus","rion","ris","rius","ro","ros","rus","s","sius","ssius","stus","tanus","tus","tys","vius","xus","yus"]
		nm6 = ["Aar","Act","Aeg","Aeth","Al","Alar","Aldr","Aldw","Aleh","Aler","Alr","And","Andr","Ansg","Anv","Ard","Arg","Arj","Ark","Arm","Armar","Arv","Ash","Aud","Bael","Bald","Balt","Bann","Belph","Ben","Bened","Beth","Bheh","Bj","Bol","Bolin","Br","Brayd","Bulv","Cad","Cadm","Can","Car","Carn","Cast","Daarm","Daem","Darn","Dav","Drum","Drust","Dur","Eadw","Ech","Eck","Ed","Efr","Eg","El","Eng","Er","Esdr","Feirr","Felg","Fr","Fug","Gal","Gann","Garr","Gerh","Gervh","Gess","Gnaer","Gnyr","Graev","Grivn","Grol","Gunn","Gym","Haak","Hagr","Halbr","Haldr","Har","Harv","Has","Hect","Heinm","Helbr","Helg","Hengh","Herv","Hoen","Hold","Horn","Horthg","Hr","Hwyg","Indr","Ingv","Jerr","Jog","Jogh","Jon","Jor","Jub","Jul","Jurg","KRist","Kaer","Kald","Kalg","Kard","Karl","Karr","Keil","Ker","Kj","Kl","Kordh","Kr","Kreg","Kv","Lefv","Lem","Lod","Log","Lorg","Luk","Magn","Makl","Neod","Ner","Nid","Ol","Olb","Or","Orl","Ort","Ow","Ragn","Rakm","Rald","Ran","Reg","Rem","Rog","Ryn","Sab","Seg","Segl","Sel","Sevr","Seyd","Sief","Sig","Sigv","Skv","Sv","Talb","Tark","Tarn","Tob","Torbj","Torf","Torgh","Torv","Traj","Ulr","Var","Varr","Vayl","Vos","Vulk"]
		nm7 = ["aar","ab","abro","ac","ach","aen","af","ah","aidin","ak","al","ald","an","and","ann","ant","ar","ard","aric","arl","aros","arr","art","as","ast","atan","aten","ath","ayden","eas","echt","ed","edict","egor","ehan","ehart","eifvar","ek","el","elan","em","en","eon","er","erin","esk","eyr","iak","ian","ias","ic","ick","ict","ied","ig","ik","il","in","indal","ine","invar","ion","ios","ir","is","ismund","ist","oan","oc","och","od","oec","off","ok","old","om","on","or","orn","oron","os","ot","oth","ovar","ul","ulf","ulon","un","und","ur","us","yn","yrll"]
		nm8 = ["Ash","Battle","Black","Blood","Blue","Boulder","Cog","Dagger","Dark","Dead","Death","Doom","Dragon","Fell","Fire","Frost","Ghost","Gore","Grim","Hammer","Hell","Ice","Iron","Kraken","Rage","Red","Rock","Silver","Skull","Stark","Steel","Stone","Storm","Strong","Thunder","Twice","Umber","War"]
		nm9 = ["blade","bleeder","blood","born","breaker","bringer","brow","caller","claw","cleaver","crusher","dust","fall","fang","fist","fisted","flayer","fury","gaze","hair","hammer","hand","handed","horn","howl","mane","mantle","maul","maw","moon","rage","scream","seeker","shield","slain","sword","tooth","walker","wolf"]
		nm10 = ["Aga","Agapi","Aha","Ai","Ale","Ama","Ange","Anta","Asmo","Aste","Asto","Au","Avi","Aza","Azkae","Be","Belia","Bhar'","Bo","Boka","Bray'","Car","Carna","Carnae","Cema","Chi","Chry","Corbu","Cu","Cy","Da","Dak'","Darrio","Dasei","Dra","Dri","Enp","Eoni","Fu","Gaui","Gero","Glo","Gri","Gui","Heka","Iga","Isa","Issa","Ja","Jagha","Je","Jemu","K'","Kardo","Key","Kha","Khoi","Khy","Kori","Korvy","Kyu","Lavi","Laze","Ly","Lycao","Ma","Mae","Mala","Malu","Marqo","Maxi","Mercae","Mo","Molo","Morda","Na","Naa","Nassi","Nava","Ne","Necto","Neme","No","Numi","Nyko","Pa","Pae","Paele","Pho","Pto","Rha","Rohi","Romo","Sa","Sappho","Sarpe","Sca","Scama","Sci","Senti","Sepha","Seve","Shai","Shen'","Ska","Skala","Skata","Ske","Sola","Subo","Szo","Tae","Talu","Tar'","Targu","Tela","Tho","Thu","Toha","Tsu'","Tu'","Urga","Vai'","Vara","Vashi","Vee","Vel'","Vena","Verma","Verro","Volo","Xe","Xeri","Xero","Yafri","Yaro","Zarta","Zhe","Zhru","Zu","Zuru"]
		nm11 = ["ban","bdek","be","blai","bor","bulum","caon","char","chia","chite","co","cole","cona","ctor","dae","dai","don","dor","drakk","driik","fen","frir","gan","go","gol","grim","gum","gutai","hiam","hr","jz","kal","kar","kari","katon","kha","kim","kir","kona","lach","lakim","lan","laro","lavech","lemy","ler","lgaar","lial","lian","lkca","llig","llion","llon","los","lsa","lus","mah","makar","man","mech","mine","mmon","nder","ndian","nea","nian","nid","nitan","noch","nos","pico","pito","pphon","ra","rah","ram","rast","rath","rbul","rbulo","rcyra","rdaci","rdan","rdova","ren","resh","rh","riah","riam","rian","rica","rkov","rleo","rnous","ro","ron","ros","rpico","rqol","rrion","rrox","rtath","rtes","rus","rvon","ryon","san","sarro","sein","shan","slan","ssir","stion","tai","tan","taron","tek","ter","thak","thar","ther","thigg","tikan","tor","trok","trus","vaan","var","vech","veren","viton","von","vydae","xx","zlo","zra"]
		nm12 = ["Ab","Ad","Ak","Alb","Alv","Am","Andr","Aq","Ber","Bl","Blant","Blay","C","Calg","Ch","Chr","Cort","Cyb","Dar","Dars","Dom","Elg","Eng","F","Ferr","Fur","G","Gr","Grenz","Guill","H","Hest","Inv","Iss","K","Kan","Kant","Karr","Kyr","M","Med","Mend","Mor","Morv","N","Neot","Ort","P","Ph","Phor","R","Rub","S","Sh","Sharr","Shr","Sol","T","Tar","Th","Tham","Tib","Tig","Tr","Trism","Ush","V","Vib","Vid","W","Wyrd"]
		nm13 = ["addas","ai","ake","an","ane","antar","antor","ar","are","aris","as","asi","atica","auth","ay","edth","ef","ein","elis","entre","era","erec","erro","erus","es","ev","exus","ez","iam","iar","ica","idya","iel","ikus","im","io","ios","ist","istus","it","ius","ixx","on","onus","or","orak","os","oss","ova","ox","oza","uebus","uil","uila","urus","us","yras","ys"]

		all_names = " ".join(i.lower() for i in nm1 + list("".join(i) for i in product(nm2, nm3)) + list("".join(i) for i in product(nm4, nm5)) + list("".join(i) for i in product(nm6, nm7)) + list("".join(i) for i in product(nm8, nm9)) + list("".join(i) for i in product(nm10, nm11)) + list("".join(i) for i in product(nm12, nm13)))

		if phrase.lower() not in all_names:
			return await ctx.send("not possible")

		names = []

		while len(names) != 10:
			name = ""

			while phrase.lower() not in name.lower():
				i = random.randint(0, 12)

				if i < 3:
					name = random.choice(nm1)
				elif i < 6:
					name = random.choice(nm2) + random.choice(nm3) + " " + random.choice(nm4) + random.choice(nm5)
				elif i < 9:
					name = random.choice(nm6) + random.choice(nm7) + " " + random.choice(nm8) + random.choice(nm9)
				else:
					name = random.choice(nm10) + random.choice(nm11) + " " + random.choice(nm12) + random.choice(nm13)

			names.append(name)

		await ctx.send("\n".join(set(names)))

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def spoil(self, ctx):
		"""
		`{0}spoil` __`Reveals last spoiler`__

		**Usage:** {0}spoil

		**Examples:**
		`{0}spoil` <embed>
		"""

		if not self.bot.channel_spoil_dict[str(ctx.channel.id)] or self.bot.channel_spoil_dict[str(ctx.channel.id)] is None:
			embed = discord.Embed(title = "", description = "No recent spoilers", colour = random.randint(0, 0xFFFFFF))
		else:
			channel_spoil_info = self.bot.channel_spoil_dict[str(ctx.channel.id)]
			author = channel_spoil_info[0]
			avatar_url = channel_spoil_info[1]
			timestamp = datetime.datetime.fromtimestamp(channel_spoil_info[2])
			spoiler_message = channel_spoil_info[3]
			embed = discord.Embed(title = "Last Spoiler:", description = spoiler_message, colour = random.randint(0, 0xFFFFFF), timestamp = timestamp)
			embed.set_author(name = author, icon_url = avatar_url)

		await ctx.send(embed = embed)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def statussnipe(self, ctx, *args):
		if not args:
			return await ctx.send("Please input a user.")

		embed = discord.Embed(title = "Previous Status", colour = random.randint(0, 0xFFFFFF))

		if len(ctx.message.mentions) == 1:
			user = ctx.message.mentions[0]
		elif len(args) == 1 and self.bot.get_user(int(args[0])):
			user = self.bot.get_user(int(args[0]))
		else:
			return await ctx.send("Please input only a user.")

		embed.description = self.bot.status_dict[user.id][0]
		embed.add_field(name = "New Status", value = self.bot.status_dict[user.id][1])
		embed.timestamp = datetime.datetime.utcfromtimestamp(self.bot.status_dict[user.id][2])

		await ctx.send(embed = embed)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def trivia(self, ctx, category = "any", difficulty = "any", qtype = "any"):
		"""
		`{0}trivia` __`Trivia questions`__

		**Usage:** {0}trivia [category difficulty type]

		**Categories:**
		General Knowledge, Entertainment: Books, Entertainment: Film, Entertainment: Music, Entertainment: Musicals & Theatres, Entertainment: Television, Entertainment: Video Games, Entertainment: Board Games, Science & Nature, Science: Computers, Science: Mathematics, Mythology, Sports, Geography, History, Politics, Art, Celebrities, Animals, Vehicles, Entertainment: Comics, Science: Gadgets, Entertainment: Japanese Anime & Manga, Entertainment: Cartoon & Animations

		**Difficulties:**
		easy, medium, hard

		**Type:**:
		multiple, boolean

		**Examples:**
		`{0}trivia` random trivia question in any category, difficulty, and type
		`{0}trivia general` random trivia question in general knowledge, any difficulty, any type
		`{0}trivia general easy` random trivia question in general knowledge, easy, any type
		`{0}trivia general easy boolean` random trivia question in general knowledge, easy, T/F

		use "any" in place of category/difficulty/type to leave it as randomized.
		`{0}trivia general any boolean` random trivia question in general knowledge, any difficulty, T/F
		"""

		url = "https://opentdb.com/api.php?amount=1"

		categories = [0, 1, 2, 3, 4, 5, 6, 7, 8, "General Knowledge", "Entertainment: Books", "Entertainment: Film", "Entertainment: Music", "Entertainment: Musicals & Theatres", "Entertainment: Television", "Entertainment: Video Games", "Entertainment: Board Games", "Science & Nature", "Science: Computers", "Science: Mathematics", "Mythology", "Sports", "Geography", "History", "Politics", "Art", "Celebrities", "Animals", "Vehicles", "Entertainment: Comics", "Science: Gadgets", "Entertainment: Japanese Anime & Manga", "Entertainment: Cartoon & Animations"]

		if category != "any":
			for i in range(9, len(categories)):
				if category.lower() in categories[i].lower():
					url += f"&category={i}"
					break
			else:
				return await ctx.send("Please enter a valid category.", delete_after = 5)

		if difficulty != "any":
			if difficulty.lower() in ["easy", "medium", "hard"]:
				url += f"&difficulty={difficulty.lower()}"
			else:
				return await ctx.send("Please enter a valid difficulty.", delete_after = 5)

		if qtype != "any":
			if qtype.lower() in ["multiple", "boolean"]:
				url += f"&type={qtype.lower()}"
			else:
				return await ctx.send("Please enter a valid question type.", delete_after = 5)

		question = requests.get(url).json()

		if question["response_code"] == 1:
			return await ctx.send("No questions with given parameters.", delete_after = 5)
		else:
			question = question["results"][0]

		user = ctx.author
		answers = "*You have 10 seconds to answer.*\n\n"

		correct = html.unescape(question["correct_answer"])
		q = html.unescape(question["question"])
		choices = [html.unescape(i) for i in question["incorrect_answers"]] + [correct]
		random.shuffle(choices)

		if question["type"] == "multiple":
			answers += f"1) *{choices[0]}*\n2) *{choices[1]}*\n3) *{choices[2]}*\n4) *{choices[3]}*"
		else:
			answers += f"1) *{choices[0]}*\n2) *{choices[1]}*"

		if question["difficulty"] == "easy":
			earned = 5
		elif question["difficulty"] == "medium":
			earned = 10
		else:
			earned = 15

		embed = discord.Embed(title = q, description = answers)
		embed.add_field(name = "Difficulty", value = f"`{question['difficulty']}`", inline = True)
		embed.add_field(name = "Category", value = f"`{question['category']}`", inline = True)
		embed.add_field(name = "Type", value = f"`{question['type']}`", inline = True)
		embed.add_field(name = "Value", value = str(earned), inline = True)

		await ctx.send(embed = embed)

		def check(m):
			return m.channel == ctx.channel and m.author == ctx.author

		try:
			answer = await self.bot.wait_for("message", timeout = 10, check = check)
		except asyncio.TimeoutError:
			await ctx.send("Timed out.", delete_after = 5)
			return await ctx.send(f"Incorrect. The correct answer is {correct}.")

		if answer.content.startswith(self.bot.command_prefix):
			await ctx.send(f"Incorrect. The correct answer is {correct}.")
		else:
			try:
				index = int(answer.content) - 1
			except ValueError:
				return await ctx.send(f"Incorrect. The correct answer is {correct}.")

			if index == choices.index(correct):
				await ctx.send(f"Correct! You earned **{earned}** coins.")
				self.bot.user_data[str(user.id)]["coins"] += earned
				self.bot.update_data(user)
			else:
				await ctx.send(f"Incorrect. The correct answer is {correct}.")

def setup(bot):
	bot.add_cog(Fun(bot))
