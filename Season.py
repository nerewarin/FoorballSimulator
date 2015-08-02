# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'
from DataStoring import save_ratings, CON, CUR
import DataStoring as db
import DataParsing
from Team import Team, Teams
from Leagues import League
from Cups import Cup
from UEFA_Champions_League import UEFA_Champions_League
import values as v
from values import Coefficients as C, TournamentSchemas as schemas, UEFA_CL_TYPE_ID, \
    UEFA_EL_TYPE_ID, VALUES_VERSION, UEFA_TOURNAMENTS_ID, UEFA_CL_SCHEMA, UEFA_EL_SCHEMA
import util
import sys
import warnings

class Season(object):

    """
    creates all tournament
    """
    def __init__(self):
        """

        :param season_year: string like "2014/2015"
        :return:
        """
        # int id, str year
        self.season_id, self.year = self.saveSeason()
        if self.year <= db.START_SIM_SEASON:
            print "setNationalResults by rating for first season"
        else:
            print "setNationalResults by position of previous national leagues results"


        # classnames of tournaments
        self.tourn_classes = [clsname[0] for clsname in db.select(what="name", table_names=db.TOURNAMENTS_TYPES_TABLE,
                                                           fetch="all", ind="all")]

        # print "self.id, self.year", self.id, self.year
        season_tournaments = db.select(what=["id", "type", "id_country"],
                                            table_names=db.TOURNAMENTS_TABLE, fetch="all", ind = "all")
        # print "season_tournaments=", season_tournaments
        self.tourn_classes = [clname[0] for clname in db.select(what="name", table_names=db.TOURNAMENTS_TYPES_TABLE, fetch="all", ind="all")]
        # print "tourn_classes =%s" % self.tourn_classes
        # TODO support UEFA
        # for tournament in season_tournaments:
        # while UEFA unsupported, run only national tournaments
        # split tournaments by type
        self.national_tournaments = season_tournaments[2:]
        self.nations = len(self.national_tournaments) / 2
        if self.nations % 2:
            raise ValueError, "number of Leagues and Cups hould equals"

        self.leagues = self.national_tournaments[:self.nations]
        self.cups    = self.national_tournaments[self.nations:]

        self.uefa_tournaments = season_tournaments[:2]

        # move UEFA tournaments to the end
        self.tournaments = self.national_tournaments + self.uefa_tournaments


    def getID(self):
        return self.season_id

    def getNations(self):
        return self.nations

    def getNationalResults(self, tourn_id = None):
        """
        return list of teams ordered by result of the last tournament_played
        :param tourn_id:  id from Tournaments (if None, return full dictionary)
        :return:
        """
        if not tourn_id:
            return self.teams
        return self.teams.getTournResults(tourn_id)

    # @util.timer # profit 6 sec to 1 sec by multi-values inserting
    def RunNationalTournaments(self):
        """
        storing all info about previous played tournaments to united dictionary (Team.Teams instance)
        """
        self.teams = Teams(self.season_id, self.year, self.nations)

        # LEAGUES ***********
        # get last Leagues results and run new Leagues
        tourn_type_id = self.leagues[0][1] # 0 cause any number is ok
        classname = self.tourn_classes[tourn_type_id - 1].replace(" ", "_")
        tourn_class = getattr(sys.modules[__name__], classname)
        for tournament in self.leagues:
            tourn_id = tournament[0]
            # tourn_type_id = tournament[1] - common use in line above
            country_id = tournament[2]

            if self.year <= db.START_SIM_SEASON:
                # print "setNationalResults by rating for first season"

                # get all team ids from defined country id - like they ordered by default in team_info table
                # print "self.country_id=", self.country_id
                teams_tuples = db.select(what="id", table_names=db.TEAMINFO_TABLE, where=" WHERE ",
                                         columns="id_country ", sign=" = ", values=country_id, fetch="all", ind="all")
                teams_indexes = [team[0] for team in teams_tuples]

            else:
                # print "setNationalResults by position of previous national leagues results"

                # query to tournament_played table to get id_tournament
                query_tourn_id = "SELECT id FROM %s WHERE id_season = '%s' AND id_type = '%s';" % \
                                 (db.TOURNAMENTS_PLAYED_TABLE, self.season_id, tourn_type_id)
                print "query_tourn_id =", query_tourn_id
                query_to_results = "SELECT id_team FROM %s WHERE id_tournament = '%s';" % \
                                   (db.TOURNAMENTS_RESULTS_TABLE, query_tourn_id)
                print "query_to_results =", query_to_results

                teams_tuples = db.select(what="id", table_names=db.TOURNAMENTS_RESULTS_TABLE, where=" WHERE ",
                                         columns="id_tournament ", sign=" = ", values=query_tourn_id, fetch="all",
                                         ind="all")
                teams_indexes = [team[0] for team in teams_tuples]

            # store teams for league in external class
            # self.teams.setTournResults(tourn_id, [Team(ind) for ind in teams_indexes])
            self.teams.setTournResults(tourn_id, teams_indexes)
            # print "self.teams", self.teams
            #
            # print "tourn_id=%s, classname=%s, country_id=%s" %\
            #       (tourn_id, classname, country_id)

            # FOR NOW WE ARE READY TO RUN NEW NATIONAL LEAGUE
            # RUN TOURNAMENT (members will be collected by tournament itself)
            # tourn = tourn_class(name=tourn_id, season=self.season_id, year=self.year, # TODO SEASON OBJ INSTEAD OF ID
            tourn = tourn_class(name=tourn_id, season=self.getID(), year=self.year,
                                members = self.teams.getTournResults(tourn_id), country_id=country_id)
            final_table = tourn.run()
            # print "final_table\n", final_table
            # print "NEED TO UPDATE self.teams() WHILE WE REMEMBER ABOUT THIS RESULTS"

            # TEAMS
            # # sort teams by pos from table of just played tournament
            # teams_by_pos = [result["Team"] for result in final_table]
            # # print "teams_by_pos", [team.getID() for team in teams_by_pos]
            # self.teams.setTournResults(tourn_id, teams_by_pos)
            # # print "updated self.teams", [team.getID() for team in self.teams.getTournResults(tourn_id)]

            # IDS
            teams_ind_by_pos = [result["Team"].getID() for result in final_table]
            # print "teams_by_pos", [team.getID() for team in teams_by_pos]
            self.teams.setTournResults(tourn_id, teams_ind_by_pos)
            # print "updated self.teams", [team.getID() for team in self.teams.getTournResults(tourn_id)]

        # print "\nfinally_print_all_teams"
        print "National leagues (%s) were played and stored in db" % self.nations
        # print "self.teams", self.teams, "\n"

        # CUPS ***********
        # tourn_type_id = self.cups[0][1] # 0 cause any number is ok
        # classname = self.tourn_classes[tourn_type_id - 1].replace(" ", "_")
        # tourn_class = getattr(sys.modules[__name__], classname)
        tourn_class = getattr(sys.modules[__name__], "Cup")
        for tournament in self.cups:
            cup_id = tournament[0]
            # we run national cup using seeding corresponding to national league results
            # this expression is true while tournaments are stored in this order in database and
            # in self.national_tournaments
            league_id = cup_id - self.nations
            country_id = tournament[2]
            cup = Cup(name=cup_id, season=self.season_id, year=self.year,
                                members = self.teams.getTournResults(league_id), country_id=country_id)
            cupwinner = cup.run()[0]
            cupwinner_id  = [cupwinner.getID()]
            self.teams.setTournResults(cup_id, cupwinner_id)
            # print "update winner for cup", [team.getID() for team in self.teams.getTournResults(cup_id)]
        print "National Cups (%s) were played and stored in db" % self.nations


    def get_ntp(self):
        """
        setting teams for every round by their national results
        """
        # UEFA CL ********
        tourn_class = getattr(sys.modules[__name__], "UEFA_Champions_League")
        tourn_id = UEFA_CL_TYPE_ID
        # preparing teams to CL 0 should we do it here or by UEFA Tournament itself?

        # sort self.teams by tournament (country) ratings
        self.ntp_teams = self.teams.sortedByCountryPos(self.season_id)
        print "ok sort self.teams by tournament (country) ratings"
        # for teams in self.ntp_teams:
        #     print [team.getID() for team in teams]
        return self.ntp_teams


    def run(self):
        """
        runs all national and international tournmanets of the season
        """

        # make a dict of {tourn_id - teams}, where teams is list, sorted by rating (if 1st season)
        # or position from prev. national league
        # and then run
        self.RunNationalTournaments()
        print "ok RunNationalTournaments\n"
        print "print ratings"
        print [team.getRating() for team in self.teams.get_team()]
        # for team in self.teams.get_team():
        #     print team.getRating()

        # # shift_seed is used to shift indexes of seeded members in cases - if some country has'n got so many counties
        # # to pass them to UEFA cup, so shift nation
        # self.shift_nation = 0
        # # or if member seeded to UEFA_EL by Cup was already seeded to UEFA_CL - so get team from next pos of national
        # # league
        # self.shift_team = 0

        self.RunUEFATournaments()
        print "ok RunUEFATournaments\n"

    #     # after all
    #     # save_ratings(con, cur, [self.season_year], teamsL)
    # TODO recompute and save countries rating in db
    # TODO save teams rating in db

    def RunUEFATournaments(self):
        """
        run UEFA tournaments
        """
        self.run_UEFA_Champions_League()
        print "ok run_UEFA_Champions_League\n"
        print "print ratings"
        print [team.getRating() for team in self.teams.get_team()]
        # for team in self.teams.get_team():
        #     print team.getRating()

        self.run_UEFA_Europa_League()
        print "ok run_UEFA_Europa_League\n"
        print "print ratings"
        print [team.getRating() for team in self.teams.get_team()]
        # for team in self.teams.get_team():
        #     print team.getRating()

    def run_UEFA_Champions_League(self):
        # RUN UEFA CL
        tourn_class = getattr(sys.modules[__name__], "UEFA_Champions_League")
        UEFA_CL_tourn = tourn_class(season = self,
                                     year = self.year,
                                     # members = members,
                                     # pair_mode = pair_mode,
                                     # seeding = seeding,
                                     save_to_db = True,
                                     # prefix = sub_tourn_name,
                                     type_id = UEFA_CL_TYPE_ID)

        # save for future access to UEFA_EL for seeding
        self.UEFA_CL_members = UEFA_CL_tourn.getMember()

        UEFA_CL_tourn.run()

        # save group_third_places
        self.CL_EL_seeding = UEFA_CL_tourn.get_group3()
        # get Qual 3 and Qual 4 losers
        q3 = [i[0] for i in db.select(what="id_team", table_names=db.TOURNAMENTS_RESULTS_TABLE, where=" WHERE ",
                                     columns="position", sign=" LIKE ", values="'Q%3'", fetch="all", ind="all")]
        q4 = [i[0] for i in db.select(what="id_team", table_names=db.TOURNAMENTS_RESULTS_TABLE, where=" WHERE ",
                                     columns="position", sign=" LIKE ", values="'Q%4'", fetch="all", ind="all")]
        self.CL_EL_seeding["Qualification 3"] = q3
        self.CL_EL_seeding["Qualification 4"] = q4
        # print "self.teams", self.teams
        # print "self.teams", self.teams.sortedByID(), len(self.teams.sortedByID())
        # print "self.teams", self.teams[q3[0]]

    def get_CL_EL_seeding(self, key = None):
        print "self.CL_EL_seeding", self.CL_EL_seeding
        if key:
            return self.CL_EL_seeding[key]
        return self.CL_EL_seeding

    def get_UEFA_CL_members(self):
        """
        used by UEFA_EL to check cup winner not already seeded in CL this season
        """
        return self.UEFA_CL_members

    def check_seed_in_CL(self, team):
        """
        used for UEFA Europe League to check if cup winners were already seed in Champion League
        """
        if team in self.UEFA_CL_members:
            return True
        return False

    def run_UEFA_Europa_League(self):
        tourn_class = getattr(sys.modules[__name__], "UEFA_Champions_League") # TODO NEED NEW CLASS OR NOT?
        UEFA_EL_tourn = tourn_class(season = self,
                                     year = self.year,
                                     # members = members,
                                     # pair_mode = pair_mode,
                                     seeding = UEFA_EL_SCHEMA,
                                     save_to_db = True,
                                     # prefix = sub_tourn_name,
                                     type_id = UEFA_EL_TYPE_ID)

        # # save for future access to UEFA_EL for seeding
        # UEFA_EL_members = UEFA_EL_tourn.getMember()

        results = UEFA_EL_tourn.run()
        print results




    def saveSeason(self):
        """
        insert new row to SEASONS_TABLE, defining new id,
        return id and name of new rows
        """
        print "saving season to database"
        columns = db.select(table_names=db.SEASONS_TABLE, fetch="colnames", suffix = " LIMIT 0")[1:]
        # print "SEASONS_TABLE columns are ", columns
        # values = db.select(table_names=db.SEASONS_TABLE, fetch="one", suffix = " LIMIT 0")[1:]

        last_season = db.trySQLquery(query="SELECT name FROM %s ORDER BY ID DESC LIMIT 1"
                                      % db.SEASONS_TABLE, fetch="one")

        print "last_season year %s" % last_season

        # seasons will be simulated starting from initial reference season, it should already be in database,
        # of it it was truncated, create it now
        if not last_season:
            # if initial season was truncated, create it with id=1 and then normally create new_season with id=2
            initial_season = "'" + db.START_SEASON + "'"
            db.insert(db.SEASONS_TABLE, columns, initial_season)
            last_season = db.START_SEASON

        # increment string 2014/2015 to 2015/2016
        new_season = "'" + str([(int(year) + 1) for year in last_season.split("/")])[1:-1].replace(", ", "/") + "'"

        print "new_season year %s" % new_season
        values = new_season

        # save season with new name in db
        db.insert(db.SEASONS_TABLE, columns, values)

        new_season_id = db.trySQLquery(query="SELECT id FROM %s ORDER BY ID DESC LIMIT 1"
                                           % db.SEASONS_TABLE, fetch="one")
        return new_season_id, new_season

# TEST
@util.timer
def Test(*args, **kwargs):
    """
    Test Season Class

    :param args:
    :param kwargs: test arguments are listed below

    by default, save_db = True,  all other options are disabled

    :return:
    """


    # used by clearing inserted rows by test after it runs
    last_m_row = db.trySQLquery(query="SELECT id FROM %s ORDER BY ID DESC LIMIT 1"
                                      % db.MATCHES_TABLE, fetch="one")
    last_tp_row = db.trySQLquery(query="SELECT id FROM %s ORDER BY ID DESC LIMIT 1"
                                       % db.TOURNAMENTS_PLAYED_TABLE, fetch="one")
    last_tr_row = db.trySQLquery(query="SELECT id FROM %s ORDER BY ID DESC LIMIT 1"
                                       % db.TOURNAMENTS_RESULTS_TABLE, fetch="one")
    last_season_row = db.trySQLquery(query="SELECT id FROM %s ORDER BY ID DESC LIMIT 1"
                                       % db.SEASONS_TABLE, fetch="one")

    t_num = 1
    if "t_num" in kwargs:
        t_num = kwargs["t_num"]


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

    if pre_truncate:
        # db.truncate(db.TOURNAMENTS_PLAYED_TABLE)
        # db.truncate(db.TOURNAMENTS_RESULTS_TABLE)
        # db.truncate(db.MATCHES_TABLE)
        # # db.truncate(db.SEASONS_TABLE)
        # # delete all seasons but initial - but serial dowsn't drops
        # db.trySQLquery(query = "DELETE FROM %s WHERE id > '1'" % db.SEASONS_TABLE)

        # # better (but slower) to use full recreation
        db.Test()

    # RUN SEASON
    for t_ in range(t_num):
        print "\n=======================================\nTEST SEASON %s" % (t_ + 1)
        tst_season = Season()
        tst_season.run()

    if post_truncate:
        db.truncate(db.TOURNAMENTS_PLAYED_TABLE)
        db.truncate(db.TOURNAMENTS_RESULTS_TABLE)
        db.truncate(db.MATCHES_TABLE)
        db.truncate(db.SEASONS_TABLE)



if __name__ == "__main__":
    # team_num = 3
    # for pair_mode in range(2):
    #     Test("League", team_num = team_num, pair_mode = pair_mode, print_matches = True, print_ratings = False)

    # HOW MANY SEASONS WILL BE CREATED DURING THE TEST
    TESTS_NUM = 1
    # PRINT MATCHES AFTER RUN
    PRINT_MATCHES = False
    PRINT_MATCHES = True
    # PRINT RATINGS AFTER RUN
    PRINT_RATINGS = True
    PRINT_RATINGS = False
    # RESET ALL MATCHES DATA BEFORE TEST
    PRE_TRUNCATE = False
    PRE_TRUNCATE = True
    # RESET ALL MATCHES DATA AFTER TEST
    POST_TRUNCATE = False
    # POST_TRUNCATE = True
    # SAVE TO DB - to avoid data integrity (if important data in table exists), turn it off
    SAVE_TO_DB = False
    SAVE_TO_DB = True

    Test(t_num = TESTS_NUM, print_matches = PRINT_MATCHES, print_ratings = PRINT_RATINGS,
             pre_truncate = PRE_TRUNCATE, post_truncate = POST_TRUNCATE, save_to_db = SAVE_TO_DB)



        # Test("League", team_num = t_num, pair_mode = pair_mode,
        #      print_matches = PRINT_MATCHES, print_ratings = PRINT_RATINGS,
        #      pre_truncate = PRE_TRUNCATE, post_truncate = POST_TRUNCATE, save_to_db = SAVE_TO_DB)
