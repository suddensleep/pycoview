"""Main module."""

import pickle as pk
from datetime import datetime

import argparse
import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

TABLE_URL = "https://coronavirus.health.ny.gov/county-county-breakdown-positive-cases"

def write_new_file(table_dict):
    filename = datetime.strftime(datetime.now(), "%Y%m%d%H%M%s")
    with open(f"../data/{filename}.pkl", "wb") as f:
        pk.dump(table_dict, f)

def append_to_file(new_table_dict, fn):
    fn_suff = datetime.strftime(datetime.now(), "%Y%m%d%H%M%s")
    with open(f"../data/{fn}.pkl", "rb") as f:
        old_table_dict = pk.load(f)
    for key in new_table_dict:
        if key in old_table_dict:
            old_table_dict[key].update(new_table_dict[key])
        else:
            old_table_dict[key] = new_table_dict[key]
    with open(f"../data/{fn}_{fn_suff}.pkl", "wb") as f:
        pk.dump(old_table_dict, f)
    return f"{fn}_{fn_suff}"

def plot_counties(fn):
    with open(f"../data/{fn}.pkl", "rb") as f:
        table_dict = pk.load(f)
    fig, ax = plt.subplots(figsize=(20, 20))
    for key in table_dict:
        sorted_items = sorted(list(table_dict[key].items()), key=lambda x: x[0])
        plt.plot(
            [item[0] for item in sorted_items],
            [item[1] for item in sorted_items],
            label=key
        )
    plt.legend()
    plt.savefig(f"../data/pictures/{fn}.png")
        
def main(fn):
    r = requests.get(TABLE_URL)
    
    soup = BeautifulSoup(r.text, "html.parser")
    for item in soup.findAll("div", {"class": "wysiwyg--field-webny-wysiwyg-title"}):
        if not "Last Update: " in item.text:
            continue
        date = datetime.strptime(
            item.text.lstrip("Last Update: "),
            "%B %d, %Y | %I:%M%p"
        )
    
    table = soup.findAll("td")
    
    table_dict = {
        table[2*i].text.strip().strip(":").strip(): {date: int(table[2*i+1].text.replace(",", ""))}
        for i in range(int(len(table) / 2))
    }
    if fn:
        new_fn = append_to_file(table_dict, fn)
        plot_counties(new_fn)
    else:
        write_new_file(table_dict)
    
parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    "--fn",
    help="file you want to seed with",
    type=str,
    default=""
)

args = parser.parse_args()

main(args.fn)
