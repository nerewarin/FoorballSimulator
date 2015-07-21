# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'
from DataStoring import save_ratings, CON, CUR

class Season(object):
    """
    creates all tournament
    """
    def __init__(self, season_year):
        """

        :param season_year: string like "2014/2015"
        :return:
        """
        pass
    # TODO 1) see League about converting round_num to 1/4, final, qual , etc
    # TODO 2) add schemes of UEFA tournaments with the help of reglaments wiki

        self.season_year = season_year
        teamsL = []
        print "sorting teamsL by Ratings"
        teamsL.sort(key=lambda x: -x.getRating())


        # save_ratings(con, cur, [season_year], teamsL)

    def run(self):
        # connect to DB
        con, cur = CON, CUR

        # TODO run every match that exists in table "Tournaments"

    columns = table_name, tournament_name, tournament_type, tournament_country
    counter += gen_national_tournaments(con, cur, columns, "Cup", sorted_countries)

        # after all
        save_ratings(con, cur, [self.season_year], teamsL)
