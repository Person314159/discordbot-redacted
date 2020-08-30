#!/usr/bin/python3
import random
from hungergames_data import *

def hungergames(args):
	"""
	`{0}hungergames` __`Hunger Games generator`__
	**Aliases**: hg

	**Usage:** {0}hungergames <person 1 | person 2 | etc.>

	**Examples:**
	`{0}hungergames a | b | c` generate Hunger Games scenario
	"""

	args = args.split(" | ")

	if len(args) == 1:
		# print("You need at least two people to play hunger games.")
		return
	elif len(args) > 50:
		# print("Too many people.")
		return

	players = [Player(i) for i in args]
	total_died = []
	placements = ["Placements:"]
	kills = ["Kills:"]
	counter = 1
	history = []

	def round(event_type, counter, died, total_died):
		msgs = []

		def pick_events(event_list, fatal_event_list, died = died, msgs = msgs):
			current_players = [i for i in players if i.is_alive]

			while len(current_players) > 0:
				rng = random.uniform(0, 1)

				if rng > 0.75:
					event = random.choice(fatal_event_list)
				else:
					event = random.choice(event_list)

				if event.num_players <= len(current_players):
					chosen = random.sample(current_players, event.num_players)
					msgs1, chosen, died = event.action(died, total_died, chosen)
					msgs += msgs1

					for i in chosen:
						current_players.remove(i)

			return msgs

		if event_type == EventType.Bloodbath:
			msgs.append("BLOODBATH:")
			msgs = pick_events(bloodbath, fatal_bloodbath)
		elif event_type == EventType.Day:
			msgs.append(f"DAY {counter}:")
			msgs = pick_events(day, fatal_day)
		elif event_type == EventType.Night:
			msgs.append(f"NIGHT {counter}:")
			msgs = pick_events(night, fatal_night)
		elif event_type == EventType.Feast:
			msgs.append(f"FEAST:")
			msgs = pick_events(feast, fatal_feast)
		elif event_type == EventType.Arena:
			arena_choice = random.choice(arena)
			msgs.append(f"ARENA: {arena_choice.name}")
			msgs = pick_events(arena_choice.events, arena_choice.events)

		return msgs, died

	def game(state, counter, died, total_died = total_died):
		msgs, died = round(state, counter, died, total_died)
		nonlocal history
		history += msgs
		send_message = "\n".join(msgs)

		# print(send_message)

		return died

	died = game(EventType.Bloodbath, 1, [])
	num_alive = len([i for i in players if i.is_alive])

	while num_alive > 1:
		rng = random.uniform(0, 1)

		if rng > 0.95:
			died = game(EventType.Feast, counter, died)
			num_alive = len([i for i in players if i.is_alive])

			if num_alive <= 1:
				break
		elif 0.95 >= rng and rng > 0.85:
			died = game(EventType.Arena, counter, died)
			num_alive = len([i for i in players if i.is_alive])

			if num_alive <= 1:
				break

		died = game(EventType.Day, counter, died)
		num_alive = len([i for i in players if i.is_alive])

		if num_alive <= 1:
			break

		if not died:
			history.append("No cannon shots can be heard in the distance.")
		else:
			history.append(f"{len(died)} cannon {'shot' if len(died) == 1 else 'shots'} can be heard in the distance for {', '.join([i.name for i in died])}.")

		died = game(EventType.Night, counter, [])
		num_alive = len([i for i in players if i.is_alive])

		if num_alive <= 1:
			break

		counter += 1

	if num_alive == 1:
		total_died.append([i for i in players if i.is_alive][0])
		history.append(f"**{[i for i in players if i.is_alive][0].name}** is the winner!")
	elif num_alive == 0:
		history.append("Nobody won! They all died!")
		pass

	total_died = total_died[::-1]

	for i in total_died:
		if total_died.index(i) == 10:
			placements.append(f"11th: {i.name} ({i.xp} XP)")
		elif total_died.index(i) == 11:
			placements.append(f"12th: {i.name} ({i.xp} XP)")
		elif total_died.index(i) == 12:
			placements.append(f"13th: {i.name} ({i.xp} XP)")
		elif total_died.index(i) % 10 == 0:
			placements.append(f"{total_died.index(i) + 1}st: {i.name} ({i.xp} XP)")
		elif total_died.index(i) % 10 == 1:
			placements.append(f"{total_died.index(i) + 1}nd: {i.name} ({i.xp} XP)")
		elif total_died.index(i) % 10 == 2:
			placements.append(f"{total_died.index(i) + 1}rd: {i.name} ({i.xp} XP)")
		else:
			placements.append(f"{total_died.index(i) + 1}th: {i.name} ({i.xp} XP)")

	history += placements
	# print("\n".join(placements))

	kills_list = sorted(total_died, key = lambda x: x.kills, reverse = True)

	for i in kills_list:
		if i.kills != 0:
			kills.append(f"{i.kills}: {i.name}")

	history += kills
	# print("\n".join(kills))

	return history, players

max_kills = (0, [])
max_xp = (0, [])

for i in range(10000):
	history, players = hungergames("")

	curr_kills = max([player.kills for player in players])
	curr_xp = max([player.xp for player in players])

	if curr_kills > max_kills[0]:
		max_kills = (curr_kills, history)

	if curr_xp > max_xp[0]:
		max_xp = (curr_xp, history)


with open("hungergames.txt", "w") as f:
	f.write("\n".join(max_kills[1] + ["\n"] + max_xp[1]))