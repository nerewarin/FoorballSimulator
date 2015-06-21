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
import os, operator, sys, time

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


def createTeamsFromExcelTable(teamsL, excelFilename = "Rating.xls"):
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
        print "tables of DB ", cur.fetchall()


        # COUNTRIES COUNTER DICT
        countries = util.Counter()
        for team in teamsL:
            countries[team.getCountry()] +=1
        print "countries", countries

        # when sorted, we can define country_ID for team with maximum teams
        sorted_countries = sorted(countries.items(), key=operator.itemgetter(1), reverse=True)
        # sorted_x will be a list of tuples sorted by the second element in each tuple. dict(sorted_x) == x.
        print "sorted_countries", sorted_countries


        # CREATE TABLE TeamInfo
        table_name = "TeamInfo"
         # print "isTeamInfo exists()?", exists(cur, "TeamInfo", dbname, schema)
        recreating = True
        # create table if it doesn't exists or need recreating
        if not tableExists(cur, table_name) or recreating:
            # print "%s exists but I think, its not complete, so recreating" % table_name
            print "%s recreating" % table_name
            # DROP AND RECREATE
            # trySQLquery(cur, 'DROP TABLE RL_TeamCountries')
            # query = 'DROP TABLE TeamInfo'
            trySQLquery(cur.execute, 'DROP TABLE %s' % table_name)
            # trySQLquery(cur, 'DROP TABLE Countries')

            createTable_TeamInfo(cur, con, table_name, team_count, countries, teamsL)
        else:
            print "%s is already exists" % table_name


        # CREATE TABLE TeamCountries
        # isTeamCountry = False
        # isTeamCountry = True
        table_name = "Countries"
        if not tableExists(cur, table_name):
            print "%s exists but I think, its not complete, so recreating" % table_name
            # # DROP AND RECREATE
            # cur.execute('DROP TABLE Countries')
            trySQLquery(cur.execute, 'DROP TABLE %s' % table_name)
            # print "DROP table Countries ok"
            createTable_Countries(cur, con, table_name, team_count, sorted_countries)
        else:
            print "%s is already exists" % table_name

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


def createTable_TeamInfo(cur, con, table_name, team_count, sorted_countries, teamsL):
    try:
        cur.execute('CREATE TABLE %s(team_ID INTEGER PRIMARY KEY, team_Name VARCHAR(30), team_RuName VARCHAR(30), countryID VARCHAR(3))' % table_name)
        print "create table %s ok" % table_name
        for ind in xrange(team_count):
            team = teamsL[ind]
            teamID = ind+1
            teamName = util.unicode_to_str(team.getName())
            teamRuName = team.getRuName()
            teamCountry = team.getCountry()
            # print "teamCountry =", teamCountry
            # country_ID = countries[teamCountry] # NO!!!
            # country_ID = sorted_countries[ind]
            cur.execute("""SELECT country_ID FROM Countries WHERE country_name = %s;""", (teamCountry, )) # ok
            country_ID = cur.fetchone()[0]

            # print "country_ID = ", country_ID, type(country_ID)
            # teamRating = team.getRating()

            ## create table
            query =  "INSERT INTO TeamInfo (team_ID, team_Name, team_RuName, countryID) VALUES (%s, %s, %s, %s);"
            data = (teamID, teamName, teamRuName, country_ID)
            # data = (teamID, unicode_to_str(teamName), unicode_to_str(teamRuName), country_ID)
            print "insert data", data, "to table TeamInfo"
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

        # INSERT TO TABLE Countries
        for ind, (country, teams_count) in enumerate(sorted_countries):
            query =  "INSERT INTO %s (country_ID, country_name, teams_count) VALUES (%s, %s, %s);"
            data = (table_name, ind+1, country, teams_count)
            print "insert data", data, "to table Countries"
            cur.execute(query, data)

        con.commit()
    except db.DatabaseError, e:
        print e.pgerror.decode('utf8')
        sys.exit(1)


def createTable_RL_TeamCountries(cur, con, team_count, countries):
    try:
        # CREATE TABLES
        cur.execute('CREATE TABLE RL_TeamCountries(\
                    team_ID INTEGER references TeamInfo(team_ID),\
                    country_ID INTEGER references Countries(country_ID))')
        print "create table RL_TeamCountries ok"


        # INSERT TO TABLE RL_TeamCountries
        for ind in range(team_count):
            team = teamsL[ind]
            team_ID = ind + 1 # it will works still teamInfo is unmutable
            # country_ID = countries[team]
            print "here is problem! but we dont need RL between teams and counties cause this info is now in TeamInfo"
            country_ID = countries[team]
            query =  "INSERT INTO RL_TeamCountries (team_ID, country_ID) VALUES (%s, %s);"
            data = (team_ID, country_ID)

        # for ind, (country, teams_count) in enumerate(sorted_countries):
        #     query =  "INSERT INTO Countries (country_ID, country_name, teams_count) VALUES (%s, %s, %s);"
        #     data = (ind+1, country, teams_count)
        #     print "insert data", data, "to table Countries"
        #     cur.execute(query, data)

        con.commit()
    except db.DatabaseError, e:
        print e.pgerror.decode('utf8')
        sys.exit(1)

def TestStorage(storage, teamsL):
    if storage == "Excel":
        excelFilename = "Rating.xls"
        # # read from Excel table (create it if not exists)
        # teamsL = createTeamsFromExcelTable(teamsL, excelFilename)
        createExcelTable(excelFilename, teamsL)
        teamsL = createTeamsFromExcelTable(teamsL, excelFilename)
        DataParsing.printParsedTable(teamsL)

    elif storage == "Postgre":
        createDB(teamsL, "Postgre")

    else:
        print "Unknown storage type", storage
        sys.exit(1)

if __name__ == "__main__":
    print "DataStoring Test"
    # create teams list
    teamsL = DataParsing.createTeamsFromHTML()
    # DataParsing.printParsedTable(teamsL)

    STORAGES = ["Postgre", "Excel"]
    DELAY_TIME = 1.5 # sec
    delays = 0
    start_time = time.time()
    for storage_type in STORAGES:
        print "\nTest storage_type = %s" % storage_type
        time.sleep(DELAY_TIME)
        delays += DELAY_TIME
        TestStorage(storage_type, teamsL)

    print time.time() - start_time - delays
