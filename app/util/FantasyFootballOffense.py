from app.constants.FantasyFootballConstants import FantasyFootballConstants as ffc

"""
Method to return a fantasy point calculation based on past offensive career stats
"""


def calc_past_offensive_fantasy_value(career, year):
	result = 0
	for index, row in career.iterrows():
		# filter for the given season year
		# ex. the 2017 year is the 2017-2018 season
		if (8 <= row.date.month <= 12 and row.date.year == year) or \
				(1 <= row.date.month <= 2 and row.date.year == year + 1):
			# points from Passing
			points_from_pass_yds = \
				calc_offensive_fantasy_value_by_yards(row[ffc.STATS_KEY_OFF_PASS_YDS], ffc.STATS_VAL_OFF_PASS_YDS)
			result = result + points_from_pass_yds
			points_from_pass_tds = \
				calc_offensive_fantasy_value_by_tds(row[ffc.STATS_KEY_OFF_PASS_TD], ffc.STATS_VAL_OFF_PASS_TD)
			result = result + points_from_pass_tds
			points_from_pass_ints = \
				calc_offensive_fantasy_value_by_ints(row[ffc.STATS_KEY_OFF_PASS_INT], ffc.STATS_VAL_OFF_PASS_INT)
			result = result + points_from_pass_ints
			 
			# points from Rushing
			points_from_rush_yds = \
				calc_offensive_fantasy_value_by_yards(row[ffc.STATS_KEY_OFF_RUSH_YDS], ffc.STATS_VAL_OFF_RUSH_YDS)
			result = result + points_from_rush_yds
			points_from_rush_tds = \
				calc_offensive_fantasy_value_by_tds(row[ffc.STATS_KEY_OFF_RUSH_TD], ffc.STATS_VAL_OFF_RUSH_TD)
			result = result + points_from_rush_tds

			# points from Receiving
			points_from_recv_yds = \
				calc_offensive_fantasy_value_by_yards(row[ffc.STATS_KEY_OFF_RECV_YDS],ffc.STATS_VAL_OFF_RECV_YDS)
			result = result + points_from_recv_yds
			points_from_recv_tds = \
				calc_offensive_fantasy_value_by_tds(row[ffc.STATS_KEY_OFF_RECV_TD],ffc.STATS_VAL_OFF_RECV_TD)
			result = result + points_from_recv_tds

			# points from Kick Returns
			points_from_kick_return_yds = \
				calc_offensive_fantasy_value_by_yards(row[ffc.STATS_KEY_OFF_RTRN_YDS], ffc.STATS_VAL_OFF_RTRN_YDS)
			result = result + points_from_kick_return_yds
			points_from_kick_return_tds = \
				calc_offensive_fantasy_value_by_tds(row[ffc.STATS_KEY_OFF_RTRN_TD], ffc.STATS_VAL_OFF_RTRN_TD)
			result = result + points_from_kick_return_tds
	return result


"""
Method to return fantasy point calculations for a player's entire offensive career.
A career is a list of games.  This function returns a numpy array with an element
for every season in the player's career.
"""


def calc_past_offensive_fantasy_values(career):
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

	for year in range(first_year, last_year + 1, 1):
		fantasy_value_for_year = calc_past_offensive_fantasy_value(career, year)
		seasons.append(fantasy_value_for_year)

	return seasons


"""
Method to return a fantasy point calculation based on pass, rush, or recv yards
"""


def calc_offensive_fantasy_value_by_yards(yards, chart):
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
Method to return a fantasy point calculation based on any offensive TD.
By default 6 pts are awarded per TD no matter how the TD is scored.
"""


def calc_offensive_fantasy_value_by_tds(tds, td_value):
	return tds * td_value


"""
Method to return a fantasy point calculation for intercepted passes.
This intvalue is often a negative number.
"""


def calc_offensive_fantasy_value_by_ints(ints, int_value):
	return ints * int_value

