"""Main module."""

#import pickle as pk
import pandas as pd

from datetime import datetime

import argparse
import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

TABLE_URL = "https://coronavirus.health.ny.gov/county-county-breakdown-positive-cases"

def soup2dict(soup):
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

    return table_dict, date

def mash_dfs(table_dict, date):
    old_df = pd.read_csv(f"../data/latest_df.tsv", sep="\t", header=0, index_col=0)
    if str(date) not in old_df.columns:
        df = pd.DataFrame.from_dict(table_dict, orient="index")
        new_df = pd.concat([old_df, df], axis=1)
    else:
        new_df = old_df
    new_df.to_csv("../data/latest_df_new.tsv", sep="\t", header=True, index=True)

    return new_df

def plot_counties(df):
    fig, ax = plt.subplots(figsize=(20, 20))
    df.transpose().plot(ax=ax)
    plt.legend()
    plt.savefig(f"../data/pictures/latest_new.png")
        
def main():
    r = requests.get(TABLE_URL)
    
    soup = BeautifulSoup(r.text, "html.parser")
    
    table_dict, date = soup2dict(soup)

    new_df = mash_dfs(table_dict, date)

    plot_counties(new_df)

    
parser = argparse.ArgumentParser()

args = parser.parse_args()

main()
