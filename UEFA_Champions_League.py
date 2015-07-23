# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

import Team
from Cups import Cup
import DataStoring as db
import util
from Leagues import League, TeamResult
import Match as M
from values import Coefficients as C, TournamentSchemas as schemas
from operator import attrgetter, itemgetter
import random
import time
import os
import warnings

# TODO func here aboid importing - delete it if DB is installed on executable env
def trySQLquery(a,b,c):
    return a

def connectDB(a="",b="",c="",d=""):
    return a,cur()

class cur():
    def execute(self):
        return None

class UEFA_League(Cup):
    def __init__(self, id, season, members, delta_coefs, pair_mode, seeding, state_params = ("final_stage", )):
    # def __init__(self, name, season, members, delta_coefs, pair_mode = 1, seeding = "A1_B16",
    #              state_params = ("final_stage", ), save_to_db = True, prefix = ""):


        """
        UEFA_Champ_L is a tournament, implemented as three tournaments:
        Qualification Cup, Group League, Play-Off Cup.

        Num of rounds and pairs in every tournament defined by schema

        :param name:
        :param season:
        :param members:
        :param delta_coefs:
        :param schema:
        :param pair_mode:
        :param state_params:
        :return:
        """
        self.con, self.cur =  db.connectGameDB()
        self.id = id
        self.seeding = seeding
        self.season = season
        self.prev_season = season -1

        if members:
            # EXTERNAL
            # all members came as arguments and were initially sorted
            self.members = members
        else:
            # INTERNAL
            # class will get all teams from database by itself
            self.setMembers()
            self.members = self.getMember()

        super(UEFA_League, self).__init__(id, season, self.members, delta_coefs, state_params)#(self, tournament, season, members, delta_coefs)


        # self.results - empty list. after run() it will be filled as following:
        # [team_champion, team_finished_in_final, teams_finished_in_semi-final, ... , teams_finished_in_qualRoundn, ...
        # teams_finished_in_qualRound1# ]
        print "\nWELCOME TO UEFA LEAGUE *** id = %s season_id = %s ***" % (id, season)

        state = {st:None for st in state_params}

        for member in self.members:
            self.results.append(TeamResult(member, state).get4table())

        # print "self.results", self.results
        # initialize net
        # self.net = "not implemented yet"
        self.net = {}
        self.round_names = "not computed" # TODO make branch: get from params (if external scheme exists) OR compute in run()


    def setMembers(self):
        """
        defines members for every round
        convert indexes of countries, from what championships members are getting, to indexes of self.members for every team

        :return:
        """
        self.members = []
        # define only those members, that are independent of results in
        self.members_by_round = []

        # parsing stored in schema values
        self.stages = []

# TODO round_info  [{"count": x , "toss" : "not_same_country_and_played_in_group"}, {


        for stage in self.seeding:
            # print stage
            stage_members = []
            for stage_name, stage_info in stage.iteritems():
                print "stage_name %s" %stage_name
                # print stage_name, stageV
                classname = stage_info["classname"]
                parts = stage_info["parts"]
                pair_mode = stage_info["pair_mode"]
                round_info = stage_info["tindx_in_round"]
                for round_num, seeded_sources in round_info.items():
                    print "round_num = %s" % round_num#, members_schema
                    for source, pos in seeded_sources.iteritems():
                        print "sourcse, pos = ", source, pos
                        if isinstance(source, tuple):
                            if isinstance(pos, int):
                                print "seed from national League"
                                tournament_type = "League"
                                position = pos
                            elif pos == "cupwinner":
                                print "seed from national Cup"
                                tournament_type = "Cup"
                                position = 1
                            else:
                                raise Exception, "unknown pos %s type %s" % (pos, type(pos))



                            # tst = db.select("id", db.COUNTRY_RATINGS_TABLENAME, " WHERE ", "id_season", " = ", self.prev_season, fetch = "all")
                            # print "tst", tst  # ok

                            # get list of indexes of countries ids with a given rating from previous season
                            # query =  "SELECT id FROM %s WHERE id_season = '%s' and pos IN %s;"
                            # data =  (db.COUNTRY_RATINGS_TABLENAME, self.prev_season, source)
                            # query =  "SELECT id FROM country_ratings WHERE id_season = '%s' and pos IN %s;"
                            query =  "SELECT id FROM %s " % db.COUNTRY_RATINGS_TABLENAME + "WHERE id_season = '%s' and position IN %s;"
                            data =  (self.prev_season, source)
                            # print query
                            # print data
                            # print query % data
                            # countries_ids = db.trySQLquery("execute", query, data, fetch = "all_tuples", ind = 0)
                            self.cur.execute(query, data)
                            fetched = self.cur.fetchall()
                            # countries_ids = self.cur.fetchall()
                            countries_ids = [country_id[0] for country_id in fetched]

                            print "countries_ids", countries_ids
                            # print "countries_ids", countries_ids[0]

                            # countries_ids = cur.fetchall()[0]

                            # search for tournament_id of League of this country
                            query =  "SELECT id FROM %s WHERE type = '%s' and id_country IN '%s';"
                            data =  (db.TOURNAMENTS_TABLENAME, tournament_type, countries_ids)
                            db.trySQLquery(cur.mogrify, query, data)
                            id_types = cur.fetchall()[0]

                            # get from tournaments_played needed results ids
                            query =  "SELECT id FROM %s WHERE id_season = '%s' and id_type IN '%s';"
                            data =  (db.TOURNAMENTS_TABLENAME, self.season, id_types)
                            db.trySQLquery(cur.mogrify, query, data)
                            id_tournaments = cur.fetchall()[0]

                        elif source == "CL":
                            id_types = (0, )
                            position = pos

                        else:
                            raise Exception, "unknown source %s ,type %s" % (source, type(source))

                        # get from tournament_results id of team with a given position
                        query =  "SELECT id_team FROM %s WHERE position = '%s' and id_tournaments IN '%s';"
                        data =  (db.TOURNAMENTS_RESULTS_TABLE, position, id_types)
                        db.trySQLquery(cur.mogrify, pos, data)
                        id_teams = cur.fetchall()[0]

                        # add team ids to members of the current stage
                        stage_members += id_teams


                        # query = "SELECT id from %s WHERE
                        # data =  (db.TOURNAMENTS_PLAYED_TABLE, self.season, source,)

                        # # TODO fetch all for every variant of structure
                        # for country_pos in source:
                        #     # placeholders = ', '.join(source)
                        #
                        #
                        #
                        #
                        #     country_ids = "select * from COUNTRY_RATINGS_TABLENAME where id_season = '%s' and pos in '%s'" % (self.season, country_positions)


                             # , pos = (self.season, pos)
                            # what = "id"
                            # table = db.COUNTRY_RATINGS_TABLENAME
                            # columns = ["id_season", "pos"]
                            # values = (self.season, pos)
                            # fetch = "all"


                        # # for every country, select
                        #     if isinstance(pos, int):
                        #         tournament_type = "League"
                        #
                        #
                        #     # stage_members = select
                        #     # TODO select pos from Tournaments type = League national = country_id of current season
                        #     # query = "SELECT ... "
                        #     # data = ""
                        #     # team = trySQLquery(cur.execute, query, data)
                        #     team_id = db.select("id", table_names=db.TOURNAMENTS_RESULTS_TABLE, where=" WHERE ", columns, " = ", values, )
                        #     stage_members.append(team)
                        #
                        #
                        # # elif isinstance(members_source, str) and members_source == "CL":
                        # elif source == "CL":
                        #     # get 3 / 4 round / group loosers
                        #     # TODO select from Tournaments type = CL national = international, round looser = pos (get from CL results) of current season
                        #     pass


            #     # print  "stage_type__" , stage_type
            #     if not stage_type:
            #         raise Exception, "undefined stage_type"
            #     if not stage_pair_mode:
            #         raise Exception, "undefined stage_pair_mode"
            #     self.stages.append((stage_name, stage_type, stage_pair_mode))
            #
            # if roundname:
            #     print roundname
            # # round = stage_name + roundname
            # self.members_by_round.append(stage_members)

    def run(self, print_matches = False):
        for stage in self.stages:
            stage_name, stage_type, stage_pair_mode = stage
            print stage




    def test(self, print_matches = False, print_ratings = False):
        print "\nTEST CUP CLASS\n"
        print "pair_mode = %s\nseeding = %s\n" % (self.pair_mode, self.seeding)
        print "initial Net:"
        print self#.printTable()
        if print_matches:
            print "\nMatches:"
        self.run(print_matches)
        print "\nWinner:\n%s" % self.getWinner()
        # print "\nresults:\n%s" % [(k, [team.getName() for team in self.results[k]] ) for k in self.results.keys()]
        print "\nresults:"
        for k in self.results.keys():
            # TODO sort results ny round (maybe store them in list)
            print k, [team.getName() for team in self.results[k]]
        print "\nFinal Net:\n", str(self), "\n"

        # ratings after league
        # print "print_ratings = %s" % print_ratings
        # print "self.getMember() %s" % self.getMember()
        if print_ratings:
            for team in self.getMember():
                print team.getName(), team.getRating()






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
            # old-styled
            # teams.append(Team.Team("FC team%s" % teamN, "RUS", rating, "Команда%s" % teamN, uefa_pos))
            # new-styled
            # teams.append(Team.Team(teamN))

        # TEST CUP CLASS
        if "ChL" in args:

            # schema =
            # for seeding in Cup.getSeedings(Cup):
            #     print seeding
            # pair_mode = 0 # one match
            pair_mode = 1 # home + guest every match but the final
            # pair_mode = 2 # home + guest every match

            # print_matches = False
            print_matches = True

            print_ratings = False
            # print_ratings = True

            s =  Cup("no Cup, just getSeedings", "", teams, coefs, pair_mode)
            # seedings = s.getSeedings()
            # print "seedings", seedings

            # seeding schema schemas().get_CL_schema()
            seeding = schemas().get_CL_schema()
            # tstcp = UEFA_League("test UEFA Champions league", "2015/2016", teams, coefs, pair_mode, seeding)
            members = None
            tstcp = UEFA_League(id = 0, season = 2, members = members, delta_coefs=coefs, pair_mode = pair_mode, seeding=seeding)
            # tstcp.test(print_matches, print_ratings)
            # # Cup("testCup", "2015/2016", teams, coefs, pair_mode).run()


    Test("ChL", team_num = 200)





