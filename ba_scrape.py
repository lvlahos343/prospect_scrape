"""
Functions for scraping data from Baseball America.
"""


def ba_username():
    return 'lvlahos343@gmail.com'


def ba_password():
    return 'B@P@ss123'


def ba_player_li_parse(player_li, report_date, player_team, report_type = 'team_list'):
    """
    Generates a PlayerReport from a given li object.
    :param player_li: li object from BeautifulSoup
    :param report_date: Date of the given report.
    :param player_team: Team for the given player.
    :param report_type: Type of report being generated. Default of `team_list`
    :return: PlayerReport Object
    """
    p_report = PlayerReport(source = 'BA', date = report_date, report_type = report_type)

    # get player info
    p_report_top = player_li.find('div', {'class': 'report-top'}).text.strip()
    p_report.rank = p_report_top.split('.')[0]
    p_report.name = re.split(r'\d\.', p_report_top)[1].split(' | ')[0].strip()
    p_report.id = player_li.get('id')
    p_report.pos = re.split(r'\d\.', p_report_top)[1].split(' | ')[1].strip()

    # get report text
    p_report_text = player_li.find('div', {'class': 'player-report'})
    for br in p_report_text.find_all('br'):
        br.replace_with('\n')
    p_report_text = p_report_text.text.replace('\n\n', '\n').strip()
    newline_space_ind = p_report_text.find('\n ')
    while newline_space_ind >= 0:
        p_report_text = p_report_text.replace('\n ', '\n').strip()
        newline_space_ind = p_report_text.find('\n ')
    p_report.report_txt = p_report_text

    return p_report


def ba_2023_team_scrape(html_soup, team_name):
    """
    Parses a 2023 BA Top-10 Team List page.
    :param html_soup: BeautifulSoup object of a BP Top-10 Team list.
    :param team_name: Three-letter code for this team.
    :return: List of PlayerReport objects.
    """
    list_date = '2023-01-01'

    # get list of player reports
    player_reports = html_soup.find('div', {'class': 'player-reports'})
    player_reports = player_reports.find_all('li')

    # process player reports
    top10_reports = [ba_player_li_parse(x, player_team = team_name, report_date = list_date) for x in player_reports]
    [print(x) for x in top10_reports]
    return top10_reports
