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


def createTeamsFromExcelTable(excelFilename = "Rating.xls"):
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
        name = row[1]
        country = row[3]
        rating = row[4]
        ruName = row[2]
        uefaPos = row[0]
        teamsL.append(Team.Team(name, country, rating, ruName, uefaPos))
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
        dbname="FootballSimDB"
        dbpassword = "1472258369"
        team_count = DataParsing.createTeamsFromHTML("get count")
        schema = 'public'

        con = db.connect(dbname=dbname, user=dbuser, host = 'localhost', password=dbpassword)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()

        cur.execute('SELECT version()')
        ver = cur.fetchone()
        # print ver # ('PostgreSQL 9.4.4, compiled by Visual C++ build 1800, 64-bit',)

        # CREATE DB
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


        # CONNECT
        # con = None
        try:
            con = db.connect(database=dbname, user=dbuser)
            cur = con.cursor()
            cur.execute('SELECT version()')
            ver = cur.fetchone()
            # print "db ver = ", ver

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


        # CREATE TABLE TeamInfo
        table_name = "TeamInfo"
         # print "isTeamInfo exists()?", exists(cur, "TeamInfo", dbname, schema)
        recreating = True
        # recreating = True
        print
        # create table if it doesn't exists or need recreating

        if not tableExists(cur, table_name):
            print "%s\" not exists, creating" % table_name
            createTable_TeamInfo(cur, con, table_name, team_count, countries, teamsL)

        elif recreating:
            print "%s recreating" % table_name
            trySQLquery(cur.execute, 'DROP TABLE %s' % table_name)
            createTable_TeamInfo(cur, con, table_name, team_count, countries, teamsL)
        else:
            print "%s is already exists" % table_name


        # CREATE TABLE TeamCountries
        table_name = "Countries"
        recreating = True
        recreating = False
        print
        if not tableExists(cur, table_name):
            print "%s\" not exists, creating" % table_name
            createTable_Countries(cur, con, table_name, team_count, sorted_countries)
        elif recreating:
            print "%s exists but recreating enabled" % table_name
            # # DROP AND RECREATE
            trySQLquery(cur.execute, 'DROP TABLE %s' % table_name)
            con.commit()
            print "DROP table Countries ok"
            createTable_Countries(cur, con, table_name, team_count, sorted_countries)
        else:
            print "%s is already exists" % table_name

        # CREATE TABLE Tournaments
        table_name = "Tournaments"
        recreating = True
        print
        if not tableExists(cur, table_name) or recreating:
            if recreating:
                print "%s exists but recreating enabled" % table_name
            else:
                print "%s\" not exists, creating" % table_name
            tournament_ID = "ID"
            tournament_name = "name"
            tournament_type = "type"
            tournament_country = "country"
            tournament_teams_count = "teams_count"
            createTable_Tournaments(cur, con, recreating, table_name, tournament_ID, tournament_name, tournament_type, tournament_country, tournament_teams_count, sorted_countries)
            # column_names = ["ID", "name", "type", "country"]
            # createTable_Tournaments(cur, con, recreating, table_name, column_names)
        else:
            print "\n%s is already exists" % table_name


        # # CREATE TABLE RL_TeamCountries (relation between TeamInfo and Countries)
        # isTeamCountry = True # NO CREATING
        # if not isTeamCountry:
        #     # # DROP AND RECREATE
        #     # cur.execute('DROP TABLE RL_TeamCountries')
        #     # print "DROP table Countries ok"
        #     createTable_RL_TeamCountries(cur, con, team_count, countries)
        # else:
        #     print "%s is already exists" % table_name



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


# def trySQLquery(cur, func, query, data = None):
def trySQLquery(func, query, data = None):
    try:
        # print query, data
        return func(query, data)

    except db.DatabaseError, e:
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

def createTable_TeamInfo(cur, con, table_name, team_count, sorted_countries, teamsL):
    try:
        # cur.execute('CREATE TABLE %s('
        #             'team_ID INTEGER PRIMARY KEY, '
        #             'team_Name VARCHAR(30), '
        #             'team_RuName VARCHAR(30), '
        #             'countryID VARCHAR(3))' % table_name)
        cur.execute('CREATE TABLE %s('
            'team_ID INTEGER PRIMARY KEY, '
            'team_Name VARCHAR(30), '
            'team_RuName VARCHAR(30), '
            'countryID VARCHAR(3),'
            'team_emblem bytea)' % table_name)


        print "create table %s ok" % table_name
        for ind in xrange(team_count):
            team = teamsL[ind]
            teamID = ind+1
            teamName = util.unicode_to_str(team.getName())
            teamRuName = team.getRuName()
            teamCountry = team.getCountry()
            teamEmblem = open(DataParsing.EMBLEMS_STORAGE_FOLDER +  teamName + ".png", 'rb').read()

            cur.execute("""SELECT country_ID FROM Countries WHERE country_name = %s;""", (teamCountry, )) # ok
            country_ID = cur.fetchone()[0]
            # TODO replace country by country_ID as attribute of Team class

            # create table
            query =  "INSERT INTO TeamInfo (team_ID, team_Name, team_RuName, countryID, team_emblem) VALUES (%s, %s, %s, %s, %s);"
            # query =  "INSERT INTO TeamInfo (team_ID, team_Name, team_RuName, countryID) VALUES (%s, %s, %s, %s);"

            # use psycopg2.Binary(binary) from http://iamtgc.com/using-python-to-load-binary-files-into-postgres/
            data = (teamID, teamName, teamRuName, country_ID, db.Binary(teamEmblem), )
            # data = (teamID, teamName, teamRuName, country_ID, teamEmblem, )
            # data = (teamID, unicode_to_str(teamName), unicode_to_str(teamRuName), country_ID)
            # print "insert data", data, "to table TeamInfo"
            print "insert data to table TeamInfo"
            trySQLquery(cur.execute, query, data)

        con.commit()
    except db.DatabaseError, e:
        # print 'Error %s' % e.pgerror.decode('utf8')
        print e.pgerror.decode('utf8')
        sys.exit(1)


def createTable_Countries(cur, con, table_name, team_count, sorted_countries):
    try:
        # CREATE TABLES
        cur.execute('CREATE TABLE %s(\
                    country_ID INTEGER PRIMARY KEY,\
                    country_name VARCHAR(3),\
                    teams_count INTEGER\
                    )' % table_name)
        print "create table Countries ok"
        con.commit()

        # INSERT TO TABLE Countries
        for ind, (country, teams_count) in enumerate(sorted_countries):
            # query =  "INSERT INTO %s (country_ID, country_name, teams_count) VALUES (%s, %s, %s);" % ("Countries", ind+1, country, teams_count)
            query =  "INSERT INTO %s (country_ID, country_name, teams_count) VALUES ('%s', '%s', '%s');" % (table_name, ind+1, country, teams_count)
            # data = (table_name, ind+1, country, teams_count)
            # print "insert data", data, "to table Countries"
            cur.execute(query)
        print "inserted %s rows to %s" % (len(sorted_countries), table_name)
        con.commit()

    except db.DatabaseError, e:
        print e.pgerror.decode('utf8')
        sys.exit(1)


def createTable_RL_TeamCountries(cur, con, team_count, countries):
    raise NotImplementedError, "we do not need this table until team_name exists in team_info explicitly. We'll need \
                                it if we want to have 1st-normalized-DB"
    # try:
    #     # CREATE TABLES
    #     cur.execute('CREATE TABLE RL_TeamCountries(\
    #                 team_ID INTEGER references TeamInfo(team_ID),\
    #                 country_ID INTEGER references Countries(country_ID))')
    #     print "create table RL_TeamCountries ok"
    #
    #
    #     # INSERT TO TABLE RL_TeamCountries
    #     for ind in range(team_count):
    #         team = teamsL[ind]
    #         team_ID = ind + 1 # it will works still teamInfo is unmutable
    #         # country_ID = countries[team]
    #         print "here is problem! but we dont need RL between teams and counties cause this info is now in TeamInfo"
    #         country_ID = countries[team]
    #         query =  "INSERT INTO RL_TeamCountries (team_ID, country_ID) VALUES (%s, %s);"
    #         data = (team_ID, country_ID)
    #
    #     # for ind, (country, teams_count) in enumerate(sorted_countries):
    #     #     query =  "INSERT INTO Countries (country_ID, country_name, teams_count) VALUES (%s, %s, %s);"
    #     #     data = (ind+1, country, teams_count)
    #     #     print "insert data", data, "to table Countries"
    #     #     cur.execute(query, data)
    #
    #     con.commit()
    # except db.DatabaseError, e:
    #     print e.pgerror.decode('utf8')
    #     sys.exit(1)


def createTable_Tournaments(cur, con, recreating, table_name, tournament_ID, tournament_name, tournament_type, tournament_country, tournament_teams_num, sorted_countries):#team_count, sorted_countries, teamsL):
# def createTable_Tournaments(cur, con, recreating, table_name, column_names):#team_count, sorted_countries, teamsL):
    # trySQLquery(cur.execute,  'CREATE TABLE Tournaments
    if recreating:
        trySQLquery(cur.execute, 'DROP TABLE %s' % table_name)
        print "table %s dropped" % table_name
    query = 'CREATE TABLE %s(\
                    %s INTEGER PRIMARY KEY,\
                    %s VARCHAR(30),\
                    %s VARCHAR(15),\
                    %s VARCHAR(4), \
                    %s INTEGER)' % (table_name, tournament_ID, tournament_name, tournament_type, tournament_country, tournament_teams_num)
                    # %s VARCHAR(3))" % (table_name, column_names[0], column_names[1], column_names[2], column_names[3])
    trySQLquery(cur.execute, query)
    print "create table %s ok" % table_name

    # columns = (tournament_ID, tournament_name, tournament_type, tournament_country)
    # INSERT TO TABLE Tournaments
    def insert_tournament_to_DB_table(t_id, t_name, t_type, t_country, t_teams_num):
        query =  "INSERT INTO %s (%s, %s, %s, %s, %s) VALUES ('%s', '%s', '%s', '%s', '%s');" % \
                 (table_name,
                  tournament_ID, tournament_name, tournament_type, tournament_country, tournament_teams_num,
                  t_id, t_name, t_type, t_country, t_teams_num)
        trySQLquery(cur.execute, query)

    t_id = 0
    t_name = "UEFA Champions League" # error was because of %s instead of '%s' in SQL-query
    t_type = "UEFA_Champ_L"
    t_country = "UEFA" # international
    # t_pteams = 32
    t_teams_num = 77
    insert_tournament_to_DB_table(t_id, t_name, t_type, t_country, t_teams_num)

    t_id += 1
    t_name = "UEFA Europa League" # error was because of %s instead of '%s' in SQL-query
    t_type = "UEFA_Euro_L"
    t_teams_num = 195
    insert_tournament_to_DB_table(t_id, t_name, t_type, t_country, t_teams_num)

    def gen_national_tournaments(start_id, t_type):
        t_id = int(start_id)
        for ind, (t_country, teams_count) in enumerate(sorted_countries):
            t_id += 1
            t_name = t_country + " " + t_type
            insert_tournament_to_DB_table(t_id, t_name, t_type, t_country, teams_count)
        return t_id

    t_id = gen_national_tournaments(t_id, "League")
    t_id = gen_national_tournaments(t_id, "Cup")

    print "inserted %s rows to %s" % (t_id+1, table_name)

    con.commit()



def TestStorage(storage, teamsL):
    if storage == "Excel":
        excelFilename = "Rating.xls"
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
    def Test():
        print "DataStoring Test\n"
        # create teams list
        teamsL = DataParsing.createTeamsFromHTML()
        # teamsL = DataParsing.createTeamsFromHTML("creating")
        # DataParsing.printParsedTable(teamsL)

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

    Test()