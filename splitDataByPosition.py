##################################################################
#
# splitDataByPosition.py
#
# Description: Take a large input file of games and split it into
#  train and test data sets by position
# Author: Ken Reeser
# Since: 2018-08-13
#
##################################################################

#!/usr/bin/python

import json
from sklearn.model_selection import train_test_split
import pandas as pd
#import numpy as np


def __filter_by_season(date):
    if 8 <= date.month <= 12:
        return date.year
    else:
        return date.year - 1


def main():

    # some initial setup
    all_profile_path = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\profiles_1534254607.3839095.json'
    all_games_path = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\games_1534254679.891445.json'
    games_train_path = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\games_train.json'
    profile_train_path = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\profile_train.json'
    games_test_path = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\games_test.json'
    profile_test_path = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\profile_test.json'
    first_year_dict_path = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\first_year_dict.json'
    games_last_season_path = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\games_last_season.json'

    # split the data into train and test sets
    profiles_df = pd.read_json(all_profile_path)
    # profiles_df.set_index('player_id', inplace=True)
    print("Splitting profile data into train and test sets.")
    train_profile_df, test_profile_df = train_test_split(profiles_df, test_size=0.4, random_state=42)

    # persist the split profile data to disk
    # train_profile_df.to_json(profile_train_path,date_format='iso')
    # test_profile_df.to_json(profile_test_path,date_format='iso')

    # find games corresponding to the position and train/test split
    games_df = pd.read_json(all_games_path)
    print("Dropping duplicate game data.")
    games_df.drop_duplicates(subset=['game_id', 'player_id'], inplace=True)

    print("Initializing first year dictionary.")
    first_year_dict = {}
    for player_id in games_df.player_id.unique():
        game_list = games_df.loc[games_df.player_id == player_id]
        player_id_str = str(player_id)
        if game_list is not None and len(game_list) > 0:
            for index, row in game_list.iterrows():
                if 8 <= row.date.month <= 12:
                    season_year = row.date.year
                else:
                    season_year = row.date.year - 1

                if first_year_dict.get(player_id_str) is None:
                    first_year_dict[player_id_str] = int(season_year)
                else:
                    if int(season_year) < first_year_dict.get(player_id_str):
                        first_year_dict[player_id_str] = int(season_year)

    print("Writing first year dictionary to file.")
    with open(first_year_dict_path, 'w') as fydf:
        fydf.write(json.dumps(first_year_dict))

    print("First year dictionary initialization complete.")

    print("Initializing games last season.")
    games_df['season'] = games_df['date'].apply(__filter_by_season)
    games_last_season = games_df.loc[games_df['season'] == 2017]

    print("Writing games last season to file.")
    games_last_season.to_json(games_last_season_path, date_format='iso')
    print("Games last season initialization complete.")

    print("Splitting game data into train and test sets.")
    train_games_df = games_df.loc[games_df.player_id.isin(train_profile_df.player_id)]
    # new_train_games_df = train_games_df.copy().set_index(['game_id', 'player_id'])
    test_games_df = games_df.loc[games_df.player_id.isin(test_profile_df.player_id)]
    # new_test_games_df = test_games_df.copy().set_index(['game_id', 'player_id'])
    # new_train_games_df.index.values.tofile("C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\new_train_games_df.txt", sep="\r\n")
    # new_test_games_df.index.values.tofile("C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\new_test_games_df.txt", sep="\r\n")

    # persist the split game data to disk
    # train_games_df.to_json(games_train_path,date_format='iso')
    # test_games_df.to_json(games_test_path,date_format='iso')

    write_train_test_data_by_position(train_profile_df, test_profile_df, train_games_df, test_games_df, "QB")
    write_train_test_data_by_position(train_profile_df, test_profile_df, train_games_df, test_games_df, "WR")
    write_train_test_data_by_position(train_profile_df, test_profile_df, train_games_df, test_games_df, "RB")
    write_train_test_data_by_position(train_profile_df, test_profile_df, train_games_df, test_games_df, "TE")
    write_train_test_data_by_position(train_profile_df, test_profile_df, train_games_df, test_games_df, "K")
    write_train_test_data_by_position(train_profile_df, test_profile_df, train_games_df, test_games_df, "DEF")
    write_train_test_data_by_position(train_profile_df, test_profile_df, train_games_df, test_games_df, "DF")
    write_train_test_data_by_position(train_profile_df, test_profile_df, train_games_df, test_games_df, "DB")


def write_train_test_data_by_position(train_profile_df, test_profile_df, train_games_df, test_games_df, position):

    # map the given position to a list of possible position values
    pos_list = []
    if position == "DB":
        pos_list = ["DB", "CB", "-S\"", "-S-", "S-", "SS", "FS"]
    elif position == "DF":
        pos_list = ["DL", "DE", "DT", "DG", "LB", "NT"]
    elif position == "DEF":
        pos_list = ["DB", "CB", "-S\"", "-S-", "S-", "SS", "FS", "DL", "DE", "DT", "DG", "LB", "NT"]
    elif position == "RB":
        pos_list = ["FB", "HB", "TB", "BB", "WB", "RB", "-B\"", "-B-", "B-"]
    elif position == "WR":
        pos_list = ["SE", "SB", "SR", "FL", "WR", "-E\"", "-E-", "E-"]
    elif position == "K":
        pos_list = ["K", "PR", "P"]
    elif position == "QB":
        pos_list = ["QB"]
    elif position == "TE":
        pos_list = ["TE"]
    
    # find only the games and profile data for the given position
    print("Splitting profile data into train and test sets for position: " + position)
    train_pos_profile_df = train_profile_df.loc[train_profile_df.position.isin(pos_list)]
    train_pos_profile_df.reset_index(drop=True, inplace=True)
    test_pos_profile_df = test_profile_df.loc[test_profile_df.position.isin(pos_list)]
    test_pos_profile_df.reset_index(drop=True, inplace=True)
    print("Splitting game data into train and test sets for position: " + position)
    train_pos_games_df = train_games_df.loc[train_games_df.player_id.isin(train_pos_profile_df.player_id)]
    train_pos_games_df.reset_index(drop=True, inplace=True)
    test_pos_games_df = test_games_df.loc[test_games_df.player_id.isin(test_pos_profile_df.player_id)]
    test_pos_games_df.reset_index(drop=True, inplace=True)

    # persist the split game data to disk by position
    games_pos_train_path = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\games_' + position + '_train.json'
    profile_pos_train_path = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\profile_' + position + '_train.json'
    games_pos_test_path = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\games_' + position + '_test.json'
    profile_pos_test_path = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\profile_' + position + '_test.json'

    print("Persisting profile data for position: " + position)
    train_pos_profile_df.to_json(profile_pos_train_path, date_format='iso')
    test_pos_profile_df.to_json(profile_pos_test_path, date_format='iso')

    print("Persisting game data for position: " + position)
    train_pos_games_df.to_json(games_pos_train_path, date_format='iso')
    test_pos_games_df.to_json(games_pos_test_path, date_format='iso')


if __name__ == "__main__":
   main()
