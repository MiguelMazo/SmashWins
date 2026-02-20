# Find out what tag = the right ID.
# Input Tag, return List of IDs with Characters

import csv
import pandas
import polars
import pickle
import sqlite3
import pprint, pickle

def findIDs(tag, db):
    print("Starting Code");
    conn = sqlite3.connect(db) 
    c = conn.cursor()
    c.execute("SELECT player_id, tag, characters FROM players WHERE tag = '" + tag + "'");

    data = c.fetchall();
    players = polars.DataFrame(schema = [('PlayerID', str), ('Tag', str), ('Character', str), ('GameCount', int)]);
    for row in data:
        #print(row[2]);
        if (row[2] == '""'):
            character = "None"
            gamesPlayed = 0;
        else:     
            index1 = row[2].index('":');
            character = row[2][11:index1];

            index1+=3;
            try:
                index2 = row[2].index(',');
                gamesPlayed = row[2][index1:index2];

            except:
                gamesPlayed = row[2][index1:len(row[2])-1];
        
        #(row[0], row[1], character, int(gamesPlayed));
        #players[tag] = row[0], row[1], character, int(gamesPlayed));
     
        df = polars.DataFrame({'PlayerID': row[0], 'Tag': row[1], 'Character': character, 'GameCount': int(gamesPlayed)})
        players.extend(df);

    players = players.sort("GameCount", descending=True);
    print(players);


    


def main():
    pkl_file = open('pickles/56473.pkl', 'rb');
    data = pickle.load(pkl_file);
    pprint.pprint(data);
    pkl_file.close();
    database = "ultimate_player_database.db"
    tag = "Burst"
    findIDs(tag, database);

main();