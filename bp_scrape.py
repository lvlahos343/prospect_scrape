"""
Functions for scraping data from Baseball Prospectus.
"""

from PlayerReport import *
from datetime import datetime
import re

def bp_cookie_dict():
    # cookie string text file
    cookie_file = '../raw_data/bp_cookie-str.txt'

    # load cookie string
    with open(cookie_file) as f:
        cookie_str = f.read()

    # construct dictionary
    cookie_dict = {}
    cookie_items = cookie_str.split('; ')
    for ci in cookie_items:
        ci_split = ci.strip().split('=')
        cookie_dict[ci_split[0]] = ci_split[1]

    return cookie_dict


def bp_username():
    return 'lvlahos343@gmail.com'

def bp_password():
    return 'Pr0sp3ctScr@per'

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


def top10_player_report_parse(report_ps):
    """
    :param report_ps: A list of the p tags consiting of a top-10 player's report.
    :return: A list, with report text, ofp, and var
    """
    report_ind = [i for i, x in enumerate(report_ps) if x.text.startswith('The Report:')][0]
    ofp_ind = [i for i, x in enumerate(report_ps) if x.text.startswith('OFP:')][0]

    # get report values
    report_txt = '\n'.join([x.text for x in report_ps[report_ind:ofp_ind]]).strip()
    ofp = report_ps[ofp_ind].text.split(' ')[1]
    var = report_ps[ofp_ind].text.split('Variance:')[1].split('.')[0].strip()

    return [report_txt, ofp, var]


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
    bio_origin = bio_obj.find('li', {'class': 'origin'}).text.strip('.')
    if 'Drafted' in bio_origin:
        p_report.group = 'R4'
    elif 'NDFA' in bio_origin:
        p_report.group = 'R4'
    elif 'Signed' in bio_origin:
        p_report.group = 'IFA'

    # get report indices
    player_ps = player_div.find_all('p')
    if len(player_ps) != 0:
        parsed_report = top10_player_report_parse(player_ps)
        p_report.report_txt = parsed_report[0]
        p_report.ofp = parsed_report[1]
        p_report.var = parsed_report[2]

    # return the report object
    return p_report


def bp_2023_team_scrape(html_soup, team_name):
    """
    Parses a 2023 BP Top-10 Team List page.
    :param html_soup: BeautifulSoup object of a BP Top-10 Team list.
    :param team_name: Name of the team for this list.
    :return: List of PlayerReport objects.
    """

    # get date
    html_date = html_soup.find('a', {'class': 'date'})
    list_date = datetime.strptime(html_date.text.strip(), "%B %d, %Y").date().isoformat()

    # get article and p indices
    article_soup = html_soup.find('div', {'class', 'col-xs-12 col-sm-8 article-content'})
    article_tags = article_soup.find_all(['div', 'p'], recursive = False)
    tt_inds = [i for i, x in enumerate(article_tags) if x.has_attr('class') and x['class'] == ['player', '2020top10']]
    ntt_start = [i for i, x in enumerate(article_tags) if x.text.strip().startswith('11.')][0]
    ntt_end = [i for i, x in enumerate(article_tags) if x.text.strip().startswith('Top Talents 25')][0]

    # start list
    team_reports = []

    # process top 10 reports
    cur_ind = tt_inds[0]
    tt_index = 0
    while cur_ind < ntt_start:
        # parse current report
        cur_report = player_2020top10_parse(article_tags[cur_ind], report_date = list_date, player_team = team_name)
        cur_ind += 1
        tt_index += 1

        # get hanging ps if they were missing from the top10 player div
        if cur_report.report_txt == '' and tt_index < 10: # stop at next top-10 ind
            player_ps = []
            while cur_ind < tt_inds[tt_index]:
                player_ps.append(article_tags[cur_ind])
                cur_ind += 1
            parsed_report = top10_player_report_parse(player_ps)
            cur_report.report_txt = parsed_report[0]
            cur_report.ofp = parsed_report[1]
            cur_report.var = parsed_report[2]

        elif cur_report.report_txt == '': # stop at the start of the not top-10 inds
            player_ps = []
            while cur_ind < ntt_start:
                player_ps.append(article_tags[cur_ind])
                cur_ind += 1
            parsed_report = top10_player_report_parse(player_ps)
            cur_report.report_txt = parsed_report[0]
            cur_report.ofp = parsed_report[1]
            cur_report.var = parsed_report[2]

        # add report to list
        team_reports.append(cur_report)

    # process non-top 10 ps
    ntt_reports = []
    cur_report = PlayerReport(source='BP', date=list_date, report_type='team_list')
    for cur_p in article_tags[ntt_start:ntt_end]:
        if re.match(r'^\d\d', cur_p.text.strip()):
            # dump previous report
            ntt_reports.append(cur_report)
            cur_report = PlayerReport(source='BP', date=list_date, report_type='team_list')

            # create new report
            cur_report.name = re.split(r'\d\.', cur_p.text.strip())[1].split(',')[0].strip()
            cur_href = cur_p.find('a', href=True)
            if cur_href is not None:
                cur_report.id = bp_player_id_from_url(cur_p.find('a', href=True)['href'])
            cur_report.pos = cur_p.text.strip().split(', ')[1].split(' ')[0]
            cur_report.team = team_name
            cur_report.rank = cur_p.text.strip().split('.')[0]
        else:
            cur_report.report_txt_append(cur_p.text.strip())
    ntt_reports.append(cur_report)
    ntt_reports = ntt_reports[1:]
    team_reports = team_reports + ntt_reports
    [x.remove_non_ascii() for x in team_reports]

    return team_reports


def bp_2023_team_wrapper():
    # get files
    bp_html_path = '../raw_data/bp_2023_team/'
    bp_html_files = [f for f in listdir(bp_html_path) if isfile(join(bp_html_path, f))]

    # get reports
    report_list = []
    for bpf in bp_html_files:
        bp_team = bpf.split('_')[2]
        print(bp_team)
        html_page = open(join(bp_html_path, bpf), encoding='utf8')
        html_soup = bs(html_page, 'html.parser')
        report_list = report_list + bp_2023_team_scrape(html_soup, team_name='ARZ')
    print(len(report_list))

    # create document
    ba_23_tlr_file = '../processed_data/bp_2023_top-10_reports.csv'
    out_csv = open(ba_23_tlr_file, 'w', newline = '')
    csvwriter = csv.writer(out_csv)
    doc_fields = ['Source', 'Date', 'Report Type',
                  'Name', 'ID', 'POS', 'Team', 'Group',
                  'Rank', 'Report', 'OFP', 'Var']
    csvwriter.writerow(doc_fields)
    #csvwriter.writerows([x.p_report_vector() for x in report_list])
    for x in report_list:
        csvwriter.writerow(x.p_report_vector())