# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'
from DataStoring import save_ratings, CON, CUR
import DataStoring as db
import DataParsing
from Leagues import League
from Cups import Cup
from UEFA_Champions_League import UEFA_Champions_League
import values as v
import util
import sys

class Season(object):

    """
    creates all tournament
    """
    def __init__(self):
        """

        :param season_year: string like "2014/2015"
        :return:
        """
        self.season_id, self.year = self.saveSeason()
        # print "self.id, self.year", self.id, self.year


    # # TODO 1) see League about converting round_num to 1/4, final, qual , etc
    # # TODO 2) add schemes of UEFA tournaments with the help of reglaments wiki


    def run(self):
        # # connect to DB
        # con, cur = CON, CUR

        # TODO run every match that exists in table "Tournaments"
        season_tournaments = db.select(what=["id", "type", "id_country"],
                                            table_names=db.TOURNAMENTS_TABLE, fetch="all", ind = "all")
        print "season_tournaments=", season_tournaments
        tourn_classes = [clname[0] for clname in db.select(what="name", table_names=db.TOURNAMENTS_TYPES_TABLE, fetch="all", ind="all")]
        print "tourn_classes =%s" % tourn_classes
        # TODO support UEFA
        # for tournament in season_tournaments:
        # while UEFA unsupported, run only national tournaments
        # national_tournaments = season_tournaments[2:]
        # uefa_tournaments = season_tournaments[:2]
        # move UEFA tournaments to the end
        tournaments = season_tournaments[2:] + season_tournaments[:2]
        for tournament in tournaments:
            tourn_id = tournament[0]
            tourn_type_id = tournament[1]
            # example: tourn_type_id = 3 for league, so index 2 in list of tourn_classes names
            classname = tourn_classes[tourn_type_id - 1].replace(" ", "_")
            country_id = tournament[2]
            tourn_class = getattr(sys.modules[__name__], classname)

            country_name = db.select(what="name", table_names=db.COUNTRIES_TABLE, where=" WHERE ", columns="id", sign=" = ",
                      values=country_id, fetch="one", ind=0)
            print "tourn_id=%s, classname=%s, country_id=%s, country_name=%s" %\
                  (tourn_id, classname, country_id, country_name)
            # teamnames = DataParsing.parse_domesticleague_results(country_name)
            # print "teamnames", teamnames
            # if tourn_id == 82:
            #     pass

            # RUN TOURNAMENT (members will be collected by tournament itself)
            tourn = tourn_class(name=tourn_id, season=self.season_id, year=self.year, country_id=country_id)
            # tourn.run()


            # if country_id:
            #     print "play national tournament"
            # else:
            #     print "play UEFA tournament"
        # columns = table_name, tournament_name, tournament_type, tournament_country
        # counter += gen_national_tournaments(con, cur, columns, "Cup", sorted_countries)

        # after all
        # save_ratings(con, cur, [self.season_year], teamsL)


    def saveSeason(self):
        """
        insert new row to SEASONS_TABLE, defining new id,
        return id and name of new rows
        """
        print "saving season to database"
        columns = db.select(table_names=db.SEASONS_TABLE, fetch="colnames", suffix = " LIMIT 0")[1:]
        print "SEASONS_TABLE columns are ", columns
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
        # # better (but slowler) to use full recreation
        db.Test()

    # RUN SEASON
    for t_ in range(t_num):
        print "\n=======================================\nTEST SEASON %s" % (t_ + 1)
        Season().run()

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
