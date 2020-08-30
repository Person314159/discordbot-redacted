import random
import re
from enum import Enum


class Player:
	def __init__(self, name):
		self.name = name
		self.health = 100
		self.is_alive = True
		self.kills = 0
		self.xp = 0

	def take_damage(self, damage):
		if self.is_alive:
			self.health -= damage
			self.health += round(self.xp / 5)

			if self.health <= 0:
				self.die()
			elif self.health > 100:
				self.health = 100

	def die(self):
		self.health = 0
		self.is_alive = False

class EventType(Enum):
	Bloodbath = 1
	Day = 2
	Night = 3
	Feast = 4
	Arena = 5

class Event:
	def __init__(self, name, event_type, is_fatal, damage, hurt, num_players, killers, killed):
		self.name = name
		self.event_type = event_type
		self.is_fatal = is_fatal
		self.damage = damage
		self.hurt = hurt
		self.num_players = num_players
		self.killers = killers
		self.killed = killed

	def weighted_shuffle(self, chosen):
		return sorted(chosen, key=lambda player: -random.random() ** (1.0 / (player.xp + 1)))

	def action(self, chosen):
		died = []

		if self.is_fatal:
			chosen = self.weighted_shuffle(chosen)
			
			if self.killers:
				for i in self.killers:
					chosen[i].xp += 30
					chosen[i].kills += len(self.killed)

			for i in self.killed:
				chosen[i].die()
				died.append(chosen[i])
		else:
			if self.damage:
				for i in self.hurt:
					chosen[i].take_damage(self.damage)

					if not chosen[i].is_alive:
						died.append(chosen[i])

		msg = str(self.name).format(*[str(i.name) for i in chosen])

		for i in range(1, self.num_players):
			if (self.damage or self.is_fatal) and (i - 1 not in self.hurt + self.killed + self.killers):
				chosen[i - 1].xp += 10

		return [msg], died

class ArenaEvent:
	def __init__(self, name, events):
		self.name = name
		self.events = events

bloodbath = [
	Event("**{0}** grabs a shovel.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** grabs a backpack and retreats.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** and **{1}** fight for a bag. **{0}** gives up and retreats.", EventType.Bloodbath, False, 0, [], 2, [], []),
	Event("**{0}** and **{1}** fight for a bag. **{1}** gives up and retreats.", EventType.Bloodbath, False, 0, [], 2, [], []),
	Event("**{0}** finds a bow, some arrows, and a quiver.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** runs into the cornucopia and hides.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** takes a handful of throwing knives.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** rips a mace out of **{1}**'s hands.", EventType.Bloodbath, False, 0, [], 2, [], []),
	Event("**{0}** finds a canteen full of water.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** stays at the cornucopia for resources.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** gathers as much food as they can.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** grabs a sword.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** takes a spear from inside the cornucopia.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** finds a bag full of explosives.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** clutches a first aid kit and runs away.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** takes a sickle from inside the cornucopia.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}**, **{1}**, and **{2}** work together to get as many supplies as possible.", EventType.Bloodbath, False, 0, [], 3, [], []),
	Event("**{0}** runs away with a lighter and some rope.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** snatches a bottle of alcohol and a rag.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** finds a backpack full of camping equipment.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** grabs a backpack, not realizing it is empty.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** breaks **{1}**'s nose for a basket of bread.", EventType.Bloodbath, False, 10, [1], 2, [], []),
	Event("**{0}** stabs **{1}** with a tree branch.", EventType.Bloodbath, False, 30, [1], 2, [], []),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** share everything they gathered before running.", EventType.Bloodbath, False, 0, [], 4, [], []),
	Event("**{0}** retrieves a trident from inside the cornucopia.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** grabs a jar of fishing bait while **{1}** gets fishing gear.", EventType.Bloodbath, False, 0, [], 2, [], []),
	Event("**{0}** scares **{1}** away from the cornucopia.", EventType.Bloodbath, False, 0, [], 2, [], []),
	Event("**{0}** grabs a shield leaning on the cornucopia.", EventType.Bloodbath, False, 0, [], 1, [], []),
	Event("**{0}** snatches a pair of sais.", EventType.Bloodbath, False, 0, [], 1, [], [])
]
day = [
	Event("**{0}** goes hunting.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** injures themselves.", EventType.Day, False, 10, [0], 1, [], []),
	Event("**{0}** explores the arena.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** scares **{1}** off.", EventType.Day, False, 0, [], 2, [], []),
	Event("**{0}** diverts **{1}**'s attention and runs away.", EventType.Day, False, 0, [], 2, [], []),
	Event("**{0}** stalks **{1}**.", EventType.Day, False, 0, [], 2, [], []),
	Event("**{0}** fishes.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** camouflauges themselves in the bushes.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** steals from **{1}** while they aren't looking.", EventType.Day, False, 0, [], 2, [], []),
	Event("**{0}** makes a wooden spear.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** discovers a cave.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** attacks **{1}**, but they manage to escape.", EventType.Day, False, 0, [], 2, [], []),
	Event("**{0}** chases **{1}**.", EventType.Day, False, 0, [], 2, [], []),
	Event("**{0}** runs away from **{1}**.", EventType.Day, False, 0, [], 2, [], []),
	Event("**{0}** collects fruit from a tree.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** stabs **{1}** with a tree branch.", EventType.Day, False, 30, [1], 2, [], []),
	Event("**{0}** receives a hatchet from an unknown sponsor.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** receives clean water from an unknown sponsor.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** receives medical supplies from an unknown sponsor.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** receives fresh food from an unknown sponsor.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** receives an explosive from an unknown sponsor.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** searches for a water source.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** defeats **{1}** in a fight, but spares their life.", EventType.Day, False, 30, [1], 2, [], []),
	Event("**{0}** and **{1}** work together for the day.", EventType.Day, False, 0, [], 2, [], []),
	Event("**{0}** begs for **{1}** to kill them. **{1}** refuses, keeping **{0}** alive.", EventType.Day, False, 0, [], 2, [], []),
	Event("**{0}** tries to sleep through the entire day.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** raid **{4}**'s camp while they are hunting.", EventType.Day, False, 0, [], 5, [], []),
	Event("**{0}** constructs a shack.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** overhears **{1}** and **{2}** talking in the distance.", EventType.Day, False, 0, [], 3, [], []),
	Event("**{0}** practices their archery.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** thinks about home.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** is pricked by thorns while picking berries.", EventType.Day, False, 5, [0], 1, [], []),
	Event("**{0}** tries to spear fish with a trident.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** searches for firewood.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** and **{1}** split up to search for resources.", EventType.Day, False, 0, [], 2, [], []),
	Event("**{0}** picks flowers.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** tends to **{1}**'s wounds.", EventType.Day, False, -15, [1], 2, [], []),
	Event("**{0}** sees smoke rising in the distance, but decides not to investigate.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** sprains their ankle while running away from **{1}**.", EventType.Day, False, 5, [0], 2, [], []),
	Event("**{0}** makes a slingshot.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** travels to higher ground.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** discovers a river.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** hunts for other tributes.", EventType.Day, False, 0, [], 1, [], []),
	Event("**{0}** and **{1}** hunt for other tributes.", EventType.Day, False, 0, [], 2, [], []),
	Event("**{0}**, **{1}**, and **{2}** hunt for other tributes.", EventType.Day, False, 0, [], 3, [], []),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** hunt for other tributes.", EventType.Day, False, 0, [], 4, [], []),
	Event("**{0}**, **{1}**, **{2}**, **{3}**, and **{4}** hunt for other tributes.", EventType.Day, False, 0, [], 5, [], []),
	Event("**{0}** questions their sanity.", EventType.Day, False, 0, [], 1, [], [])
]
night = [
	Event("**{0}** starts a fire.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** sets up camp for the night.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** loses sight of where they are.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** climbs a tree to rest.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** stabs **{1}** with a tree branch.", EventType.Night, False, 30, [1], 2, [], []),
	Event("**{0}** goes to sleep.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** and **{1}** tell stories about themselves to each other.", EventType.Night, False, 0, [], 2, [], []),
	Event("**{0}** sneaks up on **{1}** and does 1000 years of pain on them.", EventType.Night, False, 70, [1], 2, [], []),
	Event("**{0}**'s Winter Social performance was so bad it earraped **{1}**, **{2}** and **{3}**.", EventType.Night, False, 15, [1, 2, 3], 4, [], []),
	Event("**{0}**, **{1}**, **{2}**, **{3}**, and **{4}** sleep in shifts.", EventType.Night, False, 0, [], 5, [], []),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** sleep in shifts.", EventType.Night, False, 0, [], 4, [], []),
	Event("**{0}**, **{1}**, and **{2}** sleep in shifts.", EventType.Night, False, 0, [], 3, [], []),
	Event("**{0}** and **{1}** sleep in shifts.", EventType.Night, False, 0, [], 2, [], []),
	Event("**{0}** tends to their wounds.", EventType.Night, False, -15, [0], 1, [], []),
	Event("**{0}** sees a fire, but stays hidden.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** screams for help.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** stays awake all night.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** passes out from exhaustion.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** cooks their food before putting the fire out.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** and **{1}** run into each other and decide to truce for the night.", EventType.Night, False, 0, [], 2, [], []),
	Event("**{0}** fends **{1}**, **{2}**, and **{3}** away from their fire.", EventType.Night, False, 0, [], 4, [], []),
	Event("**{0}**, **{1}**, and **{2}** discuss the games and what might happen in the morning.", EventType.Night, False, 0, [], 3, [], []),
	Event("**{0}** cries themselves to sleep.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** tries to treat their infection.", EventType.Night, False, -10, [0], 1, [], []),
	Event("**{0}** and **{1}** talk about the tributes still alive.", EventType.Night, False, 0, [], 2, [], []),
	Event("**{0}** is awoken by nightmares.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** and **{1}** huddle for warmth.", EventType.Night, False, 0, [], 2, [], []),
	Event("**{0}** thinks about winning.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** tell each other ghost stories to lighten the mood.", EventType.Night, False, 0, [], 4, [], []),
	Event("**{0}** looks at the night sky.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** defeats **{1}** in a fight, but spares their life.", EventType.Night, False, 30, [1], 2, [], []),
	Event("**{0}** begs for **{1}** to kill them. **{1}** refuses, keeping **{0}** alive.", EventType.Night, False, 0, [], 2, [], []),
	Event("**{0}** destroys **{1}**'s supplies while they are asleep.", EventType.Night, False, 0, [], 2, [], []),
	Event("**{0}** lets **{1}** into their shelter.", EventType.Night, False, 0, [], 2, [], []),
	Event("**{0}** receives a hatchet from an unknown sponsor.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** receives clean water from an unknown sponsor.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** receives medical supplies from an unknown sponsor.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** receives fresh food from an unknown sponsor.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** receives an explosive from an unknown sponsor.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** tries to sing themselves to sleep.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** attempts to start a fire, but is unsuccessful.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** thinks about home.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** tends to **{1}**'s wounds.", EventType.Night, False, -15, [1], 2, [], []),
	Event("**{0}** quietly hums.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}**, **{1}**, and **{2}** cheerfully sing songs together.", EventType.Night, False, 0, [], 3, [], []),
	Event("**{0}** is unable to start a fire and sleeps without warmth.", EventType.Night, False, 0, [], 1, [], []),
	Event("**{0}** and **{1}** hold hands.", EventType.Night, False, 0, [], 2, [], []),
	Event("**{0}** convinces **{1}** to snuggle with them.", EventType.Night, False, 0, [], 2, [], []),
	Event("**{0}** questions their sanity.", EventType.Night, False, 0, [], 1, [], [])
]
feast = [
	Event("**{0}** gathers as much food into a bag as they can before fleeing.", EventType.Feast, False, 0, [], 1, [], []),
	Event("**{0}** sobs while gripping a photo of their friends and family.", EventType.Feast, False, 0, [], 1, [], []),
	Event("**{0}** and **{1}** decide to work together to get more supplies.", EventType.Feast, False, 0, [], 2, [], []),
	Event("**{0}** stabs **{1}** with a tree branch.", EventType.Feast, False, 30, [1], 2, [], []),
	Event("**{0}** and **{1}** get into a fight over raw meat, but **{1}** gives up and runs away.", EventType.Feast, False, 0, [], 2, [], []),
	Event("**{0}** and **{1}** overeat and have stomach aches for the rest of the day.", EventType.Feast, False, 1, [0, 1], 2, [], []),
	Event("**{0}** and **{1}** get into a fight over raw meat, but **{0}** gives up and runs away.", EventType.Feast, False, 0, [], 2, [], []),
	Event("**{0}**, **{1}**, and **{2}** confront each other, but grab what they want slowly to avoid conflict.", EventType.Feast, False, 0, [], 3, [], []),
	Event("**{0}** destroys **{1}**'s memoirs out of spite.", EventType.Feast, False, 0, [], 2, [], []),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** team up to grab food, supplies, weapons, and memoirs.", EventType.Feast, False, 0, [], 4, [], []),
	Event("**{0}** steals **{1}**'s memoirs.", EventType.Feast, False, 0, [], 2, [], []),
	Event("**{0}** takes a staff leaning against the cornucopia.", EventType.Feast, False, 0, [], 1, [], []),
	Event("**{0}** stuffs a bundle of dry clothing into a backpack before sprinting away.", EventType.Feast, False, 0, [], 1, [], [])
]
arena = [
	ArenaEvent("Wolf mutts are let loose in the arena.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** is crushed by a pack of wolf mutts.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** is eaten by wolf mutts.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** knocks **{1}** out and leaves them for the wolf mutts.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** pushes **{1}** into a pack of wolf mutts.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("As **{0}** and **{1}** fight, a pack of wolf mutts show up and kill them both.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("Acidic rain pours down on the arena.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** is unable to find shelter and dies.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** trips face first into a puddle of acidic rain.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** injures **{1}** and leaves them in the rain to die.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** refuses **{1}** shelter, killing them.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** shoves **{1}** into a pond of acidic rain, but is pulled in by **{1}**, killing them both.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("A cloud of poisonous smoke starts to fill the arena.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** is engulfed in the cloud of poisonous smoke.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** sacrifices themselves so **{1}** can get away.", EventType.Arena, True, 0, [], 2, [], [0]),
		Event("**{0}** slowly pushes **{1}** closer into the cloud until they can't resist any more.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** and **{1}** agree to die in the cloud together, but **{0}** pushes **{1}** in without warning.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** and **{1}** decide to run into the cloud together.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("A monstrous tornado wreaks havoc on the area.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** is sucked into the tornado.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** is incapacitated by flying debris and dies.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** pushes **{1}** into an incoming boulder.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** stabs **{1}**, then pushes them close enough to the tornado to suck them in.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** tries to save **{1}** from being sucked into the tornado, only to be sucked in as well.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("A swarm of tracker jackers invades the arena.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** is stung to death.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** slowly dies from the tracker jacker toxins.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** knocks **{1}** unconscious and leaves them there as bait.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("While running away from the tracker jackers, **{0}** grabs **{1}** and throws them to the ground.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** and **{1}** run out of places to run and are stung to death.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("A tsunami rolls into the the arena.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** is swept away.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** fatally injures themselves on debris.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** holds **{1}** underwater to drown.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** defeats **{1}**, but throws them in the water to make sure they die.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** and **{1}** smash their heads together as the tsunami rolls in, leaving them both to drown.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("A fire spreads throughout the arena.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("The fire catches up to **{0}**, killing them.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("A fireball strikes **{0}**, killing them.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** kills **{1}** in order to utilize a body of water safely.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** falls to the ground, but kicks **{1}** hard enough to then push them into the fire.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** and **{1}** fail to find a safe spot and suffocate.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("The arena's border begins to rapidly contract.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** is electrocuted by the border.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** trips on a tree root and is unable to recover fast enough.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** restrains **{1}** to a tree and leaves them to die.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** pushes **{1}** into the border while they are not paying attention.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("Thinking they could escape, **{0}** and **{1}** attempt to run through the border together.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("Monkey mutts fill the arena.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** dies from internal bleeding caused by a monkey mutt.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** is pummeled to the ground and killed by a troop of monkey mutts.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** uses **{1}** as a shield from the monkey mutts.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** injures **{1}** and leaves them for the monkey mutts.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("While running, **{0}** falls over and grabs **{1}** on the way down. The monkey mutts kill them.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("Carnivorous squirrels start attacking the tributes.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** is brutally attacked by a scurry of squirrels.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** tries to kills as many squirrels as they can, but there are too many.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** uses the squirrels to their advantage, shoving **{1}** into them.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}**, in agony, kills **{1}** so they do not have to be attacked by the squirrels.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("The squirrels separate and kill **{0}** and **{1}**.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("A volcano erupts at the center of the arena.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** is buried in ash.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** suffocates.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** pushes **{1}** in the lava.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** dips their weapon in the lava and kills **{1}** with it.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("As **{0}** trips over **{1}** into the lava, they grab **{1}** and pulls them down with themselves.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("The arena turns pitch black and nobody can see a thing.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** trips on a rock and falls off a cliff.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** accidently makes contact with spiny, lethal plant life.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** flails their weapon around, accidently killing **{1}**.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** finds and kills **{1}**, who was making too much noise.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("While fighting, **{0}** and **{1}** lose their balance, roll down a jagged hillside, and die.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("The remaining tributes begin to hallucinate.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** eats a scorpion, thinking it is a delicate dessert.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** hugs a tracker jacker nest, believing it to be a pillow.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** mistakes **{1}** for a bear and kills them.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** drowns **{1}**, who they thought was a shark trying to eat them.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** and **{1}** decide to jump down the rabbit hole to Wonderland, which turns out to be a pit of rocks.", EventType.Arena, True, 0, [], 2, [], [0, 1])
	]),
	ArenaEvent("The tributes find themselves at Trans.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** tries to break down the ELI door but gets knocked backwards off the balcony.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("A magic Shao lands on **{0}**, ending their misery.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** makes a trap out of Flex Tape, trapping **{1}**.", EventType.Arena, True, 0, [], 2, [0], [1]),
		Event("**{0}** tried to ship **{1}** with **{2}**. **{1}** got mad and killed **{0}**.", EventType.Arena, True, 0, [], 3, [1], [0]),
		Event("**{0}** thought it said gullible on the ceiling.", EventType.Arena, False, 2, [0], 1, [], []),
		Event("**{0}** gets trapped at Town Hall and dies.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** puts mistletoe on a stick and waves it above **{1}** and **{2}**. **{1}**, embarrassed, kills **{0}** and **{2}** in unbridled rage.", EventType.Arena, True, 0, [], 3, [1], [0, 2]),
		Event("Saf comes and yells at **{0}**, **{1}**, and **{2}**, causing **{0}** and **{1}** to commit suicide.", EventType.Arena, True, 0, [], 3, [], [0, 1]),
		Event("**{0}** joins Student Council and never returns.", EventType.Arena, True, 0, [], 1, [], [0]),
		Event("**{0}** sits in the Lounge/ELI alone.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** plays Smash with **{1}** in the ELI and loses.", EventType.Arena, False, 5, [0], 2, [], []),
		Event("**{0}** tries to escape through the ceiling. They get lost and are unable to find their way out.", EventType.Arena, True, 0, [], 1, [], [0])
	]),
	ArenaEvent("The snapping of fingers is heard in the background. Some of the tributes start to disappear.", [
		Event("**{0}** survives.", EventType.Arena, False, 0, [], 1, [], []),
		Event("**{0}** fades out of existence.", EventType.Arena, True, 0, [], 1, [], [0])
	])
]
fatal_bloodbath = [
	Event("**{0}** steps off their podium too soon and blows up.", EventType.Bloodbath, True, 0, [], 1, [], [0]),
	Event("**{0}** throws a knife into **{1}**'s head.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** accidently steps on a landmine.", EventType.Bloodbath, True, 0, [], 1, [], [0]),
	Event("**{0}** catches **{1}** off guard and kills them.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** work together to drown **{2}**.", EventType.Bloodbath, True, 0, [], 3, [0, 1], [2]),
	Event("**{0}** strangles **{1}** after engaging in a fist fight.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** shoots an arrow into **{1}**'s head.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** cannot handle the circumstances and commits suicide.", EventType.Bloodbath, True, 0, [], 1, [], [0]),
	Event("**{0}** bashes **{1}**'s head against a rock several times.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** snaps **{1}**'s neck.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** decapitates **{1}** with a sword.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** spears **{1}** in the abdomen.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** sets **{1}** on fire with a molotov.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** falls into a pit and dies.", EventType.Bloodbath, True, 0, [], 1, [], [0]),
	Event("**{0}** stabs **{1}** while their back is turned.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** severely injures **{1}**, but puts them out of their misery.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** severely injures **{1}** and leaves them to die.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** are absorbed into the mass of Jerry Shao.", EventType.Bloodbath, True, 0, [], 2, [], [0, 1]),
	Event("**{0}** bashes **{1}**'s head in with a mace.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** pushes **{1}** off a cliff during a knife fight.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** throws a knife into **{1}**'s chest.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** is unable to convince **{1}** to not kill them.", EventType.Bloodbath, True, 0, [], 2, [1], [0]),
	Event("**{0}** convinces **{1}** to not kill them, only to kill **{1}** instead.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** falls into a frozen lake and drowns.", EventType.Bloodbath, True, 0, [], 1, [], [0]),
	Event("**{0}**, **{1}**, and **{2}** start fighting, but **{1}** runs away as **{0}** kills **{2}**.", EventType.Bloodbath, True, 0, [], 3, [0], [2]),
	Event("**{0}** kills **{1}** with their own weapon.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** overpowers **{1}**, killing them.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** sets an explosive off, killing **{1}**.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** sets an explosive off, killing **{1}**, and **{2}**.", EventType.Bloodbath, True, 0, [], 3, [0], [1, 2]),
	Event("**{0}** sets an explosive off, killing **{1}**, **{2}**, and **{3}**.", EventType.Bloodbath, True, 0, [], 4, [0], [1, 2, 3]),
	Event("**{0}** sets an explosive off, killing **{1}**, **{2}**, **{3}** and **{4}**.", EventType.Bloodbath, True, 0, [], 5, [0], [1, 2, 3, 4]),
	Event("**{0}** kills **{1}** as they try to run.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** threaten a double suicide. It fails and they die.", EventType.Bloodbath, True, 0, [], 2, [], [0, 1]),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** form a suicide pact, killing themselves.", EventType.Bloodbath, True, 0, [], 4, [], [0, 1, 2, 3]),
	Event("**{0}** kills **{1}** with a hatchet.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** fight **{2}** and **{3}**. **{0}** and **{1}** survive.", EventType.Bloodbath, True, 0, [], 4, [0, 1], [2, 3]),
	Event("**{0}** and **{1}** fight **{2}** and **{3}**. **{2}** and **{3}** survive.", EventType.Bloodbath, True, 0, [], 4, [2, 3], [0, 1]),
	Event("**{0}** attacks **{1}**, but **{2}** protects them, killing **{0}**.", EventType.Bloodbath, True, 0, [], 3, [2], [0]),
	Event("**{0}** severely slices **{1}** with a sword.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** strangles **{1}** with a rope.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** kills **{1}** for their supplies.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** shoots an arrow at **{1}**, but misses and kills **{2}** instead.", EventType.Bloodbath, True, 0, [], 3, [0], [2]),
	Event("**{0}** shoots a poisonous blow dart into **{1}**'s neck, slowly killing them.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** stabs **{1}** in the back with a trident.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}**, **{1}**, and **{2}** get into a fight. **{0}** triumphantly kills them both.", EventType.Bloodbath, True, 0, [], 3, [0], [1, 2]),
	Event("**{0}**, **{1}**, and **{2}** get into a fight. **{1}** triumphantly kills them both.", EventType.Bloodbath, True, 0, [], 3, [1], [0, 2]),
	Event("**{0}**, **{1}**, and **{2}** get into a fight. **{2}** triumphantly kills them both.", EventType.Bloodbath, True, 0, [], 3, [2], [0, 1]),
	Event("**{0}** finds **{1}** hiding in the cornucopia and kills them.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** finds **{1}** hiding in the cornucopia, but **{1}** kills them.", EventType.Bloodbath, True, 0, [], 2, [1], [0]),
	Event("**{0}** kills **{1}** with a sickle.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** fight for a bag. **{0}** strangles **{1}** with the straps and runs.", EventType.Bloodbath, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** fight for a bag. **{1}** strangles **{0}** with the straps and runs.", EventType.Bloodbath, True, 0, [], 2, [1], [0]),
	Event("**{0}** repeatedly stabs **{1}** to death with sais.", EventType.Bloodbath, True, 0, [], 2, [0], [1])
]
fatal_day = [
	Event("**{0}** takes the full force of a No U from **{1}**.", EventType.Day, True, 0, [], 2, [1], [0]),
	Event("**{0}** catches **{1}** off guard and kills them.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** throws a knife into **{1}**'s head.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** begs for **{1}** to kill them. **{1}** reluctantly obliges, killing **{0}**.", EventType.Day, True, 0, [], 2, [1], [0]),
	Event("**{0}** and **{1}** work together to drown **{2}**.", EventType.Day, True, 0, [], 3, [0, 1], [2]),
	Event("**{0}** strangles **{1}** after engaging in a fist fight.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** shoots an arrow into **{1}**'s head.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** bleeds out due to untreated injuries.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** cannot handle the circumstances and commits suicide.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** bashes **{1}**'s head against a rock several times.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** unknowingly eats toxic berries.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** silently snaps **{1}**'s neck.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** taints **{1}**'s food, killing them.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** decapitates **{1}** with a sword.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** dies from an infection.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** spears **{1}** in the abdomen.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** sets **{1}** on fire with a molotov.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** falls into a pit and dies.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** stabs **{1}** while their back is turned.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** severely injures **{1}**, but puts them out of their misery.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** severely injures **{1}** and leaves them to die.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** bashes **{1}**'s head in with a mace.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** attempts to climb a tree, but falls to their death.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** pushes **{1}** off a cliff during a knife fight.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** throws a knife into **{1}**'s chest.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}**'s trap kills **{1}**.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** kills **{1}** while they are resting.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** is unable to convince **{1}** to not kill them.", EventType.Day, True, 0, [], 2, [1], [0]),
	Event("**{0}** convinces **{1}** to not kill them, only to kill **{1}** instead.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** falls into a frozen lake and drowns.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}**, **{1}**, and **{2}** start fighting, but **{1}** runs away as **{0}** kills **{2}**.", EventType.Day, True, 0, [], 3, [0], [2]),
	Event("**{0}** kills **{1}** with their own weapon.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** overpowers **{1}**, killing them.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** sets an explosive off, killing **{1}**.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** sets an explosive off, killing **{1}**, and **{2}**.", EventType.Day, True, 0, [], 3, [0], [1, 2]),
	Event("**{0}** sets an explosive off, killing **{1}**, **{2}**, and **{3}**.", EventType.Day, True, 0, [], 4, [0], [1, 2, 3]),
	Event("**{0}** sets an explosive off, killing **{1}**, **{2}**, **{3}** and **{4}**.", EventType.Day, True, 0, [], 5, [0], [1, 2, 3, 4]),
	Event("**{0}** kills **{1}** as they try to run.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** threaten a double suicide. It fails and they die.", EventType.Day, True, 0, [], 2, [], [0, 1]),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** form a suicide pact, killing themselves.", EventType.Day, True, 0, [], 4, [], [0, 1, 2, 3]),
	Event("**{0}** dies from hypothermia.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** dies from hunger.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** dies from thirst.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** kills **{1}** with a hatchet.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** fight **{2}** and **{3}**. **{0}** and **{1}** survive.", EventType.Day, True, 0, [], 4, [0, 1], [2, 3]),
	Event("**{0}** and **{1}** fight **{2}** and **{3}**. **{2}** and **{3}** survive.", EventType.Day, True, 0, [], 4, [2, 3], [0, 1]),
	Event("**{0}** dies trying to escape the arena.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** dies of dysentery.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** accidently detonates a land mine while trying to arm it.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** attacks **{1}**, but **{2}** protects them, killing **{0}**.", EventType.Day, True, 0, [], 3, [2], [0]),
	Event("**{0}** ambushes **{1}** and kills them.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** accidently steps on a landmine.", EventType.Day, True, 0, [], 1, [], [0]),
	Event("**{0}** severely slices **{1}** with a sword.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** strangles **{1}** with a rope.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** kills **{1}** for their supplies.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** shoots an arrow at **{1}**, but misses and kills **{2}** instead.", EventType.Day, True, 0, [], 3, [0], [2]),
	Event("**{0}** shoots a poisonous blow dart into **{1}**'s neck, slowly killing them.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}**, **{1}**, and **{2}** successfully ambush and kill **{3}**, **{4}**, and **{5}**.", EventType.Day, True, 0, [], 6, [0, 1, 2], [3, 4, 5]),
	Event("**{0}**, **{1}**, and **{2}** unsuccessfully ambush **{3}**, **{4}**, and **{5}**, who kill them instead.", EventType.Day, True, 0, [], 6, [3, 4, 5], [0, 1, 2]),
	Event("**{0}** forces **{1}** to kill **{2}** or **{3}**. They decide to kill **{2}**.", EventType.Day, True, 0, [], 4, [1], [2]),
	Event("**{0}** forces **{1}** to kill **{2}** or **{3}**. They decide to kill **{3}**.", EventType.Day, True, 0, [], 4, [1], [3]),
	Event("**{0}** forces **{1}** to kill **{2}** or **{3}**. They refuse to kill, so **{0}** kills them instead.", EventType.Day, True, 0, [], 4, [0], [1]),
	Event("**{0}** poisons **{1}**'s drink, but mistakes it for their own and dies.", EventType.Day, True, 0, [], 2, [], [0]),
	Event("**{0}** poisons **{1}**'s drink. They drink it and die.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** stabs **{1}** in the back with a trident.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** attempts to climb a tree, but falls on **{1}**, killing them both.", EventType.Day, True, 0, [], 2, [], [0, 1]),
	Event("**{0}**, **{1}**, and **{2}** get into a fight. **{0}** triumphantly kills them both.", EventType.Day, True, 0, [], 3, [0], [1, 2]),
	Event("**{0}**, **{1}**, and **{2}** get into a fight. **{1}** triumphantly kills them both.", EventType.Day, True, 0, [], 3, [1], [0, 2]),
	Event("**{0}**, **{1}**, and **{2}** get into a fight. **{2}** triumphantly kills them both.", EventType.Day, True, 0, [], 3, [2], [0, 1]),
	Event("**{0}** kills **{1}** with a sickle.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}**, **{1}**, **{2}**, **{3}**, and **{4}** track down and kill **{5}**.", EventType.Day, True, 0, [], 6, [0, 1, 2, 3, 4], [5]),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** track down and kill **{4}**.", EventType.Day, True, 0, [], 5, [0, 1, 2, 3], [4]),
	Event("**{0}**, **{1}**, and **{2}** track down and kill **{3}**.", EventType.Day, True, 0, [], 4, [0, 1, 2], [3]),
	Event("**{0}**, and **{1}** track down and kill **{2}**.", EventType.Day, True, 0, [], 3, [0, 1], [2]),
	Event("**{0}** tracks down and kills **{1}**.", EventType.Day, True, 0, [], 2, [0], [1]),
	Event("**{0}** repeatedly stabs **{1}** to death with sais.", EventType.Day, True, 0, [], 2, [0], [1])
]
fatal_night = [
	Event("**{0}** catches **{1}** off guard and kills them.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** throws a knife into **{1}**'s head.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** begs for **{1}** to kill them. **{1}** reluctantly obliges, killing **{0}**.", EventType.Night, True, 0, [], 2, [1], [0]),
	Event("**{0}** and **{1}** work together to drown **{2}**.", EventType.Night, True, 0, [], 3, [0, 1], [2]),
	Event("**{0}** strangles **{1}** after engaging in a fist fight.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** shoots an arrow into **{1}**'s head.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** bleeds out due to untreated injuries.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** cannot handle the circumstances and commits suicide.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** bashes **{1}**'s head against a rock several times.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** unknowingly eats toxic berries.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** silently snaps **{1}**'s neck.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** taints **{1}**'s food, killing them.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** decapitates **{1}** with a sword.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** dies from an infection.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** spears **{1}** in the abdomen.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** sets **{1}** on fire with a molotov.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** falls into a pit and dies.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** stabs **{1}** while their back is turned.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** severely injures **{1}**, but puts them out of their misery.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** severely injures **{1}** and leaves them to die.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** bashes **{1}**'s head in with a mace.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** attempts to climb a tree, but falls to their death.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** pushes **{1}** off a cliff during a knife fight.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** throws a knife into **{1}**'s chest.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}**'s trap kills **{1}**.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** kills **{1}** while they are sleeping.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** is unable to convince **{1}** to not kill them.", EventType.Night, True, 0, [], 2, [1], [0]),
	Event("**{0}** convinces **{1}** to not kill them, only to kill **{1}** instead.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** falls into a frozen lake and drowns.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}**, **{1}**, and **{2}** start fighting, but **{1}** runs away as **{0}** kills **{2}**.", EventType.Night, True, 0, [], 3, [0], [2]),
	Event("**{0}** kills **{1}** with their own weapon.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** overpowers **{1}**, killing them.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** sets an explosive off, killing **{1}**.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** sets an explosive off, killing **{1}**, and **{2}**.", EventType.Night, True, 0, [], 3, [0], [1, 2]),
	Event("**{0}** sets an explosive off, killing **{1}**, **{2}**, and **{3}**.", EventType.Night, True, 0, [], 4, [0], [1, 2, 3]),
	Event("**{0}** sets an explosive off, killing **{1}**, **{2}**, **{3}** and **{4}**.", EventType.Night, True, 0, [], 5, [0], [1, 2, 3, 4]),
	Event("**{0}** kills **{1}** as they try to run.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** threaten a double suicide. It fails and they die.", EventType.Night, True, 0, [], 2, [], [0, 1]),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** form a suicide pact, killing themselves.", EventType.Night, True, 0, [], 4, [], [0, 1, 2, 3]),
	Event("**{0}** dies from hypothermia.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** dies from hunger.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** dies from thirst.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** kills **{1}** with a hatchet.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** fight **{2}** and **{3}**. **{0}** and **{1}** survive.", EventType.Night, True, 0, [], 4, [0, 1], [2, 3]),
	Event("**{0}** and **{1}** fight **{2}** and **{3}**. **{2}** and **{3}** survive.", EventType.Night, True, 0, [], 4, [2, 3], [0, 1]),
	Event("**{0}** dies trying to escape the arena.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** dies of dysentery.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** accidently detonates a land mine while trying to arm it.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** attacks **{1}**, but **{2}** protects them, killing **{0}**.", EventType.Night, True, 0, [], 3, [2], [0]),
	Event("**{0}** ambushes **{1}** and kills them.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** accidently steps on a landmine.", EventType.Night, True, 0, [], 1, [], [0]),
	Event("**{0}** severely slices **{1}** with a sword.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** strangles **{1}** with a rope.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** kills **{1}** for their supplies.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** shoots an arrow at **{1}**, but misses and kills **{2}** instead.", EventType.Night, True, 0, [], 3, [0], [2]),
	Event("**{0}** shoots a poisonous blow dart into **{1}**'s neck, slowly killing them.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}**, **{1}**, and **{2}** successfully ambush and kill **{3}**, **{4}**, and **{5}**.", EventType.Night, True, 0, [], 6, [0, 1, 2], [3, 4, 5]),
	Event("**{0}**, **{1}**, and **{2}** unsuccessfully ambush **{3}**, **{4}**, and **{5}**, who kill them instead.", EventType.Night, True, 0, [], 6, [3, 4, 5], [0, 1, 2]),
	Event("**{0}** forces **{1}** to kill **{2}** or **{3}**. They decide to kill **{2}**.", EventType.Night, True, 0, [], 4, [1], [2]),
	Event("**{0}** forces **{1}** to kill **{2}** or **{3}**. They decide to kill **{3}**.", EventType.Night, True, 0, [], 4, [1], [3]),
	Event("**{0}** forces **{1}** to kill **{2}** or **{3}**. They refuse to kill, so **{0}** kills them instead.", EventType.Night, True, 0, [], 4, [0], [1]),
	Event("**{0}** poisons **{1}**'s drink, but mistakes it for their own and dies.", EventType.Night, True, 0, [], 2, [], [0]),
	Event("**{0}** poisons **{1}**'s drink. They drink it and die.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** stabs **{1}** in the back with a trident.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** attempts to climb a tree, but falls on **{1}**, killing them both.", EventType.Night, True, 0, [], 2, [], [0, 1]),
	Event("**{0}**, **{1}**, and **{2}** get into a fight. **{0}** triumphantly kills them both.", EventType.Night, True, 0, [], 3, [0], [1, 2]),
	Event("**{0}**, **{1}**, and **{2}** get into a fight. **{1}** triumphantly kills them both.", EventType.Night, True, 0, [], 3, [1], [0, 2]),
	Event("**{0}**, **{1}**, and **{2}** get into a fight. **{2}** triumphantly kills them both.", EventType.Night, True, 0, [], 3, [2], [0, 1]),
	Event("**{0}** kills **{1}** with a sickle.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}**, **{1}**, **{2}**, **{3}**, and **{4}** track down and kill **{5}**.", EventType.Night, True, 0, [], 6, [0, 1, 2, 3, 4], [5]),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** track down and kill **{4}**.", EventType.Night, True, 0, [], 5, [0, 1, 2, 3], [4]),
	Event("**{0}**, **{1}**, and **{2}** track down and kill **{3}**.", EventType.Night, True, 0, [], 4, [0, 1, 2], [3]),
	Event("**{0}**, and **{1}** track down and kill **{2}**.", EventType.Night, True, 0, [], 3, [0, 1], [2]),
	Event("**{0}** tracks down and kills **{1}**.", EventType.Night, True, 0, [], 2, [0], [1]),
	Event("**{0}** repeatedly stabs **{1}** to death with sais.", EventType.Night, True, 0, [], 2, [0], [1])
]
fatal_feast = [
	Event("**{0}** throws a knife into **{1}**'s head.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** accidently steps on a landmine.", EventType.Feast, True, 0, [], 1, [], [0]),
	Event("**{0}** catches **{1}** off guard and kills them.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** work together to drown **{2}**.", EventType.Feast, True, 0, [], 3, [0, 1], [2]),
	Event("**{0}** puts a grape in a microwave. It explodes and so do they.", EventType.Feast, True, 0, [], 1, [], [0]),
	Event("**{0}** strangles **{1}** after engaging in a fist fight.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** shoots an arrow into **{1}**'s head.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** bleeds out due to untreated injuries.", EventType.Feast, True, 0, [], 1, [], [0]),
	Event("**{0}** cannot handle the circumstances and commits suicide.", EventType.Feast, True, 0, [], 1, [], [0]),
	Event("**{0}** bashes **{1}**'s head against a rock several times.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** snaps **{1}**'s neck.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** decapitates **{1}** with a sword.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** dies from an infection.", EventType.Feast, True, 0, [], 1, [], [0]),
	Event("**{0}** spears **{1}** in the abdomen.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** sets **{1}** on fire with a molotov.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** falls into a pit and dies.", EventType.Feast, True, 0, [], 1, [], [0]),
	Event("**{0}** stabs **{1}** while their back is turned.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** severely injures **{1}**, but puts them out of their misery.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** severely injures **{1}** and leaves them to die.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** bashes **{1}**'s head in with a mace.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** pushes **{1}** off a cliff during a knife fight.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** throws a knife into **{1}**'s chest.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}**'s trap kills **{1}**.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** is unable to convince **{1}** to not kill them.", EventType.Feast, True, 0, [], 2, [1], [0]),
	Event("**{0}** convinces **{1}** to not kill them, only to kill **{1}** instead.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** falls into a frozen lake and drowns.", EventType.Feast, True, 0, [], 1, [], [0]),
	Event("**{0}**, **{1}**, and **{2}** start fighting, but **{1}** runs away as **{0}** kills **{2}**.", EventType.Feast, True, 0, [], 3, [0], [2]),
	Event("**{0}** kills **{1}** with their own weapon.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** overpowers **{1}**, killing them.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** sets an explosive off, killing **{1}**.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** sets an explosive off, killing **{1}**, and **{2}**.", EventType.Feast, True, 0, [], 3, [0], [1, 2]),
	Event("**{0}** sets an explosive off, killing **{1}**, **{2}**, and **{3}**.", EventType.Feast, True, 0, [], 4, [0], [1, 2, 3]),
	Event("**{0}** sets an explosive off, killing **{1}**, **{2}**, **{3}** and **{4}**.", EventType.Feast, True, 0, [], 5, [0], [1, 2, 3, 4]),
	Event("**{0}** kills **{1}** as they try to run.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** threaten a double suicide. It fails and they die.", EventType.Feast, True, 0, [], 2, [], [0, 1]),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** form a suicide pact, killing themselves.", EventType.Feast, True, 0, [], 4, [], [0, 1, 2, 3]),
	Event("**{0}** kills **{1}** with a hatchet.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** and **{1}** fight **{2}** and **{3}**. **{0}** and **{1}** survive.", EventType.Feast, True, 0, [], 4, [0, 1], [2, 3]),
	Event("**{0}** and **{1}** fight **{2}** and **{3}**. **{2}** and **{3}** survive.", EventType.Feast, True, 0, [], 4, [2, 3], [0, 1]),
	Event("**{0}** attacks **{1}**, but **{2}** protects them, killing **{0}**.", EventType.Feast, True, 0, [], 3, [2], [0]),
	Event("**{0}** ambushes **{1}** and kills them.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** severely slices **{1}** with a sword.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** strangles **{1}** with a rope.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** kills **{1}** for their supplies.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** shoots an arrow at **{1}**, but misses and kills **{2}** instead.", EventType.Feast, True, 0, [], 3, [0], [2]),
	Event("**{0}** shoots a poisonous blow dart into **{1}**'s neck, slowly killing them.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}**, **{1}**, and **{2}** successfully ambush and kill **{3}**, **{4}**, and **{5}**.", EventType.Feast, True, 0, [], 6, [0, 1, 2], [3, 4, 5]),
	Event("**{0}**, **{1}**, and **{2}** unsuccessfully ambush **{3}**, **{4}**, and **{5}**, who kill them instead.", EventType.Feast, True, 0, [], 6, [3, 4, 5], [0, 1, 2]),
	Event("**{0}** stabs **{1}** in the back with a trident.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}**, **{1}**, and **{2}** get into a fight. **{0}** triumphantly kills them both.", EventType.Feast, True, 0, [], 3, [0], [1, 2]),
	Event("**{0}**, **{1}**, and **{2}** get into a fight. **{1}** triumphantly kills them both.", EventType.Feast, True, 0, [], 3, [1], [0, 2]),
	Event("**{0}**, **{1}**, and **{2}** get into a fight. **{2}** triumphantly kills them both.", EventType.Feast, True, 0, [], 3, [2], [0, 1]),
	Event("**{0}** kills **{1}** with a sickle.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}**, **{1}**, **{2}**, **{3}**, and **{4}** track down and kill **{5}**.", EventType.Feast, True, 0, [], 6, [0, 1, 2, 3, 4], [5]),
	Event("**{0}**, **{1}**, **{2}**, and **{3}** track down and kill **{4}**.", EventType.Feast, True, 0, [], 5, [0, 1, 2, 3], [4]),
	Event("**{0}**, **{1}**, and **{2}** track down and kill **{3}**.", EventType.Feast, True, 0, [], 4, [0, 1, 2], [3]),
	Event("**{0}**, and **{1}** track down and kill **{2}**.", EventType.Feast, True, 0, [], 3, [0, 1], [2]),
	Event("**{0}** tracks down and kills **{1}**.", EventType.Feast, True, 0, [], 2, [0], [1]),
	Event("**{0}** repeatedly stabs **{1}** to death with sais.", EventType.Feast, True, 0, [], 2, [0], [1])
]
