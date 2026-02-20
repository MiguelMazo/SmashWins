import sqlite3
import csv
import pandas
import polars

def addRowToWins(tag, result, df, table, playerID):
    enemyID = "";
    bestWins = polars.DataFrame(schema= [("tag", str) , ("rating", float),("character", str), ("country", str), ("id", int)]);
    
    if table[1] == playerID:
        enemyID = table[2];
    else:
        enemyID = table[1];
    # ID is an Integer. However, not all IDs are integers. Challonge IDs can be strings, so I converted the entire thing into strings, but u can only do that by casting with polars
    if enemyID in df["id"].cast(polars.Utf8):
        if playerID in result:
            bestWins = result[playerID][1];
        else:
            result[playerID] = (tag, bestWins, playerID);

        bestWins.extend(df.filter(polars.col("id").cast(polars.Utf8) == enemyID));

def createDB(db_file, data):
    conn = sqlite3.connect(db_file)
    c = conn.cursor();
    counter = 0;

    print("Inserting basic info");  
    sqlQuery = "INSERT INTO players (Tag,NewColumn) VALUES ('Skew',('1', '2'))";
    c.execute(sqlQuery);
    conn.commit();

    print("Length of Data: " + str(len(data)));
    for key in data:

        print(str(counter) + " / " + str(len(data)));
        counter += 1;
        #create a table for each player
        currentPlayer = data[key][0];
        #print(currentPlayer);

        #Current fix to apostrophes for NOW, will think up a better solution later
        if "'" in currentPlayer:
            currentPlayer = currentPlayer.replace("\'", "");
            print("Replacing!");
        elif "\"" in currentPlayer:
            currentPlayer = currentPlayer.replace("\"", "");
            print("Replacing!");
        
        print("Making the DB for: " + currentPlayer + ", ID: " + data[key][2]);
        

        #Populate each table with the dataframe's data
        print("This is the DataFrame: ")
        print(data[key][1]);
        for row in data[key][1].iter_rows():
            print(row);
            if not data[key][1].is_empty():
                tag = str(row[0]);

                #Current fix to apostrophes for NOW, will think up a better solution later
                if "'" in tag:
                    tag = tag.replace("'", "");
                    print("Replacing!");
                elif "\"" in tag:
                    tag = tag.replace("\"", "");
                    print("Replacing!");
                
                c.execute("INSERT INTO '" + currentPlayer + "' (tag, rating, character, country, id) VALUES ('" + tag +  "', '" + str(row[1]) + "', '" + str(row[2]) + "', '" + str(row[3]) + "', '" + str(row[4]) + "')");
            else: 
                print("Empty!");

        print("DONE")
        print();
        conn.commit();


def DBcreator(db, ranking, wifi):
    print("Starting Code");
    conn = sqlite3.connect(db) 
    c = conn.cursor()
    
    print("Reading database");
    c.execute("SELECT winner_id,p1_id,p2_id,tournament_key FROM sets");
    data = c.fetchall();

    data = data[:5];
    print("Reading Rankings")
    df = polars.read_csv(ranking);

    #Make an empty dictionary Key = PlayerID, Value = (tag, bestWins, id);
    newList = {};
    tracker = 0;
    for table in data:
        print("" + str(tracker) + " / " + str(len(data)));
        tracker += 1;
        try:
            c.execute("SELECT tag FROM players WHERE player_id = '" + table[0] + "'");
            tag = c.fetchall()[0][0];
            if wifi == 0:
                c.execute("SELECT online FROM tournament_info WHERE key = '" + table[3] + "'");
                isOnline = c.fetchall();
                if isOnline[0][0] == 0:
                    addRowToWins(tag, newList, df, table, table[0]);
        
            elif wifi == 1:
                c.execute("SELECT online FROM tournament_info WHERE key = '" + table[3] + "'");
                isOnline = c.fetchall();
                if isOnline[0][0] == 1:
                    addRowToWins(tag, newList, df, table, table[0]);
        
            else:   
                addRowToWins(tag, newList, df, table, table[0]);
        except:
            print("A Tag caused an error and a table was not generated.");

    #unordered = most recent wins, ordered = highest ranking wins
    for key in newList:
        newList[key] = (newList[key][0], newList[key][1].unique(), newList[key][2]);
        newList[key] = (newList[key][0], newList[key][1].sort("rating", descending=True), newList[key][2]);

    return(newList);



db = "ultimate_player_database.db"
ranking = "seeding algo ranking.csv"
newDB = "bestWinsDatabase.db"

# 0 = Offline, 1 = Wifi, 2 = Both
wifi = 0;

data = DBcreator(db, ranking, wifi);
createDB(newDB, data);