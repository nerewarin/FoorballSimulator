__author__ = 'NereWARin'
# -*- coding: utf-8 -*-
import Team
import util
import Match as M
from values import Coefficients as C
from operator import attrgetter, itemgetter

class League():
    """
    represents Foorball League

    """
    def __init__(self, name, members, deltaCoefs):
        """

        :param name: League name and year
        :param members: list of teams
        :param deltaCoefs: coefficients stored in values to compute ratings changing after match followed bby its result
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
        # print self.results
        self.table = Table(self.results)

        # self.results = []
        # for member in self.members:
        #     self.results.append(TeamResults(member, self.state))
        # # print self.results

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
        # teams = self.getMember()
        # rounds = len(teams)
        #
        # for round_num in range(1, 2 * rounds):
        #     if round_num < rounds:
        #         team1 = team2... # home . guest change

        # opponents = self.getMember()
        # matchNum = 0
        # teams list - favorites first
        # for t in self.getMember():
        #     print t

        teams = self.getMember()
        for team in teams:
            print team#, type(team)
        # favorites = self.getMember()
        # # for t in favorites:
        # #     print t
        # # teams list - outsiders first
        # outsiders = reversed(favorites)

        teams_num = len(teams)
        # teams_num = len(favorites)
        tours = teams_num - 1
        # rounds = teams_num * 2
        # for every pair of teams, create 2 matches -  Home and Guest (two rounds)
        rounds = 2 # круги чемпионата
        matches_in_round = util.edges_of_figure(teams_num)
        matches_in_tour = teams_num // 2
        print "rounds = %s, teams_num = %s, matches_in_tour = %s" % (rounds, teams_num, matches_in_tour)

        # hometeam switcher
        counter = 0
        for round in range(rounds):
            for tour in range(tours):
                counter += 1
                team_indexes = range(teams_num)
                # print type(team_indexes), team_indexes
                for match_ind in range(matches_in_tour):
                    # team1_ind =  tour + match_ind
                    # team2_ind =  - team1_ind - 1
                    if match_ind == matches_in_tour - 1 and tour == tours - 1:
                        team1_ind = (match_ind + 1 ) % teams_num
                    else:
                        team1_ind =  match_ind % teams_num
                    team2_ind =  - (team1_ind + 1 + tour) % teams_num
                    # print  team1_ind
                    # print  team2_ind, "(", team1_ind + 1 + tour,  (- (team1_ind + 1 + tour)) % teams_num, ")"

                    # while team1_ind == team2_ind:
                    #     # team2_ind =- 1
                    #     team2_ind -= 1

                    # team1 = teams[team1_ind]
                    # team2 = teams[team2_ind]


                    # print team_indexes
                    team1_ind = team_indexes.pop(tour % len(team_indexes))
                    # team1_ind = team_indexes.pop(match_ind % len(team_indexes))
                    # team1_ind = team_indexes.pop(0)
                    # team1 = teams[team_indexes.pop(0)]
                    team1 = teams[team1_ind]
                    team2_ind = team_indexes.pop()
                    # team2 = teams[team_indexes.pop()]
                    team2 = teams[team2_ind]
                    # print team1_ind, team2_ind, team_indexes
                    # print team1, team2

                    roundN = round + 1
                    tour_in_round = tour + 1
                    tourN = tour + tours*(round) + 1
                    matchN = match_ind + 1 + (tourN - 1) * matches_in_tour
                    # print "round %s. tour %s (%s). match %s, team1 = %s , team2 = %s" \


                    # define home and guest team
                    if counter % 2:
                        pair = (team1, team2)
                        # print "round %s. tour %s (%s). match %s, %s | %s F" \
                        #   % (roundN, tour_in_round, tourN, matchN, team1_ind + 1, team2_ind + 1)
                        print "round %s. tour %s (%s). match %s, %s | %s F" \
                          % (roundN, tour_in_round, tourN, matchN, team1_ind , team2_ind )
                        # print "team1_ind", team1_ind
                    else:
                        pair = (team2, team1)
                        # print "round %s. tour %s (%s). match %s, %s | %s" \
                        #   % (roundN, tour_in_round, tourN, matchN, team2_ind + 1, team1_ind + 1)
                        print "round %s. tour %s (%s). match %s, %s | %s" \
                          % (roundN, tour_in_round, tourN, matchN, team2_ind , team1_ind )

                    # print "round %s. tour %s (%s). match %s, %s - %s" \
                    #      % (roundN, tour_in_round, tourN, matchN, team1, team2)

                    #  CORRECT PRINT
                    # print "round %s. tour %s (%s). match %s, %s - %s" \
                    #      % (roundN, tour_in_round, tourN, matchN, pair[0], pair[1])

                    #     # TODO create matches
                    # match = M.Match(pair, self.deltaCoefs, self.getLeagueName() + str(tour + 1))


                    # match = M.Match(pair, self.deltaCoefs, "%s round %s. tour %s. match %s"  \
                    #                 % (self.getLeagueName(), roundN, tourN, matchN))
                    # match.run()
                    # print match

        # for tour in range(tours * rounds):
        # # for team1 in favorites:
        #     print "tour", tour + 1
        #     # print "round % teams_num", round % teams_num
        #     # team1 = favorites[tour % tours]
        #     team1 = favorites[tour % teams_num]
        #     print "team1", team1


            # for team2 in outsiders:
            # # for team2 in outsiders:
            # #     print "outsiders", outsiders
            #     print "team2", team2
            #     if team1 != team2:
            #         if tour % 2:
            #             pair = (team2, team1)
            #         else:
            #             pair = (team1, team2) # leader at home
            #         # matchNum += 1
            #         match = M.Match(pair, self.deltaCoefs, self.getLeagueName() + str(tour + 1))
            #         match.run()
            #         print match

        #
        # for team1 in self.getMember():
        #     for team2 in self.getMember():
        #         if team1 != team2:
        #             matchNum += 1
        #             match = M.Match((team1, team2), self.deltaCoefs, self.getLeagueName() + str(matchNum))
        #             match.run()
        #             print match.printResult()
        #     # self, members, deltaCoefs, name = "no name match"):
        #     # TODO update ratings
        #     # raise NotImplementedError
        return None

class TeamResults():
    """
    represemts results of team in league as dict
    """
    def __init__(self, team, state):
        self.result = state
        self.team = team
        # self.name =

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
         for team, result in self.results.iteritems():
            self.table.append([team.getName(), result['P'], result['W'], result['D'], result['L'],
                                               result['GF'],result['GA'], result['GD'], result['PTS']])
            # self.table.append({team.getName():result})
            # self.table.append({team.getName(), result})

         # print "unsorted table", self.table

         # self.table = sorted(self.table, key=attrgetter('PTS', 'GD', 'GF'))
         # self.table = sorted(self.table, key=itemgetter(1)['PTS'], itemgetter(1)['GD'], itemgetter(1)['GF'])
         self.table = sorted(self.table, key=itemgetter(-1, -2, -4)) # ('PTS', 'GD', 'GF')
         # self.table = sorted(self.table, key=__getitem__
         # itemgetter(1)['PTS'], itemgetter(1)['GD'], itemgetter(1)['GF'])

         # print "sorted table", self.table

    def getTable(self):
        return self.table

    def __str__(self):
        strRow = "Team, P, W, D, L, GF, GA, GD, PTS"
        for row in self.table:
            strRow += "\n"
            for col in row:
                strRow += str(col) + " "
        return strRow

    def updateTable(self, teams, result):
        # TODO
        raise NotImplementedError

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
    team4 = Team.Team("FC Spartak Moskva", "RUS", 37.099, "Спартак Москва", 56)
    team5 = Team.Team("FC team5", "RUS", 36.099, "team5", 57)
    team6 = Team.Team("FC team6", "RUS", 36.099, "team6", 57)
    team7 = Team.Team("FC team7", "RUS", 36.099, "team7", 57)
    team8 = Team.Team("FC team8", "RUS", 36.099, "team8", 57)
    # testLeague = League("testLeague", [team1,team2,team3, team4], coefs)
    testLeague = League("testLeague", [team1,team2,team3, team4, team5,team6,team7, team8], coefs)
    # testLeague.getTable()
    print "initial Table:"
    print testLeague#.printTable()
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

