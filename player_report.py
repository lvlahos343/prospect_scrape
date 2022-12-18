class PlayerReport:

    def __init__(self, source, date = '', report_type = ''):
        self.source = source
        self.date = date
        self.report_type = report_type

        # set null variables
        self.name = ''
        self.id = ''
        self.pos = ''
        self.rank = ''
        self.report_txt = ''
        self.ofp = ''
        self.var = ''

    def p_report_vector(self):
        """
        Use this function to change format of reports.
        :return: A formatted vector w/ player information.
        """

        p_report_vec = [self.source, self.date, self.report_type,
                        self.name, self.id, self.pos,
                        self.rank, self.report_txt, self.ofp, self.var]

        return p_report_vec