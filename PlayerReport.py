class PlayerReport:

    def __init__(self, source, date = '', report_type = ''):
        self.source = source
        self.date = date
        self.report_type = report_type

        # set null variables
        self.name = ''
        self.id = ''
        self.pos = ''
        self.team = ''
        self.group = ''
        self.rank = ''
        self.report_txt = ''
        self.ofp = ''
        self.var = ''

    def __str__(self):
        """
        :return: String representation of object.
        """
        report_detail_str = ','.join([self.source, self.date, self.report_type])
        player_detail_str = ','.join([self.name, self.id, self.pos, self.team, self.group])
        report_metric_str = ','.join([self.rank, self.ofp, self.var])
        p_report_str = '\n'.join([report_detail_str, player_detail_str, report_metric_str, self.report_txt])

        return p_report_str

    def report_txt_append(self, new_txt, str_delim = '\n'):
        """
        Appends given text to the current report_txt variable.
        :param new_txt: Text to be appended.
        :param str_delim: Delimiter to be used; default of new line
        """
        self.report_txt = str_delim.join([self.report_txt, new_txt]).strip()

    def p_report_vector(self):
        """
        Use this function to change format of reports.
        :return: A formatted vector w/ player information.
        """

        p_report_vec = [self.source, self.date, self.report_type,
                        self.name, self.id, self.pos, self.team, self.group,
                        self.rank, self.report_txt.strip(), self.ofp, self.var]

        return p_report_vec

    def remove_non_ascii(self):
        self.report_txt = self.report_txt.encode('ascii', errors = 'ignore').decode()