# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

import Team
from Cups import Cup
import util
from Leagues import League, TeamResult
import Match as M
from values import Coefficients as C
from operator import attrgetter, itemgetter
import random
import time
import os
import warnings

class UEFA_Champ_L(Cup):
    def __init__(self, name, season, members, delta_coefs, schema, pair_mode = 1, state_params = ("final_stage", )):
        """
        UEFA_Champ_L is a tournament, implemented as three tournaments:
        Qualification Cup, Group League, Play-Off Cup.

        Num of rounds and pairs in every tournament defined by schema

        :param name:
        :param season:
        :param members:
        :param delta_coefs:
        :param schema:
        :param pair_mode:
        :param state_params:
        :return:
        """

        super(Cup, self).__init__(name, season, members, delta_coefs, state_params)#(self, name, season, members, delta_coefs)

        # self.results - empty list. after run() it will be filled as following:
        # [team_champion, team_finished_in_final, teams_finished_in_semi-final, ... , teams_finished_in_qualRoundn, ...
        # teams_finished_in_qualRound1# ]
        print "\nWELCOME TO *** %s %s ***" % (name.upper(), season)

        state = {st:None for st in state_params}

        for member in self.members:
            self.results.append(L.TeamResult(member, state).get4table())
        # print "self.results", self.results
        # initialize net
        self.net = "not implemented yet"
        self.round_names = "not computed" # TODO make branch: get from params (if external scheme exists) OR compute in run()

schema

    def setMembers(self):
        """
        defines members for every round
        :return:
        """
        self.members = []
        for


    def test(self, print_matches = False, print_ratings = False):
        print "\nTEST CUP CLASS\n"
        print "pair_mode = %s\nseeding = %s\n" % (self.pair_mode, self.seeding)
        print "initial Net:"
        print self#.printTable()
        if print_matches:
            print "\nMatches:"
        self.run(print_matches)
        print "\nWinner:\n%s" % self.getWinner()
        # print "\nresults:\n%s" % [(k, [team.getName() for team in self.results[k]] ) for k in self.results.keys()]
        print "\nresults:"
        for k in self.results.keys():
            # TODO sort results ny round (maybe store them in list)
            print k, [team.getName() for team in self.results[k]]
        print "\nFinal Net:\n", str(self), "\n"

        # ratings after league
        # print "print_ratings = %s" % print_ratings
        # print "self.getMember() %s" % self.getMember()
        if print_ratings:
            for team in self.getMember():
                print team.getName(), team.getRating()






# TEST
if __name__ == "__main__":
    @util.timer
    def Test(*args, **kwargs):
        # VERSION = "v1.1"
        with open(os.path.join("", 'VERSION')) as version_file:
            values_version = version_file.read().strip()
        coefs = C(values_version).getRatingUpdateCoefs("list")

        teams = []
        team_num = kwargs["team_num"]
        for i in range(team_num):
            teamN = i + 1
            rating = team_num - i
            uefa_pos = teamN
            teams.append(Team.Team("FC team%s" % teamN, "RUS", rating, "Команда%s" % teamN, uefa_pos))

        # TEST CUP CLASS
        if "ChL" in args:

            schema =
            # for seeding in Cup.getSeedings(Cup):
            #     print seeding
            # pair_mode = 0 # one match
            pair_mode = 1 # home + guest every match but the final
            # pair_mode = 2 # home + guest every match

            # print_matches = False
            print_matches = True

            print_ratings = False
            # print_ratings = True

            s =  Cup("no Cup, just getSeedings", "", teams, coefs, pair_mode)
            seedings = s.getSeedings()
            # print "seedings", seedings
            for seeding in seedings:
                # print seeding , "seeding"
                # print "teams, coefs, pair_mode, seeding", teams, coefs, pair_mode, seeding
                tstcp = Cup("test UEFA Champions league", "2015/2016", teams, coefs, pair_mode, seeding)
                tstcp.test(print_matches, print_ratings)
            # # Cup("testCup", "2015/2016", teams, coefs, pair_mode).run()


    Test("ChL", team_num = 100)





