import discord
from discord.ext import commands

from datetime import datetime
import pytz
import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

tz = pytz.timezone("Asia/Shanghai")
date = datetime.now(tz = tz).strftime("%b %d")

default_play_time = "21:00"
play_time = default_play_time
players = []
maybe_players = []
previous_msg = None
map_vote = False
map_vote_players = set()
map_vote_results = {"Skeld":0, "MiraHQ":0, "Polus":0}


bot = commands.Bot(command_prefix = '!')

emote_one = "1\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}"
emote_two = "2\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}"
emote_three = "3\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}"


@bot.command()
async def commands(ctx):
	out_string =""
	out_string += "-!play = starts a queue for 21:00\n"
	out_string += "-!play [time] = starts a queue for [time]\n"
	out_string += "-!imsus [name(optional)] = adds you to an existing queue with optional name (or for signing up for other people)\n"
	out_string += "-!imnotsus [name(optional)] = removes you from the queue\n"
	out_string += "-!changetime [time] = changes game time to [time]\n"
	out_string += "-!session = resends current session info\n"
	out_string += "-!reset = empties queue\n"
	out_string += "-!mapvote = start a poll for map selection, !endvote to end the vote\n"
	out_string += "-!skeld = brings up an image of the map skeld\n"
	out_string += "-!mirahq = brings up an image of the map mirahq\n"
	out_string += "-!polus = brings up an image of the map polus\n"
	await ctx.send(out_string)

@bot.command()
async def mapvote(ctx):
	global map_vote
	global map_vote_players
	global map_vote_results
	map_vote = True
	map_vote_players = set()
	map_vote_results = {"Skeld":0, "MiraHQ":0, "Polus":0}
	out_string = ""
	out_string += "Vote on the map choice for today's session by reacting to this message!\n"
	out_string += ":one: for Skeld\n"
	out_string += ":two: for MiraHQ\n"
	out_string += ":three: for Polus\n\n"
	out_string += "Reply with !endvote to end the vote"
	msg = await ctx.send(out_string)
	await msg.add_reaction(emote_one)
	await msg.add_reaction(emote_two)
	await msg.add_reaction(emote_three)
	def check(reaction, user):
		return reaction.message == msg
	while map_vote:
		reaction, user = await bot.wait_for("reaction_add", check = check)
		if user.display_name not in map_vote_players:
			map_vote_players.add(user.display_name)
			if reaction.emoji == emote_one:
				map_vote_results["Skeld"] += 1
			elif reaction.emoji == emote_two:
				map_vote_results["MiraHQ"] +=1
			elif reaction.emoji == emote_three:
				map_vote_results["Polus"] +=1

@bot.command()
async def endvote(ctx):
	global map_vote
	global map_vote_results
	if not map_vote:
		await ctx.send("No map vote has been called yet, use !mapvote to call a vote")
	else:
		map_vote = False
		res = max(map_vote_results, key=lambda k:map_vote_results[k])
		await ctx.send("The result is: " + res + "!")

@bot.command()
async def reset(ctx):
	global players
	global play_time
	players = []
	play_time = default_play_time
	await ctx.send("Yes")
	if previous_msg is not None:
		await previous_msg.edit(content = session_msg())

@bot.command()
async def play(ctx, time = default_play_time):
	global play_time
	global players
	global previous_msg
	if time == "reset":
		players = []
	if previous_msg is not None:
		await previous_msg.delete()
	play_time = time
	previous_msg = await ctx.send(session_msg())
	await previous_msg.pin()
	def check(reaction, user):
		return reaction.message == previous_msg
	while True:
		reaction, user = await bot.wait_for("reaction_add", check = check)
		if user.display_name not in players:
			players.append(user.display_name)
		await previous_msg.edit(content = session_msg())

@bot.command()
async def changetime(ctx, time = default_play_time):
	global play_time
	global previous_msg
	play_time = time
	if previous_msg is not None:
		await previous_msg.edit(content = session_msg())
	await ctx.send("Game time updated")

@bot.command()
async def imsus(ctx,*args):
	global previous_msg
	global players
	if args:
		name = ""
		for x in args:
			name += x
			name += " "
		name = name[:-1]
		register_name = name
	else:
		register_name = ctx.author.display_name
	if register_name.upper() not in (name.upper() for name in players):
		players.append(register_name)
		if previous_msg is not None:
			await previous_msg.edit(content = session_msg())
		else:
			previous_msg = await ctx.send(session_msg())
		await ctx.message.delete()
	else:
		await ctx.send("Bruh you already signed up, I think you're sus")

@bot.command()
async def imnotsus(ctx, *args):
	global previous_msg
	global players
	if args:
		name = ""
		for x in args:
			name += x
			name += " "
		name = name[:-1]
		register_name = name
	else:
		register_name = ctx.author.display_name
	if register_name.upper() in (name.upper() for name in players):
		players.remove(register_name)
		if previous_msg is not None:
			await previous_msg.edit(content = session_msg())
		else:
			previous_msg = await ctx.send(session_msg())
		await ctx.message.delete()
	else:
		await ctx.send("How can you be not sus if you were never sused in the first place :thinking:\n big sus "+ register_name + " btw")

@bot.command()
async def session(ctx):
	global previous_msg
	global players
	if previous_msg is not None:
		await previous_msg.delete()
		previous_msg = await ctx.send(session_msg())
		await previous_msg.pin()
	else:
		await ctx.send("No session has been initiated yet, type !play to initiate a session")

@bot.command()
async def skeld(ctx):
	await ctx.send(file = discord.File('Skeld.jpg'))

@bot.command()
async def mirahq(ctx):
	await ctx.send(file = discord.File('Mirahq.png'))

@bot.command()
async def polus(ctx):
	await ctx.send(file = discord.File('Polus.png'))

@bot.command()
async def emojiname(ctx, emoji):
	await ctx.send(get_name(emoji))


def session_msg():
	global players
	global play_time
	global date
	update_date()

	out_string = ""
	start_string = "Whoever is down to play later today at " + play_time + " GMT+8(HK/TW/SG Time) " + date + ", react to this message or reply with !imsus below\n\nIf you want to leave after you signed up, reply with !imnotsus to exit queue"
	out_string += start_string
	if players:
		player_string = ""
		for i, name in enumerate(players, 1):
			player_string += str(i)
			player_string += ". "
			player_string += name
			player_string += "\n"
		out_string += "\n\nCrew for today's game at " + play_time + " GMT+8:\n\n" + player_string
	return out_string

def update_date():
	global date
	date = datetime.now(tz = tz).strftime("%b %d")

def get_name(s):
	return s.encode("ascii", "namereplace")
bot.run(DISCORD_TOKEN)
