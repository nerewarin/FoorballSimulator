# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

"""
Define Team class
"""

# import from util provided by AI EDX course project AI WEEK9 - REINFORCEMENT LEARNING
# (in other modules)
import time
import warnings
# from DataStoring import CON, CUR, TEAMINFO_TABLE, trySQLquery, select
# from DataStoring import trySQLquery, select
import DataStoring as db

class Team():
    """
    represents team
    """
    def __init__(self, id, name = None, country=None, rating=None, ruName=None, uefaPos=None, countryID=None, UEFAratings = []):
        self.id = id
        # at start, when database initially filled, id of every team = 0 (not used),
        # and all other parameters are stored here like in buffer.
        # when DB is already initialized we can initialze Team only by id and other attributes we get from SQL
        if not name: # and not country e.t.c
            # self.name = db.select(what = "*", table_names=db.TEAMINFO_TABLE, columns="id", values=self.id,
            #                       where = " WHERE ", sign = " = ")
            teaminfo_data = db.select(what = "*", table_names=db.TEAMINFO_TABLE, columns="id", values=self.id,
                                  where = " WHERE ", sign = " = ", fetch="all")
            # print id
            # print "stored_data",  stored_data
            assert id == teaminfo_data[0], "incorrect id response! %s" % (teaminfo_data, )
            self.id, self.name, self.ruName, self.countryID, emblem = teaminfo_data

            team_ratings  = db.select(what = ["rating", "position"], table_names=db.TEAM_RATINGS_TABLENAME, columns="id", values=self.id,
                                  where = " WHERE ", sign = " = ", fetch="all")
            self.rating, self.uefaPos = team_ratings
            # print "self.rating, self.uefaPos", self.rating, self.uefaPos
            self.country = db.select(what = "name", table_names=db.COUNTRIES_TABLE, columns="id", values=self.countryID,
                                  where = " WHERE ", sign = " = ", fetch="one")
        # if not country: ;else: self.country = country
        else:
            self.name  = name
            self.country = country
            self.rating = rating
            self.ruName = ruName
            self.uefaPos = uefaPos
            self.countryID = countryID
        self.last_ratings = UEFAratings
        self.methods = ["getUefaPos", "getName", "getRuName", "getCountry", "getRating"]

    def __str__(self):
        return self.name

    def getID(self):
        return self.id

    def getUefaPos(self):
        """
        current position in UEFA rating
        """
        return self.uefaPos

    def getName(self):
        return self.name

    def getCountry(self):
        return self.country

    def getCountryID(self):
        return self.countryID

    def getRating(self):
        """
        points in UEFA rating table
        """
        return self.rating

    def getLast5Ratings(self):
        return self.last_ratings

    def getRuName(self):
        return self.ruName

    def setRating(self, rating):
        self.rating = rating

    def setCountryID(self, countryID):
        """
        first, teams are created with empty country_ID
        then, table of DB "Countries" is created where country_ID are born
        and then they can be assigned to teams
        :param countryID:
        :return:
        """
        self.countryID = countryID

    def attrib(self, func_index):
        return getattr(self, self.methods[func_index])

def testTeam():
    # old-styled - name instead of id
    # Spartak = Team("Spartak Moscow", "RUS", 1, "Спартак Москва", 56)

    # new-styled - id only (need postgres)
    Real = Team(1)
    Spartak = Team(56)
    teamnames = [value.getName() for varname, value in locals().iteritems()]
    assert teamnames == ['Real Madrid CF', 'FC Spartak Moskva'], "wrong teamnames response %s" % teamnames



if __name__ == "__main__":
    print "Team test"
    start_time = time.time()
    # test team class
    testTeam()
    print "time = ", time.time() - start_time
    # # print to console all teams
    # DataParsing.printParsedTable(teamsL)





