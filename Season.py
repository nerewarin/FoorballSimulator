# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'
from DataStoring import save_ratings

class Season(object):
    """
    creates all tournament
    """
    def __init__(self, season_year):
        pass
    # TODO 1) see League about converting round_num to 1/4, final, qual , etc
    # TODO 2) add schemes of UEFA tournaments with the help of reglaments wiki

        teamsL = []
        print "sorting teamsL by Ratings"
        teamsL.sort(key=lambda x: -x.getRating())


        save_ratings(con, cur, [season_year], teamsL)