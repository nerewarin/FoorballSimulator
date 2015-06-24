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
        # self.state = {}
        # for k, v in locals().iteritems():
        #     if len(k) < 4:
        #         self.state[k] = v
        state = {}
        for k, v in locals().iteritems():
            if len(k) < 4:
                state[k] = v

        # # initial results
        # self.results = {}
        # for member in self.members:
        #     self.results[member] = self.state
        # # print self.results
        # self.table = Table(self.results)

        # initial results
        self.results = []
        for member in self.members:
            self.results.append(TeamResult(member, state).get4table())
        # print self.results
        self.table = Table(self.results)



        # self.results = []
        # for member in self.members:
        #     self.results.append(TeamResults(member, self.state))
        # # print self.results

        # self.table = Table(self.results)

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
                matches = []
                counter += 1
                team_indexes = range(teams_num)
                # print type(team_indexes), team_indexes
                for match_ind in range(matches_in_tour):
                    # # team1_ind =  tour + match_ind
                    # # team2_ind =  - team1_ind - 1
                    # if match_ind == matches_in_tour - 1 and tour == tours - 1:
                    #     team1_ind = (match_ind + 1 ) % teams_num
                    # else:
                    #     team1_ind =  match_ind % teams_num
                    # team2_ind =  - (team1_ind + 1 + tour) % teams_num
                    # # print  team1_ind
                    # # print  team2_ind, "(", team1_ind + 1 + tour,  (- (team1_ind + 1 + tour)) % teams_num, ")"
                    #
                    # # while team1_ind == team2_ind:
                    # #     # team2_ind =- 1
                    # #     team2_ind -= 1
                    #
                    # # team1 = teams[team1_ind]
                    # # team2 = teams[team2_ind]


                    # print team_indexes
                    team1_ind = team_indexes.pop(0) # tour % len(team_indexes)
                    # team1_ind = team_indexes.pop(match_ind % len(team_indexes))
                    # team1_ind = team_indexes.pop(0)
                    # team1 = teams[team_indexes.pop(0)]
                    team1 = teams[team1_ind]
                    # print len(team_indexes) - tour, len(team_indexes)
                    # print len(team_indexes[1:])- tour, len(team_indexes)
                    # print [1][-1]
                    # team2_ind = team_indexes.pop( (len(team_indexes[1:]) - tour) % len(team_indexes)  )
                    team2_ind = team_indexes.pop( -1  - tour  % len(team_indexes)  )
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
                        tindxs = (team1_ind, team2_ind)
                        pair = (team1, team2)
                        # # print "round %s. tour %s (%s). match %s, %s | %s F" \
                        # #   % (roundN, tour_in_round, tourN, matchN, team1_ind + 1, team2_ind + 1)
                        # print "round %s. tour %s (%s). match %s, %s | %s F" \
                        #   % (roundN, tour_in_round, tourN, matchN, team1_ind , team2_ind )
                        # # print "team1_ind", team1_ind
                    else:
                        tindxs = (team2_ind, team1_ind)
                        pair = (team2, team1)
                        # # print "round %s. tour %s (%s). match %s, %s | %s" \
                        # #   % (roundN, tour_in_round, tourN, matchN, team2_ind + 1, team1_ind + 1)
                        # print "round %s. tour %s (%s). match %s, %s | %s" \
                        #   % (roundN, tour_in_round, tourN, matchN, team2_ind , team1_ind )

                    # print "round %s. tour %s (%s). match %s, %s - %s" \
                    #      % (roundN, tour_in_round, tourN, matchN, team1, team2)

                    #  CORRECT PRINT
                    # print "round %s. tour %s (%s). match %s, %s - %s" \
                    #      % (roundN, tour_in_round, tourN, matchN, pair[0], pair[1])

                    #     # TODO create matches
                    # match = M.Match(pair, self.deltaCoefs, self.getLeagueName() + str(tour + 1))


                    match = M.Match(pair, self.deltaCoefs, "%s round %s. tour %s. match %s"  \
                                    % (self.getLeagueName(), roundN, tourN, matchN))
                    match_score = match.run()
                    print match
                    # matches.append((pair, match))


                    # for i in range(len(pair)):
                    #     print "i", i
                    #     team = pair[i]
                    #     for team, result in self.results.iteritems():
                    #         print team, result
                    #     print type(self.results[team]), self.results[team]
                    #     for k,v in self.results[team].iteritems():
                    #         print team, k,v
                    #         if k == "P":
                    #             self.results[team]["P"] += 1

                        # self.results[team]["P"] += 1
                        # for team, result in self.results.iteritems():
                        #     print "updated", team, result

                    for res in self.results:
                        print res

                    for i in range(len(pair)):
                        # print "i", i
                        # team = pair[i]
                        team_i = tindxs[i]
                        # print team, team_ind
                        result = self.results[team_i]
                        # print result

                        # update results
                        result["P"] += 1

                        if match.getWinner() == i: # WIN
                            result["W"] += 1
                            result["PTS"] += 3
                        elif match.getWinner() == 2:
                            result["D"] += 1
                            result["PTS"] += 1
                        else:
                            result["L"] += 1

                        gf =  match_score[i]
                        result["GF"] +=  gf      # goals of current team
                        ga = match_score[i-1]
                        result["GA"] +=  ga   # goals of opponent team
                        result["GD"] +=  (gf - ga)

                    print "updated"
                    # print result
                    # print self.results
                    for res in self.results:
                        print res
                    print


                    #     for team, result in self.results.iteritems():
                    #         print team, result
                    #     print type(self.results[team]), self.results[team]
                    #     for k,v in self.results[team].iteritems():
                    #         print team, k,v
                    #         if k == "P":
                    #             self.results[team]["P"] += 1
                    # print self.results[team1_ind]
                    # print self.results[team2_ind]
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

        self.table.update(self.results)
        return self.table

class TeamResult():
    """
    represemts results of team in league as dict
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
            # print '{0} = {1}'.format(name, value)

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
        # for team, result in self.results.iteritems():
        #    self.table.append([team.getName(), result['P'], result['W'], result['D'], result['L'],
        #                                       result['GF'],result['GA'], result['GD'], result['PTS']])
        # self.table = sorted(self.table, key=itemgetter(-1, -2, -4)) # ('PTS', 'GD', 'GF')

        # for result in self.results:
        #     print result

        self.table = sorted(self.results, key=itemgetter('PTS', 'GD', 'GF'), reverse=True) # ('PTS', 'GD', 'GF')

    def getTable(self):
        return self.table

    def __str__(self):
        columns = ["Team", "P", "W", "D", "L", "GF", "GA", "GD", "PTS"]
        strRow = ""
        for col in columns:
            strRow += col + " "
        # for row in self.table:
        for ind, team in enumerate(self.table):
            strRow += "\n"
            for col in columns:
                # print ind, team, col
                strRow += str(team[col]) + " "
            # for col in row:
            #     strRow += str(col) + " "
        return strRow

    def update(self, results, team_inds = "all"):
        # TODOself.table
        if team_inds == "all":
            self.results = results
        else:
            for team_ind in team_inds:
                self.results[team_ind] = results.pop()
        self.table = sorted(self.results, key=itemgetter('PTS', 'GD', 'GF'), reverse=True) # ('PTS', 'GD', 'GF')
        #
        # # raise NotImplementedError
        # for ind in len(teams):

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
    testLeague = League("testLeague", teams, coefs)
    # testLeague.getTable()
    print "initial Table:"
    print testLeague#.printTable()
    print "\nMatches:"
    testLeague.run()
    print "Final Table:\n", testLeague
    for team in teams:
        print team.getRating()

