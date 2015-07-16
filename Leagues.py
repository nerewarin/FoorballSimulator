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
import collections
import os
import warnings
from copy import copy, deepcopy

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

        home_ind, guest_ind = tindxs


        pair = (self.getMember(home_ind), self.getMember(guest_ind))

        # for now self.pair_host uses in another way...
        # # check this pair config is new (there was not match with this teams with these home-guest roles)
        # if (home_ind, guest_ind) in self.pair_host:
        #     print "pair = ", [team.getName() for team in pair]
        #     # raise Exception, "home-guest roles are not uniq for this pair!"
        #     raise Exception, "home-guest roles are not uniq for this pair!"
        #
        # # self.pair_host.add((home_ind, guest_ind))

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
        if teams_num < 2:
            return self.table

        matches_in_tour = teams_num // 2

        odd_league = teams_num % 2

        # round robin https://ru.wikipedia.org/wiki/%D0%9A%D1%80%D1%83%D0%B3%D0%BE%D0%B2%D0%B0%D1%8F_%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0
        matches_in_tour += odd_league
        tours = teams_num - 1 + odd_league

        # if 0, first match starts with favorite at home (as guest otherwise)
        # it is important in leagues of two members and pair_mode = 0, cause only one match is played in this case
        self.rnd_role = random.randint(0,1)
        if print_matches:
            print "self.rnd_role" , self.rnd_role

        # rounds of league
        rounds = 1
        if self.pair_mode:
            rounds += 1

        # for check RoundRobin only! - comment it or move to test section if slows the execution
        # make home teams count equal for every member
        # count matches played at home for every team by int index of members list
        self.home_mathes_count = {}
        for tind in range(len(self.members)):
            self.home_mathes_count[tind] = 0

        iter_teamind = range(teams_num)

        matchN = 0 # sequentially numbered
        if print_matches:
            print "self.pair_mode = %s" % self.pair_mode
            print "teams_num = %s" % teams_num

        # generate matches
        for round in range(rounds):

            if print_matches:
                print "\nround %s" % (round + 1)

            # define shedule generator
            shedule_gen = roundRobin(iter_teamind)

            # for pair in roundRobin(range(team_num)):
            #     # print "__", pairings
            #     print pair

            # v3 store last match role for every team as a boolean
            self.pair_host = {}
            for tind in range(len(self.members)):
                # 0 is False, 1 (second round) is True
                self.pair_host[tind] = round


            team_indexes = list(iter_teamind)

            # if odd_league:
            #     # in round robin we append "rest" symbol means that if opponent == rest, this team skips this round
            #     team_indexes.append(rest)

            # for tour in range(tours):
            for tour, parings in enumerate(shedule_gen):
                if print_matches:
                    print "tour %s of %s" % (tour + 1, tours*(rounds))

                roundN = round + 1
                tourN = tour + tours*(round)

                for match_ind, pair in enumerate(parings):

                    if not match_ind and tour % 2:
                        pair = (pair[1], pair[0])

                    if (self.rnd_role + round ) % 2:
                        tindxs = (pair[1], pair[0])
                    else:
                        tindxs = pair

                    matchN += 1

                    # self.RunMatchUpdateResults(tindxs, roundN, tour, tourN, match_ind + prefix, matchN, print_matches)
                    self.RunMatchUpdateResults(tindxs, roundN, tour, tourN, match_ind, matchN, print_matches)



        # print self.home_mathes_count
        # check all values are the same, i.e.
        # all teams played exactly the same count of home matches
        # solution from http://stackoverflow.com/questions/17821079/how-to-check-if-two-keys-in-dict-hold-the-same-value
        dd = defaultdict(set)
        for k, v in self.home_mathes_count.items():
            dd[v].add(k)
        dd = { k : v for k, v in dd.items() if len(v) > 1 }
        # print "ddd", dd


        if len(dd.keys()) > 1:
            print "home_mathes_count by team index are ", self.home_mathes_count

            if (not odd_league) and (self.pair_mode == 0):
                if len(dd.keys()) == 2:
                    # "its ok to be like 7/8 matches in league of 16 teams (15 rounds, odd)"
                    # warnings.warn("no way to fix, its math! maybe I shall add random for computing home-guest roles if equality of its count unreachable")
                    return self.table.update(self.results)

            print "ddd_error"
            for k,v in dd.iteritems():
                print k,v

            raise Exception, "not all teams played exactly the same count of home matches, see above"
            #     warnings.warn("maybe I shall add random for computing home-guest roles if equality of its count unreachable")
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


def roundRobin(units, sets=None):
    """ Generates a schedule of "fair" pairings from a list of units """
    if len(units) % 2:
        units.append(None)
    count    = len(units)
    sets     = sets or (count - 1)
    half     = count / 2
    schedule = []
    for turn in range(sets):
        pairings = []
        for i in range(half):
            # print "i", i
            pair = (units[i], units[count-i-1])
            if not None in pair:
                pairings.append(pair)
            # pairings.append((units[i], units[count-i-1]))
        units.insert(1, units.pop())
        # print "pairings", pairings

        yield pairings
    # return schedule



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
        pair_mode = kwargs["pair_mode"]

        for i in range(team_num):
            # teamN = i + 1
            teamN = i
            rating = team_num - i
            uefa_pos = teamN
            teams.append(Team.Team("FC team%s" % teamN, "RUS", rating, "Р С™Р С•Р СР В°Р Р…Р Т‘Р В°%s" % teamN, uefa_pos))

        # # TEST LEAGUE CLASS
        if "League" in args:

            League("testLeague", "2015/2016", teams, coefs, pair_mode).test(print_matches, print_ratings)
            # League("testLeague", "2015/2016", teams, coefs).run()

        if "roundRobin" in args:
            print "TEST roundRobin"
            # for team_l in range(team_num):
                # for pair in roundRobin(range(team_l)):
            for pair in roundRobin(range(team_num)):
                # print "__", pairings
                print pair

    # team_num = 3
    # for pair_mode in range(2):
    #     Test("League", team_num = team_num, pair_mode = pair_mode, print_matches = True, print_ratings = False)

    start_num = 20
    end_num = 21
    step = 1
    # pair_modes = (0, )
    pair_modes = (1, )
    # pair_modes = (0, 1)
    # print_matches = True
    print_matches = False
    print_ratings = False
    for t_num in range(start_num, end_num, 1):
        for pair_mode in pair_modes:
            print "\nt_num = %s\n" % t_num
            Test("League", team_num = t_num, pair_mode = pair_mode, print_matches = print_matches, print_ratings = print_ratings)
            # Test("roundRobin", team_num = t_num, pair_mode = pair_mode, print_matches = print_matches, print_ratings = print_ratings)