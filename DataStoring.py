__author__ = 'NereWARin'
# -*- coding: utf-8 -*-

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

# CREATE EXCEL TABLE
def createExcelTable(filename, teamsL):
    # create Excel table, if not exists
    if os.path.isfile(filename):
         print "initial xls was already created, see", filename
         return

    print "creating Excel Table", filename
    book = xlwt.Workbook(encoding="utf-8")

    sheet1 = book.add_sheet("Sheet 1")

    headers = ["№", "teamName", "ruName", "country", "rating 2014/2015"]
    # attributes = ["getName", "getCountry", "getRating", "getRuName"]

    for j, header in enumerate(headers):
        # print 0, j, header
        sheet1.write(0, j, header)
    for i, team  in enumerate(teamsL):
        for j in range(len(headers)):
            sheet1.write(i+1, j, team.attrib(j)())

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
        country = row[3]
        rating = row[4]
        ruName = row[2]
        uefaPos = row[0]
        countryID = "undefined"
        teamsL.append(Team.Team(name, country, rating, ruName, uefaPos, countryID))
        # print name, country, rating, ruName, uefaPos
    # print to console all teams
    return teamsL


# CREATE DATABASE AND TABLES
def createDB(teamsL, storage = "Postgre"):
    if storage == "Postgre":
        # https://www.ibm.com/developerworks/ru/library/l-python_part_11/
        django_ver = django.VERSION
        # using example from http://ideafix.name/wp-content/uploads/2012/05/Python-10.pdf
        db_api =  db.apilevel
        db_paramstyle = db.paramstyle
        db_threadsafety = db.threadsafety
        # http://stackoverflow.com/questions/19426448/creating-a-postgresql-db-using-psycopg2

        dbuser = "postgres"
        dbpassword = "1472258369"

        # connect to default DB (is specific DB not exists)
        con = db.connect(dbname='postgres', user=dbuser, host = 'localhost', password=dbpassword)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()

        cur.execute('SELECT version()')
        ver = cur.fetchone()
        print ver # ('PostgreSQL 9.4.4, compiled by Visual C++ build 1800, 64-bit',)

        # CREATE DB for this application
        dbname="FootballSimDB".lower()
        # team_count = DataParsing.createTeamsFromHTML("get count")
        team_count = len(teamsL)
        schema = 'public'

        trySQLquery(cur.execute, 'SELECT exists(SELECT 1 from pg_catalog.pg_database where datname = %s)', (dbname,))
        isDB = cur.fetchone()[0]
        # print "BD exists?", isDB
        if not isDB:
            print "Database %s not found, creating" % dbname
            try:
                cur.execute('CREATE DATABASE ' + dbname)
            except db.DatabaseError, x:
                print x.pgerror.decode('utf8')
            con.commit()
        else:
            print "Database %s found" % dbname



        try:
            con = db.connect(database=dbname, user=dbuser)
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


        # TODO DANGEROUS SECTION
        print "\nCLEARING ALL ROWS OF Countries, Team_Info, Tournaments"
        # trySQLquery(cur.execute, 'DELETE FROM %s' % "Team_Info")
        # trySQLquery(cur.execute, 'TRUNCATE \'%s\', \'%s\', \'%s\' RESTART IDENTITY', ("Team_Info", "Countries", "Tournaments"))
        trySQLquery(cur.execute, 'TRUNCATE Countries, Team_Info, Tournaments RESTART IDENTITY CASCADE')
        print "ok\n"

        # CREATE TABLE TeamCountries
        table_name = "Countries"
        recreating = True
        recreating = False
        columnsInfo = list(sorted_countries)
        create_db_table(recreating, cur, con, table_name, fill_countries, columnsInfo)


        def assign_country_to_teams():
            # now we must set CountryID to teams objects
            for team in teamsL:
                # trySQLquery(cur.execute, "SELECT id FROM Countries WHERE name = %s", (team.getName(), ))
                # country_id = cur.fetchone()[0]
                teamCountry = team.getCountry()
                country_ID = select_country_id(cur, teamCountry)
                team.setCountryID(country_ID)

        assign_country_to_teams()

        # CREATE TABLE TeamInfo
        table_name = "Team_Info"
        recreating = True
        recreating = False
        # create table if it doesn't exists or need recreating
        columnsInfo = (team_count, sorted_countries, teamsL)
        create_db_table(recreating, cur, con, table_name, fill_TeamInfo, columnsInfo )


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

        # close connection to DB
        if con:
            con.close()
        # delete cursor to DB
        if cur:
            cur.close()

# def exists(cur, table_name, dbname, schema):
def tableExists(cur, table_name):
   try:
        cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (table_name.lower(),))
        isTeamInfo = cur.fetchone()[0]
        # another way
        # cur.execute("select * from information_schema.tables where table_name=%s", (table_name.lower(),))
        # isTeamInfo = bool(cur.rowcount)
        return isTeamInfo

   except db.DatabaseError, e:
        print e.pgerror.decode('utf8')
        sys.exit(1)


def select_country_id(cur, country_name):
    """
    converts string name to id by using
     select id from table "Countries"
    :param country_name:
    :return:
    """
    cur.execute("""SELECT id FROM Countries WHERE name = %s;""", (country_name, )) # ok
    country_ID = cur.fetchone()[0]
    return country_ID


# def trySQLquery(cur, func, query, data = None):
def trySQLquery(func, query, data = None):
    try:
        # print "query = \n %s" % query, type(query)
        # print "data = ", data
        return func(query, data)

    except db.DatabaseError, e:
        print "error when executing trySQLquery"
        print e.pgerror.decode('utf8')
        sys.exit(1)
#
# def saveData(table, data):
#     query =  "INSERT INTO %s (team_ID, team_Name, team_RuName, countryID) VALUES (%s, %s, %s, %s);"
#     data = (table, teamID, teamName, teamRuName, data)
#     # # data = (teamID, unicode_to_str(teamName), unicode_to_str(teamRuName), country_ID)
#     # print "insert data", data, "to table TeamInfo"
#     # trySQLquery(cur.execute, query, data)
#     # trySQLquery( query =  "INSERT INTO TeamInfo (team_ID, team_Name, team_RuName, countryID) VALUES (%s, %s, %s, %s);"
#     #         data = (teamID, teamName, teamRuName, country_ID))

def fill_TeamInfo(cur, con, table_name, columnsInfo):
    try:
        team_count, sorted_countries, teamsL = columnsInfo

        # cur.execute('CREATE TABLE %s('
        #     'team_ID INTEGER PRIMARY KEY, '
        #     'team_Name VARCHAR(30), '
        #     'team_RuName VARCHAR(30), '
        #     'countryID VARCHAR(3),'
        #     'team_emblem bytea)' % table_name)
        #
        #
        # print "create table %s ok" % table_name

        for ind in xrange(team_count):
            team = teamsL[ind]
            teamName = util.unicode_to_str(team.getName())
            # avoiding problem to "u witk points" in Bayern Munchen
            teamName = util.unicode_to_str(team.getName()).replace("\'", "")
            # teamRuName = team.getRuName()
            teamRuName = util.unicode_to_str(team.getRuName())
            teamCountry = team.getCountry()
            print teamName
            if teamName == "College Europa FC":
                teamEmblem = open(DataParsing.EMBLEMS_STORAGE_FOLDER +  "Europa FC" + ".png", 'rb').read()
            else:
                teamEmblem = open(DataParsing.EMBLEMS_STORAGE_FOLDER +  teamName + ".png", 'rb').read()

            # cur.execute("""SELECT id FROM Countries WHERE name = %s;""", (teamCountry, )) # ok
            # country_ID = cur.fetchone()[0]
            country_ID = team.getCountryID()

            # fill table
            # data = (table_name, str(teamName), teamRuName, country_ID, db.Binary(teamEmblem))
            data = (table_name, str(teamName), teamRuName, country_ID)
            # data = (table_name, str(teamName), country_ID)
            # print data
            # query =  "INSERT INTO %s (name, runame, id_country, team_emblem) VALUES ('%s', '%s', '%s', '%s');" % data
            query =  "INSERT INTO %s (name, runame, id_country) VALUES ('%s', '%s', '%s');" % data
            # query =  "INSERT INTO %s (name, id_country) VALUES ('%s', '%s');" % data
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
        # # CREATE TABLES
        # cur.execute('CREATE TABLE %s(\
        #             country_ID INTEGER PRIMARY KEY,\
        #             country_name VARCHAR(3),\
        #             teams_count INTEGER\
        #             )' % table_name)
        # print "create table Countries ok"
        # con.commit()

        # INSERT TO TABLE Countries [table_name, team_count, sorted_countries]
        for ind, (country, teams_count) in enumerate(sorted_countries):
            # query =  "INSERT INTO %s (country_ID, country_name, teams_count) VALUES (%s, %s, %s);" % ("Countries", ind+1, country, teams_count)
            query =  "INSERT INTO %s (name, teams_count) VALUES ('%s', '%s');" % (table_name, country, teams_count)
            # data = (table_name, ind+1, country, teams_count)
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
# def createTable_Tournaments(cur, con, recreating, table_name, column_names):#team_count, sorted_countries, teamsL):

    tournament_name, tournament_type, tournament_country, sorted_countries = columnsInfo

    # query = 'CREATE TABLE %s(\
    #                 %s INTEGER PRIMARY KEY,\
    #                 %s VARCHAR(30),\
    #                 %s VARCHAR(15),\
    #                 %s VARCHAR(4), \
    #                 %s INTEGER)' % (table_name, tournament_ID, tournament_name, tournament_type, tournament_country, tournament_teams_num)
    #                 # %s VARCHAR(3))" % (table_name, column_names[0], column_names[1], column_names[2], column_names[3])
    # trySQLquery(cur.execute, query)
    # print "create table %s ok" % table_name

    # columns = (tournament_ID, tournament_name, tournament_type, tournament_country)
    # INSERT TO TABLE Tournaments
    def insert_tournament_to_DB_table(t_name, t_type, t_country = None):#, t_teams_num):
        # for national tournaments
        if t_country:
            query =  "INSERT INTO %s (%s, %s, %s) VALUES ('%s', '%s', '%s');" % \
                     (table_name,
                      tournament_name, tournament_type, tournament_country,
                      t_name, t_type, t_country) #t_teams_num)
        # for international tournaments
        else:
            query =  "INSERT INTO %s (%s, %s) VALUES ('%s', '%s');" % \
                     (table_name,
                      tournament_name, tournament_type,
                      t_name, t_type)
        # print tournament_name, tournament_type, tournament_country, t_name, t_type, t_country
        trySQLquery(cur.execute, query)
        con.commit()

    t_name = "UEFA Champions League" # error was because of %s instead of '%s' in SQL-query
    t_type = "UEFA_CL"
    # t_country = "UEFA" # international
    # t_pteams = 32
    t_teams_num = 77
    # insert_tournament_to_DB_table(t_name, t_type, t_country)#, t_teams_num)
    insert_tournament_to_DB_table(t_name, t_type)#, t_teams_num)

    t_name = "UEFA Europa League" # error was because of %s instead of '%s' in SQL-query
    t_type = "UEFA_EL"
    t_teams_num = 195
    insert_tournament_to_DB_table(t_name, t_type)#, t_teams_num)
    # insert_tournament_to_DB_table(t_name, t_type, t_country)#, t_teams_num)

    def gen_national_tournaments(t_type):
        counter = 0
        for t_country, teams_count in sorted_countries:
            t_name = t_country + " " + t_type
            country_ID = select_country_id(cur, t_country)
            # insert_tournament_to_DB_table(t_name, t_type, t_country)#, teams_count)
            insert_tournament_to_DB_table(t_name, t_type, country_ID)#, teams_count)
            counter += 1
        return counter

    counter = 2
    counter += gen_national_tournaments("League")
    counter += gen_national_tournaments("Cup")

    print "inserted %s rows to %s" % (counter, table_name)

    con.commit()



def TestStorage(storage, teamsL):
    if storage == "Excel":
        excelFilename = "initial rating.xls"
        # # read from Excel table (create it if not exists)
        # teamsL = createTeamsFromExcelTable(teamsL, excelFilename)
        createExcelTable(excelFilename, teamsL)
        teamsL = createTeamsFromExcelTable(excelFilename)
        DataParsing.printParsedTable(teamsL)

    elif storage == "Postgre":
        createDB(teamsL, "Postgre")

    else:
        print "Unknown storage type", storage
        sys.exit(1)


if __name__ == "__main__":
    # @util.timer
    def Test(data_source):
        print "DataStoring Test\n"
        # create teams list
        if data_source == "actual":
            teamsL = DataParsing.createTeamsFromHTML()
            # teamsL = DataParsing.createTeamsFromHTML("creating")
        elif data_source == "may 2015":
            # collect data from previously saved ratings
            teamsL = createTeamsFromExcelTable()
        else:
            raise Exception, "unknown argument to test function! Use \"actual\" to download info from UEFA site" \
                             " or \"may 2015\" to use fixed stored data"
        DataParsing.printParsedTable(teamsL)

        # STORAGES = ["Postgre", "Excel"]
        STORAGES = ["Postgre"]
        # DELAY_TIME = 1.5 # sec
        DELAY_TIME = 0
        delays = 0
        start_time = time.time()
        for storage_type in STORAGES:
            print "\nTest storage_type = %s" % storage_type
            time.sleep(DELAY_TIME)
            delays += DELAY_TIME
            TestStorage(storage_type, teamsL)

        print time.time() - start_time - delays

    Test("may 2015")