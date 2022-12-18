"""
Functions for scraping data from Baseball Prospectus.
"""

from player_report import *
from datetime import datetime
import re


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


def player_2020top10_parse(player_div, report_date, player_team, report_type = 'team_list'):
    """
    :param player_div: BeautifulSoup object for a 2020top10 div object.
    :param report_date: Date of report in YYYY-MM-DD format as string.
    :param player_team: Team of the player being scraped.
    :param report_type: Type of report; default of 'team_list'
    :return A PlayerReport object.
    """
    # create object
    p_report = PlayerReport(source = 'BP', date = report_date, report_type = report_type)

    # get bio information
    bio_obj = player_div.find('ul', {'class': 'bio'})
    p_report.name = bio_obj.find('li', {'class': 'name'}).text
    p_report.id = bp_player_id_from_url(bio_obj.find('a', href = True)['href'])
    p_report.pos = bio_obj.find('li', {'class': 'pos'}).text.split(': ')[-1]
    p_report.team = player_team
    p_report.rank = bio_obj.find('li', {'class': 'rank'}).text.strip('.')

    # get report indices
    player_ps = player_div.find_all('p')
    report_ind = [i for i, x in enumerate(player_ps) if x.text.startswith('The Report:')][0]
    ofp_ind = [i for i, x in enumerate(player_ps) if x.text.startswith('OFP:')][0]

    # get report values
    p_report.report_txt = '\n'.join([x.text for x in player_ps[report_ind:ofp_ind]])
    p_report.ofp = player_ps[ofp_ind].text.split(' ')[1]
    p_report.var = player_ps[ofp_ind].text.split('Variance:')[1].split('.')[0].strip()

    # return list
    return p_report


def bp_2023_team_scrape(html_soup, team_name):
    """
    Parses a 2023 BP Top-10 Team List page.
    :param html_soup: BeautifulSoup object of a BP Top-10 Team list.
    :return: List of PlayerReport objects.
    """

    # get date
    html_date = html_soup.find('a', {'class': 'date'})
    list_date = datetime.strptime(html_date.text.strip(), "%B %d, %Y").date().isoformat()

    # get top 10 reports
    top10_divs = html_soup.find_all('div', {'class': 'player 2020top10'})
    top10_reports = [player_2020top10_parse(x, player_team = team_name, report_date = list_date) for x in top10_divs]

    # get non-top 10 ps
    all_ps = html_soup.find_all('p')
    ntt_start = [i for i, x in enumerate(all_ps) if x.text.strip().startswith('11.')][0]
    ntt_end = [i for i, x in enumerate(all_ps) if x.text.strip().startswith('Top Talents 25')][0]
    ntt_ps = all_ps[ntt_start:ntt_end]

    # process non-top 10 ps
    ntt_reports = []
    cur_report = PlayerReport(source='BP', date=list_date, report_type='team_list')
    for cur_p in ntt_ps:
        if re.match(r'^\d\d', cur_p.text.strip()):
            # dump previous report
            ntt_reports.append(cur_report)
            cur_report = PlayerReport(source='BP', date=list_date, report_type='team_list')

            # create new report
            cur_report.name = re.split(r'\d\.', cur_p.text.strip())[1].split(',')[0].strip()
            cur_report.id = bp_player_id_from_url(cur_p.find('a', href=True)['href'])
            cur_report.pos = cur_p.text.strip().split(', ')[1].split(' ')[0]
            cur_report.team = team_name
            cur_report.rank = cur_p.text.strip().split('.')[0]
        else:
            cur_report.report_txt_append(cur_p.text.strip())
    ntt_reports.append(cur_report)
    ntt_reports = ntt_reports[1:]

    team_reports = top10_reports + ntt_reports
    return team_reports