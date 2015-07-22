# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'


"""
create storage from HTML to Excel or Database
"""

import Team
import DataParsing
import util

import xlwt # write Excel xls
import xlrd # read Excel xls
import psycopg2 as db
import django
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os, operator, sys, time, warnings


### CONSTANTS ###

# database info
# DBNAME ="FootballSimDB".lower()
DBNAME ="football_sim".lower()
DBUSER = "postgres"
DBHOST = 'localhost'
DBPASSWORD = "GameDB"
SCHEMA = 'public'
# database connection
def connectGameDB(dbname=DBNAME, user=DBUSER, host = DBHOST, password=DBPASSWORD):
    con = db.connect(dbname=dbname, user=user, host = host, password=password)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    print "Database %s connected" % dbname
    return con, cur

CON, CUR = connectGameDB()


# season that ratings will be filled as initial (defines only tournament of field "tournament" in season - data will be parsed
# from default "2014/2015" season
START_SEASON = "2014/2015"

# table names
TEAMINFO_TABLENAME = "Team_Info"
COUNTRIES_TABLENAME = "Countries"
TOURNAMENTS_TABLENAME = "Tournaments"
CONSTANT_TABLES = (TEAMINFO_TABLENAME, COUNTRIES_TABLENAME, TOURNAMENTS_TABLENAME)
SEASONS_TABLENAME = "seasons"
TEAM_RATINGS_TABLENAME = "team_ratings"
COUNTRY_RATINGS_TABLENAME = "country_ratings"
PREDEFINED_TABLES = (SEASONS_TABLENAME, TEAM_RATINGS_TABLENAME, COUNTRY_RATINGS_TABLENAME)
MATCHES_TABLE = "matches"
TOURNAMENTS_PLAYED_TABLE = "tournaments_played"
TOURNAMENTS_RESULTS_TABLE = "tournament_results"



# CREATE EXCEL TABLE
def createExcelTable(filename, teamsL, overwrite = False):
    # create Excel table, if not exists
    if os.path.isfile(filename):
        if overwrite:
            print "overwritting %s" % filename
        else:
            print "initial xls was already created, see", filename
            return

    print "creating Excel Table", filename
    book = xlwt.Workbook(encoding="utf-8")

    sheet1 = book.add_sheet("Sheet 1")

    headers = ["№", "teamName", "ruName", "country", "rating 2014/2015", "10/11", "11/12", "12/13", "13/14", "14/15"]
    # attributes = ["getName", "getCountry", "getRating", "getRuName"]

    for j, header in enumerate(headers):
        # print 0, j, header
        sheet1.write(0, j, header)
    for i, team  in enumerate(teamsL):
        last_ratings = team.getLast5Ratings()
        for j in range(len(headers)):
            if j > 4:
                data = last_ratings.pop()
            else:
                data = team.attrib(j)()
            sheet1.write(i+1, j, data)


    book.save(filename)


def createTeamsFromExcelTable(excelFilename = "initial rating.xls"):
    """
    create list of Team objects, sorted by rating
    :param excelFilename: table that stores all ratings
    :return:
    """

    # read ExcelTable
    rb = xlrd.open_workbook(excelFilename,formatting_info=True)
    sheet = rb.sheet_by_index(0)
    # create teams list
    # create teams list sorted by rating
    teamsL = []
    for rownum in range(1, sheet.nrows): # exclude 1 cause there are headers
        row = sheet.row_values(rownum)
        # print row#.encode('utf8')
        name = row[1].replace("\'", "").replace("/", "-")
        print "creating teamsL", util.unicode_to_str(name)
        country = str(row[3])
        rating = float(row[4])
        ruName = row[2]
        uefaPos = int(row[0])
        countryID = "undefined"
        teamsL.append(Team.Team(name, country, rating, ruName, uefaPos, countryID))
        # print tournament, country, rating, ruName, uefaPos
    # print to console all teams
    return teamsL


# CREATE DATABASE AND TABLES
def createDB(teamsL, storage = "Postgre", overwrite = False):
    if storage == "Postgre":
        # https://www.ibm.com/developerworks/ru/library/l-python_part_11/
        django_ver = django.VERSION
        # using example from http://ideafix.tournament/wp-content/uploads/2012/05/Python-10.pdf
        db_api =  db.apilevel
        db_paramstyle = db.paramstyle
        db_threadsafety = db.threadsafety
        # http://stackoverflow.com/questions/19426448/creating-a-postgresql-db-using-psycopg2

        # connect to default DB (is specific DB not exists)
        # con, cur = connectGameDB(dbname='postgres', user=DBUSER, host = 'localhost', password=DBPASSWORD)
        con, cur = CON, CUR

        cur.execute('SELECT version()')
        ver = cur.fetchone()
        print ver # ('PostgreSQL 9.4.4, compiled by Visual C++ build 1800, 64-bit',)



        # team_count = DataParsing.createTeamsFromHTML("get count")
        team_count = len(teamsL)

        # CREATE DB for this application
        trySQLquery(cur.execute, 'SELECT exists(SELECT 1 from pg_catalog.pg_database where datname = %s)', (DBNAME,))
        isDB = cur.fetchone()[0]
        # print "BD exists?", isDB
        if not isDB:
            print "Database %s not found, creating" % DBNAME
            try:
                cur.execute('CREATE DATABASE ' + DBNAME)
            except db.DatabaseError, x:
                print x.pgerror.decode('utf8')
            con.commit()
        else:
            print "Database %s found" % DBNAME



        try:
            con = db.connect(database=DBNAME, user=DBUSER)
            cur = con.cursor()
            cur.execute('SELECT version()')
            ver = cur.fetchone()
            print "db ver = ", ver

        except db.DatabaseError, e:
            print 'Error %s' % e
            sys.exit(1)


        # PRINT EXISTING TABLES
        trySQLquery(cur.execute, """SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'""")
        print "tables of DB ", [tabletuple[0] for tabletuple in cur.fetchall()]


        # COUNTRIES COUNTER DICT
        countries = util.Counter()
        for team in teamsL:
            countries[team.getCountry()] +=1
        print "countries:teams_num", countries

        # when sorted, we can define country_ID for team with maximum teams
        sorted_countries = sorted(countries.items(), key=operator.itemgetter(1), reverse=True)
        # sorted_x will be a list of tuples sorted by the second element in each tuple. dict(sorted_x) == x.
        print "sorted_countries", sorted_countries


        if overwrite:
            # delete all data from constant and predefined tables and later fill again
            tables = ""
            for table in (CONSTANT_TABLES + PREDEFINED_TABLES):
                truncate(table)
            # for table in (CONSTANT_TABLES + PREDEFINED_TABLES):
            #     tables += (table + ", ")
            # tables = tables[:-2]
            # truncate_query = 'TRUNCATE ' + tables + ' RESTART IDENTITY CASCADE;'
            #
            # print "\nTRUNCATING ALL ROWS OF tables %s" % tables
            #
            # trySQLquery(cur.execute, truncate_query)
            # print "ok\n"


        def create_db_table(recreating, cur, con, table_name, func, columns_info):
            if not tableExists(cur, table_name):
                print "%s\" not exists, creating" % table_name
                func(cur, con, table_name, columns_info)
            elif recreating:
                print "%s exists but recreating enabled" % table_name
                # # DROP AND RECREATE
                trySQLquery(cur.execute, 'DROP TABLE %s' % table_name)
                con.commit()
                print "DROP table %s ok" %table_name
                # createTable_Countries(cur, con, table_name, team_count, sorted_countries)
                func(cur, con, table_name, columns_info)
            # elif recreating == "refill":
            #     # delete content not dropping table
            #     print "refill %s" % table_name
            #     trySQLquery(cur.execute, 'DELETE FROM %s' % table_name)
            #     func(cur, con, table_name, columns_info)
            else:
                print "%s is already exists" % table_name
                if recreating != "only inserting":
                    print "refill %s" % table_name
                    # trySQLquery(cur.execute, 'DELETE FROM %s' % table_name)
                    func(cur, con, table_name, columns_info)
            print


        # CREATE TABLE TeamCountries
        table_name = "Countries"
        # recreating = True
        recreating = False
        columnsInfo = list(sorted_countries)
        create_db_table(recreating, cur, con, table_name, fill_countries, columnsInfo)


        def assign_country_to_teams():
            for team in teamsL:
                teamCountry = team.getCountry()
                country_ID = get_country_id(cur, teamCountry)
                team.setCountryID(country_ID)

        # now we must set CountryID to teams objects
        assign_country_to_teams()

        # CREATE TABLE TeamInfo
        recreating = True
        recreating = False
        # create table if it doesn't exists or need recreating
        columnsInfo = (team_count, sorted_countries, teamsL)
        create_db_table(recreating, cur, con, TEAMINFO_TABLENAME, fill_TeamInfo, columnsInfo )


        # CREATE TABLE Tournaments
        table_name = "Tournaments"
        recreating = True
        recreating = False
        # tournament_ID = "ID"
        tournament_name = "name"
        tournament_type = "type"
        tournament_country = "id_country"
        # tournament_teams_count = "teams_count"
        columnsInfo = (tournament_name, tournament_type, tournament_country, sorted_countries)
        create_db_table(recreating, cur, con, table_name, fill_tournaments, columnsInfo )

        if overwrite:
            # FILL TEAMS AND COUNTRIES RATINGS FROM ONE PREVIOUSLY PLAYED "Basic" SEASON
            save_ratings(con, cur, [START_SEASON], teamsL)


        # close connection to DB
        if con:
            con.close()
        # delete cursor to DB
        if cur:
            cur.close()




def select(what = "*", table_names = "", where = "", columns = "", sign = "", values = "", suffix = "", fetch = "one"):

    inputs = (what, table_names, columns, values)
    outputs = []
    for input in inputs:

        if isinstance(input, list):
            output = ""
            for input_part in input:
                output += (str(input_part) + ", ")
            output = output[:-2]
        else:
            output = str(input)
        outputs.append(output)

    _what, tables, cols, vals = outputs
    select_query = 'SELECT '+ _what + ' FROM ' + tables + where + cols + sign + vals + suffix + ';'
    # select_query = 'SELECT * FROM ' + tables + ' WHERE '  + cols + " = " + vals + ';'
    print "select_query = ", select_query


    trySQLquery(CUR.execute, select_query)
    if fetch == "one":
        return CUR.fetchone()[0]
    elif fetch == "all":
        return CUR.fetchall()[0]
    elif fetch == "colnames":
        return [desc[0] for desc in CUR.description]
    else:
        raise NotImplementedError, "unknown fetch parameter"


def insert(table, columns, values):
    """

    :param table:
    :param columns:
    :param values:
    :param fetch:
    :return:
    """
    # vals  = (', '.join('"' + item + '"' for item in values if isinstance(item, str)))
    # vals = ""
    # for val in values:
    #     if isinstance(val, str)):
    #         vals +=
    # print "vals", vals
    # inputs = (columns, vals)

    inputs = (columns, values)
    # print "inputs =", inputs
    outputs = []
    for ind, input in enumerate(inputs):

        if isinstance(input, list):
            output = ""
            for input_part in input:
                # if ind == 1 and isinstance(input_part, str):  # only for string values!
                if ind == 1 : #only for  values!
                    # if isinstance(input_part, str):
                #     # add additional quotes to format values as ('%s', ..)
                #     print "AHAA"
                    output += ("'" + str(input_part) + "', ")
                    # output += ("\'" + str(input_part) + "\', ")
                    # else:

                else:
                    output += (str(input_part) + ", ")
                # output += (str(input_part) + ", ")
                # print "output", output
            output = output[:-2]
            # print "output = ", output
        else:
            output = str(input)
        outputs.append(output)

    cols, vals = outputs
    # print "vals = ", vals
    # print "sting vals", vals

    insert_query = 'INSERT INTO ' + table + ' (' + cols + ') VALUES (' + vals + ');'
    print "insert_query = ",  insert_query
    trySQLquery(CUR.execute, insert_query)


def truncate(table):
    """
    clears all rows of db table
    :param table:
    :return:
    """
    # TODO implement passing parameter "start_row" to truncate tests with other info integrity
    print "\nTRUNCATING ALL ROWS OF table %s" % table
    truncate_query = 'TRUNCATE ' + table + ' RESTART IDENTITY CASCADE;'
    trySQLquery(query=truncate_query)
    print "ok\n"


# def exists(cur, table_name, dbname, schema):
def tableExists(cur, table_name):
   try:
        cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (table_name.lower(),))
        isTeamInfo = cur.fetchone()[0]
        return isTeamInfo

   except db.DatabaseError, e:
        print e.pgerror.decode('utf8')
        sys.exit(1)


def get_country_id(cur, country_name):
    """
    converts string tournament to id by using
     select id from table "Countries"
    :param country_name:
    :return:
    """
    cur.execute("""SELECT id FROM Countries WHERE name = %s;""", (country_name, )) # ok
    country_ID = cur.fetchone()[0]
    return country_ID


def get_id_from_value(cur, table_name, column, value):
    """
    converts value to id
    :param cur:
    :param table:
    :param column:
    :param value:
    :return:
    """
    print "table_name, column, value =", table_name, column, value
    cur.execute("""SELECT id FROM %s WHERE %s = '%s';""", (table_name, column, value)) # ok
    id = cur.fetchone()[0]
    return id

# def trySQLquery(cur, func, query, data = None):
def trySQLquery(func = CUR.execute, query = None, data = None):
    try:
        # print "query = \n %s" % query, type(query)
        # print "data = ", data
        return func(query, data)

    except db.DatabaseError, e:
        print "error when executing trySQLquery"
        print e.pgerror.decode('utf8')
        sys.exit(1)

def save_ratings(con, cur, seasons, teamsL):
    """

    :param con: connection
    :param cur: cursor
    :param seasons:  string like "2014/2015"
    :param teamsL:
    :return:
    """
    print "save ratings for seasons", seasons

    # FILL SEASON NAMES
    for ind, season in enumerate(seasons):
        # print "season", season

        season_id = fill_season(con, cur, season)
        # if isinstance(season, str):
        #     # convert season year to ID
        #     season_id = fill_season(con, cur, season)
        #
        # elif isinstance(season, int):
        #     # or use it implicitly
        #     season_id = int(season)
        #
        # else:
        #     raise TypeError, "unknown season type"

        fill_teams_ratings(con, cur, season_id, teamsL)

        fill_countries_ratings(con, cur, season_id, teamsL)


def fill_season(con, cur, season):
    """
    add new row (id-name) to SEASONS_TABLENAME
    :param con:
    :param cur:
    :param season:
    :return:
    """
    data = (SEASONS_TABLENAME, season)
    trySQLquery(cur.execute, "INSERT INTO %s (name) VALUES ('%s');" % data)
    con.commit()
    # get last season ID (from last row)
    cur.execute("""SELECT id FROM seasons WHERE name = %s;""", (str(season),)) # ok
    season_id = cur.fetchall()[0][0]
    con.commit()
    return season_id


def fill_teams_ratings(con, cur, season_id, teamsL):
    """
    add new rows to (id, season, teamID, rating, uefa_pos)
    teamsL must be sorted

    :param con:
    :param cur:
    :param season_id:
    :param teamsL:  must be already sorted by rating and ind = UEFApos + 1 for teamsl[ind]
    :return:
    """
    for ind, team in enumerate(teamsL):
        # team_id = get_id_from_value(cur, TEAMINFO_TABLENAME, "name", team.getName())
        team_id = ind + 1
        position = ind + 1
        rating = team.getRating()
        # print "team_id %s, season %s, rating %s, position %s" % (team_id, season_id, rating, position)
        columns = ("id_season", "id_team", "rating", "position")
        values = (season_id, team_id, rating, position)
        data = [TEAM_RATINGS_TABLENAME] + list(columns) + list(values)
        trySQLquery(cur.execute, "INSERT INTO %s (%s, %s, %s, %s) VALUES ('%s', '%s', '%s', '%s');" % tuple(data))
        con.commit()
    print "inserted %s rows to %s" % (len(teamsL), TEAM_RATINGS_TABLENAME)


def fill_countries_ratings(con, cur, season_id, teamsL):
    """
    for given season adds new rows to country_ratings table

    Problem! normalized sum of teams rating not equals country_rating from UEFA site for 2014/2015,
    England must be 2nd but its 4th - this is cause I compute country_ratings only as sum of teams_ratings of
    2015/2015 divided my teams in country
    Solving :
    this is because in previous seasons teams in UEFA not constant!
    in 2015 there were 454 but in 2011 there were only 439!

    :param con:
    :param cur:
    :param season_id:
    :return:
    """

    # print "fill_countries_ratings"
    country_ratings = {}
    for team in teamsL:
        teamID = team.getCountryID()
        # team_rating = team.getRating()
        # print "team_rating", team_rating, type(team_rating)

        # sum of all team ratings
        if teamID not in country_ratings.keys():
            country_ratings[teamID] = [0, 0] # fist is rating, second is count of appended team ratings for country

        # increase sum of ratings
        country_ratings[teamID][0] +=  team.getRating()
        # increment teams_count
        country_ratings[teamID][1] +=  1
    # print "countryID_and_sum_of_team_ratings", country_ratings

    # normalize sums by teams_count
    for country_id, (sum_of_teams_ratings, teams_count) in country_ratings.iteritems():
        # teams_count = trySQLquery(cur, con, ".............")
        country_ratings[country_id] = float(sum_of_teams_ratings) / teams_count
        # print country_id, (sum_of_teams_ratings, teams_count)
        # print "normalized rating for ", country_id, " = ", country_ratings[country_id]
    # print "\nnormalized ratings", country_ratings

    sorted_country_ratings = sorted(country_ratings.items(), key=operator.itemgetter(1), reverse = True)
    # print "sorted_country_ratings", sorted_country_ratings
    # # for tple in sorted_country_ratings:
    # #     print tple

    # country_ratings.items() in a list of sorted tuples (id, rating)
    position = 0
    for ind, (country_id, country_rating) in enumerate(sorted_country_ratings):
        position = ind + 1
        # insert to database
        columns = ["id_season", "id_country", "rating", "position"]
        values = [season_id, country_id, country_rating, position]
        data = columns + values
        query = "INSERT INTO " + COUNTRY_RATINGS_TABLENAME + " (%s, %s, %s, %s) VALUES ('%s', '%s', '%s', '%s');" % tuple(data)
        # print query
        trySQLquery(cur.execute, query)
    print "inserted %s rows to %s" % (position, COUNTRY_RATINGS_TABLENAME)
    con.commit()



def fill_TeamInfo(cur, con, table_name, columnsInfo):
    try:
        team_count, sorted_countries, teamsL = columnsInfo

        for ind in xrange(team_count):
            team = teamsL[ind]
            # teamName = util.unicode_to_str(team.getName())
            # avoiding problem with "'s" in Saint Patrick's Athletic FC
            teamName = util.unicode_to_str(team.getName()).replace("\'", "")
            # teamRuName = team.getRuName()
            teamRuName = util.unicode_to_str(team.getRuName())
            teamCountry = team.getCountry()
            if teamName == "College Europa FC":
                teamEmblem = open(DataParsing.EMBLEMS_STORAGE_FOLDER +  "Europa FC" + ".png", 'rb').read()
            else:
                teamEmblem = open(DataParsing.EMBLEMS_STORAGE_FOLDER +  teamName + ".png", 'rb').read()

            # cur.execute("""SELECT id FROM Countries WHERE tournament = %s;""", (teamCountry, )) # ok
            # country_ID = cur.fetchone()[0]
            country_ID = team.getCountryID()

            # fill table
            # data = (table_name, str(teamName), teamRuName, country_ID, db.Binary(teamEmblem))
            data = (table_name, str(teamName), teamRuName, country_ID)
            # data = (table_name, str(teamName), country_ID)
            # print data
            # query =  "INSERT INTO %s (tournament, runame, id_country, team_emblem) VALUES ('%s', '%s', '%s', '%s');" % data
            query =  "INSERT INTO %s (name, runame, id_country) VALUES ('%s', '%s', '%s');" % data
            # query =  "INSERT INTO %s (tournament, id_country) VALUES ('%s', '%s');" % data
            # query =  "INSERT INTO TeamInfo (team_ID, team_Name, team_RuName, countryID) VALUES (%s, %s, %s, %s);"

            # use psycopg2.Binary(binary) from http://iamtgc.com/using-python-to-load-binary-files-into-postgres/
            # data = (str(table_name), teamName, teamRuName, country_ID, db.Binary(teamEmblem), )
            # data = (teamID, teamName, teamRuName, country_ID, teamEmblem, )
            # data = (teamID, unicode_to_str(teamName), unicode_to_str(teamRuName), country_ID)
            # print "insert data", data, "to table TeamInfo"
            # trySQLquery(cur.execute, query, data)
            trySQLquery(cur.execute, query)
            con.commit()

        print "inserted %s rows to %s" % (team_count, table_name)
        con.commit()
    except db.DatabaseError, e:
        # print 'Error %s' % e.pgerror.decode('utf8')
        print e.pgerror.decode('utf8')
        sys.exit(1)


def fill_countries(cur, con, table_name, sorted_countries):
    try:
        # INSERT TO TABLE Countries [table_name, team_count, sorted_countries]
        for ind, (country, teams_count) in enumerate(sorted_countries):
            query =  "INSERT INTO %s (name, teams_count) VALUES ('%s', '%s');" % (table_name, country, teams_count)
            # print "insert data", data, "to table Countries"
            cur.execute(query)
        print "inserted %s rows to %s" % (len(sorted_countries), table_name)
        con.commit()

    except db.DatabaseError, e:
        print e.pgerror.decode('utf8')
        sys.exit(1)


def fill_tournaments(cur, con, table_name, columnsInfo):#team_count, sorted_countries, teamsL):
    """
    fill all needed tournament info to database table
    :param cur:
    :param con:
    :param table_name:
    :param columnsInfo:
    :return:
    """
    tournament_name, tournament_type, tournament_country, sorted_countries = columnsInfo
    columns = table_name, tournament_name, tournament_type

    # INSERT TO TABLE Tournaments

    counter = 0 # just for printing
    t_name = "UEFA Champions League" # error was because of %s instead of '%s' in SQL-query
    t_type = "UEFA_CL"
    # t_country = "UEFA" # international
    # t_pteams = 32
    t_teams_num = 77
    # insert_tournament_to_DB_table(t_name, t_type, t_country)#, t_teams_num)
    insert_tournament_to_DB_table(con, cur, columns, t_name, t_type)#, t_teams_num)
    counter += 1

    t_name = "UEFA Europa League" # error was because of %s instead of '%s' in SQL-query
    t_type = "UEFA_EL"
    t_teams_num = 195
    insert_tournament_to_DB_table(con, cur, columns, t_name, t_type)#, t_teams_num)
    # insert_tournament_to_DB_table(t_name, t_type, t_country)#, t_teams_num)
    counter += 1

    columns = table_name, tournament_name, tournament_type, tournament_country
    counter += gen_national_tournaments(con, cur, columns, "League", sorted_countries)
    counter += gen_national_tournaments(con, cur, columns, "Cup", sorted_countries)

    print "inserted %s rows to %s" % (counter, table_name)

    con.commit()


def insert_tournament_to_DB_table(con, cur, columns, t_name, t_type, t_country = None):#, t_teams_num):
    # for national tournaments
    if t_country:
        table_name, tournament_name, tournament_type, tournament_country = columns
        query =  "INSERT INTO %s (%s, %s, %s) VALUES ('%s', '%s', '%s');" % \
                 (table_name,
                  tournament_name, tournament_type, tournament_country,
                  t_name, t_type, t_country) #t_teams_num)
    # for international tournaments (all but country_ID will be inserted)
    else:
        table_name, tournament_name, tournament_type = columns
        query =  "INSERT INTO %s (%s, %s) VALUES ('%s', '%s');" % \
                 (table_name,
                  tournament_name, tournament_type,
                  t_name, t_type)
    # print "insert_tournament_to_DB_table"
    # print query
    trySQLquery(cur.execute, query)
    con.commit()


def gen_national_tournaments(con, cur, columns, t_type, sorted_countries):
    counter = 0
    for t_country, teams_count in sorted_countries:
        t_name = t_country + " " + t_type
        country_ID = get_country_id(cur, t_country)
        # insert_tournament_to_DB_table(t_name, t_type, t_country)#, teams_count)
        insert_tournament_to_DB_table(con, cur, columns, t_name, t_type, country_ID)#, teams_count)
        counter += 1
    return counter


def TestStorage(storage, teamsL, overwrite = False):
    if storage == "Excel":
        excelFilename = "initial rating.xls"
        # # read from Excel table (create it if not exists)
        # teamsL = createTeamsFromExcelTable(teamsL, excelFilename)
        createExcelTable(excelFilename, teamsL, overwrite)
        teamsL = createTeamsFromExcelTable(excelFilename)
        DataParsing.printParsedTable(teamsL)

    elif storage == "Postgre":
        createDB(teamsL, "Postgre", overwrite)

    else:
        print "Unknown storage type", storage
        sys.exit(1)


if __name__ == "__main__":
    @util.timer
    def Test(data_source):
        print "DataStoring Test\n"
        # create teams list
        if data_source == "HTML":
            teamsL = DataParsing.createTeamsFromHTML()
            # teamsL = DataParsing.createTeamsFromHTML("creating")
        elif data_source == "Excel":
            # collect data from previously saved ratings
            teamsL = createTeamsFromExcelTable()
        else:
            raise Exception, "unknown argument to test function! Use \"actual\" to download info from UEFA site" \
                             " or \"may 2015\" to use fixed stored data"
        DataParsing.printParsedTable(teamsL)

        # STORAGES = ["Postgre", "Excel"]
        # STORAGES = ["Excel"]
        STORAGES = ["Postgre"]
        # DELAY_TIME = 1.5 # sec
        OVERWRITE = True
        # OVERWRITE = False # if false, all data will be added as additional rows to the end of tables

        DELAY_TIME = 0
        delays = 0
        start_time = time.time()
        for storage_type in STORAGES:
            print "\nTest storage_type = %s" % storage_type
            time.sleep(DELAY_TIME)
            delays += DELAY_TIME
            TestStorage(storage_type, teamsL, OVERWRITE)

        # print time.time() - start_time - delays

    data_source = "HTML"
    # data_source = "Excel"
    Test(data_source)