__author__ = 'NereWARin'
# -*- coding: utf-8 -*-
import Team

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
        self.createTable()

    def getLeagueName(self):
        return self.name

    def getMember(self, index = None):
        if teamName:
            return self.members[index]
        else:
            return self.members

    def createTable(self):
        self.table = []
        for ind, team in enumerate(self.members):
            # TODO
            self.table.append([ind+1, team.getName(), 0])

    def getTable(self):
        return self.table

    def printTable(self):
        for row in self.table:
            strRow = ""
            for col in row:
                strRow += str(col) + " "
            print strRow

    def updateTable(self):
        # TODO
        raise NotImplementedError

    def run(self):
        # opponents = self.getMember()
        for team in self.getMember():
            # TODO
            raise NotImplementedError


# TEST
if __name__ == "__main__":
    print "\nTEST LEAGUE CLASS\n"
    team1 = Team.Team("Manchester City FC", "ENG", 87.078, "Манчестер Сити", 17)
    team2 = Team.Team("FC Shakhtar Donetsk", "UKR", 85.899, "Шахтер Донецк", 18)
    team3 = Team.Team("Juventus", "ITA", 90.935, "Ювентус", 14)
    testLeague = League([team1,team2,team3], "testLeague")
    print testLeague.getTable()
    testLeague.printTable()
    # for i in range(10):
    #     testMatch = Match((team1, team2), "testMatch%s" % (i + 1))
    #     testMatch.run()
    #     print testMatch.printResult()
    # for i in range(10):
    #     testMatch = Match((team2, team1), "testMatch%s" % (i + 11))
    #     testMatch.run()
    #     print testMatch.printResult()
