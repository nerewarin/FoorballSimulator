__author__ = 'NereWARin'
# -*- coding: utf-8 -*-
import Team
import util
import Match as M
from values import Coefficients as C
from operator import attrgetter, itemgetter

class League():
    """
    represents Football League

    """
    def __init__(self, name, season, members, delta_coefs):
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
        self.name = name
        self.season = season
        self.members = members
        self.delta_coefs = delta_coefs
        # self.statistics = {} # scores, goals +, -, difference

        # statistics/results of team in league
        # column names given from http://www.premierleague.com/en-gb/matchday/league-table.html
        P,	W,	D,	L,	GF,	GA,	GD,	PTS = 0,0,0,0,0,0,0,0

        # collect state attributes to dict (exclude league name, members and etc)
        state = {}
        for k, v in locals().iteritems():
            if len(k) < 4:
                state[k] = v

        # initial results
        self.results = []
        for member in self.members:
            self.results.append(TeamResult(member, state).get4table())
        # print self.results
        self.table = Table(self.results)

    def __str__(self):
        """
        calls __str__ method of Table class
        """
        return str(self.table)

    def getLeagueName(self):
        return self.name

    def getMember(self, index = None):
        if index:
            return self.members[index]
        else:
            return self.members

    def run(self):
        """
        generate matches, every match team rating and result updates
        after all, table updates and returns
        """
        teams = self.getMember()
        # for team in teams:
        #     print team#, type(team)

        teams_num = len(teams)
        tours = teams_num - 1
        rounds = 2 # rounds of league
        matches_in_tour = teams_num // 2
        print "rounds = %s, teams_num = %s, matches_in_tour = %s" % (rounds, teams_num, matches_in_tour)

        # generate matches
        for round in range(rounds):
            for tour in range(tours):
                team_indexes = range(teams_num)
                for match_ind in range(matches_in_tour):

                    team1_ind = team_indexes.pop(0) # tour % len(team_indexes)
                    team2_ind = team_indexes.pop( -1  - tour  % len(team_indexes)  )

                    roundN = round + 1
                    tourN = tour + tours*(round) + 1
                    matchN = match_ind + 1 + (tourN - 1) * matches_in_tour
                    # print "round %s. tour %s (%s). match %s, team1 = %s , team2 = %s" \

                    # define home and guest team
                    if not (tour % 2):
                        tindxs = (team1_ind, team2_ind)
                    else:
                        tindxs = (team2_ind, team1_ind)

                    pair = (teams[tindxs[0]], teams[tindxs[1]])
                    match = M.Match(pair, self.delta_coefs, "%s %s. round %s. tour %s. match %s"  \
                                    % (self.getLeagueName(), self.season, roundN, tourN, matchN))
                    match_score = match.run()
                    print match

                    # for res in self.results:
                    #     print res

                    for i in range(len(pair)):
                        team_i = tindxs[i]
                        result = self.results[team_i]

                        # update results
                        result["P"] += 1

                        if match.getWinner() == i: # WIN
                            result["W"] += 1
                            result["PTS"] += 3

                        elif match.getWinner() == 2: # DRAW
                            result["D"] += 1
                            result["PTS"] += 1

                        else:                        # LOSE
                            result["L"] += 1

                        gf =  match_score[i]
                        result["GF"] +=  gf      # goals of current team
                        ga = match_score[i-1]
                        result["GA"] +=  ga   # goals of opponent team
                        result["GD"] +=  (gf - ga)

                    # print "updated"
                    # for res in self.results:
                    #     print res
                    # print

        # update and return rable
        return self.table.update(self.results)

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

    def __str__(self):
        columns = ["Team", "P", "W", "D", "L", "GF", "GA", "GD", "PTS"]
        strRow = ""
        for col in columns:
            strRow += col + " "
        for ind, team in enumerate(self.table):
            strRow += "\n"
            for col in columns:
                strRow += str(team[col]) + " "
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
    # VERSION = "v1.1"
    import os
    with open(os.path.join("", 'VERSION')) as version_file:
        values_version = version_file.read().strip()
    coefs = C(values_version).getRatingUpdateCoefs("list")

    print "\nTEST LEAGUE CLASS\n"
    # team1 = Team.Team("Manchester City FC", "ENG", 87.078, "Манчестер Сити", 17)
    # team2 = Team.Team("FC Shakhtar Donetsk", "UKR", 85.899, "Шахтер Донецк", 18)
    # team3 = Team.Team("Juventus", "ITA", 90.935, "Ювентус", 14)
    # team4 = Team.Team("FC Spartak Moskva", "RUS", 37.099, "Спартак Москва", 56)
    team1 = Team.Team("FC team1", "RUS", 836.099, "team1", 571)
    team2 = Team.Team("FC team2", "RUS", 736.099, "team2", 572)
    team3 = Team.Team("FC team3", "RUS", 636.099, "team3", 573)
    team4 = Team.Team("FC team4", "RUS", 536.099, "team4", 574)
    team5 = Team.Team("FC team5", "RUS", 436.099, "team5", 575)
    team6 = Team.Team("FC team6", "RUS", 436.099, "team6", 576)
    team7 = Team.Team("FC team7", "RUS", 336.099, "team7", 577)
    team8 = Team.Team("FC team8", "RUS", 236.099, "team8", 578)
    # teams = [team1,team2,team3, team4]
    teams = [team1,team2,team3, team4, team5,team6,team7, team8]
    testLeague = League("testLeague", "2015/2016", teams, coefs)
    # testLeague.getTable()
    print "initial Table:"
    print testLeague#.printTable()
    print "\nMatches:"
    testLeague.run()
    print "\nFinal Table:\n", testLeague, "\n"
    for team in teams:
        print team.getName(), team.getRating()