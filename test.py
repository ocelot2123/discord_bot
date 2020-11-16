import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

import mysql.connector as mysql
from mysql.connector import errorcode
import time

import random
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASS = os.getenv("MYSQL_PASS")

bot = commands.Bot(command_prefix = "!")

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
	update_recip_sql = "UPDATE people recipient = {0} WHERE disc_id = {1}"
	update_santa_sql = "UPDATE people santa = {0} WHERE disc_id = {1}"
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

	await ctx.send("ok")
	cursor.close()
	db.close()

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
		user = bot.get_user(user_id)
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
bot.run(DISCORD_TOKEN)