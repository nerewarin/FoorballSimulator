# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

import Team
import util
# import Cups
import Match as M
from values import Coefficients as C
from operator import attrgetter, itemgetter
import random
import time
import os
import warnings

class League(object):
    """
    represents Football League

    """
    def __init__(self, name, season, members, delta_coefs, state_params = ("P",	"W","D","L","GF","GA","GD","PTS")):
        """

        :param name: League name and year
        :param members: list of teams
        :param delta_coefs: coefficients stored in values to compute ratings changing after match followed bby its result

        results is a list of dicts with following  attributes:
        # P - Played
        # W - Won
        # D - Drawn
        # L - Lost
        # GF - Goals For
        # GA - Goals Against
        # GD - Goal Difference
        # PTS - Points

        :return:
        """
        # super(League, self).__init__(name, season, members, delta_coefs)
        self.name = name
        self.season = season
        self.members = members
        self.delta_coefs = delta_coefs

        state = {st:0 for st in state_params}

        # initial results
        # after next block it will be filled by all state_params=0
        self.results = []

        # check self is League (not a subclass Cup)
        if "PTS" in state_params:
            print "\nWELCOME TO LEAGUE ***", name.upper(), season, "***"
            # initialize table
            for member in self.members:
                self.results.append(TeamResult(member, state).get4table())
            # print "self.results", self.results
            self.table = Table(self.results)
        # else its cup, so self.net will be created instead of table


    def __str__(self):
        """
        calls __str__ method of Table class
        """
        return str(self.table)

    def getName(self):
        return self.name

    def getMember(self, index = None):
        if index:
            return self.members[index]
        else:
            return self.members

    def getTable(self):
        return self.table

    def getWinner(self):
        return self.table.getTeam(0)["Team"]

    def getTeamByPosInTable(self, pos):
        return self.table.getTeam(pos)["Team"]

    def run(self, print_matches = False):
        """
        generate matches, every match team rating and result updates
        after all, table updates and returns
        """

        teams = self.getMember()
        teams_num = len(teams)

        tours = teams_num - 1
        rounds = 2 # rounds of league
        matches_in_tour = teams_num // 2
        # print "rounds = %s, teams_num = %s, matches_in_tour = %s" % (rounds, teams_num, matches_in_tour)

        # generate matches
        for round in range(rounds):
            for tour in range(tours):
                team_indexes = range(teams_num)
                for match_ind in range(matches_in_tour):

                    team1_ind = team_indexes.pop(0) # tour % len(team_indexes)
                    team2_ind = team_indexes.pop( -1  - tour  % len(team_indexes)  )

                    # define home and guest team
                    if not (tour % 2):
                        tindxs = (team1_ind, team2_ind)
                    else:
                        tindxs = (team2_ind, team1_ind)

                    pair = (teams[tindxs[0]], teams[tindxs[1]])

                    roundN = round + 1
                    tourN = tour + tours*(round) + 1
                    matchN = match_ind + 1 + (tourN - 1) * matches_in_tour
                    match = M.Match(pair, self.delta_coefs, "%s %s. round %s. tour %s(%s). match %s(%s)"  \
                                    % (self.getName(), self.season, roundN, tour+1, tourN, match_ind + 1, matchN))
                    match_score = match.run()
                    if print_matches:
                         print match

                    for i in range(len(pair)):
                        team_i = tindxs[i]
                        result = self.results[team_i]

                        # update results
                        result["P"] += 1

                        # if match.getWinner() == i: # WIN
                        if match.getOutcome() == i: # WIN
                            result["W"] += 1
                            result["PTS"] += 3

                        elif match.getOutcome() == 2: # DRAW
                            result["D"] += 1
                            result["PTS"] += 1

                        else:                        # LOSE
                            result["L"] += 1

                        gf =  match_score[i]
                        result["GF"] +=  gf      # goals of current team
                        ga = match_score[i-1]
                        result["GA"] +=  ga   # goals of opponent team
                        result["GD"] +=  (gf - ga)

        # update and return table
        return self.table.update(self.results)

    def test(self,print_matches = False, print_ratings = False):
        print "\nTEST LEAGUE CLASS"
        # print "initial Table:"
        # print self#.printTable()
        if print_matches: print "\nMatches:\n"
        self.run(print_matches)
        print "\nFinal Table:\n", self, "\n"
        print "Winner:\n%s\n" % self.getWinner()
        # ratings after league
        if print_ratings:
            print "updated ratings:"
            for team in self.getMember():
                print team.getName(), team.getRating()

    def saveData(self):
        #TODO save League Results in particial Table for season
        raise NotImplemented



class TeamResult():
    """
    represents results of team in league as dict
    """
    def __init__(self, team, state):
        self.result = state
        self.team = team

    def getTeam(self):
        return self.team

    def getState(self):
        return self.result

    def get4table(self):
        all = self.result.copy()
        all["Team"] = self.team.getName()
        return all

    def update(self, **kwargs):
        for key, value in kwargs.items():
            self.result[key] = value

# print TeamResult("aa", {"a":1, "b":2}).getAll()

class Table():
    """
    LeagueTable
    """
    def __init__(self, results):
        """

        :type self: object
        """
        self.table = []
        self.results = results
        self.table = sorted(self.results, key=itemgetter('PTS', 'GD', 'GF'), reverse=True) # ('PTS', 'GD', 'GF')

    def getTable(self):
        return self.table

    def getTeam(self, pos):
        return self.table[pos]

    def __str__(self):
        columns = ["Team", "P", "W", "D", "L", "GF", "GA", "GD", "PTS"]
        strRow = "            "
        for col in columns:
            strRow += col + "      "
        for ind, team in enumerate(self.table):
            strRow += "\n%s. " % (ind+1) + "     "
            for col in columns:
                strRow += str(team[col]) + "     "
        return strRow

    def update(self, results, team_inds = "all"):
        if team_inds == "all":
            self.results = results
        else:
            for team_ind in team_inds:
                self.results[team_ind] = results.pop()
        self.table = sorted(self.results, key=itemgetter('PTS', 'GD', 'GF'), reverse=True) # ('PTS', 'GD', 'GF')
        return self.table

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

        # # TEST LEAGUE CLASS
        if "League" in args:

            print_matches = False
            # print_matches = True

            print_ratings = False
            # print_ratings = True

            League("testLeague", "2015/2016", teams, coefs).test(print_matches, print_ratings)
            # League("testLeague", "2015/2016", teams, coefs).run()


        # TEST CUP CLASS
        if "Cup" in args:

            # for seeding in Cup.getSeedings(Cup):
            #     print seeding
            # pair_mode = 0 # one match
            pair_mode = 1 # home + guest every match but the final
            # pair_mode = 2 # home + guest every match

            print_matches = False
            # print_matches = True

            print_ratings = False
            # print_ratings = True

            s =  Cups.Cup("no Cup, just getSeedings", "", teams, coefs, pair_mode)
            seedings = s.getSeedings()
            # print "seedings", seedings
            for seeding in seedings:
                # print seeding , "seeding"
                # print "teams, coefs, pair_mode, seeding", teams, coefs, pair_mode, seeding
                tstcp = Cups.Cup("testCup", "2015/2016", teams, coefs, pair_mode, seeding)
                tstcp.test(print_matches, print_ratings)
            # # Cup("testCup", "2015/2016", teams, coefs, pair_mode).run()


    # Test("League", "Cup", team_num = 20)
    Test("League", team_num = 101)
    # Test("Cup", team_num = 20)