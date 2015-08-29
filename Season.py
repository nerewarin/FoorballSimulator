# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'
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
        self.prev_season = self.season_id - 1
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

        # while UEFA unsupported, run only national tournaments
        # split tournaments by type
        self.national_tournaments = season_tournaments[2:]
        self.nations = len(self.national_tournaments) / 2
        if self.nations % 2:
            raise ValueError, "number of Leagues and Cups hould equals"

        self.national_leagues = self.national_tournaments[:self.nations]
        self.national_cups    = self.national_tournaments[self.nations:]

        self.uefa_tournaments = season_tournaments[:2]

        # move UEFA tournaments to the end
        self.tournaments = self.national_tournaments + self.uefa_tournaments

        # create teams instances and get all its data from database
        # Teams contains method setTournResults to quick access to results of current tournament used by cups and UEFA
        self.teams = Teams(self.season_id, self.year, self.nations)

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
        run national leagues and cups, storing all results in database
        """
        self.RunNationalLeagues()
        self.RunNationalCups()

    def RunNationalLeagues(self):
        """
        run all national leagues:
        - get tournaments ids from season_tournaments
        - get members for every national league
        - run leagues simulations
        - store tournament_played, tournament_results, matches
        ratings of teams updated in team instances (in RAM)
        """
        tourn_type_id = self.national_leagues[0][1] # 0 cause any number is ok
        classname = self.tourn_classes[tourn_type_id - 1].replace(" ", "_")
        tourn_class = getattr(sys.modules[__name__], classname)

        # TODO ALWAYS ENGLAND LEAGUE IF NOT FIRST SIM SEASON!!! CHECK TOURNAMENT ID!!

        for tournament in self.national_leagues:
            tourn_id = tournament[0]
            # tourn_type_id = tournament[1] - already defined above
            country_id = tournament[2]

            # get last Leagues results and run new Leagues
            members = self.teams.getTournResults(tourn_id)
            # if this is the 1st season simulation (prev results not stored in RAM), get it from database and save as
            # an attribute of Teams instance
            if not members:
                if self.year <= db.START_SIM_SEASON:
                    # print "setNationalResults by rating for first season"

                    # get all team ids from defined country id - like they ordered by default in team_info table
                    # print "self.country_id=", self.country_id
                    teams_tuples = db.select(what="id", table_names=db.TEAMINFO_TABLE, where=" WHERE ",
                                             columns="id_country ", sign=" = ", values=country_id, fetch="all", ind="all")
                    teams_indexes = [team[0] for team in teams_tuples]

                else:
                    # print "setNationalResults by position of previous national national_leagues results"

                    # query to tournament_played table to get id_tournament from prev season
                    query_tourn_played_id = "SELECT id FROM %s WHERE id_season = '%s' AND id_type = '%s'" % \
                                     (db.TOURNAMENTS_PLAYED_TABLE, self.prev_season, tourn_id)
                    print "query_tourn_played_id =", query_tourn_played_id
                    db.trySQLquery(func="execute", query=query_tourn_played_id)
                    query_tourn_played_id = db.CUR.fetchone()[0]
                    # query_to_results = "SELECT id_team FROM %s WHERE id_tournament = '(%s)';" % \
                    #                    (db.TOURNAMENTS_RESULTS_TABLE, query_tourn_played_id)
                    # print "query_to_results =", query_to_results

                    teams_tuples = db.select(what="id_team", table_names=db.TOURNAMENTS_RESULTS_TABLE, where=" WHERE ",
                                             columns="id_tournament ", sign=" = ", values=query_tourn_played_id, fetch="all",
                                             ind="all")
                    # teams_tuples = db.trySQLquery(func="execute", query=query_to_results)
                    teams_indexes = [team[0] for team in teams_tuples]

                # store teams indexes
                self.teams.setTournResults(tourn_id, teams_indexes)
                # now we can get teams instances from that indexes
                members = self.teams.getTournResults(tourn_id)
            else:
                pass

            # FOR NOW WE ARE READY TO RUN NEW NATIONAL LEAGUE
            # RUN TOURNAMENT (members will be collected by tournament itself)
            # tourn = tourn_class(name=tourn_id, season=self.season_id, year=self.year,
            #  TODO SEASON OBJ INSTEAD OF ID
            tourn = tourn_class(name=tourn_id, season=self.getID(), year=self.year,
                                members = members, country_id=country_id)
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

            # store teams for league in external class
            self.teams.setTournResults(tourn_id, teams_ind_by_pos)
            # print "updated self.teams", [team.getID() for team in self.teams.getTournResults(tourn_id)]

        # print "\nfinally_print_all_teams"
        print "National leagues (%s) were played and stored in db" % self.nations
        # print "self.teams", self.teams, "\n"

    def RunNationalCups(self):
        """
        run all national leagues:
        - get tournaments ids from season_tournaments
        - get members for every national cup by getting members in order of pos from national tournament results
        - run cups simulations
        - store tournament_played, tournament_results, matches
        ratings of teams updated in team instances (in RAM)
        """
        tourn_class = getattr(sys.modules[__name__], "Cup")
        for tournament in self.national_cups:
            cup_id = tournament[0]
            # we run national cup using seeding corresponding to national league results
            # this expression is true while tournaments are stored in this order in database and
            # in self.national_tournaments
            league_id = cup_id - self.nations
            country_id = tournament[2]
            cup = tourn_class(name=cup_id, season=self.season_id, year=self.year,
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

        # after all season simulation, save countries and teams updated ratings
        self.save_ratings_to_db()

    def save_countries_ratings(self):
        """
        store updated countries ratings
        """
        raise NotImplementedError

    def save_teams_ratings(self):
        """
        store updated teams ratings
        """
        team_ratings = [format(team.getRating(), '.3f') for team in self.teams.get_team()]
        raise NotImplementedError

    def save_ratings_to_db(self):
        """
        save new counties and teams ratings in database
        """
        print "save_ratings_to_db after season %s" % self.year
        db.fill_countries_ratings(self.season_id, self.teams.get_team())
        db.fill_teams_ratings(self.season_id, self.teams.sorted_by_rating())


    def RunUEFATournaments(self):
        """
        run UEFA tournaments
        """
        self.run_UEFA_Champions_League()
        print "ok run_UEFA_Champions_League\n"
        print "print ratings"
        print [format(team.getRating(), '.3f') for team in self.teams.get_team()]
        # for team in self.teams.get_team():
        #     print team.getRating()

        self.run_UEFA_Europa_League()
        print "ok run_UEFA_Europa_League\n"
        print "print ratings"
        print [format(team.getRating(), '.3f') for team in self.teams.get_team()]
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
        # get Qual 3 and Qual 4 loosers indexes
        q3 = [i[0] for i in db.select(what="id_team", table_names=db.TOURNAMENTS_RESULTS_TABLE, where=" WHERE ",
                                     columns="position", sign=" LIKE ", values="'Q%3'", fetch="all", ind="all")]
        q4 = [i[0] for i in db.select(what="id_team", table_names=db.TOURNAMENTS_RESULTS_TABLE, where=" WHERE ",
                                     columns="position", sign=" LIKE ", values="'Q%4'", fetch="all", ind="all")]
        self.CL_EL_seeding["Qualification 3"] = [self.teams.get_team(ind-1) for ind in q3]
        self.CL_EL_seeding["Qualification 4"] = [self.teams.get_team(ind-1) for ind in q4]
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
                                    name = UEFA_EL_TYPE_ID,
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
    TESTS_NUM = 2
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
