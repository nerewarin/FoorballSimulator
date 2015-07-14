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
        home_ind = tindxs[0]
        guest_ind = tindxs[1]
        if tindxs in self.pair_host:
            # swap home-guest to guest-home
            home_ind = tindxs[1]
            guest_ind = tindxs[0]

        # else:
            # if (tindxs[1], tindxs[0]) not in self.pair_host:
                # # all variants clear (for pair_mode = 0) so we can choose the most honest way
                # if self.home_mathes_count[tindxs[0]] > self.home_mathes_count[tindxs[1]]:
                #     home_ind = tindxs[1]
                #     guest_ind = tindxs[0]
            # else:
            #     if self.home_mathes_count[tindxs[0]] > self.home_mathes_count[tindxs[1]]:
            #         home_ind = tindxs[1]
            #         guest_ind = tindxs[0]

        indxs = (home_ind, guest_ind)

        pair = (self.getMember(home_ind), self.getMember(guest_ind))
        # check this pair config is new (there was not match with this teams with these home-guest roles)
        if (home_ind, guest_ind) in self.pair_host:
            print "pair = ", [team.getName() for team in pair]
            # raise Exception, "home-guest roles are not uniq for this pair!"
            raise Exception, "home-guest roles are not uniq for this pair!"

        # self.pair_host.add((home_ind, guest_ind))


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
            team_i = indxs[i]
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

        # TODO fix odd number of terams in League
        matches_in_tour = teams_num // 2

        odd_league = teams_num % 2

        # round robin https://ru.wikipedia.org/wiki/%D0%9A%D1%80%D1%83%D0%B3%D0%BE%D0%B2%D0%B0%D1%8F_%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0
        matches_in_tour += odd_league

        next_skip = None

        # if 0, first match starts with favorite at home (as guest otherwise)
        # it is important in leagues of two members and pair_mode = 0, cause only one match is played in this case
        self.rnd_role = random.randint(0,1)
        print "self.rnd_role" , self.rnd_role

        tours = teams_num - 1 + odd_league

        # rounds of league
        rounds = 1
        if self.pair_mode:
            rounds += 1


        # # generate pairs
        # # pairs = set([])
        # pairs = {}
        # # matches = []
        # # home-guest roles switcher
        # hg = 0
        # # self.pair_mode = 0
        # pairs = []
        # for t1 in range(teams_num):
        #     # pairs[t1] = []
        #     for t2 in range(t1 + 1, teams_num):
        #         pairs.append((t1, t2))
        # print "pairs", pairs
        # print "len(matches) %s, sum_ariphmetic %s" % (len(pairs), teams_num*(teams_num-1)/2)

                # if t1 != t2:
                #
                #     if pairs.has_key(t2):
                #         if t1 not in pairs[t2]:
                #             pairs[t1].append(t2)
                #     else:
                #         pairs[t1].append(t2)

                    # # tinds = (t1, t2)
                    # # print "candidate", tinds
                    # pairs.add((t1, t2))
                    # if self.pair_mode:
                    #     pairs.add((t2, t1))
                    # else:
                    #     a = set()
                    #     a.add(t1)
                    #     a.add(t2)
                    #     pairs.add(a)
                    # #     # matches.append((tinds[hg % 2], tinds[(hg + 1) % 2] ))
                    # # else:
                    # #     if (t2, t1) not in matches and (t1, t2) not in matches:
                    # #         # matches.append((tinds[hg % 2], tinds[(hg + 1) % 2] ))
                    # #         matches.add((tinds[hg % 2], tinds[(hg + 1) % 2] ))
                    # # hg += 1
        # print "len(matches) %s, sum_ariphmetic %s" % (len(pairs), teams_num*(teams_num-1)/2)
        # print pairs
        # # for m in pairs:
        # #     print m
        # # if rounds:


        # odd_team is a list of rest teams (is teams num is odd) who did'nt meet a opponent in current tour
        # to meet another rest in the next tour
        skip_team = []
        # make home teams count equal for every member
        # count matches played at home for every team by int index of members list
        self.home_mathes_count = {}
        for tind in range(len(self.members)):
            self.home_mathes_count[tind] = 0


        # v2 after every match, add tuple (home, guest) indexes to store this config and do not repeat
        # (swith home for next match of this pair)
        # self.pair_host = set([])



        # opponents is a set of team-set pairs, where the last set includes all remaining opponents to play
        # all_opponents = {}
        iter_teamind = range(teams_num)
        # for teamind in iter_teamind:
        #     # available opponents of team
        #     team_opps =  [t for t in iter_teamind]
        #     # exclude self from list of available team opponents
        #     team_opps.remove(teamind)
        #     # add list of opponents to common dict
        #     all_opponents[teamind] = team_opps
        # print "all_opponents", all_opponents

        matchN = 0 # sequentially numbered
        prefix = 0
        print "self.pair_mode = %s" % self.pair_mode
        print "teams_num = %s" % teams_num

        # symbol indicates that team in rest
        rest = "x"

        # generate matches
        for round in range(rounds):
            played_pairs = set()

            print "\nround %s" % round
            # # played_pairs = set()
            # # copy all_opponents
            # # we don't need deepcopy here (but can), cause elements of all_opponents are just int
            # opponents = deepcopy(all_opponents)
            # print "opponents %s" % opponents

            # fucking pair that rests in the end
            last_pair = []

            # played = set([])

            # v3 store last match role for every team as a boolean
            self.pair_host = {}
            for tind in range(len(self.members)):
                # 0 is False, 1 (second round) is True
                self.pair_host[tind] = round


            team_indexes = list(iter_teamind)
            for tour in range(tours):

                # storage of teams not played this tour yet

                roundN = round + 1
                tourN = tour + tours*(round)

                if print_matches:
                    print "\ntour %s of %s" % (tourN + 1, tours*(rounds))

                if odd_league:
                    # if number of league members is odd, one team must skip match in every tour

                    # index of team that skip this tour
                    # skip_team = team_indexes.pop( - (1 + tour) % len(team_indexes))
                    # print "skip_team %s" % skip_team
                    # next_skip = team_indexes[ (- (1 + tour) ) % len(team_indexes)]
                    # # print "next_skip", next_skip
                    # team_indexes.insert(0, rest)
                    team_indexes.append(rest)


                print "ini team_indexes", team_indexes
                # team_indexes = collections.deque(team_indexes)
                # print "deq", team_indexes


                def shift(seq, n):
                    n = n % len(seq)
                    return seq[n:] + seq[:n]

                # don't shift on first tour
                if tour:
    #                     n = n % len(seq)
    # return seq[n:] + seq[:n]
                    team_indexes.remove(0)
                    print "removed_0", team_indexes
                    # team_indexes = team_indexes[::-1]
                    team_indexes = shift(team_indexes, 1)

                    print "shifted_team_indexes!! ", team_indexes
                    team_indexes.insert(0, 0)
                    print "restored_team0!! ", team_indexes

                # always even lenght of teams (if initially odd, including rest team)
                lTI = len(team_indexes)
                middle = lTI // 2


                half1 = team_indexes[:middle]
                half2 = team_indexes[middle:]
                print "halfs", half1, half2

                for match_ind in range(matches_in_tour):
                    print "match_ind %s of %s" %(match_ind+1, matches_in_tour)
                    print "team_indexes", team_indexes
                    # define team1
                    # remove t1 from not yet played in current tour
                    # get t1 as first team not played in this round

                    # print "\nmi team_indexes", team_indexes
                    # team1_ind = team_indexes[match_ind]

                    team1_ind = half1[match_ind]
                    # print "(-1-tour) % len(team_indexes) = ", ((-1-tour) % len(team_indexes)), "(", (-1-tour) , "%", len(team_indexes), ")"
                    # team2_ind = team_indexes[(-1-match_ind-tour) % len(team_indexes)]
                    # team2_ind = team_indexes[-1 - match_ind - tour]
                    # team2_ind = half2[(-1 - match_ind - tour) % len(half2)]
                    team2_ind = half2[(-1 - match_ind) % len(half2)]
                    # print "team2_ind", type(team2_ind), team2_ind

                    tindxs =  (team1_ind, team2_ind)
                    print "tindxs", tindxs

                    if rest in tindxs or team1_ind == team2_ind:
                        continue

                    # for team_ind in tindxs:
                    #     team_indexes.remove(team_ind)

                    # lenTI = len(team_indexes)
                    #
                    # i = -1
                    # step = int(i)
                    #
                    #
                    # team2_vars = [opp for opp in opponents[team1_ind] if opp in team_indexes]
                    #
                    # print "team2_vars", team2_vars, "for team =", team1_ind
                    # team2_ind = team2_vars[i % len(team2_vars)]
                    #
                    #
                    # # if lenTI == 3:
                    # #
                    # #     print "five teams league problem"
                    # #
                    # #     temp_ti = list(team_indexes)
                    # #     temp_ti.remove(team2_ind)
                    # #     print "temp_ti", temp_ti
                    # #     print "last_pair", last_pair
                    # #
                    # #     if temp_ti in last_pair:
                    # #         i -= step
                    # #         team2_ind = team_indexes[i % lenTI]
                    # #
                    # #     #
                    # #     # temp_ops = deepcopy(opponents)
                    # #     # temp_ti =  deepcopy(team_indexes)
                    # #     #
                    # #     # temp_t2 = team_indexes[i % lenTI]
                    # #     #
                    # #     # # remove t2 from not yet played in current tour
                    # #     # temp_ti.remove(temp_t2)
                    # #     #
                    # #     # # remove t2 from opponents of t1 available in this round
                    # #     # temp_ops[team1_ind].remove(temp_t2)
                    # #     #
                    # #     # # remove t1 from opponents of t2 from remaining in this round
                    # #     # temp_ops[temp_t2].remove(team1_ind)
                    # #
                    #
                    #
                    # def consistent(pair):
                    #     """
                    #     checking arc consistency op pair
                    #     """
                    #     if tour+1 == 4:
                    #         pass
                    #
                    #     print "\ncheck consistent for pair", pair
                    #     team1_ind, team2_ind = pair
                    #
                    #     temp_ops = deepcopy(opponents)
                    #     temp_ti =  deepcopy(team_indexes)
                    #
                    #     # team2_vars = [opp for opp in temp_ops[team1_ind] if opp in team_indexes]
                    #
                    #
                    #     # temp_t2 = team_indexes[i % lenTI]
                    #
                    #     # print "temp_ops", temp_ops
                    #     # print "temp_ti", temp_ti
                    #     # print "played_pairs", played_pairs
                    #
                    #
                    #     # remove t2 from not yet played in current tour
                    #     # temp_ti.remove(temp_t2)
                    #     temp_ti.remove(team2_ind)
                    #
                    #     # remove t2 from opponents of t1 available in this round
                    #     # try:
                    #     #     temp_ops[team1_ind].remove(temp_t2)
                    #     # except:
                    #     #     warnings.warn("team2_ind not removed from temp_ops[temp_t1]" )                        try:
                    #     # temp_ops[team1_ind].remove(temp_t2)
                    #     temp_ops[team1_ind].remove(team2_ind)
                    #
                    #     # remove t1 from opponents of t2 from remaining in this round
                    #     # try:
                    #     #     temp_ops[temp_t2].remove(team1_ind)
                    #     # except:
                    #     #     warnings.warn("team1_ind not removed from temp_ops[temp_t2]" )
                    #     # temp_ops[temp_t2].remove(team1_ind)
                    #     temp_ops[team2_ind].remove(team1_ind)
                    #
                    #     for team in temp_ops.keys():
                    #         if team1_ind in temp_ops[team]:
                    #             temp_ops[team].remove(team1_ind)
                    #         if team2_ind in temp_ops[team]:
                    #             temp_ops[team].remove(team2_ind)
                    #
                    #     # print "if we remove pair from future variants.."
                    #     # print "temp_ops", temp_ops
                    #     # print "temp_ti", temp_ti
                    #     # print "played_pairs", played_pairs
                    #
                    #     # if its last tour, don't worry about
                    #
                    #     # print "tourtour", tour
                    #     if tour == 0 and round == 1:
                    #         pass
                    #
                    #     temp_pair = (team1_ind, team2_ind)
                    #     for ind in temp_pair:
                    #         # what is all rests is a next_skip? (five teams league problem)
                    #         # print "next_skip", next_skip
                    #         # try:
                    #         #     if next_skip in temp_ops[ind]:
                    #         #         pass
                    #         # except:
                    #         #     pass
                    #
                    #         if next_skip in temp_ops[ind]:
                    #             temp_ops[ind].remove(next_skip)
                    #         if not temp_ops[ind]:
                    #             # if no move variants for team0 for last tour - don't worry cause team0 skips last tour
                    #             print "tour, tours", tour+1, tours
                    #             if tour+1 == tours:
                    #                 print "don't worry for no rest variants cause its last tour"
                    #             elif (not ind) and (tours - (tour+1) == 1):
                    #                 print "no more variants for tem0 in last tour - it's ok"
                    #             else:
                    #                 return False
                    #
                    #
                    #     # print "check consistent of last pair "
                    #     # print "temp_ops", temp_ops
                    #     # print "temp_ti", temp_ti
                    #     # print "played_pairs", played_pairs
                    #
                    #     if len(temp_ti) == 2:
                    #         print "check_last_pair"
                    #
                    #         if tuple(temp_ti) in played_pairs:
                    #             return False
                    #
                    #
                    #
                    #     # check if remaining team will not have a rest in next tour
                    #     # next_tour = tour + 1
                    #     # next_skip = team_indexes[ (- (1 + tour) ) % len(team_indexes)]
                    #     # print "next_skip %", next_skip
                    #     return True
                    #
                    # print "candidates team1_ind, team1_ind", (team1_ind, team2_ind)
                    # # while (team2_ind not in opponents[team1_ind]) or (not consistent((team1_ind, team2_ind))) :
                    # while not consistent((team1_ind, team2_ind)) :
                    #     # print "opp? %s consistent? %s" % (team2_ind in opponents[team1_ind], consistent((team1_ind, team2_ind)))
                    #     i += step
                    #
                    #     # # check arc consistency (five teams league problem)
                    #     # # V2
                    #     # team2_ind = team_indexes[i % lenTI]
                    #     # print "while"
                    #     # print "team_indexes", team_indexes
                    #
                    #         # if (team1_ind, team2_ind)
                    #
                    #     # check arc consistency (five teams league problem)
                    #     # V1
                    #     # if len(team_indexes) < 4:
                    #     #     checked = False
                    #     #     while not checked:
                    #     #         print "five teams league problem"
                    #     #         temp_ops = deepcopy(opponents)
                    #     #         temp_ti =  deepcopy(team_indexes)
                    #     #
                    #     #         temp_t2 = team_indexes[i % lenTI]
                    #     #
                    #     #         # remove t2 from not yet played in current tour
                    #     #         temp_ti.remove(temp_t2)
                    #     #
                    #     #         # remove t2 from opponents of t1 available in this round
                    #     #         temp_ops[team1_ind].remove(temp_t2)
                    #     #
                    #     #         # remove t1 from opponents of t2 from remaining in this round
                    #     #         temp_ops[temp_t2].remove(team1_ind)
                    #     # # else:
                    #     #     team2_ind = team_indexes[i % lenTI]
                    #     #     if i < -(lenTI+1) or i > (lenTI+1):
                    #     #         raise Exception, "cannot find opponent"
                    #
                    #
                    #     # team2_ind = team_indexes[i % lenTI]
                    #     team2_ind = team2_vars[i % len(team2_vars)]
                    #     if i < -2*(lenTI+1) or i > 2*(lenTI+1):
                    #         raise Exception, "cannot find opponent"
                    #
                    #
                    #
                    #
                    # # remove t2 from not yet played in current tour
                    # team_indexes.remove(team2_ind)
                    #
                    # # remove t2 from opponents of t1 available in this round
                    # opponents[team1_ind].remove(team2_ind)
                    #
                    # # remove t1 from opponents of t2 from remaining in this round
                    # opponents[team2_ind].remove(team1_ind)
                    #
                    # tindxs = (team1_ind, team2_ind)
                    #
                    # played_pairs.add(tindxs)


                    # if previous match was at home, so guest now
                    if self.pair_host[team1_ind]:
                        # reset role holder
                        self.pair_host[team1_ind] = 0
                        if not self.rnd_role:
                            tindxs = (team2_ind, team1_ind)
                    else:
                        # print "last match if team%s was home" % team1_ind
                        # set role holder
                        self.pair_host[team1_ind] = 1
                        if self.rnd_role:
                            tindxs = (team2_ind, team1_ind)

                    # # if (tourN + round) % 2:
                    # # if (tourN % 2):
                    # # if not (matchN % 2):
                    #     tindxs = (team2_ind, team1_ind)

                    # match = M.Match(pair, self.delta_coefs, "%s %s. round %s. tour %s(%s). match %s(%s)"  \
                    #                 % (self.getName(), self.season, roundN, tour+1, tourN, match_ind + 1, matchN))
                    self.RunMatchUpdateResults(tindxs, roundN, tour, tourN, match_ind + prefix, matchN, print_matches)
                    matchN += 1

                # print (team1_ind, team2_ind)
                last_pair.append((team1_ind, team2_ind))


                #
                # # print "TOUR_COMPLETE!"
                # # print "team_indexes %s" % team_indexes
                # odd_team.extend(team_indexes)
                # if len(odd_team) > 1:
                #     tindxs = (odd_team.pop(), odd_team.pop())
                #     # pair = (teams[tindxs[0]], teams[tindxs[1]])
                #     self.RunMatchUpdateResults(tindxs, roundN, tour+1, tourN, match_ind + 1, matchN, print_matches)
                #     matchN += 1
                #
                # elif len(odd_team) > 2:
                #     raise Exception, "ERROR in League.run - odd_team list should not include more then two teams!"


                # # make additional match if len(members) is odd
                # if odd_match and (tour % 2):
                #     print "need odd_match!"
                #     # print "team_indexes %s" % team_indexes

        print self.home_mathes_count
        # check all values are the same, i.e.
        # all teams played exactly the same count of home matches
        # solution from http://stackoverflow.com/questions/17821079/how-to-check-if-two-keys-in-dict-hold-the-same-value
        dd = defaultdict(set)
        for k, v in self.home_mathes_count.items():
            dd[v].add(k)
        dd = { k : v for k, v in dd.items() if len(v) > 1 }



        if len(dd.keys()) > 1:
            print "home_mathes_count by team index are ", self.home_mathes_count


            if (not odd_league) and (self.pair_mode == 0):
                warnings.warn("no way to fix, its math! maybe I shall add random for computing home-guest roles if equality of its count unreachable")
                return self.table.update(self.results)

            print "ddd"
            for k,v in dd.iteritems():
                print k,v

            raise Exception, "not all teams played exactly the same count of home matches, see above"
            if self.pair_mode:
                raise Exception, "not all teams played exactly the same count of home matches, see above"
            # else:
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


    # team_num = 3
    # for pair_mode in range(2):
    #     Test("League", team_num = team_num, pair_mode = pair_mode, print_matches = True, print_ratings = False)



    start_num = 0
    end_num = 5
    step = 1
    pair_modes = (0, )
    # pair_modes = (0, 1)
    print_matches = True
    print_ratings = False
    for t_num in range(start_num, end_num, 1):
        for pair_mode in pair_modes:
            print "\nt_num = %s\n" % t_num
            Test("League", team_num = t_num, pair_mode = pair_mode, print_matches = print_matches, print_ratings = print_ratings)