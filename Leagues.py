# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

import Team
import util
# import Cups
from Team import Team
import Match as M
import DataStoring as db
import values as v
from values import Coefficients as C, LEAGUE_TYPE_ID
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
    def __init__(self,
                 name = None,
                 season = None,
                 year = None,
                 members = None,
                 delta_coefs = C(v.VALUES_VERSION).getRatingUpdateCoefs("list"),
                 pair_mode = 1,
                 seeding = "rnd",
                 state_params = ("P","W","D","L","GF","GA","GD","PTS"),
                 save_to_db = True,
                 prefix = "",
                 type_id = LEAGUE_TYPE_ID,
                 country_id = None):
        """

        :param name: League tournament id (type) - not unique id used in tourn_results!
        # do not pass this parameter to class if league is national cause it wont't be saved in tourn_played
        :param season: id
        :param members: list of teams
        :param delta_coefs: coefficients stored in values to compute ratings changing after match followed bby its result
        :param prefix: used for composite tournament like UEFA to add "Group A " or "Qualification " to roundname when
         save tournament results


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

        # super(League, self).__init__(tournament, season, members, delta_coefs)

        # if (not prefix) and name:
        #     raise ValueError, "League will not be saved cause id is predefined bur type is not UEFA (cause prefix)!"
        self.id = name # TODO name = id ? in tourn_played  - only for UEFA. if not, it will be filled in the 1st row of run()
        self.name = name
        self.season = season
        self.year = None
        self.members = members
        self.delta_coefs = delta_coefs
        self.seeding = seeding # not used in League - used hardcoded roundRobin instead
        self.pair_mode = pair_mode
        self.save_to_db = save_to_db
        self.prefix = prefix
        self.type_id = type_id # 3 for League
        self.country_id = country_id # for getMembers

        # get members from database and set to self.members
        if not members:
            self.setMembers()

        state = {st:0 for st in state_params}

        # initial results
        # after next block it will be filled by all state_params=0
        # results is a list of dicts {"Team" : , ... "PTS" = x}
        # in run() method it will be moved to final self.table, that is the same but sorted
        self.results = []

        # check self is League (not a subclass Cup)
        if "PTS" in state_params:
            # print "\nWELCOME TO LEAGUE ***", name.upper(), season, "***"
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

    def setMembers(self):
        """
        defines members for league/cup as a list from database - logic is the same for both league and cup
        :return:
        """
        self.members = []
        if self.year <= db.START_SIM_SEASON:
            # print "setMembers by rating for first season"
            # get all team ids from defined country id - like they ordered by default in team_info table
            # print "self.country_id=", self.country_id
            teams_tuples = db.select(what="id", table_names=db.TEAMINFO_TABLE, where=" WHERE ", columns="id_country ",
                              sign=" = ", values=self.country_id, fetch="all", ind="all")
            teams_indexes = [team[0] for team in teams_tuples]
            self.members = [Team(ind) for ind in teams_indexes]
        else:
            print "setMembers by position from previous league"
            raise NotImplementedError

    def getID(self):
        return self.id

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


    def RunMatchUpdateResults(self, tindxs, round, print_matches):
        """
        helper func
        runs match and updates League result
        """

        home_ind, guest_ind = tindxs


        pair = (self.getMember(home_ind), self.getMember(guest_ind))

        # # old-style
        # match = M.Match(pair, self.delta_coefs, "%s %s. round %s. tour %s. match %s"
        #                 % (self.getName(), self.season, roundN, tourN+1, match_ind+1))

        # new-style

        # match = M.Match(pair, self.delta_coefs, tournament=season_name + " " + str(tourn_name), round = round, save_to_db=self.save_to_db)
        match = M.Match(pair, self.delta_coefs, tournament=self.getID(), round = round, save_to_db=self.save_to_db)

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
        if self.prefix:
            # if League is a part of tournament (for example, UEFA),
            # get id from last played tournament stored in database
            # cause tournament id must be saved before run call this part (League)
            # id_tournament = db.select(table_names=db.TOURNAMENTS_PLAYED_TABLE,
            #                           fetch="one", suffix = " ORDER BY id DESC LIMIT 1") \
            #                 + 1
            # or just get it from arguments
            # id_tournament = self.id
            pass
        else:
            # unregistered yet - for national Leagues
            # saving tournament id before run to pass id to matches correctly
            self.id = self.saveTounramentPlayed()


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
        # if print_matches:
            # print "self.rnd_role" , self.rnd_role

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


            # for tour in range(tours):
            for tour, parings in enumerate(shedule_gen):
                if print_matches:
                    print "tour %s of %s" % (tour + 1, tours*(rounds))

                roundN = round + 1


                tourN = tour + tours*(round) + 1

                for match_ind, pair in enumerate(parings):

                    if not match_ind and tour % 2:
                        pair = (pair[1], pair[0])

                    if (self.rnd_role + round ) % 2:
                        tindxs = (pair[1], pair[0])
                    else:
                        tindxs = pair

                    matchN += 1

                    # new-styled
                    # only united "round" will be used as a readable of match in DB
                    roundname = self.prefix + "tour %s " % tourN

                    # self.RunMatchUpdateResults(tindxs, roundN, tour, tourN, match_ind + prefix, matchN, print_matches)
                    self.RunMatchUpdateResults(tindxs, roundname, print_matches)



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
                    pass
            else:
                print "ddd_error"
                for k,v in dd.iteritems():
                    print k,v

                raise Exception, "not all teams played exactly the same count of home matches, see above"
                #     warnings.warn("maybe I shall add random for computing home-guest roles if equality of its count unreachable")
        # update and return table
        table =  self.table.update(self.results)

        # save League in database
        self.saveToDB(table)

        return table


    def saveTounramentPlayed(self):
        """
        insert new row to TOURNAMENTS_PLAYED_TABLE, defining new id
        """
        # print "saving tournament name_id %s to database" % self.id
        columns = db.select(table_names=db.TOURNAMENTS_PLAYED_TABLE, fetch="colnames", suffix = " LIMIT 0")[1:]
        # print "TOURNAMENTS_PLAYED_TABLE columns are ", columns
        values = [self.season, self.id]
        # print "values are ", values
        db.insert(db.TOURNAMENTS_PLAYED_TABLE, columns, values)
        print "new tournament id (%s) of season_id (%s) inserted" % (values[1], values[0])
        # return id
        id =  db.select(table_names=db.TOURNAMENTS_PLAYED_TABLE, fetch="one", suffix = " ORDER BY id DESC LIMIT 1")
        # assert (id == self.id ), "storeed (%s) and argument (%s) id not equals!" % (id,  self.id)
        # print "id", id
        # print "id[0]", id[0]
        # return id[0]
        return id


    def saveToDB(self, table):
        """
        save League results data in database
        """

        # print "\nsaving tournament %s results  to database" % self.getName()
        columns = db.select(table_names=db.TOURNAMENTS_RESULTS_TABLE, fetch="colnames", where = " LIMIT 0")[1:]
        # print "TOURNAMENTS_RESULTS_TABLE columns are ", columns
        for ind, team in enumerate(table):
            # id_team = team.getID()
            id_team = team["Team"].getID()
            pos = ind + 1
            values = [self.id, pos, id_team]
            db.insert(db.TOURNAMENTS_RESULTS_TABLE, columns, values)
        # print "inserted %s rows to %s" % (len(table), db.TOURNAMENTS_RESULTS_TABLE)


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
        # all["Team"] = self.team.getName()
        # TODO I CHANGED IT IN 21.07  -self.team is no more teamname, its object
        all["Team"] = self.team
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
        for ind, result in enumerate(self.table):
            strRow += "\n%s. " % (ind+1) + "     "
            # first column must be teamname
            strRow += str(result["Team"].getName()) + "     "
            # others are results
            for col in columns[1:]:
                strRow += str(result[col]) + "     "
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
@util.timer
def Test(*args, **kwargs):
    """
    Test League Class

    :param args:
    :param kwargs: test arguments are listed below

    by default, save_db = True,  team_num = 20, all other options are disabled

    :return:
    """

    # used by clearing inserted rows by test after it runs
    last_m_row = db.trySQLquery(query="SELECT id FROM %s ORDER BY ID DESC LIMIT 1"
                                      % db.MATCHES_TABLE, fetch="one")
    last_tp_row = db.trySQLquery(query="SELECT id FROM %s ORDER BY ID DESC LIMIT 1"
                                       % db.TOURNAMENTS_PLAYED_TABLE, fetch="one")
    last_tr_row = db.trySQLquery(query="SELECT id FROM %s ORDER BY ID DESC LIMIT 1"
                                       % db.TOURNAMENTS_RESULTS_TABLE, fetch="one")
    print "last rows before League test are: last_m_row %s, last_tp_row %s, last_tr_row %s " % \
          ( last_m_row, last_tp_row, last_tr_row    )


    coefs = C(v.VALUES_VERSION).getRatingUpdateCoefs("list")

    teams = []
    if "team_num" in kwargs.keys():
        team_num = kwargs["team_num"]
    else:
        # default
        team_num = 20

    if "print_matches" in kwargs.keys():
        print_matches = kwargs["print_matches"]
    else:
        # default
        print_matches = False

    if "print_ratings" in kwargs.keys():
        print_ratings = kwargs["print_ratings"]
    else:
        # default
        print_ratings = False

    if "pair_mode" in kwargs.keys():
        pair_modes = kwargs["pair_mode"]
        if isinstance(pair_modes, int):
            pair_modes = (pair_modes, )
    else:
        # default
        pair_modes = (0,1,2)

    if "save_to_db" in kwargs.keys():
        save_to_db = kwargs["save_to_db"]
    else:
        # default
        save_to_db = True

    if "pre_truncate" in kwargs.keys():
        pre_truncate = kwargs["pre_truncate"]
    else:
        # default
        pre_truncate = False

    if "post_truncate" in kwargs.keys():
        post_truncate = kwargs["post_truncate"]
    else:
        # default
        post_truncate = False

    # team_num = kwargs["team_num"]
    # print_matches = kwargs["print_matches"]
    # print_ratings = kwargs["print_ratings"]
    # pair_mode = kwargs["pair_mode"]
    # save_to_db = kwargs["save_to_db"]
    # pre_truncate = kwargs["pre_truncate"]
    # post_truncate = kwargs["post_truncate"]

    if pre_truncate:
        db.truncate(db.TOURNAMENTS_PLAYED_TABLE)
        db.truncate(db.TOURNAMENTS_RESULTS_TABLE)
        db.truncate(db.MATCHES_TABLE)

    for i in range(team_num):
        # # teamN = i + 1
        # teamN = i
        # rating = team_num - i
        # uefa_pos = teamN
        # teams.append(Team.Team("FC team%s" % teamN, "RUS", rating, "Р С™Р С•Р СР В°Р Р…Р Т‘Р В°%s" % teamN, uefa_pos))
        # new-styled
        teams.append(Team(i+1))

    for pair_mode in pair_modes:
        season, year = 1, db.START_SEASON
        League(v.TEST_LEAGUE_ID, season, year, teams, coefs, pair_mode, save_to_db=save_to_db)\
            .test(print_matches, print_ratings)

    # if "roundRobin" in args:
    #     print "TEST roundRobin"
    #     for pair in roundRobin(range(team_num)):
    #         print pair

    if post_truncate:
        db.truncate(db.TOURNAMENTS_PLAYED_TABLE)
        db.truncate(db.TOURNAMENTS_RESULTS_TABLE)
        db.truncate(db.MATCHES_TABLE)



if __name__ == "__main__":
    # team_num = 3
    # for pair_mode in range(2):
    #     Test("League", team_num = team_num, pair_mode = pair_mode, print_matches = True, print_ratings = False)

    start_num = 20
    end_num = 21
    step = 1
    # pair_modes = (0, )
    pair_modes = (1, )
    # pair_modes = (0, 1)

    # PRINT MATCHES AFTER RUN
    PRINT_MATCHES = False
    PRINT_MATCHES = True
    # PRINT RATINGS AFTER RUN
    PRINT_RATINGS = True
    PRINT_RATINGS = False
    # RESET ALL MATCHES DATA BEFORE TEST
    PRE_TRUNCATE = False
    # PRE_TRUNCATE = True
    # RESET ALL MATCHES DATA AFTER TEST
    POST_TRUNCATE = False
    # POST_TRUNCATE = True
    # SAVE TO DB - to avoid data integrity (if important data in table exists), turn it off
    SAVE_TO_DB = False
    SAVE_TO_DB = True

    for t_num in range(start_num, end_num, 1):
        for pair_mode in pair_modes:
            print "\nt_num = %s\n" % t_num
            Test("League", team_num = t_num, pair_mode = pair_mode,
                 print_matches = PRINT_MATCHES, print_ratings = PRINT_RATINGS,
                 pre_truncate = PRE_TRUNCATE, post_truncate = POST_TRUNCATE, save_to_db = SAVE_TO_DB)
            # Test("roundRobin", team_num = t_num, pair_mode = pair_mode, print_matches = print_matches, print_ratings = print_ratings)