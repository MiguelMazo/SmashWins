import os
import pickle
import math
import polars
from jinja2 import Environment, FileSystemLoader


#stream = os.popen('redacted.db');
#output = stream.read();

#Env Variables
efsPath = os.environ['EFS_PATH']

def makeHTML(data, tag, lightModeToggle, pickleID):

    environment = Environment(loader=FileSystemLoader(efsPath + "templates/"))

    wins = [];
    for item in data:
        print(item);
        winTag = item[1];
        rank = item[0];
        if (rank < 10000):
            #Ranks start at 0, add 1 to make it eaiser to read
            rank += 1;
            rating = item[2];
            character = item[3];
    
            if character == None:
                character = "none";
                
            URL = "Redacted"
            #template = '{"tag": ' + winTag + ',"rank": ' + str(rank) + ',"rating": ' + str(rating) + ', "character": ' + character + '},';
            wins.append({"tag": winTag, "rank": str(rank), "rating": str(math.trunc(rating)), "character": character, "URL": URL});
        
    
    results_filename = tag + "_results.html"
    results_template = environment.get_template("resultshtml.html")
    
    
    #Set Colors for LightMode/DarkMode
    lightmode = lightModeToggle;
    colors = {};
    
    colors["background"] = "#000000";
    colors["search"] = "#202327";
    colors["hover"] = "#504e4e";
    colors["text"] = "#FFFFFF";
    colors["dividors"] = "#928989";
    colors["secondary"] = "#242222";
    colors["blue"] = "#0769aa";
    colors["lightModeButton"] = "#57abe2"

    toggle = "Light"
    if (lightmode == "Light"):
        colors["background"] = "#FFFFFF";
        colors["search"] = "#83888D";
        colors["hover"] = "#83888D";
        colors["text"] = "#000000";
        colors["dividors"] = "#000000";
        colors["secondary"] = "#F3F3F3";
        colors["blue"] = "#04436d";
        colors["lightModeButton"] = "#57abe2"
        toggle = "Dark"
        
        
    context = {
        "wins": wins,
        "tag": tag,
        "colors": colors,
        "toggle": toggle,
        "ID": pickleID,
        "mode": lightmode
    }

    return(results_template.render(context));

def lambda_handler(event, context):
    
    tag = event["queryParams"]['tag']
    try:
        pickleID = event["queryParams"]['ID']
    except: 
        pickleID = 15768
        tag = "Tweek"
        
    
    try:
        lightModeToggle = event["queryParams"]['mode'];
    except:
        lightModeToggle = "Dark";
      
    
    if(tag == "Tag Not Found"):
        print("No Data, defaulting to Tweek.")
        pickleID = 15768
        tag = "Tweek"
        
    pickleFile = efsPath + "pickles/pickles/" + str(pickleID) + ".pkl";
    
    pkl_file = open(pickleFile, 'rb');
    data = pickle.load(pkl_file);
    pkl_file.close();
    
    
    return makeHTML(data[1].rows(), tag, lightModeToggle, pickleID);
