from bs4 import BeautifulSoup as bs
import csv
from PlayerReport import *
import pandas as pd
import re
import requests
from datetime import datetime


def fg_id_from_url(fg_url):
    """
    Gets a player ID from a given FG URL.
    :param fg_url: URL to a FG player page
    :return: Player FG ID
    """
    fg_id = fg_url.split('playerid=')[1].strip()
    return fg_id


def fg_player_div_scrape(player_div, report_date, player_team, report_type = 'team_list'):
    """
    Generates a PlayerReport from a given FG div object.
    :param player_div: div object from BeautifulSoup
    :param report_date: Date of the given report.
    :param player_team: Team for the given player.
    :param report_type: Type of report being generated. Default of `team_list`
    :return: PlayerReport Object
    """
    p_report = PlayerReport(source = 'FG', date = report_date, report_type = report_type)

    # get player info
    div_header = player_div.find('div', {'class': 'table-header grey'}).find('h3', {'class', 'header-name'})
    header_text= div_header.text.strip()
    p_report.rank = header_text.split('.')[0]
    p_report.name = re.split(r'\d\.', header_text)[1].split(', ')[0].strip()
    p_report.pos = re.split(r'\d\.', header_text)[1].split(', ')[1].strip()
    p_report.team = player_team
    header_href = div_header.find('a', href = True)
    if header_href is not None:
        p_report.id = fg_id_from_url(header_href['href'])

    # get group info
    table_title = player_div.find('div', {'class': 'table-grey'}).find('div', {'class': 'table-title'}).text
    if "Signed: July 2nd Period," in table_title:
        p_report.group = 'IFA'
    else:
        p_report.group = 'R4'

    # get FV
    table_body = player_div.find('div', {'class': 'table-grey'}).find('table').text.strip()
    p_report.ofp = table_body.split('\n')[-1].strip()

    # get report text
    p_report.report_txt = player_div.find('div', {'class': 'prospects-list-summary'}).text.strip()
    p_report.remove_non_ascii()

    return p_report


def fg_2023_team_scrape(html_soup, team_name):
    """
    Scrapes prospect info from a given FG team list.
    :param html_soup: HTML Soup object for the team list page.
    :param team_name:
    :return: List of PlayerReport objects
    """

    # get date
    date_txt = html_soup.find('div', {'class': 'postmeta'}).find_all('div')[1].text
    list_date = datetime.strptime(date_txt.strip(), "%B %d, %Y").date().isoformat()

    # get all top prospect divs
    ttp_divs = html_soup.find_all('div', {'class': 'tool-item top-prospects-tool'})
    team_reports = [fg_player_div_scrape(x, list_date, team_name) for x in ttp_divs]

    return team_reports


def fg_2023_team_wrapper():
    """
    Scrapes all of BA's 2023 top-10 lists and adds to file
    :return:
    """

    # load url table
    fg_url_table = pd.read_csv('../raw_data/fg_2023_team-list_urls.csv')
    report_list = []
    for index, row in fg_url_table.iterrows():
        print(row['Team'])
        if isinstance(row['URL'], float):
            continue
        html_page = requests.get(row['URL'])
        html_soup = bs(html_page.text, 'html.parser')
        report_list = report_list + fg_2023_team_scrape(html_soup, team_name = row['Team'])
    print(len(report_list))

    # create document
    fg_23_tlr_file = '../processed_data/fg_2023_team-list_reports.csv'
    out_csv = open(fg_23_tlr_file, 'w', newline = '')
    csvwriter = csv.writer(out_csv)
    doc_fields = ['Source', 'Date', 'Report Type',
                  'Name', 'ID', 'POS', 'Team', 'Group',
                  'Rank', 'Report', 'OFP', 'Var']
    csvwriter.writerow(doc_fields)
    csvwriter.writerows([x.p_report_vector() for x in report_list])