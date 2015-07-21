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
# from DataStoring import CON, CUR, TEAMINFO_TABLENAME, trySQLquery, select
# from DataStoring import trySQLquery, select
import DataStoring as db

class Team():
    """
    represents team
    """
    def __init__(self, id, country=None, rating=None, ruName=None, uefaPos=None, countryID=None, UEFAratings = []):
        self.id = id
        self.name = db.select(what = "name", table_names=db.TEAMINFO_TABLENAME, columns="id", values=self.id,
                              where = " WHERE ", sign = " = ")

        # if not country: ;else: self.country = country
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
        # print "RATING WAS UPDATED!!!!!!!!"
        # TODO after every season i should (*OR NOT? IF USE ONLY ACTUAL RATING AAS RIGHT NOW) shift actual rating to previous and so on
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
    assert teamnames == ['Real Madrid CF', 'FC Spartak Moskva'], "wrong teamnames response"



if __name__ == "__main__":
    print "Team test"
    start_time = time.time()
    # test team class
    testTeam()
    print "time = ", time.time() - start_time
    # # print to console all teams
    # DataParsing.printParsedTable(teamsL)





