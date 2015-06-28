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

    def test(self):
        print "\nTEST LEAGUE CLASS\n"
        # print "initial Table:"
        # print self#.printTable()
        print_matches = True
        print "\nMatches:"
        self.run(print_matches)
        print "\nFinal Table:\n", self, "\n"
        print "Winner:\n%s\n" % self.getWinner()
        # ratings after league
        print "updated ratings:"
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

        # self.results - empty list. after run() it will be filled as following:
        # [team_champion, team_finished_in_final, teams_finished_in_semi-final, ... , teams_finished_in_qualRoundn, ...
        # teams_finished_in_qualRound1# ]
        print "\nWELCOME TO CUP ***", name.upper(), season, "***"

        state = {st:None for st in state_params}

        for member in self.members:
            self.results.append(TeamResult(member, state).get4table())
        # print "self.results", self.results
        # initialize net
        self.net = "not implemented yet"
        self.round_names = "not computed" # TODO make branch: get from params (if external scheme exists) OR compute in run()

    def __str__(self):
        return self.net

    def getNet(self):
        raise NotImplementedError

    def rounds_count(self, teams_num):
        """
         define rounds count
        """
        if teams_num < 1:
            raise Exception, "no teams to run cup"
        if teams_num < 2:
            warnings.warn("RUN CUP %s FOR ONE TEAM %s") % (self.name, self.getMember(0).getName())
            return 0, 0
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

    def roundNames(self, p_rounds, q_rounds):
        """
        generate round names to store and print
        (convert last round to final, last-1 to semifinal, etc.)
        :param p_rounds: number playoff rounds                  #!# starts from round 1
        :param q_rounds: numbers of qualification rounds        #!# starts from round 1
        :return:
        """
        rounds = p_rounds + q_rounds
        names = {}
        # print "we have %s rounds in Cup %s (%s in qualification, %s in playoff" % (rounds, self.getName(), q_rounds, p_rounds)

        names[rounds] = "Final"
        names[rounds-1] = "Semi-Final"

        for round in range(q_rounds + 1, rounds-1):
            names[round] = "1/%s-Final" % (2**(rounds-round))

        names[q_rounds] = "Qualification Final"
        for round in range(1, q_rounds):
            names[round] = "Qualification round %s" % round

        return names

    def run(self, print_matches = False):
        """
        generate matches, every match team rating and result updates
        after all, table updates and returns
        """
        teams = self.getMember()
        teams_num = len(teams)
        # clear results
        self.results = {}

        # seeding
        # 14-team cup example

        # play-off                                          *
        # round 1 (final)                   *                                 *
        # round 2 (semi-final)      *                *               *                 *
        # round 3 (1/4 final)    1     8         4      5         2      7         3      6
        # qualification
        # round 4 (qual 1)            8 9       4 13   5 12             7 10      3 14   6 11
        # // number = index in members + 1

        # TODO save PQplaces in table for Cup-name. if not exists, compute it

        # TODO save rounds name from rounds num for every Cup-name.

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

        def cupRound(_teams_, round_name, pair_mode, print_matches = False):
            """
            teams - only those teams that will play in that round

            """
            # rem_teams = list(teams)
            teams = list(_teams_)
            loosers = []
             # it may be match or doublematch, so struggle is a common name for it
            struggles = len(teams)/2
            matches = struggles * (pair_mode + 1)

            # cause its Cup!
            playoff = True

            if pair_mode: # Two Matches in struggle
                classname = M.DoubleMatch
            else:
                classname = M.Match
            for struggleN in range(struggles):
                team1 = teams.pop(0) # favorite
                # team2 = teams.pop() # outsider
                # TODO fix wild random! or at leat keep track of it to build self.net...
                team2 = teams.pop(random.randrange(len(teams))) # outsider
                pair = (team1, team2)
                # print "%s :  %s" % (team1, team2)
                # match_name = "%s %s. round %s. struggle %s"  \
                match_name = "%s %s. %s.%s"  \
                                % (self.getName(), self.season, round_name, struggleN)
                struggle = classname(pair, self.delta_coefs, match_name, playoff)
                struggle.run()
                if print_matches:
                    print struggle
                looser = struggle.getLooser()
                loosers.append(looser)
            # if print_matches:
            #    print "%s struggles (%s matches) were played" % (struggles, matches)

            return loosers


        def RunRoundAndUpdate(round, pair_mode, results, teams):
            # try:
            #
            # except:
            #     pass
            round_name = self.getRoundNames()[round]

            loosers = cupRound(teams, round_name, pair_mode, print_matches)

            # UPDATE RESULTS
            # TODO choose results form and net form
            # self.results.append(loosers)
            res = dict(results)
            res[round_name] = loosers

            # if print_matches:
            #     for stage, result in enumerate(self.results):
            #         print "results (loosers) of stage %s len of %s : %s" % (stage, len(self.results[stage]), [team.getName() for team in self.results[stage]])

            # return results, teams
            return res, loosers

        # CALL HELPER FUNCTIONS
        try:
            # print "teams_num", teams_num
            self.p_rounds, self.q_rounds = self.rounds_count(teams_num)#self.rounds_count(teams_num)
            # print "self.p_rounds %s, self.q_rounds %s" % (self.p_rounds, self.q_rounds)
        except:
            print "%s. need more teams to run cup" % teams_num
            raise AttributeError
        else:
            # convert number of round to round name (1/4, semi-final, etc.)
            self.round_names = self.roundNames(self.p_rounds, self.q_rounds)
            # print round_names
            all_rounds = self.p_rounds + self.q_rounds

            pteamsI, qpairs = PQplaces(self.p_rounds, self.q_rounds)


            # TODO: to support self.q_rounds > 1, need recompute qpairs and qteamsI with special logic: compute by
            # TODO: rounds_count only if external schema does't exists (else get it from additional class parameters,
            # TODO: UEFA is good example of that situation)

            # QUALIFICATION FINAL
            qteamsI = teams[pteamsI:]
            for q_round in range(1, self.q_rounds + 1):
                # print "len(teams) = %s", len(teams)
                # print "q_round", q_round
                self.results, loosers = RunRoundAndUpdate(q_round, self.pair_mode, self.results, qteamsI)
                # UPDATE LIST OF REMAINING TEAMS
                for looser in loosers:
                    teams.remove(looser)
                    qteamsI.remove(looser)


            # PLAY-OFF
            for round in range(self.q_rounds + 1, all_rounds):
                # print "len(teams) = %s", len(teams)
                # round_name = round_names[round]
                self.results, loosers = RunRoundAndUpdate(round, self.pair_mode, self.results, teams)
                for looser in loosers:
                    teams.remove(looser)

            # FINAL
            #     print "final round!"
            # print "len(teams) = %s", len(teams)
            if self.pair_mode == 1:
                # if print_matches:
                #     print "switch pair_mode from 1 to 0 so it will be only one final match!"
                pairmode = 0 # ONE MATCH FOR FINAL
            else:
                pairmode = self.pair_mode
            # round_name = round_names[all_rounds]
            self.results, loosers = RunRoundAndUpdate(all_rounds, pairmode, self.results, teams)
            for looser in loosers:
                teams.remove(looser)


            # else:
            #     self.results, teams = RunRoundAndUpdate(all_rounds + 1, self.pair_mode, self.results, teams)

            assert len(teams) == 1, "Cup ends with more than one winner!"
            self.winner = teams.pop()

        # # print result for EVERY round
        # if print_matches:
        #     for stage, result in enumerate(self.results):
        #         print "results (loosers) of stage %s len of %s : %s" % (stage, len(self.results[stage]), [team.getName() for team in self.results[stage]])
        return self.winner

    def getRoundNames(self):
        return self.round_names

    def getWinner(self):
        return self.winner

    def test(self, print_ratings = False):
        print "\nTEST CUP CLASS\n"
        print "pair_mode = %s\n" % self.pair_mode
        print "initial Net:"
        print self#.printTable()
        print "\nMatches:"
        print_matches = True
        # print_matches = False
        self.run(print_matches)
        print "\nWinner:\n%s" % self.getWinner()
        # print "\nresults:\n%s" % [(k, [team.getName() for team in self.results[k]] ) for k in self.results.keys()]
        print "\nresults:"
        for k in self.results.keys():
            # TODO sort results ny round (maybe store them in list)
            print k, [team.getName() for team in self.results[k]]
        print "\nFinal Net:\n", self, "\n"

        # ratings after league
        if print_ratings:
            for team in self.getMember():
                print team.getName(), team.getRating()


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
        team_num = kwargs["team_num"]
        for i in range(team_num):
            teamN = i + 1
            rating = team_num - i
            uefa_pos = teamN
            teams.append(Team.Team("FC team%s" % teamN, "RUS", rating, "Команда%s" % teamN, uefa_pos))

        # # TEST LEAGUE CLASS
        if "League" in args:
            League("testLeague", "2015/2016", teams, coefs).test()
            # League("testLeague", "2015/2016", teams, coefs).run()


        # TEST CUP CLASS
        if "Cup" in args:
            # pair_mode = 0 # one match
            pair_mode = 1 # home + guest every match but the final
            # pair_mode = 2 # home + guest every match
            Cup("testCup", "2015/2016", teams, coefs, pair_mode).test()
            # Cup("testCup", "2015/2016", teams, coefs, pair_mode).run()

    # Test("League", "Cup", team_num = 20)
    Test("Cup", team_num = 20)