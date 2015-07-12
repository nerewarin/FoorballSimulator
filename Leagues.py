# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

import Team
import util
# import Cups
import Match as M
from values import Coefficients as C
from operator import attrgetter, itemgetter
from collections import defaultdict
import random
import time
import numbers
import math
import os
import warnings

class League(object):
    """
    represents Football League

    """
    def __init__(self, name, season, members, delta_coefs, pair_mode = 1, seeding = "rnd", state_params = ("P",	"W","D","L","GF","GA","GD","PTS")):
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
        self.seeding = seeding
        self.pair_mode = pair_mode


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
        if isinstance(index, int):
            return self.members[index]
        else:
            return self.members

    def getTable(self):
        return self.table

    def getWinner(self):
        if self.members:
            return self.table.getTeam(0)["Team"]
        else:
            warnings.warn("call getWinner from League with no members!")
            return "no winner cause no members"

    def getTeamByPosInTable(self, pos):
        return self.table.getTeam(pos)["Team"]


    def RunMatchUpdateResults(self, tindxs, roundN, tour, tourN, match_ind, matchN, print_matches):
        """
        helper func
        runs match and updates League result
        """
        # match = M.Match(pair, self.delta_coefs, "%s %s. round %s. tour %s(%s). match %s(%s)"  \
        #     % (self.getName(), self.season,
        #        roundN, tour+1, tourN+1,
        #        match_ind+1, matchN+1))

        # # define home and guest team
        # v1 count home matches for everu team
        # print "\self.home_mathes_count                                             ", self.home_mathes_count
        # # print "\n\nself.home_mathes_count", self.home_mathes_count, "\n"
        # if self.home_mathes_count[tindxs[0]] > self.home_mathes_count[tindxs[1]]:
        #     home_ind = tindxs[1]
        #     guest_ind = tindxs[0]
        # else:
        #     home_ind = tindxs[0]
        #     guest_ind = tindxs[1]
        # pair = (self.getMember(home_ind), self.getMember(guest_ind))

        # v2 count matches for every pair
        if tindxs in self.pair_host:
            # swap home-guest to guest-home
            home_ind = tindxs[1]
            guest_ind = tindxs[0]
        else:
            home_ind = tindxs[0]
            guest_ind = tindxs[1]

        pair = (self.getMember(home_ind), self.getMember(guest_ind))
        # check this pair config is new (there was not match with this teams with these home-guest roles)
        if (home_ind, guest_ind) in self.pair_host:
            raise Exception, "home-guest roles are not uniq for this pair!", pair

        self.pair_host.add((home_ind, guest_ind))


        # print self.getMember(home_ind)
        # print self.getMember(guest_ind)
        # print "pair",  pair

        match = M.Match(pair, self.delta_coefs, "%s %s. round %s. tour %s. match %s"
                        % (self.getName(), self.season, roundN, tourN+1, match_ind+1))
        match_score = match.run()
        self.home_mathes_count[home_ind] += 1

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


    def run(self, print_matches = False):
        """
        generate matches, every match team rating and result updates
        after all, table updates and returns
        """

        teams = self.getMember()
        teams_num = len(teams)

        tours = teams_num - 1

        # rounds of league
        rounds = 1
        if self.pair_mode:
            rounds += 1

        # TODO fix odd number of terams in League
        matches_in_tour = teams_num // 2
        # m_in_tour = teams_num / 2.0
        # matches_in_tour = int(m_in_tour)
        # if (math.floor( m_in_tour ) == m_in_tour):
        #     odd_match = False
        # else:
        #     # make additional logic
        #     odd_match = True



        # odd_pair is a list of rest teams (is teams num is odd) who did'nt meet a opponent in current tour
        # to meet another rest in the next tour
        odd_pair = []
        matchN = 0
        # make home teams count equal for every member
        # count matches played at home for every team by int index of members list
        self.home_mathes_count = {}
        for tind in range(len(self.members)):
            self.home_mathes_count[tind] = 0
        # v2 after every match, add tuple (home, guest) indexes to store this config and do not repeat
        # (swith home for next match of this pair)
        self.pair_host = set([])

        # generate matches
        for round in range(rounds):
            for tour in range(tours):
                if print_matches:
                    print "tour %s" % (tour + tours*(round) + 1)
                team_indexes = range(teams_num)
                for match_ind in range(matches_in_tour):

                    team1_ind = team_indexes.pop(0) # tour % len(team_indexes)
                    team2_ind = team_indexes.pop( -1  - tour  % len(team_indexes)  )

                    roundN = round + 1
                    tourN = tour + tours*(round)
                    # matchN = match_ind + 1 + (tourN - 1) * matches_in_tour
                    #
                    # define home and guest team
                    if not (tourN % 2):
                    # if not (matchN % 2):
                        tindxs = (team1_ind, team2_ind)
                    else:
                        tindxs = (team2_ind, team1_ind)

                    pair = (teams[tindxs[0]], teams[tindxs[1]])

                    tindxs = (team1_ind, team2_ind)

                    # match = M.Match(pair, self.delta_coefs, "%s %s. round %s. tour %s(%s). match %s(%s)"  \
                    #                 % (self.getName(), self.season, roundN, tour+1, tourN, match_ind + 1, matchN))
                    self.RunMatchUpdateResults(tindxs, roundN, tour, tourN, match_ind, matchN, print_matches)
                    matchN += 1


                # print "TOUR_COMPLETE!"
                # print "team_indexes %s" % team_indexes
                odd_pair.extend(team_indexes)
                if len(odd_pair) > 1:
                    tindxs = (odd_pair.pop(), odd_pair.pop())
                    # pair = (teams[tindxs[0]], teams[tindxs[1]])
                    self.RunMatchUpdateResults(tindxs, roundN, tour+1, tourN, match_ind + 1, matchN, print_matches)
                    matchN += 1

                elif len(odd_pair) > 2:
                    raise Exception, "ERROR in League.run - odd_pair list should not include more then two teams!"


                # # make additional match if len(members) is odd
                # if odd_match and (tour % 2):
                #     print "need odd_match!"
                #     # print "team_indexes %s" % team_indexes


        # check all values are the same, i.e.
        # all teams played exactly the same count of home matches
        # solution from http://stackoverflow.com/questions/17821079/how-to-check-if-two-keys-in-dict-hold-the-same-value
        dd = defaultdict(set)
        for k, v in self.home_mathes_count.items():
            dd[v].add(k)
        dd = { k : v for k, v in dd.items() if len(v) > 1 }
        if len(dd.keys()) != 1:
            print self.home_mathes_count
            raise Exception, "not all teams played exactly the same count of home matches, see above"

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
        print_matches = kwargs["print_matches"]
        print_ratings = kwargs["print_ratings"]

        for i in range(team_num):
            # teamN = i + 1
            teamN = i
            rating = team_num - i
            uefa_pos = teamN
            teams.append(Team.Team("FC team%s" % teamN, "RUS", rating, "Команда%s" % teamN, uefa_pos))

        # # TEST LEAGUE CLASS
        if "League" in args:

            League("testLeague", "2015/2016", teams, coefs).test(print_matches, print_ratings)
            # League("testLeague", "2015/2016", teams, coefs).run()


    team_num = 9
    Test("League", team_num = team_num, print_matches = True, print_ratings = False)
    # for team_num in range(102):
    #     Test("League", team_num = team_num, print_matches = True, print_ratings = False)

    # Test("Cup", team_num = 20)