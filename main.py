# This is a sample Python script.

from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import re
import js2py
import csv
import math

from PlayerReport import *
from bp_scrape import *
from ba_scrape import *
from os import listdir
from os.path import isfile, join


def main():
    #print('Scraping BA reports:')
    #ba_2023_team_wrapper()

    print('Scraping BP reports:')
    bp_2023_team_wrapper()

    #bp_file = '../raw_data/bp_2023_team/bp_2023_MIN_team-list.html'
    #html_page = open(bp_file, encoding='utf8')
    #html_soup = bs(html_page, 'html.parser')
    #[print(x) for x in bp_2023_team_scrape(html_soup, 'MIN')]

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
