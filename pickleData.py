import csv
import pandas
import polars
import pickle
import sqlite3

def addRowToWins(tag, result, df, table, playerID, characters, tagList):
    tag = tag.upper();
    enemyID = "";
    bestWins = polars.DataFrame(schema= [("rank", polars.UInt32), ("tag", str) , ("rating", float),("character", str), ("country", str), ("id", int)]);
    players = polars.DataFrame(schema = [('PlayerID', str), ('Tag', str), ('Character', str), ('GameCount', int)]);
    if table[1] == playerID:
        enemyID = table[2];
    else:
        enemyID = table[1];
    # ID is an Integer. However, not all IDs are integers. Challonge IDs can be strings, so I converted the entire thing into strings, but u can only do that by casting with polars
    if enemyID in df["id"].cast(polars.Utf8):
        if playerID in result:
            #Update entry to existing player
            bestWins = result[playerID][1];
        else:
            # Make a new entry in result for this player
            result[playerID] = (tag, bestWins, playerID);


            # Add Player's tag to list of Tags

            #Update entry to existing tag
            if tag in tagList:
                players = tagList[tag][1];
            else:
                #Make a new Entry
                tagList[tag] = (tag, players);
            
            #String Manipulation
            if (characters == '""'):
                character = "none"
                gamesPlayed = 0; 
            else:     
                index1 = characters.index('":');
                character = characters[11:index1];

                index1+=3;
                try:
                    index2 = characters.index(',');
                    gamesPlayed = characters[index1:index2];

                except:
                    gamesPlayed = characters[index1:len(characters)-1];
            
            #Create new dataframe with data from strings
            
            #Update character w the character from rankings, which is more accurate, if possible
            #print(tag);
            row = df.filter(polars.col("id").cast(polars.Utf8) == playerID);
            #print(row);

            if (row.shape != (0,6)):
                character = row.rows()[0][3];
            else:
                character = "none";
            #print(character);
            #for row in df.iter_rows():
            tagDF = polars.DataFrame({'PlayerID': playerID, 'Tag': tag, 'Character': character, 'GameCount': int(gamesPlayed)})

            #Extend it to list
            players.extend(tagDF);
        
        bestWins.extend(df.filter(polars.col("id").cast(polars.Utf8) == enemyID));

def pickleCreator(db, ranking, wifi):
    #Connect to DB to get All Wins
    print("Starting Code");
    conn = sqlite3.connect(db) 
    c = conn.cursor()
    
    #Read Database
    print("Reading database");
    c.execute("SELECT winner_id,p1_id,p2_id,tournament_key,p1_score,p2_score FROM sets");
    data = c.fetchall();

    data = data;

    #Read Rankings
    print("Reading Rankings")
    df = polars.read_csv(ranking);

    #Add Ranks
    df = df.with_row_index();
    df = df.rename({"index":"rank"});


    #Make an empty dictionary Key = PlayerID, Value = (tag, bestWins, id);
    newList = {};
    players = {};
    tracker = 0;
    for table in data:
        #Check for DQ Wins
        if ((table[4] != -1) & (table[5] != -1)):
            try:
                print("" + str(tracker) + " / " + str(len(data)));
                tracker += 1;
                c.execute("SELECT tag, characters FROM players WHERE player_id = '" + table[0] + "'");
                #Tag for searching

                info = c.fetchall();

                tag = info[0][0];
                #Get the Character Count for the tag selection data
                charactersString = info[0][1]
                if wifi == 0:
                    c.execute("SELECT online FROM tournament_info WHERE key = '" + table[3] + "'");
                    isOnline = c.fetchall();
                    if isOnline[0][0] == 0:
                        addRowToWins(tag, newList, df, table, table[0], charactersString, players);
            
                elif wifi == 1:
                    c.execute("SELECT online FROM tournament_info WHERE key = '" + table[3] + "'");
                    isOnline = c.fetchall();
                    if isOnline[0][0] == 1:
                        addRowToWins(tag, newList, df, table, table[0], charactersString, players);
            
                else:   
                    addRowToWins(tag, newList, df, table, table[0], charactersString, players);
            except:
                if table[0] == None:
                    print("NO TAG")
                else:
                    print(table[0] + "'s tag caused a failure :>")
        else:
            print("DQ WIN")

    #unordered = most recent wins, ordered = highest ranking wins
    for key in newList:
        newList[key] = (newList[key][0], newList[key][1].unique(), newList[key][2]);
        newList[key] = (newList[key][0], newList[key][1].sort("rating", descending=True), newList[key][2]);

    for key in players:
        players[key] = (players[key][0], players[key][1].sort("GameCount", descending=True))

    return(newList, players);



db = "ultimate_player_database/ultimate_player_database.db"
ranking = "seeding algo ranking.csv"
newDB = "bestWinsDatabase.db"

# 0 = Offline, 1 = Wifi, 2 = Both
wifi = 0;

lists = pickleCreator(db, ranking, wifi);

#Pickle Results
data = lists[0];
length = len(data);
counter = 1;
for key in data:
    filename = data[key][2] + ".pkl";
    print(str(counter) + "/" + str(length) + " File: " + filename);
    counter += 1;
    try:
        output = open('pickles/' + filename, 'wb');
        pickle.dump(data[key], output);
        output.close();
    except:
        print(filename + " Caused an issue. Aborting its picklefile.");

#Pickle Tags
data = lists[1];
length = len(data);
counter = 1;
for key in data:
    filename = data[key][0] + ".pkl";
    print(str(counter) + "/" + str(length) + " File: " + filename);
    counter += 1;
    try:
        output = open('tags/' + filename, 'wb');
        pickle.dump(data[key], output);
        output.close();
    except:
        print(filename + " Caused an issue. Aborting its picklefile.");
print("DONE! ;3");