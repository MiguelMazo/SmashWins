import pickle
import polars
import math;

from jinja2 import Environment, FileSystemLoader

def makeHTML(data, tag):

    #https://ssb.wiki.gallery/images/thumb/b/bf/{{CapitalName}}HeadSSBUWebsite.png/120px-{{CapitalName}}HeadSSBUWebsite.png
    

    environment = Environment(loader=FileSystemLoader("templates/"))

    wins = [];

    for item in data:
        winTag = item[1];
        rank = item[0];
        rating = item[2];
        #https://smashiconslocation.s3.amazonaws.com/buddy.pn
        
        character = item[3];

        if character == None:
            character = "none";
        
        URL = "https://smashiconslocation.s3.amazonaws.com/" + character + ".png"
        #template = '{"tag": ' + winTag + ',"rank": ' + str(rank) + ',"rating": ' + str(rating) + ', "character": ' + character + '},';
        wins.append({"tag": winTag, "rank": str(rank), "rating": str(math.trunc(rating)), "character": character, "URL": URL});
    
    lightmode = "Light";

    results_filename = tag + "_results.html"
    results_template = environment.get_template("resultshtml.html")
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
        "mode": lightmode,
    }

    with open(results_filename, mode="w", encoding="utf-8") as results:
        results.write(results_template.render(context))
        print(f"... wrote {results_filename}")

def findData(pickleFile, tag, ID):
    pkl_file = open(pickleFile, 'rb');
    data = pickle.load(pkl_file);
    pkl_file.close();

    return data[1];


#pickleFile = "data.pkl";
tag = "Skewert";
ID = '1641578';


pickleFile = "pickles/" + ID + ".pkl";

result = findData(pickleFile, tag, ID);

makeHTML(result.rows(), tag);