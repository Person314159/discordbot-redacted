import discord
from discord.ext import commands

def disabled():
	def predicate(ctx):
		if ctx.channel.id in ctx.bot.command_toggle_dict.get(ctx.command.name, []):
			raise commands.DisabledCommand
		else:
			return True

	return commands.check(predicate)