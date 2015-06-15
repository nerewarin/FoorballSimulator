__author__ = 'NereWARin'
# -*- coding: utf-8 -*-
import Team
import Match as M
from values import Coefficients as C

class League():
    def __init__(self, members, name):
        """

        :param name:
        :param members: list of teams
        :return:
        """
        self.name = name
        self.members = members
        self.statistics = {} # scores, goals +, -, difference

        self.results = {}

        P,	W,	D,	L,	GF,	GA,	GD,	PTS = 0,0,0,0,0,0,0,0
        atributes = [P,	W,	D,	L,	GF,	GA,	GD,	PTS]
        # P	= 0
        # W	= 0
        # D 	= 0
        # L	= 0
        # GF	= 0
        # GA	= 0
        # GD	= 0
        # PTS = 0

        for member in self.members:
            self.results[member] = atributes
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
        for ind, team in enumerate(self.members):
            # TODO
            GF, GD, PTS = 0,0,0
            self.table.append([ind+1, team.getName(), GF, GD, PTS])
        # for

    def getTable(self):
        return self.table

    def printTable(self):
        for row in self.table:
            strRow = ""
            for col in row:
                strRow += str(col) + " "
            print strRow

    def updateTable(self, teams, result):
        # TODO
        raise NotImplementedError

    def run(self):
        # opponents = self.getMember()
        matchNum = 0
        for team1 in self.getMember():
            for team2 in self.getMember():
                if team1 != team2:
                    matchNum += 1
                    match = M.Match((team1, team2), C(VERSION).getRatingUpdateCoefs(), matchNum)
                    match.run()
                    print match.printResult()
        for team1 in self.getMember():
            for team2 in self.getMember():
                if team1 != team2:
                    matchNum += 1
                    match = M.Match((team1, team2), C(VERSION).getRatingUpdateCoefs(), matchNum)
                    match.run()
                    print match.printResult()
            # self, members, deltaCoefs, name = "no name match"):
            # TODO
            # raise NotImplementedError


# TEST
if __name__ == "__main__":
    VERSION = "v1.1"
    print "\nTEST LEAGUE CLASS\n"
    team1 = Team.Team("Manchester City FC", "ENG", 87.078, "Манчестер Сити", 17)
    team2 = Team.Team("FC Shakhtar Donetsk", "UKR", 85.899, "Шахтер Донецк", 18)
    team3 = Team.Team("Juventus", "ITA", 90.935, "Ювентус", 14)
    testLeague = League([team1,team2,team3], "testLeague")
    print testLeague.getTable()
    testLeague.printTable()
    testLeague.run()
    # for i in range(10):
    #     testMatch = Match((team1, team2), "testMatch%s" % (i + 1))
    #     testMatch.run()
    #     print testMatch.printResult()
    # for i in range(10):
    #     testMatch = Match((team2, team1), "testMatch%s" % (i + 11))
    #     testMatch.run()
    #     print testMatch.printResult()
