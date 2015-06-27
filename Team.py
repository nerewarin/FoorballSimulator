# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

"""
Define Team class
"""

# import from util provided by AI EDX course project AI WEEK9 - REINFORCEMENT LEARNING
# (in other modules)
import time

class Team():
    """
    represents team
    """
    def __init__(self, name, country, rating, ruName, uefaPos):
        self.name = name
        self.country = country
        self.rating = rating
        self.ruName = ruName
        self.uefaPos = uefaPos
        self.methods = ["getUefaPos", "getName", "getRuName", "getCountry", "getRating"]

    def __str__(self):
        return self.name

    def getUefaPos(self):
        """
        current position in UEFA rating
        """
        return self.uefaPos

    def getName(self):
        return self.name

    def getCountry(self):
        return self.country

    def getRating(self):
        """
        points in UEFA rating table
        """
        return self.rating

    def getRuName(self):
        return self.ruName

    def setRating(self, rating):
        self.rating = rating

    def attrib(self, func_index):
        return getattr(self, self.methods[func_index])

def testTeam():
    Spartak = Team("Spartak Moscow", "RUS", 1, "Спартак Москва", 56)




if __name__ == "__main__":
    print "Team test"
    start_time = time.time()
    # test team class
    testTeam()
    print "time = ", time.time() - start_time
    # # print to console all teams
    # DataParsing.printParsedTable(teamsL)





