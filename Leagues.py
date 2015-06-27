# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

import Team
import util
import Match as M
from values import Coefficients as C
from operator import attrgetter, itemgetter
import random
import time
import os


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
        self.results = []

        # check self is League (not a subclass Cup)
        if "PTS" in state_params:
            print "WELCOME TO LEAGUE ***", name.upper(), season, "***"
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

                    # define home and guest team
                    if not (tour % 2):
                        tindxs = (team1_ind, team2_ind)
                    else:
                        tindxs = (team2_ind, team1_ind)

                    pair = (teams[tindxs[0]], teams[tindxs[1]])

                    roundN = round + 1
                    tourN = tour + tours*(round) + 1
                    matchN = match_ind + 1 + (tourN - 1) * matches_in_tour
                    # print "round %s. tour %s (%s). match %s, team1 = %s , team2 = %s" \
                    match = M.Match(pair, self.delta_coefs, "%s %s. round %s. tour %s. match %s"  \
                                    % (self.getName(), self.season, roundN, tourN, matchN))
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

    def test(self):
        print "\nTEST LEAGUE CLASS\n"
        print "initial Table:"
        print self#.printTable()
        print "\nMatches:"
        self.run()
        print "\nFinal Table:\n", self, "\n"
        # ratings after league
        for team in self.getMember():
            print team.getName(), team.getRating()

    def saveData(self):
        #TODO save League Results in particial Table for season
        raise NotImplemented

class Cup(League):
    """
    represents Cup, some methods from League were overridden
    """
    # TODO search for Cup state , then override __ini__ or add list of state keys to parameters of __init__ \
    # its about         P,	W,	D,	L,	GF,	GA,	GD,	PTS = 0,0,0,0,0,0,0,0
    def __init__(self, name, season, members, delta_coefs, pair_mode = 1, state_params = ("final_stage", )):
        """

        :param name:
        :param season:
        :param members: should be in seeding order (1place_team, 2place_team...) . net will ve provided by that class itself
        :param delta_coefs:
        :param pair_mode: 0 - one match in pair, 1 - home & guest but the final , 2 - always home & guest
        :return:
        """
        # super(self.__class__, self).__init__(name, season, members, delta_coefs)#(self, name, season, members, delta_coefs)
        super(Cup, self).__init__(name, season, members, delta_coefs, state_params)#(self, name, season, members, delta_coefs)
        self.pair_mode = pair_mode
        # print "Cup_ini_results",self.results
        self.net = "not implemented yet"

        # self.results - empty list. after run() it will be filled as following:
        # [team_champion, team_finished_in_final, teams_finished_in_semi-final, ... , teams_finished_in_qualRoundn, ...
        # teams_finished_in_qualRound1# ]

    def __str__(self):
        return self.net

    def rounds_count(self,teams_num):
        """
         define rounds count
        """
        if teams_num < 2:
            raise Exception, "no teams to run cup"
        # remaining teams number
        rem_tn = teams_num / 2.0

        # play-off rounds num
        p_rounds = 1
        while rem_tn >= 2:
            rem_tn = rem_tn / 2
            p_rounds += 1

        # qualification rounds num
        q_rounds = 0
        if rem_tn != 1.0:
            q_rounds += 1
        return p_rounds, q_rounds

    def run(self):
        """
        generate matches, every match team rating and result updates
        after all, table updates and returns
        """
        teams = self.getMember()
        teams_num = len(teams)
        # for team in teams:
        #     print team#, type(team)

        # remaining teams
        rem_teams = list(teams)
        # if objects in list need to be independent from 1st list, use deepcopy
        # import copy
        # rem_teams = copy.deepcopy(teams)
        # print teams
        # print rem_teams
        # rem_teams[1].setRating(-100)
        # print teams[1].getRating()
        # print rem_teams[1].getRating()

        # seeding
        # 14-team cup example

        # play-off                                          *
        # round 1 (final)                   *                                 *
        # round 2 (semi-final)      *                *               *                 *
        # round 3 (1/4 final)    1     8         4      5         2      7         3      6
        # qualification
        # round 4 (qual 1)            8 9       4 13   5 12             7 10      3 14   6 11
        # // number = index in members + 1



        def PQplaces(p_rounds, q_rounds):
            """
            p_rounds - number of play-off rounds in cup
            q_rounds - number of qualification rounds in cup

            return pteam_num, qpairs
            pteam_num - number of teams witch start from playoff
            qpairs - number of pairs in qualification round
            """
            # teams in lowest play-off round
            pteam_num = 2 ** p_rounds
            # pais in highest qualification round
            qpairs = teams_num - pteam_num
            # indexes of teams that seeds directly in playoff
            pteamsI = pteam_num - qpairs
            qteams = qpairs * 2
            return pteamsI, qpairs

        def cupRound(teams, roundN, pair_mode):
            # TODO if pair_mode -> Double Match, else one Matchs
            # TODO playoff or not to params
            """
            teams - only those teams that will play in that round

            """
            # rem_teams = list(teams)
            loosers = []
            # print "teams %s len of %s, qpairs %s" % (teams, len(teams), qpairs)
             # it may be match or doublematch, so struggle is a common name for it
            struggles = len(teams)/2
            matches = struggles * (pair_mode + 1)

            if pair_mode: # Two Matches in struggle
                for struggleN in range(struggles):
                    # team1, team2 = teams.pop(0, -1)
                    team1 = teams.pop(0) # favorite
                    team2 = teams.pop() # outsider
                    pair = (team1, team2)
                    # print "%s :  %s" % (team1, team2)
                    # print "team1 = %s : team2 = %s" % (team1, team2)
                    match_name = "%s %s. round %s. struggle %s. "  \
                                    % (self.getName(), self.season, roundN, struggleN)
                    playoff = True
                    struggle = M.DoubleMatch(pair, self.delta_coefs, match_name, playoff).run()
                    # looser = pair[(pair_winner + 1) % 2]
                    # self.results.append({roundN:pair[(pair_winner + 1) % 2]})
                    loosers.append(looser)
                    # TODO ALL CODE BELOW MUST GO AWAY! REFACTOR TO ABOVE!!!
                    # TODO else.. (if not pair_mode)

                # DOUBLE MATCH (home - guest)
                # ablosute scores
                # match1 = M.Match((team1, team2), self.delta_coefs, "%s %s. round %s. tour %s. match %s"  \
                #                     % (self.getName(), self.season, "Qualification", roundN, struggleN))
                match1_score = list(M.Match((team1, team2), self.delta_coefs, "tstcupmatch").run())
                # common pair score # TODO delete logic, add onle match2_score =.. , pair score = ...
                if pair_mode:
                    match2_score = list(M.Match((team2, team1), self.delta_coefs, "tstcupmatch").run())
                    pair_score =  [match1_score[0] + match2_score[1],  match1_score[1] + match2_score[0]]
                else:
                    pair_score = match1_score
                # # not graphically
                # # print match1_score, match2_score, pair_score
                # # better way to print result is:
                # print "match %s" % struggleN, match1_score, [match2_score[1], match2_score[0]], pair_score, team1, team2

                if pair_score[0] > pair_score[1]:
                    pair_winner = 0 # TODO replace as in match.getWinner(): result_format = {"Win" : 0, "Lose" : 1, "Draw" : 2})
                elif pair_score[0] < pair_score[1]:
                    pair_winner = 1
                else: # sum of goals is equal
                    if pair_mode:
                        # rule of guest goal
                        if match2_score[1] > match1_score[1]: # first team wins guest goal rule
                            pair_winner = 0
                        elif match2_score[1] < match1_score[1]:
                            pair_winner = 1
                        else:
                            # penalty sequence
                            pair_winner, match2_score, pair_score = penalty_sequence(match2_score, pair_score)
                    else:
                        # penalty sequence
                        pair_winner, match1_score, pair_score = penalty_sequence(match1_score, pair_score)



                # TODO update results
                # print "pair_winner", pair_winner, '=', pair[pair_winner]
                # rem_teams.remove()
                looser = pair[(pair_winner + 1) % 2]
                # self.results.append({roundN:pair[(pair_winner + 1) % 2]})
                loosers.append(looser)
            print "%s struggles (%s matches) were played" % (struggles, matches)

            def print_winners():
                # print "winners", [winner.getName() for winner in winners]
                for res in self.results:
                    # loosers = [k.getName() for k in res.values()]
                    loosers_names = [ls.getName() for ls in loosers]
                    print "loosers", loosers_names

                # for round in self.results:
                #     print [team.getName() for team in round]
                # print "self.results", self.results

            # print_winners()
            return loosers

        # CALL HELPER FUNCTIONS
        try:
            # print "teams_num", teams_num
            self.p_rounds, self.q_rounds = self.rounds_count(teams_num)#self.rounds_count(teams_num)
        except:
            print "%s. need more teams to run cup" % teams_num
            raise AttributeError
        else:
            pteamsI, qpairs = PQplaces(self.p_rounds, self.q_rounds)
            # print "%s. pteam_num % s, pteams %s, qpairs %s, qteams %s" % ( teams_num, pteam_num, pteams, qpairs, qteams)
            print "run cup for %s teams: p_rounds = %s, pteamsI % s, qpairs %s (*2 = %s), sum = %s (%s)" % \
                  ( teams_num, self.p_rounds, pteamsI, qpairs, qpairs *2, qpairs *2 + pteamsI,
                    teams_num - (qpairs *2 + pteamsI))
            # print "%s. pteam_num %s, qteam_num %s" % (teams_num, pteam_num, qteam_num)
            # print "qualRound teams = %s" % teams

            qteamsI = teams[pteamsI:]
            # for team in qteamsI:
            #     print team.getName()
            # for team in teams:
            #     print team
            # TODO to support self.q_rounds > 1, need recompute qpairs and qteamsI with special logic

            # RUN QUALIFICATION ROUNDS
            for q_round in range(self.q_rounds):
                # print "q_round", q_round
                pairs = len(teams)
                q_roundN = q_round + 1
                round_name = q_roundN
                print "qualRound %s for %s teams (%s qpairs)" % (q_roundN, len(teams), qpairs)
                loosers = cupRound(qteamsI, q_roundN, self.pair_mode)

                # UPDATE RESULTS
                # print "self.results", self.results
                self.results.insert(0, loosers)
                # print "self.results", self.results

                for round in self.results:
                    print [team.getName() for team in round]

                # UPDATE LIST OF REMAINING TEAMS
                for looser in loosers:
                    teams.remove(looser)


            # RUN PLAY-OFF ROUNDS

            for p_round in range(self.p_rounds):
                print "p_round", p_round
                print len(teams), teams
                if p_round == self.p_rounds :
                    print "final round!"
                    if self.pair_mode == 1:
                        print "switch pair_mode from 1 to 0 so it will be only one final match!"
                        self.pair_mode = 0

                p_roundN = p_round + 1
                # TODO replace q_round and p_round to unified "ROUND", lastly I should compute words like "final, 1/4.. from it
                round_name = p_roundN
                loosers = cupRound(teams, round_name, self.pair_mode)

                #
                # # UPDATE RESULTS
                # # print "self.results", self.results
                # self.results.insert(0, loosers)
                # # print "self.results", self.results
                # for round in self.results:
                #     print [team.getName() for team in round]


        # p_rounds, q_rounds = (rounds_count(teams_num))
        # pteam_num = 2 ** p_rounds
        # qteam_num = teams_num - pteam_num
        # print "for teams_num %s, pteam_num %s, qteam_num %s" % (teams_num, pteam_num, qteam_num)
        # # for round in range(q_rounds):


        # while rem_teams:
        #     # TODO create match, update results
        return None

    def test(self, print_ratings = False):
        print "\nTEST CUP CLASS\n"
        print "initial Net:"
        print self#.printTable()
        print "\nMatches:"
        self.run()
        print "\nFinal Net:\n", self, "\n"

        # ratings after league
        if print_ratings:
            for team in self.getMember():
                print team.getName(), team.getRating()

    def __commented_from_League_run__(self, a, b):
        if a > b:
    ########################## copy from League.run() ****************************************
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



                        # define home and guest team
                        if not (tour % 2):
                            tindxs = (team1_ind, team2_ind)
                        else:
                            tindxs = (team2_ind, team1_ind)

                        pair = (teams[tindxs[0]], teams[tindxs[1]])

                        roundN = round + 1
                        tourN = tour + tours*(round) + 1
                        matchN = match_ind + 1 + (tourN - 1) * matches_in_tour
                        # print "round %s. tour %s (%s). match %s, team1 = %s , team2 = %s" \
                        match = M.Match(pair, self.delta_coefs, "%s %s. round %s. tour %s. match %s"  \
                                        % (self.getName(), self.season, roundN, tourN, matchN))
                        match_score = match.run()
                        print match

                        # UPDATE LEAGUE RESULTS
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
    @util.timer
    def Test(*args, **kwargs):
        # VERSION = "v1.1"
        with open(os.path.join("", 'VERSION')) as version_file:
            values_version = version_file.read().strip()
        coefs = C(values_version).getRatingUpdateCoefs("list")

        teams = []
        team_num = 50
        for i in range(team_num):
            teamN = i + 1
            rating = team_num - i
            uefa_pos = teamN
            teams.append(Team.Team("FC team%s" % teamN, "RUS", rating, "Команда%s" % teamN, uefa_pos))

        # # TEST LEAGUE CLASS
        if "League" in args:
            League("testLeague", "2015/2016", teams, coefs).test()

        # TEST CUP CLASS
        if "Cup" in args:
            # pair_mode = 0 # one match
            pair_mode = 1 # home + guest every match but the final
            # pair_mode = 2 # home + guest every match
            Cup("testCup", "2015/2016", teams, coefs, pair_mode).test()

    # Test("League", "Cup")
    Test("Cup")