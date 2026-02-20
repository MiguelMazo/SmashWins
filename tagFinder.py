import pickle
import polars
from jinja2 import Environment, FileSystemLoader

characterMappings = {};

def readPickledTags(pickleFile):
    pkl_file = open(pickleFile, 'rb');
    data = pickle.load(pkl_file);
    pkl_file.close();
    return data;

def main():
    tagToCheck = "Burst";
    pickleFile = "tags/" + tagToCheck.upper() + ".pkl";
    data = readPickledTags(pickleFile)

    environment = Environment(loader=FileSystemLoader("templates/"))
    tags = [];

    players = data[1];

    #Get data
    for row in players.iter_rows():
        playerID = row[0];
        tag = row[1];
        character = row[2];
        if character == "NO DATA":
            character = "none";
        URL = "https://smashiconslocation.s3.amazonaws.com/" + character + ".png"

        template = {"playerID": playerID, "tag": tag, "character": character, "URL": URL}
        tags.append(template);
    
    
    results_filename = tagToCheck + "_list.html"
    results_template = environment.get_template("displayTags.html")

    colors = {};
    lightmode = "Light";
    
    colors["background"] = "#000000";
    colors["search"] = "#202327";
    colors["hover"] = "#504e4e";
    colors["text"] = "#FFFFFF";
    colors["dividors"] = "#928989";
    colors["secondary"] = "#242222";
    colors["blue"] = "#0769aa";
    colors["lightModeButton"] = "#57abe2"
    colors["orange1"] = "#ff7b00";
    colors["orange2"] = "#a54f09";

    toggle = "Light"
    if (lightmode == "Light"):
        colors["background"] = "#FFFFFF";
        colors["search"] = "#83888D";
        colors["hover"] = "#83888D";
        colors["text"] = "#000000";
        colors["dividors"] = "#000000";
        colors["secondary"] = "#F3F3F3";
        colors["blue"] = "#04436d";
        colors["lightModeButton"] = "#57abe2";
        colors["orange1"] = "#be3600";
        colors["orange2"] = "#9e2d00";
        toggle = "Dark"
    
    print(lightmode);
    context = {
        "tags": tags,
        "tag": tagToCheck,
        "colors": colors,
        "toggle": toggle,
        "mode": lightmode
    }

    with open(results_filename, mode="w", encoding="utf-8") as results:
        results.write(results_template.render(context))
        print(f"... wrote {results_filename}")

main();

