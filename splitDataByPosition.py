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

def main():

    #some initial setup
    qbCareerDict = {}
    allProfilePath = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\profiles_1534254607.3839095.json'
    allGamesPath = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\games_1534254679.891445.json'
    gamesTrainPath = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\games_train.json'
    profileTrainPath = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\profile_train.json'
    gamesTestPath = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\games_test.json'
    profileTestPath = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\profile_test.json'

    #split the data into train and test sets
    profilesDf = pd.read_json(allProfilePath)
    #profilesDf.set_index('player_id', inplace=True)
    print("Splitting profile data into train and test sets.")
    trainProfileDf, testProfileDf = train_test_split(profilesDf, test_size=0.4, random_state=42)

    #persist the split profile data to disk
    #trainProfileDf.to_json(profileTrainPath,date_format='iso')
    #testProfileDf.to_json(profileTestPath,date_format='iso')

    #find games corresponding to the position and train/test split
    gamesDf = pd.read_json(allGamesPath)
    print("Dropping duplicate game data.")
    gamesDf.drop_duplicates(subset=['game_id','player_id'], inplace=True)
    print("Splitting game data into train and test sets.")
    trainGamesDf = gamesDf.loc[gamesDf.player_id.isin(trainProfileDf.player_id)]
    #newTrainGamesDf = trainGamesDf.copy().set_index(['game_id', 'player_id'])
    testGamesDf = gamesDf.loc[gamesDf.player_id.isin(testProfileDf.player_id)]
    #newTestGamesDf = testGamesDf.copy().set_index(['game_id', 'player_id'])
    #newTrainGamesDf.index.values.tofile("C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\newTrainGamesDf.txt", sep="\r\n")
    #newTestGamesDf.index.values.tofile("C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\newTestGamesDf.txt", sep="\r\n")

    #persist the split game data to disk
    #trainGamesDf.to_json(gamesTrainPath,date_format='iso')
    #testGamesDf.to_json(gamesTestPath,date_format='iso')
    
    writeTrainTestDataByPosition(trainProfileDf, testProfileDf, trainGamesDf, testGamesDf, "QB")
    writeTrainTestDataByPosition(trainProfileDf, testProfileDf, trainGamesDf, testGamesDf, "WR")
    writeTrainTestDataByPosition(trainProfileDf, testProfileDf, trainGamesDf, testGamesDf, "RB")
    writeTrainTestDataByPosition(trainProfileDf, testProfileDf, trainGamesDf, testGamesDf, "TE")
    writeTrainTestDataByPosition(trainProfileDf, testProfileDf, trainGamesDf, testGamesDf, "K")
    writeTrainTestDataByPosition(trainProfileDf, testProfileDf, trainGamesDf, testGamesDf, "DEF")
    writeTrainTestDataByPosition(trainProfileDf, testProfileDf, trainGamesDf, testGamesDf, "DF")
    writeTrainTestDataByPosition(trainProfileDf, testProfileDf, trainGamesDf, testGamesDf, "DB")

def writeTrainTestDataByPosition(trainProfileDf, testProfileDf, trainGamesDf, testGamesDf, position):

    #map the given position to a list of possible position values
    posList = []
    if position == "DB":
        posList = ["DB","CB","-S\"","-S-","S-","SS","FS"]
    elif position == "DF":
        posList = ["DL","DE","DT","DG","LB","NT"]
    elif position == "DEF":
        posList = ["DB","CB","-S\"","-S-","S-","SS","FS","DL","DE","DT","DG","LB","NT"]
    elif position == "RB":
        posList = ["FB","HB","TB","BB","WB","RB","-B\"","-B-","B-"]
    elif position == "WR":
        posList = ["SE","SB","SR","FL","WR","-E\"","-E-","E-"]
    elif position == "K":
        posList = ["K","PR","P"]
    elif position == "QB":
        posList = ["QB"]
    elif position == "TE":
        posList = ["TE"]
    
    #find only the games and profile data for the given position
    print("Splitting profile data into train and test sets for position: " + position)
    trainPosProfileDf = trainProfileDf.loc[trainProfileDf.position.isin(posList)]
    trainPosProfileDf.reset_index(drop=True,inplace=True)
    testPosProfileDf = testProfileDf.loc[testProfileDf.position.isin(posList)]
    testPosProfileDf.reset_index(drop=True,inplace=True)
    print("Splitting game data into train and test sets for position: " + position)
    trainPosGamesDf = trainGamesDf.loc[trainGamesDf.player_id.isin(trainPosProfileDf.player_id)]
    trainPosGamesDf.reset_index(drop=True,inplace=True)
    testPosGamesDf = testGamesDf.loc[testGamesDf.player_id.isin(testPosProfileDf.player_id)]
    testPosGamesDf.reset_index(drop=True,inplace=True)

    #persist the split game data to disk by position
    gamesPosTrainPath = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\games_' + position + '_train.json'
    profilePosTrainPath = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\profile_' + position + '_train.json'
    gamesPosTestPath = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\games_' + position + '_test.json'
    profilePosTestPath = 'C:\\Users\\kjree\\Workspaces\\nfl-player-stats\\profile_' + position + '_test.json'

    print("Persisting profile data for position: " + position)
    trainPosProfileDf.to_json(profilePosTrainPath,date_format='iso')
    testPosProfileDf.to_json(profilePosTestPath,date_format='iso')

    print("Persisting game data for position: " + position)
    trainPosGamesDf.to_json(gamesPosTrainPath,date_format='iso')
    testPosGamesDf.to_json(gamesPosTestPath,date_format='iso')    

if __name__ == "__main__":
   main()
