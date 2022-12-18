# This is a sample Python script.

from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
from datetime import datetime
import re

from player_report import *
from bp_scrape import *
from ba_scrape import *


def bp_2023_team_wrapper():
    html_file = '../raw_data/bp_2023_team/bp_2023_ARZ_team-list.html'
    html_page = open(html_file, encoding = 'utf8')
    html_soup = bs(html_page, 'html.parser')
    team_reports = bp_2023_team_scrape(html_soup, team_name = 'ARZ')
    [print(x) for x in team_reports]


def ba_2023_team_wrapper():
    """
    Scrapes all of BA's 2023 top-10 lists
    :return: List of PlayerReport objects
    """

    # load url table
    ba_url_table = pd.read_csv('../raw_data/ba_2023_top-10_urls.csv')
    for index, row in ba_url_table.iterrows():
        print(row['Team'], row['URL'])
        html_page = requests.get(row['URL'], auth = (ba_username(), ba_password()))
        html_soup = bs(html_page.text, 'html.parser')
        ba_2023_team_scrape(html_soup, team_name = row['Team'])
        break


def main():
    ba_2023_team_wrapper()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
