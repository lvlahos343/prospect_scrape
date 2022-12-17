# This is a sample Python script.

from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import requests
import re

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def bp_player_id_from_url(player_url):
    """
    :param player_url: URL for player's page
    :return: string giving player id; returns empty string if no id can eb found
    """

    if player_url is None:
        p_id = ''
    elif 'name=' in player_url:
        p_id = ''
    elif '=' in player_url:
        p_id = player_url.split('=')[-1]
    else:
        p_id = player_url.split('/')[-1]

    return p_id


def player_2020top10_parse(player_div):

    # get bio information
    bio_obj = player_div.find('ul', {'class': 'bio'})
    player_name = bio_obj.find('li', {'class': 'name'}).text
    player_id = bp_player_id_from_url(bio_obj.find('a', href = True)['href'])
    player_rank = bio_obj.find('li', {'class': 'rank'}).text.strip('.')
    player_pos = bio_obj.find('li', {'class': 'pos'}).text.split(': ')[-1]

    # get report indices
    player_ps = player_div.find_all('p')
    report_ind = [i for i, x in enumerate(player_ps) if x.text.startswith('The Report:')][0]
    ofp_ind = [i for i, x in enumerate(player_ps) if x.text.startswith('OFP:')][0]

    # get report values
    report_text = '\n'.join([x.text for x in player_ps[report_ind:ofp_ind]])
    ofp_val = player_ps[ofp_ind].text.split(' ')[1]
    var_val = player_ps[ofp_ind].text.split('Variance:')[1].split('.')[0].strip()

    # return list
    return([player_name, player_id, player_pos, player_rank,
            report_text, ofp_val, var_val])



def bp_2023_team_scrape(html_soup):
    # get date
    html_date = html_soup.find('a', {'class': 'date'})
    list_date = datetime.strptime(html_date.text.strip(), "%B %d, %Y").date().isoformat()
    print(list_date)

    # get top 10 reports
    top10_divs = html_soup.find_all('div', {'class': 'player 2020top10'})
    top10_reports = [player_2020top10_parse(x) for x in top10_divs]

    # get non-top 10 ps
    all_ps = html_soup.find_all('p')
    ntt_start = [i for i, x in enumerate(all_ps) if x.text.strip().startswith('11.')][0]
    ntt_end = [i for i, x in enumerate(all_ps) if x.text.strip().startswith('Top Talents 25')][0]
    ntt_ps = all_ps[ntt_start:ntt_end]

    # process non-top 10 ps
    ntt_reports = []
    cur_report = [''] * 7
    for cur_p in ntt_ps:
        if re.match(r'^\d\d', cur_p.text.strip()):
            # dump previous report
            ntt_reports.append(cur_report)
            cur_report = [''] * 7

            # create new report
            cur_report[0] = re.split(r'\d\.', cur_p.text.strip())[1].split(',')[0].strip()
            cur_report[1] = bp_player_id_from_url(cur_p.find('a', href = True)['href'])
            cur_report[2] = cur_p.text.strip().split(', ')[1].split(' ')[0]
            cur_report[3] = cur_p.text.strip().split('.')[0]
        else:
            cur_report[4] = '\n'.join([cur_report[4], cur_p.text.strip()]).strip()
    ntt_reports.append(cur_report)
    ntt_reports = ntt_reports[1:]

    team_reports = top10_reports + ntt_reports
    return(team_reports)

def main():
    html_file = '../raw_data/bp_2023_team/bp_2023_ARZ_team-list.html'
    html_page = open(html_file, encoding = 'utf8')
    html_soup = bs(html_page, 'html.parser')
    team_reports = bp_2023_team_scrape(html_soup)
    [print(x) for x in team_reports]

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
