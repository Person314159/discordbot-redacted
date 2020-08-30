#!/usr/bin/python3
import random
from itertools import combinations_with_replacement
import string

# Reference: https://arxiv.org/pdf/1602.06208v2.pdf

digits = string.digits + string.ascii_uppercase

def int2base(x: int, b: int) -> int:
	if x < 0:
		sign = -1
	elif x == 0:
		return digits[0]
	else:
		sign = 1

	x *= sign
	digs = []

	while x:
		digs.append(digits[x % b])
		x = x // b

	if sign < 0:
		digs.append("-")

	digs.reverse()

	return "".join(digs)

def sum_of_three_palindromes(n: str, g: int) -> list:
	'''
	Given a positive integer n in base g, return a list of at most three palindromes which sum to it.
	'''

	def D(n: str) -> int:
		return int(n, g) % g

	def A(n: str) -> (list, list, list, int):
		d = list(reversed([int(i, g) for i in n]))
		l = len(n)

		if d[l - 2] not in [0, 1, 2]:

			# A.1)
			if D(int2base(d[0] - d[l - 1] - d[l - 2] + 1, g)) != 0:
				return [d[l - 1]], [d[l - 2] - 1], [D(int2base(d[0] - d[l - 1] - d[l - 2] + 1, g))], 1

			# A.2)
			else:
				return [d[l - 1]], [d[l - 2] - 2], [1], 2
		else:
			if d[l - 1] != 1:

				# A.3)
				if D(int2base(d[0] - d[l - 1] + 2, g)) != 0:
					return [d[l - 1] - 1], [g - 1], [D(int2base(d[0] - d[l - 1] + 2, g))], 3

				# A.4)
				else:
					return [d[l - 1] - 1], [g - 2], [1], 4
		if d[l - 1] == 1 and d[l - 2] == 0:

			# A.5)
			if d[l - 3] <= 3 and D(int2base(d[0] - d[l - 3], g)) != 0:
				return [g - 1], [d[l - 3] + 1], [D(int2base(d[0] - d[l - 3], g))], 5

			# A.6)
			elif d[l - 3] <= 2 and D(int2base(d[0] - d[l - 3], g)) == 0:
				return [g - 1], [d[l - 3] + 2], [g - 1], 6

	def B(n: str, *k: int) -> (list, list, list, int):
		if n.startswith("102"):
			n = int2base(int(n, g) + k[0], g)

		d = list(reversed([int(i, g) for i in n]))
		l = len(n)
			

		if d[l - 1] == 1:
			if d[l - 2] <= 2:

				# Alg V
				if l % 2 == 0 and n.startswith("103"):
					if D(int2base(d[0] - d[l - 3], g)) != 0:
						return [1, d[l - 2]], [d[l - 3] - 1], [D(int2base(d[0] - d[l - 3], g))], 1
					else:
						return [1, d[l - 2]], [d[l - 3] - 2], [1], 2

				# B.1)
				if d[l - 3] >= 4 and D(int2base(d[0] - d[l - 3], g)) != 0:
					return [1, d[l - 2]], [d[l - 3] - 1], [D(int2base(d[0] - d[l - 3], g))], 1

				# B.2)
				elif d[l - 3] >= 3 and D(int2base(d[0] - d[l - 3], g)) == 0:
					return [1, d[l - 2]], [d[l - 3] - 2], [1], 2
			if d[l - 2] in [1, 2]:

				# B.3)
				if d[l - 3] in [0, 1] and d[0] == 0:
					return [1, d[l - 2] - 1], [g - 2], [1], 3

				# B.4)
				elif d[l - 3] in [2, 3] and d[0] == 0:
					return [1, d[l - 2]], [1], [g - 2], 4

				# B.5)
				elif d[l - 3] in [0, 1, 2] and d[0] != 0:
					return [1, d[l - 2] - 1], [g - 1], [d[0]], 5
				elif d[l - 3] == 3:

					# B.6)
					if D(int2base(d[0] - 3, g)) != 0:
						return [1, d[l - 2]], [2], [D(int2base(d[0] - 3, g))], 6

					# B.7)
					elif d[0] == 3:
						return [1, d[l - 2]], [1], [1], 7

	def alg1(n: str) -> list:
		d = list(reversed([int(i, g) for i in n]))
		l = len(n)
		m = (l - 1) // 2

		# Step 1
		x, y, z, Type = A(n)
		x.insert(0, 0)
		y.insert(0, 0)
		z.insert(0, 0)
		c = [0, (x[1] + y[1] + z[1]) // g]

		# Step 2
		if z[1] <= d[2 * m - 2] - 1:
			x.append(D(int2base(d[2 * m - 1] - y[1], g)))
		else:
			x.append(D(int2base(d[2 * m - 1] - y[1] - 1, g)))
		y.append(D(int2base(d[2 * m - 2] - z[1] - 1, g)))
		z.append(D(int2base(d[1] - x[2] - y[2] - c[1], g)))
		c.append((x[2] + y[2] + z[2] + c[1] - d[1]) // g)

		# Step i, 3 <= i <= m:
		for i in range(3, m + 1):
			if z[i - 1] <= d[2 * m - i] - 1:
				x.append(1)
			else:
				x.append(0)
			y.append(D(int2base(d[2 * m - i] - z[i - 1] - 1, g)))
			z.append(D(int2base(d[i - 1] - x[i] - y[i] - c[i - 1], g)))
			c.append((x[i] + y[i] + z[i] + c[i - 1] - d[i - 1]) // g)

		# Step m + 1
		x.append(0)

		temp = [sum(x[a + 1] * g ** a for a in range(m)) + sum(x[b + 1] * g ** (2 * m - b) for b in range(m)), sum(y[f + 1] * g ** f for f in range(m)) + sum(y[h + 1] * g ** (2 * m - h - 1) for h in range(m)), sum(z[i + 1] * g ** i for i in range(m)) + sum(z[j + 1] * g ** (2 * m - j - 2) for j in range(m - 1))]

		# Adjustment step

		# I.1
		if c[m] == 1:
			pass

		# I.2
		elif c[m] == 0:
			temp[0] += g ** m

		# I.3
		else:
			temp[0] += g ** m
			temp[1] -= (g ** m + g ** (m - 1))
			temp[2] -= (g - 1) * g ** (m - 1)

		return temp

	def alg2(n: str) -> list:
		d = list(reversed([int(i, g) for i in n]))
		l = len(n)
		m = l // 2

		# Step 1
		x, y, z, Type = A(n)
		x.insert(0, 0)
		y.insert(0, 0)
		z.insert(0, 0)
		c = [0, (x[1] + y[1] + z[1]) // g]

		# Step 2
		if z[1] <= d[2 * m - 3] - 1:
			x.append(D(int2base(d[2 * m - 2] - y[1], g)))
		else:
			x.append(D(int2base(d[2 * m - 2] - y[1] - 1, g)))
		y.append(D(int2base(d[2 * m - 3] - z[1] - 1, g)))
		z.append(D(int2base(d[1] - x[2] - y[2] - c[1], g)))
		c.append((x[2] + y[2] + z[2] + c[1] - d[1]) // g)

		# Step i, 3 <= i <= m - 1
		for i in range(3, m):
			if z[i - 1] <= d[2 * m - i - 1] - 1:
				x.append(1)
			else:
				x.append(0)
			y.append(D(int2base(d[2 * m - i - 1] - z[i - 1] - 1, g)))
			z.append(D(int2base(d[i - 1] - x[i] - y[i] - c[i - 1], g)))
			c.append((x[i] + y[i] + z[i] + c[i - 1] - d[i - 1]) // g)

		# Step m
		x.append(0)
		y.append(D(int2base(d[m - 1] - z[m - 1] - c[m - 1], g)))
		c.append((y[m] + z[m - 1] + c[m - 1] - d[m - 1]) // g)

		temp = [sum(x[a + 1] * g ** a for a in range(m - 1)) + sum(x[b + 1] * g ** (2 * m - b - 1) for b in range(m - 1)), sum(y[f + 1] * g ** f for f in range(m - 1)) + sum(y[h + 1] * g ** (2 * m - h - 2) for h in range(m)), sum(z[i + 1] * g ** i for i in range(m - 1)) + sum(z[j + 1] * g ** (2 * m - j - 3) for j in range(m - 1))]

		# Adjustment step

		# II.1
		if c[m] == 1:
			pass

		# II.2
		elif c[m] == 0:
			# II.2.i
			if y[m] != 0:
				temp[0] += (g ** m + g ** (m - 1))
				temp[1] -= g ** (m - 1)

			# II.2.ii
			else:

				# II.2.ii.a
				if y[m - 1] != 0:
					temp[0] += (g ** m + g ** (m - 1))
					temp[1] -= (g ** m - (g - 2) * g ** (m - 1) + g ** (m - 2))
					temp[2] += (g ** (m - 1) + g ** (m - 2))

				else:

					# II.2.ii.b
					if z[m - 1] != 0:
						temp[1] += (g ** m + g ** (m - 1) + g ** (m - 2))
						temp[2] -= (g ** (m - 1) + g ** (m - 2))

					# II.2.ii.c
					else:
						if c[m] == 0 and len(n) == 6:
							temp = [x[1] * g ** 5 + x[2] * g ** 4 + x[2] * g + x[1], y[1] * g ** 4 + y[1], z[1] * g ** 3 + z[1]]

							# Lemma 4.6 d[5] != 1
							if x[2] != 0:
								temp[0] -= (g ** 4 - (g - 1) * g ** 3 - (g - 1) * g ** 2 + g)
								temp[1] += (g ** 3 + g ** 2 + g)
							else:

								# Lemma 4.6.i d[5] != 1
								if x[1] == 1:
									temp = [2 * g ** 5 + 2, 1 * g + 1, g - 4]
								else:

									# Lemma 4.6.ii d[5] != 1
									if y[1] != g - 1:
										temp[0] -= (g ** 5 - (g - 1) * g ** 4 - (g - 1) * g + 1)
										temp[1] += (g ** 4 + (g - 2) * g ** 2 + 1)
										temp[2] += (g ** 2 + g)
									
									# Lemma 4.6.iii d[5] != 1
									if x[1] != g - 1 and z[1] == y[1] == g - 1:
										temp[0] += (g ** 5 + 1)
										temp[1] = (g + 1)
										temp[2] = (g - 4)
						else:
							temp[0] -= (g ** (m + 1) - g ** m - g ** (m - 1) + g ** (m - 2))
							temp[1] += ((g - 1) * g ** m + (g - 4) * g ** (m - 1) + (g - 1) * g ** (m - 2))
							temp[2] += (2 * g ** (m - 1) + 2 * g ** (m - 2))

		# II.3
		elif c[m] == 2:
			temp[0] += (g ** m + g ** (m - 1))
			temp[1] -= (g ** m + g ** (m - 1) + g ** (m - 2))
			temp[2] -= ((g - 1) * g ** (m - 1) + (g - 1) * g ** (m - 2))

		return temp

	def alg3(n: str) -> list:
		d = list(reversed([int(i, g) for i in n]))
		l = len(n)
		m = l // 2

		# Step 1
		x, y, z, Type = B(n)
		y.insert(0, 0)
		z.insert(0, 0)
		c = [0, (1 + y[1] + z[1]) // g]

		# Step 2
		if z[1] <= d[2 * m - 3] - 1:
			x.append(D(int2base(d[2 * m - 2] - y[1], g)))
		else:
			x.append(D(int2base(d[2 * m - 2] - y[1] - 1, g)))
		y.append(D(int2base(d[2 * m - 3] - z[1] - 1, g)))
		z.append(D(int2base(d[1] - x[1] - y[2] - c[1], g)))
		c.append((x[1] + y[2] + z[2] + c[1] - d[1]) // g)

		# Step i, 3 <= i <= m - 1
		for i in range(3, m):
			if z[i - 1] <= d[2 * m - i - 1] - 1:
				x.append(1)
			else:
				x.append(0)
			y.append(D(int2base(d[2 * m - i - 1] - z[i - 1] - 1, g)))
			z.append(D(int2base(d[i - 1] - x[i - 1] - y[i] - c[i - 1], g)))
			c.append((x[i - 1] + y[i] + z[i] + c[i - 1] - d[i - 1]) // g)

		# Step m
		y.append(D(int2base(d[m - 1] - z[m - 1] - x[m - 1] - c[m - 1], g)))
		c.append((x[m - 1] + y[m] + z[m - 1] + c[m - 1] - d[m - 1]) // g)

		temp = [sum(x[a] * g ** a for a in range(m)) + sum(x[b] * g ** (2 * m - b) for b in range(m)), sum(y[f + 1] * g ** f for f in range(m - 1)) + sum(y[h + 1] * g ** (2 * m - h - 2) for h in range(m)), sum(z[i + 1] * g ** i for i in range(m - 1)) + sum(z[j + 1] * g ** (2 * m - j - 3) for j in range(m - 1))]
		
		# Adjustment Step

		# III.1
		if c[m] == 1:
			pass
		
		# III.2
		elif c[m] == 0:
			temp[0] += g ** m
		
		# III.3
		elif c[m] == 2:

			if y[m - 1] != 0:

				# III.3.i
				if z[m - 1] != g - 1:
					temp[1] -= (g ** m + g ** (m - 1) + g ** (m - 2))
					temp[2] += (g ** (m - 1) + g ** (m - 2))
				
				# III.3.ii
				else:
					temp[0] += g ** m
					temp[1] -= (g ** m + g ** (m - 2))
					temp[2] -= ((g - 1) * g ** (m - 1) + (g - 1) * g ** (m - 2))
			else:

				# III.3.iii
				if z[m - 1] != g - 1:
					temp[0] -= (g ** (m + 1) + g ** (m - 1))
					temp[1] += ((g - 1) * g ** m - g ** (m - 1) + (g - 1) * g ** (m - 2))
					temp[2] += (g ** (m - 1) + g ** (m - 2))
				
				# III.3.iv
				else:
					temp[0] -= (g ** (m + 1) - g ** m + g ** (m - 1))
					temp[1] += ((g - 1) * g ** m + (g - 1) * g ** (m - 2))
					temp[2] -= ((g - 1) * g ** (m - 1) + (g - 1) * g ** (m - 2))

		return temp

	def alg4(n: str, *k: int) -> list:
		d = list(reversed([int(i, g) for i in n]))
		l = len(n)
		m = l // 2

		# Step 1
		if k:
			x, y, z, Type = B(n, k[0])
		else:
			x, y, z, Type = B(n)
		y.insert(0, 0)
		z.insert(0, 0)
		c = [0, (1 + y[1] + z[1]) // g]

		# Step 2
		if z[1] <= d[2 * m - 4] - 1:
			x.append(D(int2base(d[2 * m - 3] - y[1], g)))
		else:
			x.append(D(int2base(d[2 * m - 3] - y[1] - 1, g)))
		y.append(D(int2base(d[2 * m - 4] - z[1] - 1, g)))
		z.append(D(int2base(d[1] - x[1] - y[2] - c[1], g)))
		c.append((x[1] + y[2] + z[2] + c[1] - d[1]) // g)
		
		# Step i, 3 <= i <= m - 2
		for i in range(3, m - 1):
			if z[i - 1] <= d[2 * m - i - 2] - 1:
				x.append(1)
			else:
				x.append(0)
			y.append(D(int2base(d[2 * m - i - 2] - z[i - 1] - 1, g)))
			z.append(D(int2base(d[i - 1] - x[i - 1] - y[i] - c[i - 1], g)))
			c.append((x[i - 1] + y[i] + z[i] + c[i - 1] - d[i - 1]) // g)
		if z[m - 2] <= d[m - 1] - 1:
			x.append(1)
		else:
			x.append(0)
		
		# Step m - 1
		y.append(D(int2base(d[m - 1] - z[m - 2] - 1, g)))
		z.append(D(int2base(d[m - 2] - x[m - 2] - y[m - 1] - c[m - 2], g)))
		c.append((x[m - 2] + y[m - 1] + z[m - 1] + c[m - 2] - d[m - 2]) // g)

		temp = [sum(x[a] * g ** a for a in range(m)) + sum(x[b] * g ** (2 * m - b - 1) for b in range(m)), sum(y[f + 1] * g ** f for f in range(m - 1)) + sum(y[h + 1] * g ** (2 * m - h - 3) for h in range(m - 1)), sum(z[i + 1] * g ** i for i in range(m - 2)) + sum(z[j + 1] * g ** (2 * m - j - 4) for j in range(m - 1))]

		# Adjustment Step

		# IV.1
		if x[m - 1] + c[m - 1] == 1:
			pass
		
		elif x[m - 1] + c[m - 1] == 0:
			# IV.2
			if y[m - 1] != g - 1:

				# IV.2.i
				if z[m - 1] != 0:
					temp[1] += (g ** (m - 1) + g ** (m - 2))
					temp[2] -= g ** (m - 2)
				else:

					# IV.2.ii
					if y[m - 2] != 0:
						if y[m - 1] != 1:

							# IV.2.ii.a
							if z[m - 2] != g - 1:
								temp[0] += (g ** m + g ** (m - 1))
								temp[1] -= (g ** m + g ** (m - 1) + g ** (m - 2) + g ** (m - 3))
								temp[2] += (g ** (m - 1) + g ** (m - 2) + g ** (m - 3))
							
							# IV.2.ii.b
							else:
								temp[0] += (2 * g ** m + 2 * g ** (m - 1))
								temp[1] -= (g ** m + 2 * g ** (m - 1) + 2 * g ** (m - 2) + g ** (m - 3))
								temp[2] -= ((g - 1) * g ** (m - 1) - 3 * g ** (m - 2) + (g - 1) * g ** (m - 3))
						
						# IV.2.ii.c
						else:
							temp[0] += (g ** m + g ** (m - 1))
							temp[1] -= (g ** m - (g - 2) * g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
							temp[2] -= ((g - 1) * g ** (m - 1) - 3 * g ** (m - 2) + (g - 1) * g ** (m - 3))
					
					# IV.2.iii
					else:

						# IV.2.iii.a
						if z[m - 2] != g - 1:
							temp[0] -= (g ** (m + 1) - g ** m - g ** (m - 1) + g ** (m - 2))
							temp[1] += ((g - 1) * g ** m - g ** (m - 1) - g ** (m - 2) + (g - 1) * g ** (m - 3))
							temp[2] += (g ** (m - 1) + g ** (m - 2) + g ** (m - 3))
						else:

							# IV.2.iii.b
							if y[m - 1] != 1:
								temp[0] -= (g ** (m + 1) - 2 * g ** m - 2 * g ** (m - 1) + g ** (m - 2))
								temp[1] += ((g - 1) * g ** m - 2 * g ** (m - 1) - 2 * g ** (m - 2) + (g - 1) * g ** (m - 3))
								temp[2] -= ((g - 1) * g ** (m - 1) - 3 * g ** (m - 2) + (g - 1) * g ** (m - 3))
							
							# IV.2.iii.c
							else:
								temp[0] -= (g ** (m + 1) - g ** m - g ** (m - 1) + g ** (m - 2))
								temp[1] += ((g - 1) * g ** m + (g - 2) * g ** (m - 1) + (g - 2) * g ** (m - 2) + (g - 1) * g ** (m - 3))
								temp[2] -= ((g - 1) * g ** (m - 1) - 3 * g ** (m - 2) + (g - 1) * g ** (m - 3))
			
			# IV.3
			else:
				temp[0] += (g ** m + g ** (m - 1))
				temp[1] -= (g ** m + g ** (m - 1) + g ** (m - 2) + g ** (m - 3))
				temp[2] += (g ** (m - 1) + g ** (m - 2) + g ** (m - 3))
		
		# IV.4
		elif x[m - 1] == 0 and c[m - 1] == 2:
			
			# IV.4.i
			if z[m - 1] != g - 1:
				temp[1] -= (g ** (m - 1) + g ** (m - 2))
				temp[2] += g ** (m - 2)
			
			# IV.4.ii
			elif z[m - 2] != g - 1:

				# IV.4.ii.a
				if y[m - 2] != 0:
					temp[0] += (g ** m + g ** (m - 1))
					temp[1] -= (g ** m + 2 * g ** (m - 1) + 2 * g ** (m - 2) + g ** (m - 3))
					temp[2] += (g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
				
				# IV.4.ii.b
				else:
					temp[0] -= (g ** (m + 1) - g ** m - g ** (m - 1) + g ** (m - 2))
					temp[1] += ((g - 1) * g ** m - 2 * g ** (m - 1) - 2 * g ** (m - 2) + (g - 1) * g ** (m - 3))
					temp[2] += (g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
			
			# IV.4.iii
			else:

				# IV.4.iii.a
				if y[m - 1] not in [g - 1, g - 2]:
					if y[m - 2] != g - 1:
						temp[0] -= (g ** (m + 1) - (g - 2) * g ** m - (g - 2) * g ** (m - 1) + g ** (m - 2))
						temp[1] += (g ** m + 2 * g ** (m - 1) + 2 * g ** (m - 2) + g ** (m - 3))
						temp[2] -= (g ** (m - 1) + g ** (m - 2) + g ** (m - 3))
					else:
						temp[0] += ((g - 2) * g ** m + (g - 2) * g ** (m - 1))
						temp[1] -= ((g - 1) * g ** m - 2 * g ** (m - 1) - 2 * g ** (m - 2) + (g - 1) * g ** (m - 3))
						temp[2] -= (g ** (m - 1) + g ** (m - 2) + g ** (m - 3))
				
				# IV.4.iii.b
				else:
					if y[m - 2] >= 1:
						temp[0] += (2 * g ** m + 2 * g ** (m - 1))
						temp[1] -= (g ** m + 3 * g ** (m - 1) + 3 * g ** (m - 2) + g ** (m - 3))
						temp[2] -= ((g - 1) * g ** (m - 1) + (g - 4) * g ** (m - 2) + (g - 1) * g ** (m - 3))
					elif x[m - 2] >= 1:
						temp[0] -= (g ** (m + 1) - 2 * g ** m - 2 * g ** (m - 1) + g ** (m - 2))
						temp[1] += ((g - 1) * g ** m - 3 * g ** (m - 1) - 3 * g ** (m - 2) + (g - 1) * g ** (m - 3))
						temp[2] -= ((g - 1) * g ** (m - 1) + (g - 4) * g ** (m - 2) + (g - 1) * g ** (m - 3))
		
		# IV.5
		elif x[m - 1] == 1 and c[m - 1] == 1:
			if z[m - 1] != g - 1:

				# IV.5.i
				if y[m - 1] != 0:
					temp[1] -= (g ** (m - 1) + g ** (m - 2))
					temp[2] += g ** (m - 2)
				
				# IV.5.ii
				else:
					temp[0] -= (g ** m + g ** (m - 1))
					temp[1] += ((g - 1) * g ** (m - 1) + (g - 1) * g ** (m - 2))
					temp[2] += g ** (m - 2)
			else:

				# IV.5.iii
				if z[m - 2] != 0:

					# IV.5.iii.a
					if y[m - 2] != g - 1:
						temp[0] -= (g ** m + g ** (m - 1))
						temp[1] += (g ** m + g ** (m - 1) + g ** (m - 2) + g ** (m - 3))
						temp[2] -= (g ** (m - 1) + g ** (m - 2) + g ** (m - 3))
					else:

						# IV.5.iii.b
						if y[m - 1] not in [0, 1]:
							temp[0] += (g ** m + g ** (m - 1))
							temp[1] -= (g ** m + 2 * g ** (m - 1) + 2 * g ** (m - 2) + g ** (m - 3))
							temp[2] += (g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
						
						# IV.5.iii.c
						elif y[m - 1] == 0:
							temp[1] -= (g ** m - (g - 2) * g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
							temp[2] += (g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
						
						# IV.5.iii.d
						else:
							temp[1] -= (g ** m - (g - 2) * g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
							temp[2] += (g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
				else:

					# IV.5.iv
					if y[m - 2] != 0:

						# IV.5.iv.a
						if y[m - 1] not in [0, 1]:
							temp[0] += (g ** m + g ** (m - 1))
							temp[1] -= (g ** m + 2 * g ** (m - 1) + 2 * g ** (m - 2) + g ** (m - 3))
							temp[2] += (g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
						
						# IV.5.iv.b
						elif y[m - 1] == 0:
							temp[1] -= (g ** m - (g - 2) * g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
							temp[2] += (g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
						
						# IV.5.iv.c
						else:
							temp[1] -= (g ** m - (g - 2) * g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
							temp[2] += (g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
					
					# IV.5.v
					else:

						# IV.5.v.a
						if y[m - 1] not in [0, 1]:
							temp[0] -= (g ** (m + 1) - g ** m - g ** (m - 1) + g ** (m - 2))
							temp[1] += ((g - 1) * g ** m - 2 * g ** (m - 1) - 2 * g ** (m - 2) + (g - 1) * g ** (m - 3))
							temp[2] += (g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
						
						# IV.5.v.b
						elif y[m - 1] == 0:
							temp[0] -= (g ** (m + 1) + g ** (m - 2))
							temp[1] += ((g - 1) * g ** m + (g - 2) * g ** (m - 1) + (g - 2) * g ** (m - 2) + (g - 1) * g ** (m - 3))
							temp[2] += (g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
						
						# IV.5.v.c
						else:
							temp[0] -= (g ** (m + 1) + g ** (m - 2))
							temp[1] += ((g - 1) * g ** m + (g - 2) * g ** (m - 1) + (g - 2) * g ** (m - 2) + (g - 1) * g ** (m - 3))
							temp[2] += (g ** (m - 1) - (g - 2) * g ** (m - 2) + g ** (m - 3))
		
		# IV.6
		elif x[m - 1] == 1 and c[m - 1] == 2:
			temp[1] -= (g ** (m - 1) + g ** (m - 2))
			temp[2] -= ((g - 1) * g ** (m - 2))
		
		return temp

	def alg5(n: str) -> list:
		s = (g ** m + g ** (m - 1))
		n1 = int2base(int(n, g) - s, g)
		d1 = list(reversed([int(i, g) for i in n1]))

		if d1[m - 1] != 0 and d1[m]!= 0:
			k = s
		else:
			n1 = int2base(int(n, g) - 2 * s, g)
			k = 2 * s

		# i
		if not(n.startswith("104") and n1.startswith("103")) and not(n.startswith("103") and n1.startswith("102")):
			if A(n1):
				p1 = alg2(n1)
			elif B(n1):
				p1 = alg4(n1)

			p1[0] += k
			return p1
		
		# ii
		else:
			p1 = alg4(n1, k)
			p1[0] += k
			return p1

	try:
		int(n, g)
	except ValueError:
		return "Please input a valid positive integer."

	d = list(reversed([int(i, g) for i in n]))
	l = len(n)
	m = l // 2

	if l >= 7:

		# 2.3
		if l % 2 == 0:
			if A(n):
				x, y, z, Type = A(n)
				if Type >= 5:
					return [int2base(i, g) for i in alg1(n)]
				elif d[m] != 0 and d[m - 1] != 0:
					return [int2base(i, g) for i in alg2(n)]
				else:
					return [int2base(i, g) for i in alg5(n)]
			elif B(n) and d[m] != 0 and d[m - 1] != 0:
				return [int2base(i, g) for i in alg4(n)]
			else:
				return [int2base(i, g) for i in alg5(n)]
		else:
			if A(n):
				x, y, z, Type = A(n)
				if Type <= 4:
					return [int2base(i, g) for i in alg1(n)]
				elif d[m] != 0 and d[m - 1] != 0:
					return [int2base(i, g) for i in alg2(n)]
				else:
					return [int2base(i, g) for i in alg5(n)]
			elif B(n):
				return [int2base(i, g) for i in alg3(n)]
	else:
		if l == 1:
			return [n]
		
		# Lemma 4.2
		elif l == 2:
			if d[1] <= d[0]:
				return [int2base(i, g) for i in [d[1] * g + d[1], d[0] - d[1]]]
			elif d[1] > d[0] + 1:
				return [int2base(i, g) for i in [(d[1] - 1) * g + (d[1] - 1), g + d[0] - d[1] + 1]]
			elif d[1] == d[0] + 1 and d[0] >= 1:
				return [int2base(i, g) for i in [d[0] * g + d[0], g - 1, 1]]
			else:
				return [int2base(i, g) for i in [g - 1, 1]]
		
		# Lemma 4.3
		elif l == 3:
			if d[2] <= d[0]:
				return [int2base(i, g) for i in [d[2] * g ** 2 + d[1] * g + d[2] * 1, d[0] - d[2]]]
			elif d[2] >= d[0] + 1 and d[1] != 0:
				return [int2base(i, g) for i in [d[2] * g ** 2 + (d[1] - 1) * g + d[2], g + d[0] - d[2]]]
			elif d[2] >= d[0] + 1 and d[1] == 0 and D(int2base(d[2] - d[0] - 1, g)) != 0:
				return [int2base(i, g) for i in [(d[2] - 1) * g ** 2 + (g - 1) * g + (d[2] - 1), g + d[0] - d[2] + 1]]
			else:
				if d[2] >= 3:
					return [int2base(i, g) for i in [(d[2] - 2) * g ** 2 + (g - 1) * g + (d[2] - 2), 1 * g ** 2 + 1 * g + 1]]
				elif d[2] == 2:
					return [int2base(i, g) for i in [1 * g ** 2 + 1, (g - 1) * g + (g - 1), 1]]
				else:
					return [int2base(i, g) for i in [(g - 1) * g + (g - 1), 1]]

		# Lemma 4.4
		elif l == 4:

			# i
			if int(n, g) >= d[3] * g ** 3 + d[3] and (int(n, g) - (d[3] * g ** 3 + d[3]) != (2 * g ** 2 + 1) or ((int(n, g) - (d[3] * g ** 3 + d[3])) // g - 1 != D(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g)) and D(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g)) >= 1)):
				return [int2base(i, g) for i in [d[3] * g ** 3 + d[3]]] + sum_of_three_palindromes(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g), g)
			
			# ii
			elif int(n, g) - (d[3] * g ** 3 + d[3]) == (2 * g ** 2 + 1):
				if d[3] != 1 and d[3] != g - 1:
					return [int2base(i, g) for i in [(d[3] - 1) * g ** 3 + (g - 1) * g ** 2 + (g - 1) * g + (d[3] - 1), 2 * g ** 2 + 1 * g + 2]]
				elif d[3] == 1:
					return [int2base(i, g) for i in [1 * g ** 3 + 1 * g ** 2 + 1 * g + 1, (g - 2) * g + (g - 2), 3]]
				elif d[3] == g - 1:
					return [int2base(i, g) for i in [(g - 1) * g ** 3 + 1 * g ** 2 + 1 * g + (g - 1), (g - 2) * g + (g - 2), 3]]
			
			# iii
			elif (int(n, g) - (d[3] * g ** 3 + d[3])) // g - 1 == D(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g)) and 1 <= D(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g)) <= g - 2:

				# a
				if d[3] + D(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g)) == d[0]:
					if d[3] != 1:
						return [int2base(i, g) for i in [(d[3] - 1) * g ** 3 + (g - 2) * g ** 2 + (g - 2) * g + (d[3] - 1), 1 * g ** 2 + 3 * g + 1, D(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g)) * g + D(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g))]]
					else:
						return [int2base(i, g) for i in [(g - 1) * g ** 2 + (g - 1) * g + (g - 1), (D(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g)) + 1) * g + (D(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g)) + 1), 1]]

				# b
				elif d[3] + D(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g)) == g + d[0] and d[0] <= g - 1:
					return [int2base(i, g) for i in [(d[3] - 1) * g ** 3 + (g - 2) * g ** 2 + (g - 2) * g + (d[3] - 1), 1 * g ** 2 + 3 * g + 1, (D(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g))) * g + (D(int2base(int(n, g) - (d[3] * g ** 3 + d[3]), g)))]]
			
			# iv
			elif int(n, g) - d[3] * g ** 3 <= d[3] - 1 and d[3] != 1:
				return [int2base(i, g) for i in [(d[3] - 1) * g ** 3 + (g - 1) * g ** 2 + (g - 1) * g + (d[3] - 1), g + d[0] - d[3], 1]]
			
			# v
			else:
				return [int2base(i, g) for i in [(g - 1) * g ** 2 + (g - 1) * g + (g - 1), 1]]
		
		# Lemma 4.5
		elif l == 5:
			if d[4] != 1:
				return [int2base(i, g) for i in alg1(n)]
			else:

				# i
				if int(n, g) >= 1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1 and (int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1) != 2 * g ** 2 + 1 or (int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1)) // g - 1 != D(int2base(int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1), g))):
					return [int2base(i, g) for i in [1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1]] + sum_of_three_palindromes(int2base(int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1), g), g)
				
				# ii
				elif int(n, g) == (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1) + (2 * g ** 2 + 1):
					return [int2base(i, g) for i in [1 * g ** 4 + d[3] * g ** 3 + 1 * g ** 2 + d[3] * g + 1, 1 * g ** 2 + 1]]
				
				elif (int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1)) // g - 1 == D(int2base(int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1), g)) and 1 <= D(int2base(int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1), g)) <= g - 2:

					# iii
					if d[3] != 0:

						# a
						if D(int2base(int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1), g)) + 1 + d[3] <= g - 1:
							return [int2base(i, g) for i in [1 * g ** 4 + (d[3] - 1) * g ** 3 + 1 * g ** 2 + (d[3] - 1) * g + 1, (g - 1) * g ** 2 + (D(int2base(int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1), g)) + 1) * g + (g - 1), (D(int2base(int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1), g)) + 1)]]
						
						# b
						elif d[3] + 1 + D(int2base(int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1), g)) == g + d[1] and 0 <= d[1] <= g - 1:
							return [int2base(i, g) for i in [1 * g ** 4 + (d[3] - 1) * g ** 3 + 1 * g ** 2 + (d[3] - 1) * g + 1, (g - 1) * g ** 2 + (D(int2base(int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1), g)) + 1) * g + (g - 1), (D(int2base(int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1), g)) + 1)]]
					
					# iv
					else:
						return [int2base(i, g) for i in [(g - 1) * g ** 3 + (g - 1) * g ** 2 + (g - 1) * g + (g - 1), (D(int2base(int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1), g)) + 1) * g + (D(int2base(int(n, g) - (1 * g ** 4 + d[3] * g ** 3 + d[3] * g + 1), g)) + 1), 1]]
				elif int(n, g) <= 1 * g ** 4 + d[3] * g ** 3 + d[3] * g:

					# v
					if d[3] == 0:
						return [int2base(i, g) for i in [(g - 1) * g ** 3 + (g - 1) * g ** 2 + (g - 1) * g + (g - 1), 1]]
					
					# vi
					elif int(n, g) - (1 * g ** 4 + (d[3] - 1) * g ** 3 + (g - 1) * g ** 2 + (d[3] - 1) * g + 1) != 2 * g ** 2 + 1 and int(n, g) - (1 * g ** 4 + (d[3] - 1) * g ** 3 + (g - 1) * g ** 2 + (d[3] - 1) * g + 1) not in [(i + 1) * g + i for i in range(1, g - 1)]:
						return [int2base(i, g) for i in [1 * g ** 4 + (d[3] - 1) * g ** 3 + (g - 1) * g ** 2 + (d[3] - 1) * g + 1]] + sum_of_three_palindromes(int2base(int(n, g) - (1 * g ** 4 + (d[3] - 1) * g ** 3 + (g - 1) * g ** 2 + (d[3] - 1) * g + 1), g), g)
					
					# vii
					else:
						return [int2base(i, g) for i in [1 * g ** 4 + (d[3] - 1) * g ** 3 + (g - 2) * g ** 2 + (d[3] - 1) * g + 1, 1 * g ** 2 + (D(int2base(int(n, g) - (1 * g ** 4 + (d[3] - 1) * g ** 3 + (g - 1) * g ** 2 + (d[3] - 1) * g + 1), g)) + 1) * g + 1, (D(int2base(int(n, g) - (1 * g ** 4 + (d[3] - 1) * g ** 3 + (g - 1) * g ** 2 + (d[3] - 1) * g + 1), g)) - 1)]]
		
		# Lemma 4.6
		elif l == 6:
			if d[5] != 1:
				return [int2base(i, g) for i in alg2(n)]
			else:

				# Lemma 4.6.i d[5] == 1
				if D(int2base(d[0] - d[4] + 1, g)) != 0 and D(int2base(d[0] - d[4] + 2, g)) != 0:
					a = random.choice([i for i in combinations_with_replacement(range(1, g), 2) if sum(i) == g + d[4] - 1])
					x1 = a[0]
					y1 = a[1]
					z1 = D(int2base(d[0] - d[4] + 1, g))
					c1 = (x1 + y1 + z1 - d[0]) // g
					b = random.choice([i for i in combinations_with_replacement(range(g), 2) if sum(i) == g + d[3] - 1])
					x2 = b[0]
					y2 = b[1]
					z2 = D(int2base(d[1] - x2 - y2 - c1, g))
					c2 = (x2 + y2 + z2 + c1 - d[1]) // g
					f = random.choice([i for i in combinations_with_replacement(range(0, g), 2) if sum(i) == g + d[2] - c2 - z1])
					x3 = f[0]
					y3 = f[1]
					return [int2base(i, g) for i in [x1 * g ** 4 + x2 * g ** 3 + x3 * g ** 2 + x2 * g + x1, y1 * g ** 4 + y2 * g ** 3 + y3 * g ** 2 + y2 * g + y1, z1 * g ** 2 + z2 * g + z1]]

				# Lemma 4.6.ii d[5] == 1
				elif D(int2base(d[0] - d[4] + 2, g)) == 0 and d[2] != 0:
					a = random.choice([i for i in combinations_with_replacement(range(1, g), 2) if sum(i) == g + d[4] - 1])
					x1 = a[0]
					y1 = a[1]
					z1 = g - 1
					c1 = (x1 + y1 + z1 - d[0]) // g
					b = random.choice([i for i in combinations_with_replacement(range(g), 2) if sum(i) == g + d[3] - 1])
					x2 = b[0]
					y2 = b[1]
					z2 = D(int2base(d[1] - x2 - y2 - c1, g))
					c2 = (x2 + y2 + z2 + c1 - d[1]) // g
					f = random.choice([i for i in combinations_with_replacement(range(0, g), 2) if sum(i) == g + d[2] - c2 - z1])
					x3 = f[0]
					y3 = f[1]
					return [int2base(i, g) for i in [x1 * g ** 4 + x2 * g ** 3 + x3 * g ** 2 + x2 * g + x1, y1 * g ** 4 + y2 * g ** 3 + y3 * g ** 2 + y2 * g + y1, z1 * g ** 2 + z2 * g + z1]]

				# Lemma 4.6.iii d[5] == 1
				elif D(int2base(d[0] - d[4] + 2, g)) == 0 and d[2] == 0:
					if d[4] == 0 or d[4] == 1:

						# Lemma 4.6.iii.a d[5] == 1
						if d[4] == 0:
							x1 = g - 2
						
						# Lemma 4.6.iii.b d[5] == 1
						elif d[4] == 1:
							x1 = g - 1
						y1 = 1
						z1 = g - 1
						c1 = (x1 + y1 + z1 - d[0]) // g
						a = random.choice([i for i in combinations_with_replacement(range(g), 2) if sum(i) == d[3]])
						x2 = a[0]
						y2 = a[1]
						z2 = D(int2base(d[1] - x2 - y2 - c1, g))
						c2 = (x2 + y2 + z2 + c1 - d[1]) // g
						b = random.choice([i for i in combinations_with_replacement(range(0, g), 2) if sum(i) == g - c2 - z2])
						x3 = b[0]
						y3 = b[1]
						return [int2base(i, g) for i in [x1 * g ** 4 + x2 * g ** 3 + x3 * g ** 2 + x2 * g + x1, y1 * g ** 4 + y2 * g ** 3 + y3 * g ** 2 + y2 * g + y1, z1 * g ** 3 + z2 * g ** 2 + z2 * g + z1]]

					# Lemma 4.6.iii.c d[5] == 1
					elif d[4] == 2:
						x1 = g - 1
						y1 = 2
						z1 = g - 1
						c1 = (x1 + y1 + z1 - d[0]) // g
						a = random.choice([i for i in combinations_with_replacement(range(g), 2) if sum(i) == d[3]])
						x2 = a[0]
						y2 = a[1]
						z2 = D(int2base(d[1] - x2 - y2 - c1, g))
						c2 = (x2 + y2 + z2 + c1 - d[1]) // g
						if c2 != 2:
							b = random.choice([i for i in combinations_with_replacement(range(0, g), 2) if sum(i) == g - c2 - z2])
							x3 = b[0]
							y3 = b[1]
							return [int2base(i, g) for i in [x1 * g ** 4 + x2 * g ** 3 + x3 * g ** 2 + x2 * g + x1, y1 * g ** 4 + y2 * g ** 3 + y3 * g ** 2 + y2 * g + y1, z1 * g ** 3 + z2 * g ** 2 + z2 * g + z1]]
						else:
							return [int2base(i, g) for i in [g ** 5 + 2 * g ** 4 + (g - 2) * g ** 3 + (g - 2) * g ** 2 + 2 * g + 1, 1 * g ** 2 + (g - 3) * g + 1, g - 2]]
					
					# Lemma 4.6.iii.d d[5] == 1
					elif d[4] >= 3:
						c4 = (D(int2base(d[3] - 1, g)) + 1 - d[3]) // g
						z = D(int2base(d[1] - d[3] - 1 + c4, g))
						c2 = (2 - c4 + D(int2base(d[3] - 1, g)) + z - d[1]) // g
						return [int2base(i, g) for i in [g ** 5 + (1 - c4) * g ** 4 + (1 - c4) * g + 1, (d[4] - 1) * g ** 4 + D(int2base(d[3] - 1, g)) * g ** 3 + (2 - c2) * g ** 2 + D(int2base(d[3] - 1, g)) * g + (d[4] - 1), (g - 2) * g ** 2 + z * g + (g - 2)]]
				
				# Lemma 4.6.iv d[5] == 1
				elif D(int2base(d[0] - d[4] + 1, g)) == 0 and d[3] != 0:
					
					# Lemma 4.6.iv.a d[5] == 1
					if d[4] != g - 1:
						a = random.choice([i for i in combinations_with_replacement(range(1, g), 2) if sum(i) == g + d[4]])
						x1 = a[0]
						y1 = a[1]
						z1 = g - 1
						c1 = (x1 + y1 + z1 - d[0]) // g
						b = random.choice([i for i in combinations_with_replacement(range(g), 2) if sum(i) == d[3] - 1])
						x2 = b[0]
						y2 = b[1]
						z2 = D(int2base(d[1] - x2 - y2 - c1, g))
						c2 = (x2 + y2 + z2 + c1 - d[1]) // g
						f = random.choice([i for i in combinations_with_replacement(range(g), 2) if sum(i) == g + d[2] - c2 - z1])
						x3 = f[0]
						y3 = f[1]
						return [int2base(i, g) for i in [x1 * g ** 4 + x2 * g ** 3 + x3 * g ** 2 + x2 * g + x1, y1 * g ** 4 + y2 * g ** 3 + y3 * g ** 2 + y2 * g + y1, z1 * g ** 2 + z2 * g + z1]]
					
					# Lemma 4.6.iv.b d[5] == 1
					else:
						a = reversed([i for i in combinations_with_replacement(range(g), 2) if D(int2base(sum(i), g)) == d[3]])
						for j in a:
							if j[1] >= 1 and D(int2base(d[1] - 3 - j[1], g)) not in [g - 2, g - 1]:
								x = j[0]
								y = j[1]
						c1 = (3 + y + D(int2base(d[1] - 3 - y, g)) - d[1]) // g
						mu = 0
						c2 = (x + D(int2base(d[2] - x - 1 - c1 + mu, g)) + c1 + 1 - d[2]) // g
						if c2 in [0, 1]:
							pass
						else:
							mu = 1
							c2 = 1
						c3 = (x + (y - c2) + c2 - d[3]) // g
						return [int2base(i, g) for i in [g ** 5 + (3 - c3) * g ** 4 + (x - mu) * g ** 3 + (x - mu) * g ** 2 + (3 - c3) * g + 1, (g - 4) * g ** 4 + (y - c2 + mu) * g ** 3 + D(int2base(d[2] - x - 1 - c1 + mu, g)) * g ** 2 + (y - c2 + mu) * g + (g - 4), g ** 2 + (D(int2base(d[1] - 3 - y, g)) + (c2 - mu) + c3) * g + 1]]
				
				# Lemma 4.6.v d[5] == 1
				elif D(int2base(d[0] - d[4] + 1, g)) == 0 and d[3] == 0:

					# Lemma 4.6.v.a d[5] == 1
					if d[4] == 0:
						if d[2] != 0:
							return [int2base(i, g) for i in [g ** 5 + 1]] + sum_of_three_palindromes(int2base(int(n, g) - (g ** 5 + 1), g), g)
						else:
							if d[1] not in [0, g - 1]:
								return [int2base(i, g) for i in [g ** 5 + 1]] + sum_of_three_palindromes(int2base(int(n, g) - (g ** 5 + 1), g), g)
							elif d[1] == 0:
								return [int2base(i, g) for i in [g ** 5 + 1, g - 2]]
							else:
								return [int2base(i, g) for i in [(g - 1) * g ** 4 + g ** 2 + (g - 1), (g - 1) * g ** 3 + (g - 2) * g ** 2 + (g - 2) * g + (g - 1), g ** 2 + 1]]
					
					# Lemma 4.6.v.b d[5] == 1
					elif d[4] == 1:
						if d[2] >= 2 or (d[2] == 1 and d[1] not in [0, 1]):
							return [int2base(i, g) for i in [g ** 5 + g ** 4 + g + 1]] + sum_of_three_palindromes(int2base(int(n, g) - (g ** 5 + g ** 4 + g + 1), g), g)
						elif d[2] == 1:
							if d[1] == 0:
								return [int2base(i, g) for i in [g ** 5 + (g - 1) * g ** 3 + (g - 1) * g ** 2 + 1, g ** 2 + (g - 1) * g + 1, (g - 2)]]
							elif d[1] == 1:
								return [int2base(i, g) for i in [g ** 5 + g ** 4 + g + 1, (g - 1) * g + (g - 1)]]
						else:
							if d[1] >= 2:
								return [int2base(i, g) for i in [g ** 5 + g ** 4 + g + 1, (d[1] - 2) * g + (d[1] - 2), (g - d[1] + 1)]]
							elif d[1] == 1:
								return [int2base(i, g) for i in [g ** 5 + 1, g ** 4 + 1, (g - 2)]]
							else:
								return [int2base(i, g) for i in [g ** 5 + 1, (g - 1) * g ** 3 + (g - 1) * g ** 2 + (g - 1) * g + (g - 1)]]
					
					# Lemma 4.6.v.c d[5] == 1
					elif d[4] == 2:
						if d[2] >= 2 or (d[2] == 1 and d[1] not in [0, 1]):
							return [int2base(i, g) for i in [g ** 5 + 2 * g ** 4 + 2 * g + 1]] + sum_of_three_palindromes(int2base(int(n, g) - (g ** 5 + 2 * g ** 4 + 2 * g + 1), g), g)
						elif d[2] == 1:
							if d[1] == 0:
								return [int2base(i, g) for i in [g ** 5 + g ** 4 + (g - 1) * g ** 3 + (g - 1) * g ** 2 + g + 1, g ** 2 + (g - 2) * g + 1, (g - 1)]]
							elif d[1] == 1:
								return [int2base(i, g) for i in [g ** 5 + g ** 4 + (g - 1) * g ** 3 + (g - 1) * g ** 2 + g + 1, g ** 2 + (g - 1) * g + 1, (g - 1)]]
						else:
							if d[1] >= 3:
								return [int2base(i, g) for i in [g ** 5 + 2 * g ** 4 + 2 * g + 1, (d[1] - 3) * g + (d[1] - 3), (g - d[1] + 3)]]
							elif d[1] == 2:
								return [int2base(i, g) for i in [g ** 5 + g ** 4 + (g - 1) * g ** 3 + (g - 1) * g ** 2 + g + 1, g ** 2 + 1, (g - 1)]]
							elif d[1] == 1:
								return [int2base(i, g) for i in [g ** 5 + 1, 2 * g ** 4 + 2, (g - 2)]]
							else:
								return [int2base(i, g) for i in [g ** 5 + g ** 4 + (g - 1) * g ** 3 + (g - 1) * g ** 2 + g + 1, (g - 2) * g + (g - 2), 2]]
					
					# Lemma 4.6.v.d d[5] == 1
					elif d[4] == 3:
						for i in range(1, g):
							if D(int2base(d[1] - 1 - i, g)) not in [0, g - 1]:
								y = i
								break
						c1 = (2 + y + D(int2base(d[1] - 1 - y, g)) - d[1]) // g
						c2 = (g - y - 1 + D(int2base(d[2] + y + 2, g)) + g - 1 - d[2]) // g
						return [int2base(i, g) for i in [g ** 5 + (g - y - 1 - c1) * g ** 3 + (g - y - 1 - c1) * g ** 2 + 1, 2 * g ** 4 + (y - c2 + 1 + c1) * g ** 3 + D(int2base(d[2] + y + 2, g)) * g ** 2 + (y - c2 + 1 + c1) * g + 2, (g - 1) * g ** 2 + (D(int2base(d[1] - 1 - y, g)) + (c2 - 1) - c1) * g + (g - 1)]]
					
					# Lemma 4.6.v.e d[5] == 1
					else:
						for i in range(1, g):
							if D(int2base(d[1] - 1 - i, g)) not in [0, g - 1]:
								y = i
								break
						c1 = (1 + y + D(int2base(d[1] - 1 - y, g)) - d[1]) // g
						c2 = (g - y + 1 + D(int2base(d[2] + y - 1, g)) - d[2]) // g
						return [int2base(i, g) for i in [g ** 5 + 2 * g ** 4 + (g - y - c1) * g ** 3 + (g - y - c1) * g ** 2 + 2 * g + 1, (d[4] - 3) * g ** 4 + (y - c2 + c1) * g ** 3 + D(int2base(d[2] + y - 1, g)) * g ** 2 + (y - c2 + c1) * g + (d[4] - 3), g ** 2 + (D(int2base(d[1] - 2 - y, g)) + c2 - c1) * g + 1]]


# testing
# try:
# 	# for g in range(5, 11):
# 		for n in range(10300000, 10500000):
# 			n = int2base(n, 10)
# 			# n = random.randint(10 ** 7, 10 ** 8)
# 			lst = sum_of_three_palindromes(str(n), 10)

# 			if int(n) != sum([int(j) for j in lst]):
# 				print(n, lst)
# 		# print(f"done base {g}")
# except Exception:
# 	traceback.print_exc()
# 	print(n, 10)

# print(sum_of_three_palindromes("10400003", 10))
# print(sum_of_three_palindromes("10300003", 10))

# print("done")