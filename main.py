# By Miguel Mazo (Skew)
# Looks through smashdata.gg's database and sorts wins based off schustats' rankings

import sqlite3
import csv
import pandas
import polars

#Adds a row to the Wins Column
def addRowToWins(df, table, playerID, bestWins):
    enemyID = "";
    if table[0] == playerID:
        enemyID = table[1];
    else:
        enemyID = table[0];
    # ID is an Integer. However, not all IDs are integers. Challonge IDs can be strings, so I converted the entire thing into strings, but u can only do that by casting with polars
    if enemyID in df["id"].cast(polars.Utf8):
        bestWins.extend(df.filter(polars.col("id").cast(polars.Utf8) == enemyID));

#Imports smashdata.gg's Database
def importdb(db, ranking, tag, wifi, id):
    #Create sqlite3 cursor to search
    print("Starting Code");
    conn = sqlite3.connect(db) 
    c = conn.cursor()


    #Convert Tag to playerID
    #Gets SQL Query, fetchesall, then grabs the first entry, which is a tuple (0,) and grabs the first entry in the tuple
    if (id != 0):
        playerID = str(id);
    else:
        playerID = c.execute("SELECT player_id FROM players WHERE tag = '" + tag + "'").fetchall()[0][0];

    #Select all opponents where the winner was the playerTag and it wasnt a DQ
    print(playerID);
    c.execute("SELECT p1_id,p2_id,tournament_key FROM sets WHERE winner_id = " + str(playerID) + " AND NOT p1_score = '-1' AND NOT p2_score = '-1'");

    data = c.fetchall();

    #tag,rating,character,country,id
    df = polars.read_csv(ranking);
    bestWins = polars.DataFrame(schema= [("tag", str) , ("rating", float),("character", str), ("country", str), ("id", int)]);

    #Generates Text + Filename
    path = tag + "_BestWins";
    if (wifi == 0):
        print("Best Wins Offline Only");
        path += "_Offline.csv"
    
    elif (wifi == 1):
        print("Best Wins Wifi Only");
        path += "_Online.csv"
    else:
        print("Best Wins Including Wifi");
        path += "_All.csv"

    #Adds Rows to Wins
    for table in data:
        if wifi == 0:
            c.execute("SELECT online FROM tournament_info WHERE key = '" + table[2] + "'");
            isOnline = c.fetchall();
            if isOnline[0][0] == 0:
                addRowToWins(df, table, playerID, bestWins);
        
        elif wifi == 1:
            c.execute("SELECT online FROM tournament_info WHERE key = '" + table[2] + "'");
            isOnline = c.fetchall();
            if isOnline[0][0] == 1:
                addRowToWins(df, table, playerID, bestWins);
        
        else:   
            addRowToWins(df, table, playerID, bestWins);
        

    #Removes Duplicates and Sorts

    bestWins = bestWins.unique();
    bestWins = bestWins.sort("rating", descending=True);
    print(bestWins);
    
    bestWins.write_csv(path);

tag = "FD";
db = "ultimate_player_database.db"
ranking = "seeding algo ranking.csv"

#ID overrides Tag.
id = 1810011 ;
# 0 = Offline, 1 = Wifi, 2 = Both
wifi = 0
importdb(db, ranking, tag, wifi, id);

546734, 1641578