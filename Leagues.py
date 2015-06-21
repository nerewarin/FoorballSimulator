__author__ = 'NereWARin'
# -*- coding: utf-8 -*-
import Team
import Match as M
from values import Coefficients as C

class League():
    """
    represents Foorball League

    """
    def __init__(self, name, members, deltaCoefs):
        """

        :param name:
        :param members: list of teams
        :return:
        """
        self.name = name
        self.members = members
        self.deltaCoefs = deltaCoefs
        # self.statistics = {} # scores, goals +, -, difference

        # statistics/results of team in league
        # column names fet from http://www.premierleague.com/en-gb/matchday/league-table.html
        P,	W,	D,	L,	GF,	GA,	GD,	PTS = 0,0,0,0,0,0,0,0
        # P - Played
        # W - Won
        # D - Drawn
        # L - Lost
        # GF - Goals For
        # GA - Goals Against
        # GD - Goal Difference
        # PTS - Points

        # self.state = [P,	W,	D,	L,	GF,	GA,	GD,	PTS]
        # collect state attributes to dict (exclude league name, members and etc)
        self.state = {}
        for k, v in locals().iteritems():
            if len(k) < 4:
                self.state[k] = v

        # initial results
        self.results = {}
        for member in self.members:
            self.results[member] = self.state
        self.createTable()


    def getLeagueName(self):
        return self.name

    def getMember(self, index = None):
        if index:
            return self.members[index]
        else:
            return self.members

    def createTable(self):
         self.table = []
         for team, result in self.results.iteritems():
            self.table.append([team.getName(), result['P'], result['W'], result['D'], result['L'],
                                               result['GF'],result['GA'], result['GD'], result['PTS']])
         return None

    def getTable(self):
        return self.table

    def printTable(self):
        strRow = "Team, P, W, D, L, GF, GA, GD, PTS"
        for row in self.table:
            strRow += "\n"
            for col in row:
                strRow += str(col) + " "
        print strRow

    def updateTable(self, teams, result):
        # TODO
        raise NotImplementedError

    def run(self):
        # teams = self.getMember()
        # rounds = len(teams)
        #
        # for round_num in range(1, 2 * rounds):
        #     if round_num < rounds:
        #         team1 = team2... # home . guest change

        # opponents = self.getMember()
        matchNum = 0
        for team1 in self.getMember():
            for team2 in self.getMember():
                if team1 != team2:
                    matchNum += 1
                    match = M.Match((team1, team2), self.deltaCoefs, self.getLeagueName() + str(matchNum))
                    match.run()
                    print match.printResult()
        for team1 in self.getMember():
            for team2 in self.getMember():
                if team1 != team2:
                    matchNum += 1
                    match = M.Match((team1, team2), self.deltaCoefs, self.getLeagueName() + str(matchNum))
                    match.run()
                    print match.printResult()
            # self, members, deltaCoefs, name = "no name match"):
            # TODO
            # raise NotImplementedError


# TEST
if __name__ == "__main__":
    # VERSION = "v1.1"
    import os
    with open(os.path.join("", 'VERSION')) as version_file:
        values_version = version_file.read().strip()
    coefs = C(values_version).getRatingUpdateCoefs("list")

    print "\nTEST LEAGUE CLASS\n"
    team1 = Team.Team("Manchester City FC", "ENG", 87.078, "Манчестер Сити", 17)
    team2 = Team.Team("FC Shakhtar Donetsk", "UKR", 85.899, "Шахтер Донецк", 18)
    team3 = Team.Team("Juventus", "ITA", 90.935, "Ювентус", 14)
    testLeague = League("testLeague", [team1,team2,team3], coefs)
    # testLeague.getTable()
    print "initial Table:"
    testLeague.printTable()
    print "\nMatches:"
    testLeague.run()
    # for i in range(10):
    #     testMatch = Match((team1, team2), "testMatch%s" % (i + 1))
    #     testMatch.run()
    #     print testMatch.printResult()
    # for i in range(10):
    #     testMatch = Match((team2, team1), "testMatch%s" % (i + 11))
    #     testMatch.run()
    #     print testMatch.printResult()
