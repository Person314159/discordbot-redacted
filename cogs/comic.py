#!/usr/bin/python3
import datetime
import os
import random
import time

import aiohttp
import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

from util.disabled import disabled


class Comic(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name = "c&h")
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def c_and_h(self, ctx, *args):
		"""
		`{0}c&h` __`Cyanide and Happiness comics`__

		**Usage:** {0}c&h [random | index]

		**Examples:**
		`{0}c&h` returns latest c&h comic
		`{0}c&h 1024` returns 1024th c&h comic
		`{0}c&h random` returns random c&h comic
		"""

		url = "http://explosm.net/comics/"

		if args:
			if len(args) == 1:
				if args[0].lower() == "random":
					index = "random"
				else:
					try:
						index = int(args[0])
					except ValueError:
						return await ctx.send("Please input a valid index.", delete_after = 5)

				url += f"{index}"
			else:
				return await ctx.send("Please input valid arguments.", delete_after = 5)

		data = requests.get(url).text

		if data == "Could not find comic":
			return await ctx.send(data)

		soup = BeautifulSoup(data, "html.parser")

		if not args:
			url = "http:" + soup.find(id = "main-comic").attrs["src"]
		else:
			url = soup.find(property = "og:image").attrs["content"]

		index = soup.find(class_ = "favoritable js-ga-event").attrs["data-id"]
		date = soup.find(id = "comic-author").text.split("\n")[1]

		embed = discord.Embed(colour = random.randint(0, 0xFFFFFF))
		embed.set_image(url = url)
		embed.set_footer(text = f"{date} ({index})")
		await ctx.send(embed = embed)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def garfield(self, ctx, *args):
		"""
		`{0}garfield` __`Garfield comics`__

		**Usage:** {0}garfield [<year> <month> <day> | random]

		**Examples:**
		`{0}garfield` [comic]
		`{0}garfield 1979 07 19` [comic]
		`{0}garfield random` [comic]
		"""

		try:
			if not args:
				date = datetime.datetime.now()
			elif len(args) == 1 and args[0] == "random":
				date = datetime.datetime(1978, 7, 19) + datetime.timedelta(seconds = random.randint(0, int((datetime.datetime.now() - datetime.datetime(1978, 7, 19)).total_seconds())))
			else:
				date = datetime.datetime.strptime(" ".join(args), "%Y %m %d")
		except Exception:
			return await ctx.send("Please input a valid date.", delete_after = 5)

		if date > datetime.datetime.now() or date < datetime.datetime(1978, 7, 19):
			return await ctx.send(f"Please input a date between 1979-07-19 and {datetime.datetime.now().strftime('%Y-%m-%d')}.", delete_after = 5)

		year, month, day = str(date.year), str(date.month).zfill(2), str(date.day).zfill(2)

		data = requests.get(f"https://www.gocomics.com/garfield/{year}/{month}/{day}").text

		soup = BeautifulSoup(data, "html.parser")

		if soup.title.string == "404 Page Not Found - GoComics":
			return await ctx.send("Comic not found.", delete_after = 5)

		url = soup.find("picture", class_ = "item-comic-image").img.attrs["src"]

		data = requests.get(url)

		with open(f"{year}-{month}-{day}.gif", "wb") as f:
			f.write(data.content)

		embed = discord.Embed(title = f"{year}-{month}-{day}", colour = random.randint(0, 0xFFFFFF))
		embed.set_image(url = f"attachment://{year}-{month}-{day}.gif")

		await ctx.send(embed = embed, file = discord.File(f"{year}-{month}-{day}.gif"))

		os.remove(f"{year}-{month}-{day}.gif")


	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def xkcd(self, ctx, *args):
		"""
		`{0}xkcd` __`xkcd comics`__

		**Usage:** {0}xkcd [random | index]

		**Examples:**
		`{0}xkcd` returns latest xkcd comic
		`{0}xkcd 1024` returns 1024th xkcd comic
		`{0}xkcd random` returns random xkcd comic
		"""

		api_url = "https://xkcd.com{}info.0.json"

		async with aiohttp.ClientSession() as cs:
			async with cs.get(api_url.format("/")) as r:
				js = await r.json()

				if len(args) == 1:
					if args[0] == "random":
						random_comic = random.randint(0, js["num"])

						async with cs.get(api_url.format(f"/{random_comic}/")) as r:
							if r.status == 200:
								js = await r.json()
					else:
						try:
							num = int(args[0])

							if 1 <= num and num <= js["num"]:
								async with cs.get(api_url.format(f"/{args[0]}/")) as r:
									if r.status == 200:
										js = await r.json()
							else:
								raise ValueError
						except ValueError:
							return await ctx.send(f"Please enter a positive integer between 1 and {js['num']}.", delete_after = 5)

				comic_url = f"https://xkcd.com/{js['num']}/"
				date = f"{js['year']}/{js['month']}/{js['day']}"
				embed = discord.Embed(title = f"**{js['safe_title']}**", description = js["alt"], url = comic_url, colour = random.randint(0, 0xFFFFFF))
				embed.set_image(url = js["img"])
				embed.set_footer(text = f"{date} ({js['num']})")
				await ctx.send(embed = embed)

def setup(bot):
	bot.add_cog(Comic(bot))
