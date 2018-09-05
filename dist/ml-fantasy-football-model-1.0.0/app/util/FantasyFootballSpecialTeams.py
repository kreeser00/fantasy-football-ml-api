from app.constants.FantasyFootballConstants import FantasyFootballConstants as ffc

"""
Method to return a fantasy point calculation based on past kicking career stats
"""


def calc_past_special_teams_fantasy_value(career, year):
	result = 0
	for index, row in career.iterrows():
		# filter for the given season year
		# ex. the 2017 year is the 2017-2018 season
		if (8 <= row.date.month <= 12 and row.date.year == year) or \
			(1 <= row.date.month <= 2 and row.date.year == year + 1):
			# points from Kicking
			points_from_field_goals = \
				calc_special_teams_fantasy_value_by_kicks(row[ffc.STATS_KEY_OFF_KICK_FD_GL], ffc.STATS_VAL_OFF_KICK_FD_GL)
			result = result + points_from_field_goals
			points_from_extra_points = \
				calc_special_teams_fantasy_value_by_kicks(row[ffc.STATS_KEY_OFF_KICK_EX_PT], ffc.STATS_VAL_OFF_KICK_EX_PT)
			result = result + points_from_extra_points
	return result


"""
Method to return fantasy point calculations for a player's entire offensive career.
A career is a list of games.  This function returns a numpy array with an element
for every season in the player's career.
"""


def calc_past_special_teams_fantasy_values(career):
	seasons = list()
	first_year = -1
	last_year = -1
	for index, row in career.iterrows():
		if first_year == -1 or last_year == -1:
			first_year = int(row.date.year)
			last_year = int(row.date.year)
		else:
			if int(row.date.year) < first_year:
				first_year = int(row.date.year)
			if int(row.date.year) > last_year:
				last_year = int(row.date.year)

	if first_year == -1 or last_year == -1:
		return None

	# if(first_year >= 1990):

	for year in range(first_year, last_year+1, 1):
		fantasy_value_for_year = calc_past_special_teams_fantasy_value(career, year)
		seasons.append(fantasy_value_for_year)

	return seasons


"""
Method to return a fantasy point calculation based on pass, rush, or recv yards
"""


def calc_special_teams_fantasy_value_by_yards(yards, chart):
	result = 0
	rules = chart.split(",")
	for i in range(0, len(rules)):
		data = rules[i].split(":")
		threshold = int(data[0])
		value = int(data[1])
		if yards < threshold and i == 0:
			result = 0
			return result
		elif yards < threshold and i > 0:
			result = int(rules[i-1].split(":")[1])
			return result
		elif yards == threshold:
			result = value
			return result
	return result


"""
Method to return a fantasy point calculation based on any extra point or field goal.
By default 4 pts are awarded per field goal no matter the distance.
"""


def calc_special_teams_fantasy_value_by_kicks(kicks, kick_value):
	return kicks * kick_value
