#!/usr/bin/python3
import ast
import asyncio
import base64
import datetime
import mimetypes
import os
import random
import re
import time
from collections import OrderedDict
from fractions import Fraction
from io import BytesIO
from math import *

import baseconvert
import cartopy.crs as ccrs
import discord
import matplotlib.pyplot as plt
import requests
import webcolors
from arcgis.features import FeatureLayer
from bs4 import BeautifulSoup
from discord.ext import commands
from geopy.geocoders import GeoNames
from googletrans import Translator, constants
# import scipy
from PIL import Image, ImageSequence

from util.disabled import disabled
from util.elementdata import element_list
from util.staffsalaries import staff_salary_dict


class Utility(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def antipode(self, ctx):
		"""
		`{0}antipode` __`Antipodes`__

		**Usage:** {0}antipode <location>

		**Examples:**
		`{0}antipode vancouver` [two embeds]
		"""

		location = ctx.message.content[len(self.bot.command_prefix) + 9:]

		if location:
			geolocator = GeoNames(username = "person314159")
			location = geolocator.geocode(location)

			if location:
				ax = plt.axes(projection = ccrs.Orthographic(central_longitude = location.longitude, central_latitude = location.latitude))
				ax.outline_patch.set_visible(False)
				ax.background_patch.set_visible(False)
				ax.stock_img()

				plt.plot(location.longitude, location.latitude, "r+", markersize = 12)
				plt.savefig("location.png", bbox_inches = "tight", pad_inches = 0, transparent = True)

				plt.clf()

				antipode = (-location.latitude, location.longitude - 180 if location.longitude > 0 else location.longitude + 180)

				ax = plt.axes(projection = ccrs.Orthographic(central_longitude = antipode[1], central_latitude = antipode[0]))
				ax.outline_patch.set_visible(False)
				ax.background_patch.set_visible(False)
				ax.stock_img()

				plt.plot(antipode[1], antipode[0], "r+", markersize = 12)
				plt.savefig("antipode.png", bbox_inches = "tight", pad_inches = 0, transparent = True)

				location_embed = discord.Embed(title = "Location", colour = random.randint(0, 0xFFFFFF))
				antipode_embed = discord.Embed(title = "Antipode", colour = random.randint(0, 0xFFFFFF))

				location_embed.set_image(url = "attachment://location.png")
				antipode_embed.set_image(url = "attachment://antipode.png")

				location_embed.set_footer(text = f"{location.latitude}, {location.longitude}")
				antipode_embed.set_footer(text = f"{antipode[0]}, {antipode[1]}")

				await ctx.send(embed = location_embed, file = discord.File("location.png"))
				await ctx.send(embed = antipode_embed, file = discord.File("antipode.png"))

				os.remove("location.png")
				os.remove("antipode.png")

			else:
				await ctx.send("Location not found.", delete_after = 5)
		else:
			await ctx.send("Please enter a valid location.", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def bitcoin(self, ctx, *args):
		"""
		`{0}bitcoin` __`Bitcoin prices`__

		**Usage:** {0}bitcoin [currencies]

		**Examples:**
		`{0}bitcoin` [embed of CAD and USD]
		`{0}bitcoin USD` returns current Bitcoin price in USD
		`{0}bitcoin USD GBP` returns current Bitcoin price in USD and GBP
		"""

		value = requests.get("https://min-api.cryptocompare.com/data/price?&extraParams=https://www.cryptocompare.com&fsym=BTC&tsyms=USD").json()["USD"]

		if not args:
			rates = requests.get("https://api.exchangeratesapi.io/latest?base=USD&symbols=USD,CAD").json()["rates"]
			embed = discord.Embed(title = "Bitcoin Exchange Rates", colour = random.randint(0, 0xFFFFFF), timestamp = datetime.datetime.utcnow())

			for i in sorted(rates.keys()):
				currency = f"{i} {chr(ord(i[0]) + 127397)}{chr(ord(i[1]) + 127397)}"
				embed.add_field(name = currency, value = "{:.2f}".format(value * rates[i]), inline = True)

			await ctx.send(embed = embed)
		else:
			embed = discord.Embed(title = "Bitcoin Exchange Rates", colour = random.randint(0, 0xFFFFFF))

			for i in args:
				code = i.upper()
				rates = requests.get(f"https://api.exchangeratesapi.io/latest?base=USD&symbols={code}").json()

				if "error" in rates.keys():
					return await ctx.send(f"\"{i}\" was not found.", delete_after = 5)

				embed.add_field(name = f"{code} {chr(ord(code[0]) + 127397)}{chr(ord(code[1]) + 127397)}", value = "{:.2f}".format(value * rates["rates"][code]), inline = True)
			await ctx.send(embed = embed)

	# # timeout doesn't work
	# @commands.command()
	# @disabled()
	# @commands.cooldown(1, 5, commands.BucketType.user)
	# @docparams(self.bot.command_prefix)
	# async def calculate(self, ctx):
	# 	"""
	# 	`{0}calculate` __`Calculates expression`__

	# 	**Usage:** {0}calculate <expression>

	# 	**Examples:**
	# 	`{0}calculate 2+2` 5\nFor list of functions do `{0}calculate list`.
	# 	"""

	# 	new_message = ctx.message.content[(len(self.bot.command_prefix) + 10):]

	# 	if new_message:
	# 		if new_message == "list":
	# 			help_message = "Note that all trig functions are in radians.\n```a+b                      add \na-b                      subtract \na*b                      multiply \na/b                      divide \na//b                     floor(a/b) \na**b                     a^b \na%b                      a mod b, use with ints \nabs(a)                   |a| \nacos[h](a)               arccos[h] \nasin[h](a)               arcsin[h] \natan[h](a)               arctan[h] \natan2(y,x)               atan(y/x), finds correct quadrant for angle \nbin(a)                   binary conversion \nbool(expression)         returns \"True\" or \"False\" \nceil(expression)         rounds up to nearest integer \ncos[h](a)                cosine[hyperbolic] \ndegrees(a)               converts radians to degrees \ndivmod(a,b)              returns quotient and remainder of a/b \nexp(a)                   e^a \nfactorial(a)             a! (positive ints only) \nfloor(expression)        rounds down to nearest integer \nfmod(a,b)                a mod b, use with floats```"
	# 			help_message2 = "```fsum(a,[b,...])          sums list \ngamma(a)                 (a-1)! (positive reals only) \ngcd(a,b)                 returns greatest common divisor of a,b \nhex(a)                   hexadecimal conversion \nhypot(x,y)               sqrt(x^2+y^2) \nlog(a)                   log_e(a) \nlog(a,b)                 log_b(a) \nlog10(a)                 more accurate than log(a,10) \nlog2(a)                  more accurate than log(a,2) \nmax(a,[b,...])           returns largest value in list \nmin(a,[b,...])           returns smallest value in list \nmodf(a)                  returns fractional and integer parts of a \noct(a)                   octal conversion \npow(a,b)                 a^b (not precise) \nradians(a)               converts degrees to radians \nremainder(a,b)           a mod b \nround(expression, [a])   rounds expression to a places after decimal \nsin[h](a)                sine[hyperbolic] \nsqrt(a)                  square root of a \ntan[h](a)                tangent[hyperbolic] \nconstants:               e, pi, tau```"
	# 			await ctx.send(help_message)
	# 			await ctx.send(help_message2)
	# 			return

	# 		if re.search(r"exec|key|open|eval|input|(?<![cl])os|quit|sys|path|exit|raise|bot|print|help|ctx|vars|import|json|repr|list|str|\"|\'|for|guild_prefix_dict|channel_deletesnipe_dict|channel_editsnipe_dict|channel_spoil_dict|self.bot.poll_dict|user_data|command_toggle_dict", new_message):
	# 			return await ctx.send("STAHP TRYING TO BORK THE BOT", delete_after = 5)

	# 		if re.match(r"2 *\+ *2$", new_message):
	# 			await ctx.send("5")
	# 			return
	# 		else:
	# 			if re.search(r"\^", new_message):
	# 				new_message = new_message.replace("^", "**")

	# 			def result(msg):
	# 				answer = str(eval(msg))
	# 				return answer

	# 			try:
	# 				p = Process(target = result, name = "calculate", args = (new_message,), daemon = True)
	# 				p.start()
	# 				p.join(5)

	# 				if p.is_alive():
	# 					p.terminate()
	# 					p.join()
	# 					raise TimeoutError("Calculation timed out.")

	# 				Result = result(new_message)

	# 				if len(Result) > 2000:
	# 					await ctx.send("{:.15g}".format(s.Float(Result)))
	# 				else:
	# 					await ctx.send(Result)
	# 			except OverflowError:
	# 				await ctx.send("inf")
	# 			except Exception as error:
	# 				await ctx.send(error, delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def choose(self, ctx):
		"""
		`{0}choose` __`Picks one thing at random`__

		**Usage:** {0}choose <arg1> | <arg2> | ...

		**Examples:**
		`{0}choose nou | hmm` hmm
		"""

		args = ctx.message.content[len(self.bot.command_prefix) + 7:].split(" | ")

		if not args:
			await ctx.send("You didn't input anything.", delete_after = 5)
		elif len(args) == 1 and args[0] == "rep":
			user = random.choice(ctx.guild.members)

			while user == ctx.author or user.bot or user.id in [231259532863602698, 231484431532032000]:
				user = random.choice(ctx.guild.members)

			await ctx.send(user.nick if user.nick else user.name)
		else:
			await ctx.send(f"I choose **{random.choice(args)}**")

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def colour(self, ctx):
		"""
		`{0}colour` __`Colour info`__

		**Usage:** {0}colour <colour>

		**Examples:**
		`{0}colour #ffffff` returns info of colour white
		`{0}colour rgb(0, 0, 0)` returns info of colour black
		`{0}colour hsl(0, 100%, 50%)` returns info of colour red
		`{0}colour cmyk(100%, 0%, 0%, 0%)` returns info of colour cyan
		`{0}colour blue` returns info of colour blue
		"""

		def RGB_to_HSL(r, g, b):
			r /= 255
			g /= 255
			b /= 255
			c_max = max(r, g, b)
			c_min = min(r, g, b)
			delta = c_max - c_min
			l = (c_max + c_min) / 2

			if not delta:
				h = 0
				s = 0
			else:
				s = delta / (1 - abs(2 * l - 1))
				if c_max == r:
					h = 60 * (((g - b) / delta) % 6)
				elif c_max == g:
					h = 60 * ((b - r) / delta + 2)
				else:
					h = 60 * ((r - g) / delta + 4)

			s *= 100
			l *= 100
			return h, s, l

		def HSL_to_RGB(h, s, l):
			h %= 360
			s /= 100
			l /= 100
			c = (1 - abs(2 * l - 1)) * s
			x = c * (1 - abs((h / 60) % 2 - 1))
			m = l - c / 2

			if 0 <= h < 60:
				temp = [c, x, 0]
			elif 60 <= h < 120:
				temp = [x, c, 0]
			elif 120 <= h < 180:
				temp = [0, c, x]
			elif 180 <= h < 240:
				temp = [0, x, c]
			elif 240 <= h < 300:
				temp = [x, 0, c]
			else:
				temp = [c, 0, x]

			return (temp[0] + m) * 255, (temp[1] + m) * 255, (temp[2] + m) * 255

		def RGB_to_CMYK(r, g, b):
			if (r, g, b) == (0, 0, 0):
				return 0, 0, 0, 100

			r /= 255
			g /= 255
			b /= 255
			k = 1 - max(r, g, b)
			c = (1 - r - k) / (1 - k)
			m = (1 - g - k) / (1 - k)
			y = (1 - b - k) / (1 - k)
			c *= 100
			m *= 100
			y *= 100
			k *= 100
			return c, m, y, k

		def CMYK_to_RGB(c, m, y, k):
			c /= 100
			m /= 100
			y /= 100
			k /= 100
			r = 255 * (1 - c) * (1 - k)
			g = 255 * (1 - m) * (1 - k)
			b = 255 * (1 - y) * (1 - k)
			return r, g, b

		def RGB_to_HEX(r, g, b):
			return hex(r * 16 ** 4 + g * 16 ** 2 + b)[2:].zfill(6)

		def closest_colour(requested_colour):
			min_colours = {}

			for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
				r_c, g_c, b_c = webcolors.hex_to_rgb(key)
				rd = (r_c - requested_colour[0]) ** 2
				gd = (g_c - requested_colour[1]) ** 2
				bd = (b_c - requested_colour[2]) ** 2
				min_colours[(rd + gd + bd)] = name

			return min_colours[min(min_colours.keys())]

		def get_colour_name(requested_colour):
			try:
				closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
			except ValueError:
				closest_name = closest_colour(requested_colour)
				actual_name = None

			return actual_name, closest_name

		css = {"lightsalmon": "0xFFA07A", "salmon": "0xFA8072", "darksalmon": "0xE9967A", "lightcoral": "0xF08080", "indianred": "0xCD5C5C", "crimson": "0xDC143C", "firebrick": "0xB22222", "red": "0xFF0000", "darkred": "0x8B0000", "coral": "0xFF7F50", "tomato": "0xFF6347", "orangered": "0xFF4500", "gold": "0xFFD700", "orange": "0xFFA500", "darkorange": "0xFF8C00", "lightyellow": "0xFFFFE0", "lemonchiffon": "0xFFFACD", "lightgoldenrodyellow": "0xFAFAD2", "papayawhip": "0xFFEFD5", "moccasin": "0xFFE4B5", "peachpuff": "0xFFDAB9", "palegoldenrod": "0xEEE8AA", "khaki": "0xF0E68C", "darkkhaki": "0xBDB76B", "yellow": "0xFFFF00", "lawngreen": "0x7CFC00", "chartreuse": "0x7FFF00", "limegreen": "0x32CD32", "lime": "0x00FF00", "forestgreen": "0x228B22", "green": "0x008000", "darkgreen": "0x006400", "greenyellow": "0xADFF2F", "yellowgreen": "0x9ACD32", "springgreen": "0x00FF7F", "mediumspringgreen": "0x00FA9A", "lightgreen": "0x90EE90", "palegreen": "0x98FB98", "darkseagreen": "0x8FBC8F", "mediumseagreen": "0x3CB371", "seagreen": "0x2E8B57", "olive": "0x808000", "darkolivegreen": "0x556B2F", "olivedrab": "0x6B8E23", "lightcyan": "0xE0FFFF", "cyan": "0x00FFFF", "aqua": "0x00FFFF", "aquamarine": "0x7FFFD4", "mediumaquamarine": "0x66CDAA", "paleturquoise": "0xAFEEEE", "turquoise": "0x40E0D0", "mediumturquoise": "0x48D1CC", "darkturquoise": "0x00CED1", "lightseagreen": "0x20B2AA", "cadetblue": "0x5F9EA0", "darkcyan": "0x008B8B", "teal": "0x008080", "powderblue": "0xB0E0E6", "lightblue": "0xADD8E6", "lightskyblue": "0x87CEFA", "skyblue": "0x87CEEB", "deepskyblue": "0x00BFFF", "lightsteelblue": "0xB0C4DE", "dodgerblue": "0x1E90FF", "cornflowerblue": "0x6495ED", "steelblue": "0x4682B4", "royalblue": "0x4169E1", "blue": "0x0000FF", "mediumblue": "0x0000CD", "darkblue": "0x00008B", "navy": "0x000080", "midnightblue": "0x191970", "mediumslateblue": "0x7B68EE", "slateblue": "0x6A5ACD", "darkslateblue": "0x483D8B", "lavender": "0xE6E6FA", "thistle": "0xD8BFD8", "plum": "0xDDA0DD", "violet": "0xEE82EE", "orchid": "0xDA70D6", "fuchsia": "0xFF00FF", "magenta": "0xFF00FF", "mediumorchid": "0xBA55D3", "mediumpurple": "0x9370DB", "blueviolet": "0x8A2BE2", "darkviolet": "0x9400D3", "darkorchid": "0x9932CC", "darkmagenta": "0x8B008B", "purple": "0x800080", "indigo": "0x4B0082", "pink": "0xFFC0CB", "lightpink": "0xFFB6C1", "hotpink": "0xFF69B4", "deeppink": "0xFF1493", "palevioletred": "0xDB7093", "mediumvioletred": "0xC71585", "white": "0xFFFFFF", "snow": "0xFFFAFA", "honeydew": "0xF0FFF0", "mintcream": "0xF5FFFA", "azure": "0xF0FFFF", "aliceblue": "0xF0F8FF", "ghostwhite": "0xF8F8FF", "whitesmoke": "0xF5F5F5", "seashell": "0xFFF5EE", "beige": "0xF5F5DC", "oldlace": "0xFDF5E6", "floralwhite": "0xFFFAF0", "ivory": "0xFFFFF0", "antiquewhite": "0xFAEBD7", "linen": "0xFAF0E6", "lavenderblush": "0xFFF0F5", "mistyrose": "0xFFE4E1", "gainsboro": "0xDCDCDC", "lightgray": "0xD3D3D3", "silver": "0xC0C0C0", "darkgray": "0xA9A9A9", "gray": "0x808080", "dimgray": "0x696969", "lightslategray": "0x778899", "slategray": "0x708090", "darkslategray": "0x2F4F4F", "black": "0x000000", "cornsilk": "0xFFF8DC", "blanchedalmond": "0xFFEBCD", "bisque": "0xFFE4C4", "navajowhite": "0xFFDEAD", "wheat": "0xF5DEB3", "burlywood": "0xDEB887", "tan": "0xD2B48C", "rosybrown": "0xBC8F8F", "sandybrown": "0xF4A460", "goldenrod": "0xDAA520", "peru": "0xCD853F", "chocolate": "0xD2691E", "saddlebrown": "0x8B4513", "sienna": "0xA0522D", "brown": "0xA52A2A", "maroon": "0x800000"}

		def RGB(r, g, b, colour):
			h, s, l = RGB_to_HSL(r, g, b)
			c, m, y, k = RGB_to_CMYK(r, g, b)
			Hex = f"#{RGB_to_HEX(r, g, b)}"
			rgb = f"rgb({r},{g},{b})"
			hsl = f"hsl({round(float(h), 2)},{round(float(s), 2)}%,{round(float(l), 2)}%)"
			cmyk = f"cmyk({round(float(c), 2)}%,{round(float(m), 2)}%,{round(float(y), 2)}%,{round(float(k), 2)}%)"
			css_code = get_colour_name((r, g, b))[1]
			embed = discord.Embed(title = colour, description = "", colour = int(Hex[1:], 16))
			embed.add_field(name = "Hex", value = Hex, inline = True)
			embed.add_field(name = "RGB", value = rgb, inline = True)
			embed.add_field(name = "HSL", value = hsl, inline = True)
			embed.add_field(name = "CMYK", value = cmyk, inline = True)
			embed.add_field(name = "CSS", value = css_code, inline = True)
			embed.set_thumbnail(url = f"https://serux.pro/rendercolour/?rgb={r},{g},{b}")
			return embed

		def hslRGB(h, s, l, colour):
			h -= (h // 360) * 360
			r, g, b = HSL_to_RGB(h, s, l)
			c, m, y, k = RGB_to_CMYK(r, g, b)
			r = round(r)
			g = round(g)
			b = round(b)
			Hex = f"#{RGB_to_HEX(r, g, b)}"
			rgb = f"rgb({r},{g},{b})"
			hsl = f"hsl({round(float(h), 2)},{round(float(s), 2)}%,{round(float(l), 2)}%)"
			cmyk = f"cmyk({round(float(c), 2)}%,{round(float(m), 2)}%,{round(float(y), 2)}%,{round(float(k), 2)}%)"
			css_code = get_colour_name((r, g, b))[1]
			embed = discord.Embed(title = colour, description = "", colour = int(Hex[1:], 16))
			embed.add_field(name = "Hex", value = Hex, inline = True)
			embed.add_field(name = "RGB", value = rgb, inline = True)
			embed.add_field(name = "HSL", value = hsl, inline = True)
			embed.add_field(name = "CMYK", value = cmyk, inline = True)
			embed.add_field(name = "CSS", value = css_code, inline = True)
			embed.set_thumbnail(url = f"https://serux.pro/rendercolour/?rgb={r},{g},{b}")
			return embed

		def cmykRGB(c, m, y, k, colour):
			r, g, b = CMYK_to_RGB(c, m, y, k)
			h, s, l = RGB_to_HSL(r, g, b)
			r = round(r)
			g = round(g)
			b = round(b)
			Hex = f"#{RGB_to_HEX(r, g, b)}"
			rgb = f"rgb({r},{g},{b})"
			hsl = f"hsl({round(float(h), 2)},{round(float(s), 2)}%,{round(float(l), 2)}%)"
			cmyk = f"cmyk({round(float(c), 2)}%,{round(float(m), 2)}%,{round(float(y), 2)}%,{round(float(k), 2)}%)"
			css_code = get_colour_name((r, g, b))[1]
			embed = discord.Embed(title = colour, description = "", colour = int(Hex[1:], 16))
			embed.add_field(name = "Hex", value = Hex, inline = True)
			embed.add_field(name = "RGB", value = rgb, inline = True)
			embed.add_field(name = "HSL", value = hsl, inline = True)
			embed.add_field(name = "CMYK", value = cmyk, inline = True)
			embed.add_field(name = "CSS", value = css_code, inline = True)
			embed.set_thumbnail(url = f"https://serux.pro/rendercolour/?rgb={r},{g},{b}")
			return embed

		def cssRGB(colour):
			r = int(css[colour][2:4], 16)
			g = int(css[colour][4:6], 16)
			b = int(css[colour][6:], 16)
			h, s, l = RGB_to_HSL(r, g, b)
			c, m, y, k = RGB_to_CMYK(r, g, b)
			Hex = f"#{RGB_to_HEX(r, g, b)}"
			rgb = f"rgb({r},{g},{b})"
			hsl = f"hsl({round(float(h), 2)},{round(float(s), 2)}%,{round(float(l), 2)}%)"
			cmyk = f"cmyk({round(float(c), 2)}%,{round(float(m), 2)}%,{round(float(y), 2)}%,{round(float(k), 2)}%)"
			css_code = get_colour_name((r, g, b))[1]
			embed = discord.Embed(title = colour, description = "", colour = int(Hex[1:], 16))
			embed.add_field(name = "Hex", value = Hex, inline = True)
			embed.add_field(name = "RGB", value = rgb, inline = True)
			embed.add_field(name = "HSL", value = hsl, inline = True)
			embed.add_field(name = "CMYK", value = cmyk, inline = True)
			embed.add_field(name = "CSS", value = css_code, inline = True)
			embed.set_thumbnail(url = f"https://serux.pro/rendercolour/?rgb={r},{g},{b}")
			return embed

		colour = ctx.message.content[len(self.bot.command_prefix) + 7:]

		if not colour:
			await ctx.send(embed = RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), "Random Colour"))
		elif re.fullmatch(r"#([0-9A-Fa-f]{3}){1,2}", colour):
			if len(colour) == 7:
				await ctx.send(embed = RGB(int(colour[1:3], 16), int(colour[3:5], 16), int(colour[5:], 16), colour))
			elif len(colour) == 4:
				await ctx.send(embed = RGB(int(colour[1] * 2, 16), int(colour[2] * 2, 16), int(colour[3] * 2, 16), colour))
		elif re.fullmatch(r"([0-9A-Fa-f]{3}){1,2}", colour):
			if len(colour) == 6:
				await ctx.send(embed = RGB(int(colour[:2], 16), int(colour[2:4], 16), int(colour[4:], 16), colour))
			elif len(colour) == 3:
				await ctx.send(embed = RGB(int(colour[0] * 2, 16), int(colour[1] * 2, 16), int(colour[2] * 2, 16), colour))
		elif re.fullmatch(r"rgb\((\d{1,3}, *){2}\d{1,3}\)", colour):
			content = ast.literal_eval(colour[3:])
			await ctx.send(embed = RGB(content[0], content[1], content[2], colour))
		elif re.fullmatch(r"hsl\(\d{1,3}(\.\d*)?, *\d{1,3}(\.\d*)?%, *\d{1,3}(\.\d*)?%\)", colour):
			content = colour
			colour = colour[4:].split(")")[0].split(",")
			h = Fraction(colour[0])
			s = Fraction(colour[1][:-1])
			l = Fraction(colour[2][:-1])

			if h > 360 or s > 100 or l > 100:
				raise ValueError

			await ctx.send(embed = hslRGB(h, s, l, content))
		elif re.fullmatch(r"cmyk\((\d{1,3}(\.\d*)?%, *){3}\d{1,3}(\.\d*)?%\)", colour):
			content = colour
			colour = colour[5:].split(")")[0].split(",")
			c = Fraction(colour[0].split("%")[0])
			m = Fraction(colour[1].split("%")[0])
			y = Fraction(colour[2].split("%")[0])
			k = Fraction(colour[3].split("%")[0])

			if c > 100 or m > 100 or y > 100 or k > 100:
				raise ValueError

			await ctx.send(embed = cmykRGB(c, m, y, k, content))
		elif colour.lower() in css.keys():
			await ctx.send(embed = cssRGB(colour.lower()))
		else:
			return await ctx.send("You inputted an invalid colour. Please try again.", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def course(self, ctx, *args):
		"""
		`{0}course` __`UBC courses lookup`__

		**Usage:** {0}course <subject> [<course> <section>]

		**Examples:**
		`{0}course MATH` returns info on math subject
		`{0}course MATH 105` returns info on math 105 course
		`{0}course MATH 105 202` returns info on math 105 202 section
		"""

		session = "2020S"

		if not args:
			await ctx.send("You didn't enter a course.", delete_after = 5)
		elif len(args) == 1 and re.fullmatch(r"[A-Za-z]{2,4}", args[0]):
			subject = (args[0]).upper()
			data = requests.get(f"https://ubc-courses-api.herokuapp.com/{session}/{subject}").json()

			if data:
				if data["courses"] == []:
					courses = None
				else:
					courses = ", ".join(data["courses"])

				embed = discord.Embed(title = data["code"], description = data["title"], colour = random.randint(0, 0xFFFFFF))
				embed.add_field(name = "Faculty", value = data["faculty"], inline = False)
				embed.add_field(name = "All courses", value = courses, inline = False)
				embed.add_field(name = "Link", value = f"https://courses.students.ubc.ca{data['link']}", inline = False)
				embed.set_footer(text = session)
				await ctx.send(embed = embed)
			else:
				await ctx.send("Subject not found.", delete_after = 5)
		elif len(args) == 2:
			if f"{(args[0]).upper()} {args[1]}" == "UROL *" or f"{(args[0]).upper()} {args[1]}" == "PLAS *":
				subject = f"{(args[0]).upper()} {args[1]}"
				data = requests.get(f"https://ubc-courses-api.herokuapp.com/{session}/{subject}").json()
				embed = discord.Embed(title = data["code"], description = data["title"], colour = random.randint(0, 0xFFFFFF))
				embed.add_field(name = "Faculty", value = data["faculty"], inline = False)
				embed.add_field(name = "All courses", value = None, inline = False)
				embed.add_field(name = "Link", value = None, inline = False)
				embed.set_footer(text = session)
				await ctx.send(embed = embed)
			elif re.fullmatch(r"[A-Za-z]{2,4}", args[0]) and re.fullmatch(r"\d{3}[A-Za-z]?", args[1]):
				subject = (args[0]).upper()
				course = (args[1]).upper()
				data = requests.get(f"https://ubc-courses-api.herokuapp.com/{session}/{subject}/{course}").json()

				if data:
					if data["sections"] == []:
						sections = None
					else:
						sections = ", ".join(data["sections"])

					embed = discord.Embed(title = data["course_name"], description = data["course_title"], colour = random.randint(0, 0xFFFFFF))
					embed.add_field(name = "Sections", value = sections, inline = False)
					embed.add_field(name = "Link", value = f"https://courses.students.ubc.ca{data['course_link']}", inline = False)
					embed.set_footer(text = session)
					await ctx.send(embed = embed)
				else:
					await ctx.send("Course not found.", delete_after = 5)
			else:
				await ctx.send("Please enter the right args.", delete_after = 5)
		elif len(args) == 3 and re.fullmatch(r"[A-Za-z]{2,4}", args[0]) and re.fullmatch(r"\d{3}[A-Za-z]?", args[1]) and re.fullmatch(r"[A-Za-z\d]{3}", args[2]):
			subject = (args[0]).upper()
			course = (args[1]).upper()
			section = (args[2]).upper()
			data = requests.get(f"https://ubc-courses-api.herokuapp.com/{session}/{subject}/{course}/{section}").json()

			if(data):
				if data["comments"] == "":
					comments = None
				elif len(data["comments"]) > 1024:
					comments = f"{' '.join(data['comments'][:1024+1].split(' ')[0:-1])}..."
				else:
					comments = data["comments"]

				if re.fullmatch(r" *", data["status"]):
					status = None
				else:
					status = data["status"]

				if re.fullmatch(r" *", f"{data['days']} {data['start']}-{data['end']}"):
					time = None
				else:
					time = f"{data['days']} {data['start']}-{data['end']}"

				if re.fullmatch(r" *", f"{data['building']} {data['room']}"):
					location = None
				else:
					location = f"{data['building']} {data['room']}"

				embed = discord.Embed(title = data["section"], description = requests.get(f"https://ubc-courses-api.herokuapp.com/{session}/{subject}/{course}").json()["course_title"], colour = random.randint(0, 0xFFFFFF))
				embed.add_field(name = "Type", value = data["activity"], inline = True)
				embed.add_field(name = "Term", value = data["term"], inline = True)
				embed.add_field(name = "Time", value = time, inline = True)
				embed.add_field(name = "Location", value = location, inline = True)
				embed.add_field(name = "Instructors", value = ", ".join(data["instructors"]), inline = True)
				embed.add_field(name = "Status", value = status, inline = True)
				embed.add_field(name = "Total Remaining", value = data["totalRemaining"], inline = True)
				embed.add_field(name = "Currently Registered", value = data["currentlyRegistered"], inline = True)
				embed.add_field(name = "Comment", value = comments, inline = True)
				embed.add_field(name = "Link", value = f"https://courses.students.ubc.ca{data['href']}", inline = True)
				embed.set_footer(text = session)
				await ctx.send(embed = embed)
			else:
				await ctx.send("Section not found.", delete_after = 5)
		else:
			await ctx.send("Please enter the right args.", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def cv(self, ctx, *args):
		"""
		`{0}cv` __`COVID-19 Statistics`__

		**Usage:** {0}cv [page | location]

		**Examples:**
		`{0}cv` returns list of top 10 highest hit regions
		`{0}cv 12` returns page 12 of highest hit regions
		`{0}cv british columbia` returns COVID-19 cases in British Columbia
		"""

		svc = "https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/1"
		feature_layer = FeatureLayer(svc)
		query_result = feature_layer.query(out_fields = ["Confirmed", "Country_Region", "Province_State", "Deaths", "Recovered"])

		data = sorted([res.attributes for res in query_result.features if res.attributes["Confirmed"]], key = lambda x: x["Confirmed"], reverse = True)

		if len(args) <= 1:
			num_pages = ceil(len(data) / 10)
			pg = None

			if args:
				try:
					pg = int(args[0]) - 1
				except ValueError:
					pass

			if pg != None or not args:
				if not args:
					pg = 0

				if pg < 0 or pg >= num_pages:
					return await ctx.send("Please input a valid page number.", delete_after = 5)

				total_confirmed = sum(item["Confirmed"] for item in data)
				total_deaths = sum(item["Deaths"] for item in data)
				total_recovered = sum(item["Recovered"] for item in data)

				d = data[pg * 10:min([(pg + 1) * 10, len(data)])]

				embed = discord.Embed(title = "Coronavirus-Hit Regions", description = f"**Total Confirmed Cases**: **{total_confirmed}**\n**Total Deaths**: {total_deaths} ({round(total_deaths / (total_deaths + total_recovered) * 100, 1)}%)\n**Total Recovered**: {total_recovered} ({round(total_recovered / total_confirmed * 100, 1)}%)", color = random.randint(0, 0xFFFFFF))

				for item in d:
					loc = item["Country_Region"]

					if item["Province_State"] and item["Province_State"] != item["Country_Region"]:
						loc = f"{item['Province_State']}, {loc}"

					embed.add_field(name = loc, value = f"**Confirmed**: {item['Confirmed']}\n**Deaths**: {item['Deaths']} ({0 if not item['Deaths'] and not item['Recovered'] else round(item['Deaths'] / (item['Deaths'] + item['Recovered']) * 100, 1)}%)\n**Recovered**: {item['Recovered']} ({round(item['Recovered'] / item['Confirmed'] * 100, 1)}%)", inline = False)

				embed.set_footer(text = f"Page {pg + 1} of {num_pages}")

				return await ctx.send(embed = embed)

		using = None
		param = " ".join(args)

		for res in query_result.features:
			if res.attributes["Province_State"] and param.lower() in res.attributes["Province_State"].lower():
				using = res.attributes
				break
			elif param.lower() in res.attributes["Country_Region"].lower():
				using = res.attributes
				break
		else:
			return await ctx.send("Region not found.", delete_after = 5)

		embed = discord.Embed(title = f"Coronavirus Data for {param}", color = random.randint(0, 0xFFFFFF))

		loc = using["Country_Region"]

		if using["Province_State"] and using["Province_State"] != using["Country_Region"]:
			loc = f"{using['Province_State']}, {loc}"

		embed.add_field(name = "Rank", value = f"{data.index(using) + 1}/{len(data)}", inline = False)
		embed.add_field(name = "Location", value = loc, inline = False)
		embed.add_field(name = "Total Cases", value = using["Confirmed"], inline = False)
		embed.add_field(name = "Active Cases", value = f"{using['Confirmed'] - using['Deaths'] - using['Recovered']} ({round((using['Confirmed'] - using['Deaths'] - using['Recovered']) / using['Confirmed'] * 100, 1)}%)", inline = False)
		embed.add_field(name = "Deaths", value = f"{using['Deaths']} ({0 if not using['Deaths'] and not using['Recovered'] else round(using['Deaths'] / (using['Deaths'] + using['Recovered']) * 100, 1)}%)", inline = False)
		embed.add_field(name = "Recovered", value = f"{using['Recovered']} ({round(using['Recovered'] / using['Confirmed'] * 100, 1)}%)", inline = False)
		await ctx.send(embed = embed)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def decrypt(self, ctx):
		"""
		`{0}decrypt` __`Decrypts message`__

		**Usage:** {0}decrypt <text>

		**Examples:**
		`{0}decrypt 101 102 103` ABC
		"""

		msg = ctx.message.content[len(self.bot.command_prefix) + 8:]
		result = ""

		try:
			if re.fullmatch(r"([01]{8} )*[01]{8}", msg):
				result += f"Binary: {str(bytes([int(n, 2) for n in msg.split()]), encoding = 'utf8')}\n"

			if re.fullmatch(r"(\d{3} )*\d{3}", msg):
				try:
					result += f"ASCII: {str(bytes([int(n) for n in msg.split()]), encoding = 'utf8')}\n"
				except Exception:
					result += f"OCT: {str(bytes([int(n, 8) for n in msg.split()]), encoding = 'utf8')}\n"

			if re.fullmatch(r"(0x[0-9A-Fa-f]{4,} )*0x[0-9A-Fa-f]{4,}", msg):
				result += f"UNICODE: {''.join([chr(int(i, 16)) for i in msg.split()])}\n"

			if re.fullmatch(r"[^0x][0-9A-Za-z+/=]+", msg):
				result += f"BASE64: {base64.b64decode(msg.encode('utf8')).decode('utf8')}\n"

			if re.fullmatch(r"([0-9a-f]{2} )*[0-9a-f]{2}", msg):
				result += f"HEX: {str(bytes([int(n, 16) for n in msg.split()]), encoding = 'utf8')}\n"

			if re.fullmatch(r"[A-Z2-7=]+", msg):
				result += f"ASCII85: {base64.a85decode(msg.encode('utf8')).decode('utf8')}\n"

			if re.fullmatch(r"```[\!\"\#\$\%\&\'\(\)\*\+\,\-\.\/0-9\:\;\<\=\>\?\@A-Z\[\\\]\^\_\`a-u]+```", msg):
				result += f"BASE32: {base64.b64decode(msg.encode('utf8')).decode('utf8')}\n"

			else:
				result += f"ATBASH: {''.join([chr(1114111 - ord(i)) if ord(i) != 1114111 else i for i in msg])}\n"
		except Exception:
			return await ctx.send("Please enter a valid encrypted message.", delete_after = 5)

		if len(result) > 2000:
			if len(result) > 10000:
				await ctx.send("Result too large.")
			else:
				while len(result) > 2000:
					await ctx.send(result[:2000])
					result = result[2000:]

				await ctx.send(result)
		else:
			await ctx.send(result)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def element(self, ctx, arg):
		"""
		`{0}element` __`Elements of the periodic table`__

		**Usage:** {0}element <name | symbol | atomic number>

		**Examples:**
		`{0}element hydrogen` info for hydrogen
		`{0}element Se` info for selenium
		`{0}element 32` info for germanium
		"""

		try:
			number = int(arg)
		except ValueError:
			number = None

		if number:
			if number < 1 or number > 118:
				return await ctx.send(f"The element with atomic number {number} does not exist.", delete_after = 5)
			else:
				element_info = element_list[number - 1]
		else:
			element = arg.lower().capitalize()
			symbol_list = [i[2] for i in element_list]
			name_list = [i[0] for i in element_list]

			if element in symbol_list:
				element_info = element_list[symbol_list.index(element)]
			elif element in name_list:
				element_info = element_list[name_list.index(element)]
			elif element == "Random":
				element_info = random.choice(element_list)
			else:
				return await ctx.send("Please input a valid element name/number/symbol.", delete_after = 5)

		embed = discord.Embed(title = element_info[0], colour = random.randint(0, 0xFFFFFF))
		embed.add_field(name = "Atomic Number", value = element_info[1], inline = True)
		embed.add_field(name = "Symbol", value = element_info[2], inline = True)
		embed.add_field(name = "Series", value = element_info[3], inline = True)
		embed.add_field(name = "Group", value = element_info[4], inline = True)
		embed.add_field(name = "Period", value = element_info[5], inline = True)
		embed.add_field(name = "Atomic Weight", value = f"{element_info[6]} u", inline = True)
		embed.add_field(name = "Density", value = f"{element_info[7]} g/cm³", inline = True)
		embed.add_field(name = "Phase (25 °C)", value = element_info[8], inline = True)
		embed.add_field(name = "Melting Point", value = f"{element_info[9]} K", inline = True)
		embed.add_field(name = "Boiling Point", value = f"{element_info[10]} K" if "sub" != element_info[10] else element_info[10], inline = True)
		embed.add_field(name = "Atomic Radius", value = f"{element_info[11]} pm", inline = True)
		embed.add_field(name = "Stable Isotopes", value = element_info[12], inline = True)
		embed.add_field(name = "Half Life", value = element_info[13], inline = True)
		embed.add_field(name = "Electron Configuration", value = element_info[14], inline = True)
		embed.add_field(name = "Main Oxidation States", value = element_info[15], inline = True)
		embed.add_field(name = "Electronegativity", value = element_info[16], inline = True)
		embed.add_field(name = "Crystal Structure", value = element_info[17], inline = True)
		embed.add_field(name = "Discovery Year", value = element_info[18], inline = True)
		embed.set_thumbnail(url = f"attachment://{element_info[0]}.JPG")
		await ctx.send(embed = embed, file = discord.File(f"D:\My file of stuff\JPG\{element_info[0]}.JPG", f"{element_info[0]}.JPG"))

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def encrypt(self, ctx):
		"""
		`{0}encrypt` __`Encrypts message`__

		**Usage:** {0}encrypt <method> [optional arg] <text>

		**Examples:**
		`{0}encrypt ASCII ABC` 065 066 067
		`{0}encrypt binary ABC` 01000001 01000010 01000011

		**Current methods**: BINARY, ASCII, UNICODE, NUMERAL (requires base), VIGENERE (requires key), ATBASH, BASE64, HEXADECIMAL, OCTAL, BASE32, ASCII85
		"""

		args = ctx.message.content[len(self.bot.command_prefix) + 8:].split()

		if not args:
			await ctx.send("Please enter an encyption method and a text to encrypt.", delete_after = 5)
		elif len(args) == 1:
			await ctx.send("Please enter an encyption method and a text to encrypt.", delete_after = 5)
		else:
			encrypt_list = ["BINARY", "ASCII", "UNICODE", "NUMERAL", "VIGENERE", "ATBASH", "BASE64", "HEXADECIMAL", "OCTAL", "BASE32", "ASCII85"]

			if (args[0]).upper() in encrypt_list:
				method = (args[0]).upper()
			elif (args[0]).upper() == "BIN":
				method = "BINARY"
			elif (args[0]).upper() == "OCT":
				method = "OCTAL"
			elif (args[0]).upper() == "HEX":
				method = "HEXADECIMAL"
			else:
				return await ctx.send("Please enter a valid encryption method.", delete_after = 5)

			result = ""

			if method == "BINARY":
				text = " ".join(args[1:])
				result = " ".join("{:08b}".format(b) for b in text.encode("utf8"))
			elif method == "ASCII":
				text = " ".join(args[1:])
				result = " ".join("{:03}".format(b) for b in text.encode("utf8"))
			elif method == "UNICODE":
				text = " ".join(args[1:])
				result = ""

				for c in text:
					result += f"{hex(ord(c))} " if len(str(hex(ord(c)))) > 5 else f"{'0x' + hex(ord(c))[2:].zfill(4)} "
			elif method == "NUMERAL":
				try:
					base = int(args[1])
				except Exception:
					return await ctx.send("Please enter a positive integer base greater than 1.", delete_after = 5)

				text = " ".join(args[2:])
				result = []

				for b in text.encode("utf8"):
					result.append(baseconvert.base(int("{:08b}".format(b)), 2, base, string = True))

				result = " ".join(result)
			elif method == "VIGENERE":
				key = args[1]
				text = " ".join(args[2:])
				key_length = len(key)
				key_as_int = [ord(i) for i in key]
				plaintext_int = [ord(i) for i in text]

				for i in range(len(plaintext_int)):
					value = (plaintext_int[i] + key_as_int[i % key_length]) % 1114111
					result += chr(value + 65)
			elif method == "ATBASH":
				text = " ".join(args[1:])

				for i in text:
					if ord(i) != 1114111:
						result += chr(1114111 - ord(i))
					else:
						result += i
			elif method == "BASE64":
				text = " ".join(args[1:])
				result = base64.b64encode(text.encode("utf8")).decode("utf8")
			elif method == "HEXADECIMAL":
				text = " ".join(args[1:])
				result = " ".join("{:02x}".format(b) for b in text.encode("utf8"))
			elif method == "OCTAL":
				text = " ".join(args[1:])
				result = " ".join("{:08b}".format(b) for b in text.encode("utf8"))
				result = result.split()
				for i in range(len(result)):
					result[i] = oct(int(result[i], 2))[2:].zfill(3)
				result = " ".join(result)
			elif method == "BASE32":
				text = " ".join(args[1:])
				result = base64.b32encode(text.encode("utf8")).decode("utf8")
			elif method == "ASCII85":
				text = " ".join(args[1:])
				result = f"```{base64.a85encode(text.encode('utf8')).decode('utf8')}```"

			if len(result) > 2000:
				if len(result) > 10000:
					await ctx.send("Result too large.")
				else:
					while len(result) > 2000:
						await ctx.send(result[:2000])
						result = result[2000:]

					await ctx.send(result)
			else:
				await ctx.send(result)

	@commands.command(name = "id")
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def id_(self, ctx, *args):
		"""
		`{0}id` __`Returns id`__

		**Usage:** {0}id [user/channel/server]

		**Examples:**
		`{0}id` returns your own id
		`{0}id @somebub#1234` returns somebub's id
		`{0}id channel` returns channel's id
		`{0}id server` returns server's id
		"""

		await ctx.message.delete()

		if not args:
			await ctx.send(f"Your ID is {ctx.author.id}", delete_after = 5)
		elif len(args) == 1:
			if args[0] == "channel":
				return await ctx.send(f"This channel's id is {ctx.channel.id}.", delete_after = 5)
			elif args[0] == "server":
				return await ctx.send(f"This server's id is {ctx.guild.id}.", delete_after = 5)
			elif len(ctx.message.mentions) == 1:
				return await ctx.send(f"{ctx.message.mentions[0].display_name}'s ID is {ctx.message.mentions[0].id}.", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def iss(self, ctx, *args):
		"""
		`{0}iss` __`ISS Locator`__

		**Usage:** {0}iss <now | check <location>>

		**Examples:**
		`{0}iss now` shows current location of ISS
		`{0}iss check Vancouver` shows the next 5 pass times of the ISS over Vancouver
		"""

		geolocator = GeoNames(username = "person314159")

		if len(args) == 1 and args[0] == "now":
			data = requests.get("http://api.open-notify.org/iss-now.json").json()
			lat = data["iss_position"]["latitude"]
			lon = data["iss_position"]["longitude"]

			ax = plt.axes(projection = ccrs.Orthographic(central_longitude = lon, central_latitude = lat))
			ax.outline_patch.set_visible(False)
			ax.background_patch.set_visible(False)
			ax.stock_img()

			plt.plot(lon, lat, "r+", markersize = 12)
			plt.savefig("iss_location.png", bbox_inches = "tight", pad_inches = 0, transparent = True)

			location = geolocator.reverse((lat, lon), exactly_one = True)

			if location:
				location = location.address

			embed = discord.Embed(title = "ISS Locator", description = f"The ISS is currently at {lat}, {lon}, near {location}.", colour = random.randint(0, 0xFFFFFF))
			embed.set_image(url = "attachment://iss_location.png")
			await ctx.send(embed = embed, file = discord.File("iss_location.png", "iss_location.png"))
			os.remove("iss_location.png")
		elif len(args) > 1 and args[0] == "check":
			location = geolocator.geocode(" ".join(args[1:]))

			if location:
				tz = geolocator.reverse_timezone(location.point).pytz_timezone
				flyovers = requests.get(f"http://api.open-notify.org/iss-pass.json?lat={location.latitude}&lon={location.longitude}").json()["response"]

				out = f"Flyover times for {location.address}:\n"

				out += "\n".join(f"{datetime.datetime.fromtimestamp(i['risetime'], tz = tz).strftime('%b %d, %Y @ %H:%M:%S')} - {datetime.datetime.fromtimestamp(i['risetime'] + i['duration'], tz = tz).strftime('%b %d, %Y @ %H:%M:%S')}" for i in flyovers)

				await ctx.send(out)
			else:
				await ctx.send("Location not found.", delete_after = 5)
		else:
			await ctx.send("Please enter a valid location to check.", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def latex(self, ctx):
		"""
		`{0}latex` __`LaTeX equation render`__

		**Usage:** {0}latex <equation>

		**Examples:**
		`{0}latex \\frac{a}{b}` [img]
		"""

		formula = ctx.message.content[len(self.bot.command_prefix) + 6:]
		formula = formula.replace("%", "%25").replace("&", "%26")
		body = "formula=" + formula + "&fsize=30px&fcolor=FFFFFF&mode=0&out=1&remhost=quicklatex.com&preamble=\\usepackage{amsmath}\\usepackage{amsfonts}\\usepackage{amssymb}&rnd=" + str(random.random() * 100)

		try:
			img = requests.post("https://www.quicklatex.com/latex3.f", data = body.encode("utf-8"), timeout = 10)
		except Exception:
			return await ctx.send("Render timed out.", delete_after = 5)

		if img.status_code == 200:
			if img.text.startswith("0"):
				await ctx.send(file = discord.File(BytesIO(requests.get(img.text.split()[1]).content), "latex.png"))
			else:
				await ctx.send(" ".join(img.text.split()[5:]), delete_after = 5)
		else:
			await ctx.send("Something done goofed. Maybe check your syntax?", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def members(self, ctx):
		"""
		`{0}members` __`Returns list of members in server`__

		**Usage:** {0}members

		**Examples:**
		`{0}members` [list]
		"""

		member_list = []

		for member in ctx.guild.members:
			member_list.append(member.name)

		member_list.sort()
		msg = ", ".join(member_list)
		await ctx.send(msg)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def morse(self, ctx):
		"""
		`{0}morse` __`Morse code translator`__

		**Usage:** {0}morse <text or code>

		**Examples:**
		`{0}morse this is good` - .... .. ... / .. ... / --. --- --- -..
		`{0}morse - .... .. ... / .. ... / --. --- --- -..` this is good
		"""

		morse_dict = {"A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--..", "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-", "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.", "Ä": ".-.-", "À": ".--.-", "Ç": "-.-..", "Ð": "..--.", "É": "..-..", "È": ".-..-", "Ĝ": "--.-.", "Ĵ": ".---.", "Ñ": "--.--", "Ö": "---.", "Ś": "...-...", "Ŝ": "...-.", "Š": "----", "Þ": ".--..", "Ü": "..--", "Ż": "--..-", ".": ".-.-.-", ",": "--..--", "?": "..--..", "'": ".----.", "!": "-.-.--", "/": "-..-.", "(": "-.--.", ")": "-.--.-", "&": ".-...", ":": "---...", ";": "-.-.-.", "=": "-...-", "+": ".-.-.", "-": "-....-", "_": "..--.-", "\"": ".-..-.", "$": "...-..-", "@": ".--.-.", " ": "/"}
		text = ctx.message.content[len(self.bot.command_prefix) + 6:]
		translation = ""

		if re.fullmatch(r"[\.\- \/]*", text, flags=re.IGNORECASE):
			code_list = text.split()

			for i in code_list:
				if i in morse_dict.values():
					translation += list(morse_dict.keys())[list(morse_dict.values()).index(i)]
				else:
					translation += "#"
		else:
			for i in text:
				if i.upper() in morse_dict:
					translation += f"{morse_dict[i.upper()]} "
				else:
					translation += f"{i} "

		if len(translation) > 2000:
			while len(translation) > 2000:
				await ctx.send(translation[:1999])
				translation = translation[1999:]
			await ctx.send(translation)
		else:
			await ctx.send(translation)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def oeis(self, ctx, *args):
		"""
		`{0}oeis` __`Online Encyclopedia of Integer Sequences`__

		**Usage:** {0}oeis <sequence or id>

		**Examples:**
		`{0}oeis A000045` Fibonacci numbers
		`{0}oeis 1 1 2 3 5` also Fibonacci numbers
		"""

		if not args:
			return await ctx.send("Please input a sequence or ID.", delete_after = 5)
		elif len(args) == 1 and args[0].upper().startswith("A"):
			result = requests.get(f"https://oeis.org/search?q=id:{args[0]}&fmt=json").json()
		else:
			result = requests.get(f"https://oeis.org/search?q={','.join(args)}&fmt=json").json()

		if not result["results"]:
			if not result["count"]:
				return await ctx.send("No sequences were found.", delete_after = 5)
			else:
				return await ctx.send(f"There are {result['count']} relevant sequences. Please be more specific.", delete_after = 5)
		
		seq = result["results"][0]

		embed = discord.Embed(title = f"A{seq['number']:06}", description = seq["name"], url = f"https://oeis.org/A{seq['number']:06}", colour = random.randint(0, 0xFFFFFF))
		embed.add_field(name = "Sequence", value = seq["data"].replace(",", ", "))

		await ctx.send(embed = embed)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def permissions(self, ctx, *args):
		"""
		`{0}permissions` __`Permissions checker`__

		**Usage:** {0}permissions [user | role] [missing]

		**Examples:**
		`{0}permissions` checks your permissions
		`{0}permissions @abc#1234` checks permissions of abc#1234
		`{0}poll @moderator` checks permissions of the `moderator` role
		"""

		missing = False

		if args:
			if "missing" in args:
				missing = True

			if len(ctx.message.mentions) == 1:
				msg = f"**{ctx.message.mentions[0].display_name}** {'is missing' if missing else 'has'} the following perms:\n"
				user_perms = ctx.channel.permissions_for(ctx.message.mentions[0])

				for i in iter(user_perms):
					if i[1] != missing:
						msg += f"{i[0].upper()}\n"

				await ctx.send(msg)
			elif len(ctx.message.role_mentions) == 1:
				msg = f"**{ctx.message.role_mentions[0].display_name}** {'is missing' if missing else 'has'} the following perms:\n"
				role_perms = ctx.message.role_mentions[0].permissions

				for i in iter(role_perms):
					if i[1] != missing:
						msg += f"{i[0].upper()}\n"

				await ctx.send(msg)
			else:
				msg = "You are missing the following perms:\n"
				user_perms = ctx.channel.permissions_for(ctx.author)

				for i in iter(user_perms):
					if i[1] != missing:
						msg += f"{i[0].upper()}\n"

				await ctx.send(msg)
		else:
			msg = "You have the following perms:\n"
			user_perms = ctx.channel.permissions_for(ctx.author)

			for i in iter(user_perms):
				if i[1] != missing:
					msg += f"{i[0].upper()}\n"

			await ctx.send(msg)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def ping(self, ctx):
		"""
		`{0}ping` __`Bot latency`__

		**Usage:** {0}ping

		**Examples:**
		`{0}ping` ℹ️ **|** Pong! - Time taken: **69ms**
		"""

		await ctx.send(f"ℹ️ **|** Pong! - Time taken: **{round(self.bot.latency * 1000)}ms**")

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def poll(self, ctx):
		"""
		`{0}poll` __`Poll generator`__

		**Usage:** {0}poll <question | check | end> | <option> | <option> | [option] | [...]

		**Examples:**
		`{0}poll poll | yee | nah` generates poll titled "poll" with options "yee" and "nah"
		`{0}poll check` returns content of last poll
		`{0}poll end` ends current poll in channel and returns results
		"""

		poll_list = ctx.message.content[len(self.bot.command_prefix) + 5:].split(" | ")
		question = poll_list[0]
		options = poll_list[1:]

		id_ = self.bot.poll_dict[str(ctx.channel.id)]

		if question == "check":
			if not id_:
				return await ctx.send("No active poll found.", delete_after = 5)

			try:
				poll_message = await ctx.channel.fetch_message(id_)
			except discord.NotFound:
				return await ctx.send("Looks like someone deleted the poll. O O F", delete_after = 5)

			embed = poll_message.embeds[0]
			unformatted_options = [x.strip().split(": ") for x in embed.description.split("\n")]
			options_dict = OrderedDict()

			for x in unformatted_options:
				options_dict[x[0]] = x[1]

			tally = {x: 0 for x in options_dict.keys()}

			for reaction in poll_message.reactions:
				if reaction.emoji in options_dict.keys():
					async for reactor in reaction.users():
						if reactor.id != self.bot.user.id:
							tally[reaction.emoji] += 1

			output = f"Current results of the poll **\"{embed.title}\"**\nLink: {poll_message.jump_url}\n```"

			for key in tally.keys():
				if tally[key]:
					output += f"{options_dict[key]}: {'▓' * tally[key] if tally[key] == max(tally.values()) else '░' * tally[key]} ({tally[key]} votes, {round(tally[key] / sum(tally.values()) * 100, 2)}%)\n\n"

			output += "```"

			return await ctx.send(output)
		elif question == "end":
			self.bot.poll_dict[str(ctx.channel.id)] = ""
			self.bot.writeJSON(self.bot.poll_dict, "data/poll.json")

			try:
				poll_message = await ctx.channel.fetch_message(id_)
			except discord.NotFound:
				return await ctx.send("Looks like someone deleted the poll. O O F", delete_after = 5)

			embed = poll_message.embeds[0]
			unformatted_options = [x.strip().split(": ") for x in embed.description.split("\n")]
			options_dict = OrderedDict()

			for x in unformatted_options:
				options_dict[x[0]] = x[1]

			tally = {x: 0 for x in options_dict.keys()}

			for reaction in poll_message.reactions:
				if reaction.emoji in options_dict.keys():
					async for reactor in reaction.users():
						if reactor.id != self.bot.user.id:
							tally[reaction.emoji] += 1

			output = f"Final results of the poll **\"{embed.title}\"**\nLink: {poll_message.jump_url}\n```"

			for key in tally.keys():
				if tally[key]:
					output += f"{options_dict[key]}: {'▓' * tally[key] if tally[key] == max(tally.values()) else '░' * tally[key]} ({tally[key]} votes, {round(tally[key] / sum(tally.values()) * 100, 2)}%)\n\n"
				else:
					output += f"{options_dict[key]}: 0\n\n"

			output += "```"
	
			return await ctx.send(output)

		if id_:
			return await ctx.send("There's an active poll in this channel already.")

		if len(options) <= 1:
			return await ctx.send("Please enter more than one option to poll.", delete_after = 5)
		elif len(options) > 20:
			return await ctx.send("Please limit to 10 options.", delete_after = 5)
		elif len(options) == 2 and options[0] == "yes" and options[1] == "no":
			reactions = ["✅", "❌"]
		else:
			reactions = [chr(127462 + i) for i in range(26)]

		description = []

		for x, option in enumerate(options):
			description += f"\n {reactions[x]}: {option}"

		embed = discord.Embed(title = question, description = "".join(description))
		react_message = await ctx.send(embed = embed)

		for reaction in reactions[:len(options)]:
			await react_message.add_reaction(reaction)

		self.bot.poll_dict[str(ctx.channel.id)] = react_message.id
		self.bot.writeJSON(self.bot.poll_dict, "data/poll.json")

	@commands.command(name = "random")
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def _random(self, ctx, *args):
		"""
		`{0}random` __`Random thing generator`__

		**Usage:** {0}random <object> <args>

		**Examples:**
		`{0}random card` Ace of spades
		`{0}random integer 1 7` 4
		`{0}random real 1.51 3.14159` 2.6172352347
		`{0}random coins 2 0.5` Heads Tails
		`{0}random dice 3 8` 1 7 3
		**Functions:**
		`{0}random card`
		`{0}random integer <bound1> <bound2>`
		`{0}random real <bound1> <bound2>`
		`{0}random coins <number> <weight of H>`
		`{0}random dice <faces> <# of dice>`
		"""

		if not args:
			return await ctx.send("You didn't input anything.", delete_after = 5)

		if args[0] == "card":
			if len(args) > 1:
				return await ctx.send("You inputted too many args.", delete_after = 5)

			rng = random.uniform(0, 1)
			rank_list = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King"]
			suit_list = ["Spades", "Hearts", "Clubs", "Diamonds"]
			joker_list = ["Big joker", "Small joker"]

			if rng >= (26 / 27):
				await ctx.send(random.choice(joker_list))
			else:
				await ctx.send(f"{random.choice(rank_list)} of {random.choice(suit_list)}")
		elif args[0] == "integer":
			if len(args) != 3:
				return await ctx.send("Please input a range of integers.", delete_after = 5)

			try:
				bound1 = int(args[1])
				bound2 = int(args[2])
			except ValueError:
				return await ctx.send("Please enter integers for the range.", delete_after = 5)

			if bound1 <= bound2:
				await ctx.send(str(random.randint(bound1, bound2)))

			if bound1 > bound2:
				await ctx.send(str(random.randint(bound2, bound1)))
		elif args[0] == "real":
			if len(args) != 3:
				return await ctx.send("Please input a range of reals.", delete_after = 5)

			try:
				await ctx.send(str(random.uniform(float(args[1]), float(args[2]))))
			except ValueError:
				await ctx.send("Please enter real numbers for the range.", delete_after = 5)
		elif args[0] == "coins":
			if len(args) > 3:
				return await ctx.send("Please give a number of coins to flip and the weight.", delete_after = 5)

			try:
				if len(args) == 1:
					num_coins = 1
					weight = 0.5
				elif len(args) == 2:
					weight = 0.5
					num_coins = int(args[1])
				else:
					num_coins = int(args[1])
					weight = Fraction(args[2])
			except ValueError:
				return await ctx.send("Please enter a positive integer number of coins or a decimal value of probability of heads between 0 and 1.", delete_after = 5)

			msg = ""

			if num_coins < 1:
				return await ctx.send("Please enter a positive integer number of coins.", delete_after = 5)
			elif num_coins > 900:
				return await ctx.send("Please enter a smaller number of coins to flip.", delete_after = 5)

			if weight > 1 or weight < 0:
				return await ctx.send("Please enter a valid weight.", delete_after = 5)
			else:
				heads = 0
				tails = 0

				for i in range(num_coins):
					if random.random() < weight:
						msg += "H "
						heads += 1
					else:
						msg += "T "
						tails += 1

				await ctx.send(f"{msg}\nHeads: {heads}\nTails: {tails}")
		elif args[0] == "dice":
			if len(args) != 3 and len(args) != 2:
				return await ctx.send("Please give a number of dice to roll and the number of sides per die.", delete_after = 5)

			try:
				if len(args) == 2:
					num_dice = 1
				else:
					num_dice = int(args[2])

				num_side = int(args[1])
			except ValueError:
				await ctx.send("Please enter a positive integer number of dice or sides.", delete_after = 5)

			if num_dice < 1 or num_dice > 1000000:
				return await ctx.send("Please enter between 1 and 1000000 of dice.", delete_after = 5)

			if num_side > 10000000000000000000000000:
				return await ctx.send("Please enter a smaller number of sides per die.", delete_after = 5)

			if num_dice > 1000000 and num_side > 1000000:
				return await ctx.send("Please enter a different number of sides and number of dice.", delete_after = 5)

			roll_list = list(random.randint(1, num_side) for _ in range(num_dice))
			Sum = sum(roll_list)

			msg = " ".join(str(i) for i in roll_list)

			msg += f"\nsum: {Sum}"

			if len(msg) > 10000:
				await ctx.send(f"sum: {Sum}")
			else:
				await ctx.send(msg)
		else:
			await ctx.send("Please enter a valid argument.", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def reverse(self, ctx, *args):
		"""
		`{0}reverse` __`Reverses GIF`__

		**Usage:** {0}reverse <link>

		**Examples:**
		`{0}reverse https://tenor.com/view/rick-astley-dancing-singin-rick-rolled-never-gonna-give-you-up-gif-7220603` [reversed gif]
		"""

		if not args:
			gifs = ctx.attachments
		else:
			url = ctx.message.content[len(self.bot.command_prefix) + 8:]

			m = mimetypes.guess_type(url)

			if m == (None, None):
				url += ".gif"

			try:
				response = requests.get(url)

				im = Image.open(BytesIO(response.content))

				frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
				frames.reverse()
				temp = BytesIO()
				frames[0].save(temp, format = "GIF", save_all = True, append_images = frames, loop = 0)
				temp.seek(0)
				await ctx.send(file = discord.File(temp, "reversed.gif"))
			except Exception:
				return await ctx.send("invalid gif.", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def salary(self, ctx):
		"""
		`{0}salary` __`returns salary of a UBC staff member`__

		**Usage:** {0}salary <name> (if searching for full name, last name first)

		**Examples:**
		`{0}salary gateman` gateman earns $163k a year das nou
		`{0}salary dragos` dragos has a salary of $158k
		"""

		name = ctx.message.content[len(self.bot.command_prefix) + 7:]

		if len(name) < 3:
			return await ctx.send("Your search string is too short.", delete_after = 5)

		msg = "Please choose a staff member from the list below.\n"
		potential_list = list(filter(lambda i: re.search(name, i, flags = re.IGNORECASE), staff_salary_dict.keys()))

		if not potential_list:
			return await ctx.send("Your search returned no staff members. Please enter a different name.", delete_after = 5)

		if len(potential_list) > 15:
			return await ctx.send("Your search returned too many staff members. Please enter a more specific string.", delete_after = 5)

		if len(potential_list) == 1:
			staff = potential_list[0]
			await ctx.send(f"{staff} has a salary of ${staff_salary_dict[staff]}.")
		else:
			for j in range(len(potential_list)):
				msg += f"{j + 1}. {potential_list[j]}\n"

			select = await ctx.send(msg)

			async def recurse():
				def check(m):
					return m.author == ctx.author and m.channel == ctx.channel

				try:
					selection = await self.bot.wait_for("message", timeout = 5, check = check)
				except asyncio.TimeoutError:
					return await ctx.send("timed out.", delete_after = 5)

				await selection.delete()

				if selection.content == "cancel":
					return await ctx.send("search cancelled.", delete_after = 5)

				try:
					number = int(selection.content)

					if number < 1 or number > len(potential_list):
						raise ValueError
				except ValueError:
					await ctx.send(f"Please enter an integer between 1 and {len(potential_list)}.", delete_after = 1)
					await recurse()

				await select.delete()
				staff = potential_list[number - 1]
				await ctx.send(f"{staff} has a salary of ${staff_salary_dict[staff]}.")

			await recurse()

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def subs(self, ctx):
		"""
		`{0}subs` __`YouTube Subscribers`__

		**Usage:** {0}subs <channel>\ <text>

		**Examples:**
		`{0}subs pewdiepie` 97 million
		"""

		arg = ctx.message.content[len(self.bot.command_prefix) + 5:]
		data = requests.get(f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={arg}&type=channel&fields=items/snippet&key=AIzaSyAkedClIJENM-lKk5Hwziprb_E9G5bKopc").json()

		if data["items"] != []:
			channel_id = data["items"][0]["snippet"]["channelId"]
			channel_name = data["items"][0]["snippet"]["title"]
			channel_desc = data["items"][0]["snippet"]["description"]
			thumbnail = data["items"][0]["snippet"]["thumbnails"]["high"]["url"]
			subs = requests.get(f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&fields=items/statistics/subscriberCount&key=AIzaSyDUUfmvtaHY3lQ11CbkF8gplSJSXwgLe2g").json()["items"][0]["statistics"]["subscriberCount"]
			embed = discord.Embed(title = channel_name, description = channel_desc, colour = random.randint(0, 0xFFFFFF))
			embed.add_field(name = "Subscribers", value = subs, inline = False)
			embed.set_thumbnail(url = thumbnail)
			await ctx.send(embed = embed)
		else:
			embed = discord.Embed(title = arg, description = "User not found", colour = random.randint(0, 0xFFFFFF))
			await ctx.send(embed = embed)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def text(self, ctx, *args):
		"""
		`{0}text` __`Text formatting command`__

		**Usage:** {0}text "<args>" <text>

		**Examples:**
		`{0}text "bold italics" test message` ***test message***
		**Args:** `uppercase` `randomcase` `lowercase` `invert` `spacify` `codeline` `codeblock` `italics` `bold` `underline` `strikethrough`
		"""

		await ctx.message.delete()

		if not args:
			await ctx.send("You didn't input anything.", delete_after = 5)
		elif len(args) == 1:
			await ctx.send("you didn't give a string to format.", delete_after = 5)
		else:
			arg_list = args[0].split()
			msg = " ".join(args[1:])

			if (("uppercase" not in arg_list) and ("randomcase" not in arg_list) and ("lowercase" not in arg_list) and ("reverse" not in arg_list) and ("invert" not in arg_list) and ("spacify" not in arg_list) and ("codeline" not in arg_list) and ("codeblock" not in arg_list) and ("italics" not in arg_list) and ("bold" not in arg_list) and ("underline" not in arg_list) and ("strikethrough" not in arg_list)):
				await ctx.send(ctx.message.content[6:])
			else:
				if "uppercase" in arg_list:
					msg = msg.upper()

				if "randomcase" in arg_list:
					msg = list(msg)

					for x in range(len(msg)):
						flip = random.randint(0, 1)

						if flip == 0:
							msg[x] = (msg[x]).upper()
						else:
							msg[x] = (msg[x]).lower()

					msg = "".join(msg)

				if "lowercase" in arg_list:
					msg = msg.lower()

				if "reverse" in arg_list:
					msg = msg[::-1]

				if "invert" in arg_list:
					msg = msg[::-1]
					invert_list = []
					upside_down_dict = {"a":"ɐ", "b":"q", "c":"ɔ", "d":"p", "e":"ǝ", "f":"ɟ", "g":"ƃ", "h":"ɥ", "i":"ᴉ", "j":"ɾ", "k":"ʞ", "l":"ן", "m":"ɯ", "n":"u", "p":"d", "q":"b", "r":"ɹ", "t":"ʇ", "u":"n", "v":"ʌ", "w":"ʍ", "y":"ʎ", "A":"∀", "B":"𐐒", "C":"Ɔ", "D":"ᗡ", "E":"Ǝ", "F":"Ⅎ", "G":"⅁", "J":"ſ", "K":"⋊", "L":"⅂", "M":"W", "N":"И", "P":"Ԁ", "Q":"Ό", "R":"ᴚ", "T":"⊥", "U":"∩", "V":"Λ", "W":"M", "Y":"⅄", "1":"Ɩ", "2":"ㄹ", "3":"Ɛ", "4":"ᔭ", "5":"ϛ", "6":"9", "7":"Ɫ", "9":"6", "`":",", "!":"¡", "^":"⌄", "&":"⅋", "*":"∗", "(":")", ")":"(", "_":"‾", "[":"]", "{":"}", "]":"[", "}":"{", "\\":"\\\\", ";":"؛", "\'":",", "\"":"„", ",":"\'", "<":">", ".":"˙", ">":"<", "?":"¿", "ɐ":"a", "ɔ":"c", "ǝ":"e", "ɟ":"f", "ƃ":"g", "ɥ":"h", "ᴉ":"i", "ɾ":"j", "ʞ":"k", "ן":"l", "ɯ":"m", "ɹ":"r", "ʇ":"t", "ʌ":"v", "ʍ":"w", "ʎ":"y", "∀":"A", "𐐒":"B", "Ɔ":"C", "ᗡ":"D", "Ǝ":"E", "Ⅎ":"F", "⅁":"G", "ſ":"J", "⋊":"K", "⅂":"L", "И":"N", "Ԁ":"P", "Ό":"Q", "ᴚ":"R", "⊥":"T", "∩":"U", "Λ":"V", "⅄":"Y", "Ɩ":"1", "ㄹ":"2", "Ɛ":"3", "ᔭ":"4", "ϛ":"5", "Ɫ":"7", "¡":"!", "⌄":"^", "⅋":"&", "∗":"*", "‾":"_", "؛":";", "„":"\"", "˙":".", "¿":"?"}

					for i in msg:
						if i in upside_down_dict.keys():
							invert_list.append(upside_down_dict[i])
						else:
							invert_list.append(i)

					msg = "".join(invert_list)

				if "spacify" in arg_list:
					msg = " ".join(msg)

				if "codeline" in arg_list and "codeblock" not in arg_list:
					msg = f"`{msg}`"

				if "codeblock" in arg_list and "codeline" not in arg_list:
					msg = f"```{msg}```"

				if "italics" in arg_list:
					msg = f"*{msg}*"

				if "bold" in arg_list:
					msg = f"**{msg}**"

				if "underline" in arg_list:
					msg = f"__{msg}__"

				if "strikethrough" in arg_list:
					msg = f"~~{msg}~~"

				if len(msg) > 2000:
					while len(msg) > 2000:
						await ctx.send(msg[:1999])
						msg = msg[1999:]
					await ctx.send(msg)
				else:
					await ctx.send(msg)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def translate(self, ctx):
		"""
		`{0}translate` __`Google Translate`__

		**Usage:** {0}translate [source lang] | [destination lang] | <message> 

		**Examples:**
		`{0}translate french | non toi` no you
		`{0}translate french | english | non toi` no you
		`{0}translate non toi` no you
		For list of languages do `{0}translate langs`.
		"""

		if ctx.message.content[len(self.bot.command_prefix) + 10:] == "langs":
			msg = "```" + "\n".join(i + " " * (8 - len(i)) + constants.LANGUAGES[i] for i in constants.LANGUAGES) + "```"

			await ctx.send(msg)
		else:
			args = ctx.message.content[len(self.bot.command_prefix) + 10:].split(" | ")
			translator = Translator()

			if len(args) < 1 or len(args) > 3:
				return await ctx.send("Please input the correct number of arguments,", delete_after = 5)

			if len(args) == 1:
				source = "auto"
				destination = "en"
				message = args[0]
			elif len(args) == 2:
				source = args[0]
				destination = "en"
				message = args[1]
			else:
				source = args[0]
				destination = args[1]
				message = args[2]

			if not message:
				return await ctx.send("Please input a valid text to be translated.", delete_after = 5)

			translation = translator.translate(message, src = source, dest = destination)
			text = translation.text
			src = constants.LANGUAGES[translation.src.lower()]
			dest = constants.LANGUAGES[translation.dest.lower()]

			embed = discord.Embed(title = f"{src} to {dest}", colour = random.randint(0, 0xFFFFFF))
			embed.add_field(name = "Translation", value = text)
			await ctx.send(embed = embed)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def urban(self, ctx, *args):
		"""
		`{0}urban` __`UrbanDict search`__

		**Usage:** {0}urban <query> [top]

		**Examples:**
		`{0}urban no u` no u
		"""

		top = False
		definition = None

		if not args:
			return await ctx.send("Please enter a term to search.", delete_after = 5)
		elif len(args) >= 2 and args[-1] == "top":
			word = " ".join(args[:-1])
			top = True
		else:
			word = " ".join(args)

		response = requests.get("http://api.urbandictionary.com/v0/define", params = [("term", word)]).json()
		embed = discord.Embed(title = "", description = "", colour = random.randint(0, 0xFFFFFF))

		if not response["list"]:
			embed.title = "¯\_(ツ)_/¯"
			embed.description = f"Sorry, we couldn't find that term."
			return await ctx.send(embed = embed)

		if not top:
			definition = random.randrange(len(response["list"]))

		embed.title = f"**{response['list'][definition]['word']}** by **{response['list'][definition]['author']}**"
		embed.url = response["list"][definition]["permalink"]
		embed.description = response["list"][definition]["definition"]
		embed.add_field(name = "Example(s):", value = response["list"][definition]["example"], inline = False)
		embed.add_field(name = "Thumbs", value = f"👍 {response['list'][definition]['thumbs_up']} | 👎 {response['list'][definition]['thumbs_down']}", inline = False)
		await ctx.send(embed = embed)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def userinfo(self, ctx, *arg):
		"""
		`{0}userinfo` __`Discord user information`__

		**Usage:** {0}userinfo [user mention or id]

		**Examples:**
		`{0}userinfo` [info about yourself]
		`{0}userinfo 123456789012345678` [info about that user]
		`{0}userinfo @abc#1234` [info about abc#1234]
		"""

		if not arg:
			user = ctx.author
		else:
			if len(ctx.message.mentions) == 1:
				user = ctx.message.mentions[0]
			elif re.fullmatch(r"\d{18}", arg[0]):
				user = ctx.guild.get_member(int(arg[0]))

				if not user:
					return await ctx.send("That user is not in this server.", delete_after = 5)
			else:
				return await ctx.send("You inputted an invalid user.", delete_after = 5)

		playing = None
		t = ""
		activity_type = "Playing"
		custom_status = None

		if user.activity:
			activity = user.activity

			if isinstance(activity, discord.CustomActivity):
				custom_status = activity

				if len(user.activities) > 1:
					activity = user.activities[1]
				else:
					activity = None

			if activity:
				activity_type = str(activity.type).split(".")[1].capitalize() if isinstance(activity.type, discord.ActivityType) else "Playing"

				if isinstance(activity, discord.Spotify):
					playing = f"**{activity.title}** by {activity.artist}"
				elif isinstance(activity, discord.Activity):
					playing = activity.name

					if activity.timestamps:
						t = int(time.time() - activity.timestamps["start"] / 1000)

						if t > 30 * 86400:
							t = f"for {t // (30 * 86400)} {'month' if t // (30 * 86400) == 1 else 'months'}"
						elif t > 7 * 86400:
							t = f"for {t // (7 * 86400)} {'week' if t // (7 * 86400) == 1 else 'weeks'}"
						elif t > 86400:
							t = f"for {t // 86400} {'day' if t // 86400 == 1 else 'days'}"
						elif t > 3600:
							t = f"for {t // 3600} {'hour' if t // 3600 == 1 else 'hours'}"
						elif t > 60:
							t = f"for {t // 60} {'minute' if t // 60 == 1 else 'minutes'}"
						else:
							t = f"for {t} {'second' if t == 1 else 'seconds'}"
				else:
					playing = activity

		# print(user.public_flags)
		avatar = str(user.avatar_url_as(format = "png", size = 4096)) if not user.is_avatar_animated() else str(user.avatar_url_as(format = "gif", size = 4096))
		embed = discord.Embed(colour = random.randint(0, 0xFFFFFF), timestamp = datetime.datetime.utcnow())
		embed.add_field(name = "ID", value = user.id, inline = True)
		embed.add_field(name = "Nickname", value = user.display_name, inline = True)
		embed.add_field(name = "Status", value = user.status, inline = True)
		embed.add_field(name = "Custom Status", value = custom_status, inline = True)
		embed.add_field(name = activity_type, value = f"{playing} {t}", inline = True)
		embed.add_field(name = "Mention", value = user.mention, inline = True)
		embed.add_field(name = "Account Created", value = f"{user.created_at.strftime('%A, %Y %B %d @ %H:%M:%S')}", inline = True)
		embed.add_field(name = "Date Joined", value = f"{user.joined_at.strftime('%A, %Y %B %d @ %H:%M:%S')}", inline = True)
		embed.add_field(name = f"Roles [{len(user.roles)}]", value = ", ".join([str(i) for i in sorted(user.roles, key = lambda role: role.position, reverse = True)]), inline = True)
		embed.set_author(name = f"{user.name}#{user.discriminator}", icon_url = avatar)
		embed.set_thumbnail(url = avatar)
		await ctx.send(embed = embed)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def weather(self, ctx, *args):
		"""
		`{0}weather` __`Current weather`__

		**Usage:** {0}weather <city>[,country code]

		**Examples:**
		`{0}weather vancouver` vancouver, US weather
		`{0}weather vancouver,CA` vancouver, CA weather
		"""

		if not args:
			return await ctx.send("Please enter a city for weather.", delete_after = 5)

		if len(args) > 1:
			city = "+".join(args)
		else:
			city = args[0]

		data = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=ebcfef5367a51db91e4ba682e8da9c33").json()

		if data["cod"] != "404" and data["cod"] != "500":
			state_data = requests.get(f"https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?app_code=mzoz4HfdCBcVXpDJrEgUTw&app_id=6OEyWCTWosrHaebmywM9&jsonattributes=1&locationattributes=adminInfo,timeZone&mode=retrieveAreas&prox={data['coord']['lat']},{data['coord']['lon']},100").json()
			state_data2 = requests.get(f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={data['coord']['lat']}&lon={data['coord']['lon']}").json()
			city = data["name"]
			state = ""
			division_dict = {"AE": "state", "AF": "state", "AD": "county", "AL": "county", "AO": "state", "AR": "state", "AM": "city" if city == "Yerevan" else "state", "AU": "state", "AT": "state", "AZ": "state", "BA": "state", "BB": "county", "BD": "state", "BE": "state", "BF": "region", "BG": "county", "BH": "state", "BI": "state", "BJ": "state", "BN": "state", "BO": "state", "BR": "state", "BS": "state", "BT": "state", "BW": "state", "BY": "city" if city == "Minsk" else "state", "BZ": "state", "CA": "state", "CD": "state", "CF": "state", "CG": "state", "CH": "state", "CI": "state", "CM": "state", "CN": "state", "CR": "state", "CU": "state", "CV": "county", "CY": "county", "CZ": "state", "DE": "state", "DJ": "state", "DK": "state", "DM": "state", "DO": "state", "DZ": "state", "EC": "state", "EE": "county", "EG": "state", "ER": "state", "ES": "state", "ET": "region", "FI": "state", "FJ": "state", "FM": "state", "FR": "state", "GA": "state", "GB": "state", "GE": "city" if city == "Tbilisi" else "region", "GH": "state", "GM": "state", "GN": "state", "GQ": "state", "GR": "state", "GT": "state", "GW": "state", "GY": "state", "HN": "state", "HR": "county", "HT": "state", "HU": "city" if city == "Budapest" else "county", "ID": "state", "IE": "county", "IL": "state", "IN": "state", "IQ": "state", "IR": "state", "IS": "state_district", "IT": "state", "JM": "county", "JO": "state", "JP": "state", "KE": "state", "KG": "state", "KH": "state", "KI": "city" if city == "Tawara" else "", "KM": "state", "KN": "state", "KP": "state", "KR": "state", "KW": "state", "KZ": "state", "LA": "state", "LK": "state", "LR": "state", "LS": "state_district", "LT": "state", "LU": "county", "LV": "state", "LY": "state", "MA": "region", "MC": "city", "MD": "state", "ME": "county", "MG": "state", "MK": "state", "ML": "state", "MM": "state", "MN": "state", "MR": "state", "MV": "state", "MW": "state", "MX": "state", "MY": "state", "MZ": "state", "NA": "state", "NE": "region", "NG": "state", "NI": "state", "NL": "state", "NO": "county", "NP": "state_district", "NR": "county", "NZ": "state", "OM": "state", "PA": "state", "PE": "state", "PG": "state", "PH": "state", "PK": "state", "PL": "state", "PT": "state_district", "PW": "village" if city == "ngetkib" else "town" if city == "kloulklubed" else "city", "PY": "state", "QA": "state", "RO": "county", "RS": "state", "RU": "state", "RW": "state", "SA": "state", "SB": "state", "SD": "state", "SE": "state", "SG": "county", "SK": "state", "SL": "state_district", "SN": "state", "SO": "state", "SR": "state", "ST": "county", "SV": "state", "SY": "state", "SZ": "state", "TD": "state", "TG": "state", "TH": "state", "TJ": "state", "TL": "state", "TM": "state", "TN": "state", "TO": "state", "TR": "state", "TT": "state", "TZ": "state", "UA": "state", "UG": "state", "US": "state", "UY": "state", "UZ": "state", "VC": "county", "VE": "state", "VN": "state", "VU": "state", "YE": "state", "ZA": "state", "ZM": "state", "ZW": "state"}

			try:
				state = f"{state_data['response']['view'][0]['result'][0]['location']['address']['additionalData'][1]['value']}, "
				timezone = state_data["response"]["view"][0]["result"][0]["location"]["adminInfo"]["timeZoneOffset"]
				current_time = (state_data["response"]["view"][0]["result"][0]["location"]["adminInfo"]["localTime"].replace("T", " "))[:-5]
			except KeyError:
				timezone = "N/A"
				current_time = "N/A"

				try:
					state = f"{state_data2['address'][division_dict[data['sys']['country']]]}, "
				except KeyError:
					state = ""

			country = data["sys"]["country"]
			flag = f"{chr(ord(country[0]) + 127397)}{chr(ord(country[1]) + 127397)}"
			city = f"{data['name']}, {state}{country} {flag}"
			current_weather = data["weather"][0]["description"]
			icon = f"http://openweathermap.org/img/w/{data['weather'][0]['icon']}.png"
			temp = f"{data['main']['temp']} °C"
			wind = f"{round(data['wind']['speed']*3.6)} km/h"
			humidity = f"{data['main']['humidity']}%"
			cloudiness = f"{data['clouds']['all']}%"
			pressure = f"{data['main']['pressure']} hpa"
			sunrise = datetime.datetime.utcfromtimestamp(data["sys"]["sunrise"] + data["timezone"]).strftime("%H:%M:%S")
			sunset = datetime.datetime.utcfromtimestamp(data["sys"]["sunset"] + data["timezone"]).strftime("%H:%M:%S")
			embed = discord.Embed(title = city, colour = random.randint(0, 0xFFFFFF), timestamp = datetime.datetime.utcnow())
			embed.set_thumbnail(url = icon)
			embed.add_field(name = "**Weather**", value = current_weather, inline = True)
			embed.add_field(name = "**Temperature** 🌡", value = temp, inline = True)
			embed.add_field(name = "**Wind** 💨", value = wind, inline = True)
			embed.add_field(name = "**Humidity** 💦", value = humidity, inline = True)
			embed.add_field(name = "**Clouds** ☁", value = cloudiness, inline = True)
			embed.add_field(name = "**Pressure**", value = pressure, inline = True)
			embed.add_field(name = "**Sunrise** ☀", value = sunrise, inline = True)
			embed.add_field(name = "**Sunset** 🌇", value = sunset, inline = True)
			embed.add_field(name = "**Current Time** 🕛", value = current_time, inline = True)
			embed.add_field(name = "**Timezone**", value = timezone, inline = True)
			await ctx.send(embed = embed)
		else:
			await ctx.send("City not found.", delete_after = 5)

	@commands.command()
	@disabled()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def wiki(self, ctx, *args):
		"""
		`{0}wiki` __`Wikipedia Search`__

		**Usage:** {0}wiki [random | query]

		**Examples:**
		`{0}wiki random` returns random Wiki article
		`{0}wiki randomness` returns Wiki article "Randomness"
		"""

		if args:
			query = " ".join(args)

			if query == "random":
				data = BeautifulSoup(requests.get("https://en.wikipedia.org/wiki/Special:Random").content.decode("utf-8"), "html.parser")
				url = data.find("link", rel = "canonical")["href"]
				await ctx.send(url)
			else:
				result = BeautifulSoup(requests.get(f"https://en.wikipedia.org/w/index.php?sort=relevance&search={query}&title=Special%3ASearch&profile=advanced&fulltext=1&advancedSearch-current=%7B%7D&ns0=1").content.decode("utf-8"), "html.parser")

				search = result.find("li", class_ = "mw-search-result")

				if search:
					url = f"https://en.wikipedia.org{search.a['href']}"
					await ctx.send(url)
				else:
					await ctx.send("Your search returned no results.", delete_after = 5)
		else:
			await ctx.send("Please input a query.", delete_after = 5)


def setup(bot):
	bot.add_cog(Utility(bot))
