import discord
from discord.ext import commands
from datetime import datetime
import pytz
import os
import random
from dotenv import load_dotenv
import mysql.connector as mysql
from mysql.connector import errorcode
import time

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASS = os.getenv("MYSQL_PASS")

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


#SQL stuff
#SQL statement for adding to the people table
add_people = """INSERT INTO people
				(disc_id, disc_name, first_name, last_name, address, phone_num, description, gift_advisor)
				VALUES ({disc_id}, {disc_name}, {first_name}, {last_name}, {address}, {phone_num}, {description}, {gift_advisor})
				ON DUPLICATE KEY UPDATE disc_name={disc_name}, first_name={first_name}, last_name={last_name}, address={address}, phone_num={phone_num}, description={description}, gift_advisor={gift_advisor}"""

@bot.command()
async def drawsanta(ctx):
	db = mysql.connect(user = MYSQL_USER, password = MYSQL_PASS,
							host = '127.0.0.1',
							database = 'mydatabase',
							auth_plugin= 'caching_sha2_password')

	cursor = db.cursor()
	people_list = list()
	dup_list = list()
	dup_dup_list = list()
	select_sql = "SELECT disc_id FROM people;"
	update_recip_sql = "UPDATE people SET recipient = {0} WHERE disc_id = {1}"
	update_santa_sql = "UPDATE people SET santa = {0} WHERE disc_id = {1}"
	cursor.execute(select_sql)
	for res in cursor:
		for disc_id in res:
			people_list.append(disc_id)
			dup_list.append(disc_id)
			dup_dup_list.append(disc_id)

	for people in dup_dup_list:
		recip_id = ""
		if len(dup_list) == 2 and len(list(set(people_list) & set(dup_list))) > 0:
			if people != list(set(people_list) & set(dup_list))[0]:
				recip_id = list(set(people_list) & set(dup_list))[0]
			else:
				for recip in dup_list:
					if recip != people:
						recip_id = recip
		while recip_id == people or recip_id == "":
			recip_id = random.choice(dup_list)

		dup_list.remove(recip_id)
		people_list.remove(people)
		cursor.execute(update_recip_sql.format(recip_id, people))
		cursor.execute(update_santa_sql.format(people, recip_id))

	db.commit()
	cursor.close()
	db.close()
	await ctx.send("ok")

@bot.command()
async def sendinfo(ctx):
	db = mysql.connect(user = MYSQL_USER, password = MYSQL_PASS,
							host = '127.0.0.1',
							database = 'mydatabase',
							auth_plugin= 'caching_sha2_password')
	cursor = db.cursor()
	select_sql = "SELECT disc_id, recipient FROM people;"
	select_santa_sql = "SELECT * FROM people WHERE disc_id = {0}"
	cursor.execute(select_sql)
	user_recip_pair = list()
	for res in cursor:
		user_recip_pair.append(res)

	cursor = db.cursor()
	for pair in user_recip_pair:
		user_id = pair[0]
		recip_id = pair[1]
		user = await bot.fetch_user(user_id)

		cursor.execute(select_santa_sql.format(recip_id))
		for res in cursor:
			await user.send("Full Name:\n" + res[2] + " " + res[3])
			await user.send("Address:\n" + res[4])
			await user.send("Phone number:\n" + res[5])
			await user.send("Description:\n" + res[6])
			await user.send("Please consult their gift advisor if you have questions on what to get them:\n" + res[7])
	
	await ctx.send("done")
	cursor.close()
	db.close()

@bot.event
async def on_ready():
	await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type = discord.ActivityType.listening, name = "DM me with !secretsanta to join on this year\'s secret santa!"))

	create_table = """CREATE TABLE people (
		disc_id BIGINT NOT NULL,
		disc_name varchar(30) NOT NULL,
		first_name varchar(20) NOT NULL,
		last_name varchar(20) NOT NULL,
		address varchar(150) NOT NULL,
		phone_num varchar(20) NOT NULL,
		description varchar(200) NOT NULL,
		gift_advisor varchar(40) NOT NULL,
		santa BIGINT DEFAULT NULL,
		recipient BIGINT DEFAULT NULL,
		PRIMARY KEY (disc_id))"""

	#connect to DB	
	"""
	db = mysql.connect(user = MYSQL_USER, password = MYSQL_PASS,
							host = '127.0.0.1',
							database = 'mydatabase',
							auth_plugin= 'caching_sha2_password')

	cursor = db.cursor()

	try:
		print("Creating table")
		cursor.execute(create_table)
	except mysql.Error as err:
		if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
			print("table exists.")
		else:
			print(err.msg)
	else:
		print("OK")
	db.close()
	cursor.close()
	"""

@bot.command()
async def santalist(ctx):
	db = mysql.connect(user = MYSQL_USER, password = MYSQL_PASS,
							host = '127.0.0.1',
							database = 'mydatabase',
							auth_plugin= 'caching_sha2_password')

	cursor = db.cursor()

	sql = "SELECT first_name FROM people;"
	cursor.execute(sql)
	out_s = "Heres a list of people who signed up:\n"
	for i, res in enumerate(cursor, 1):
		for first_name in res:
			out_s += str(i) + ". " + first_name + "\n"
	await ctx.send(out_s)

	cursor.close()
	db.close()

@bot.command()
async def secretsanta(ctx):

	channel_type = ctx.channel.type
	if channel_type == discord.ChannelType.private:
		data_people = dict()
		data_people['disc_id'] = ctx.author.id
		"""
		data_people dict format
		data_people['disc_id'] = discord id int
		data_people['disc_name'] = discord name string
		data_people['first_name'] = first name string
		data_people['last_name'] = lats name string
		data_people['address'] = address string
		data_people['phone_num'] = phone num string
		data_people['description'] = description string
		data_people['gift_advisor'] = gift advisor string
		"""

		s = "Hi there, I will be asking you a series of questions about your personal details so your secret santa can send their gift to you! "
		s += "Feel free to call this function again if you need to change anything about your personal details.\n\n\n"
		s += "Data privacy: data will be deleted after this thing is over (I can stream that or something), but I will not be encrypting the data for privacy because I'm too lazy, "
		s += "but I will be the only one who has access to the data and you just have to take my word that I wont do anything with it. -Ed"
		await ctx.author.send(s)


		data_people["disc_name"] = "\'" + ctx.author.name + "\'"
		channel_id = ctx.channel.id
		time.sleep(3)
		def check(msg):
			return msg.channel.id == channel_id and msg.author == ctx.author
		
		await ctx.author.send("Please enter your first name:")
		msg = await bot.wait_for('message', check=check)
		data_people["first_name"] = "\'" + msg.content + "\'"
		time.sleep(1.5)
		await ctx.author.send("Please enter your last name:")
		msg = await bot.wait_for('message', check=check)
		data_people["last_name"] = "\'" + msg.content + "\'"
		time.sleep(1.5)
		await ctx.author.send("Please enter your full address:")
		msg = await bot.wait_for('message', check=check)
		data_people["address"] = "\'" + msg.content + "\'"
		time.sleep(1.5)
		await ctx.author.send("Please enter your phone number (with country code please):")
		msg = await bot.wait_for('message', check=check)
		data_people["phone_num"] = "\'" + msg.content + "\'"
		time.sleep(1.5)
		await ctx.author.send("Please write a short description of what you like so your secret santa can have an idea of what to get you:")
		msg = await bot.wait_for('message', check=check)
		data_people["description"] = "\'" + msg.content + "\'"
		time.sleep(1.5)
		await ctx.author.send("Please designate a gift advisor that your secret santa can consult with for what to get you (reply with n if you don't want to input one):")
		msg = await bot.wait_for('message', check=check)
		if msg.content.lower() == 'n':
			data_people["gift_advisor"] = "\'N/A\'"
		else:
			data_people["gift_advisor"] = "\'" + msg.content + "\'"
		time.sleep(1.5)
		
		db = mysql.connect(user = MYSQL_USER, password = MYSQL_PASS,
							host = '127.0.0.1',
							database = 'mydatabase',
							auth_plugin= 'caching_sha2_password')

		cursor = db.cursor()
		try:
			cursor.execute(add_people.format(**data_people))
			await ctx.author.send("Information received")

		except Exception as err:
			await ctx.author.send("oops something went wrong, send this to Ed:\n" + err)
			print(err)

		db.commit()
		cursor.close()
		db.close()


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
