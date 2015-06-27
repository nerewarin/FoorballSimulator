# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

"""
represents Match Class
"""

import Team
import random, os
from values import Coefficients as C


# print values.Coefficients()
# import bumpversion
# class Result():
#     def __init(self, homeScore, guestScore):
#         self.result = (homeScore, guestScore)
#     def __str(self):
#         return


class Match():
    def __init__(self, members, deltaCoefs, name = "no name match", result_format = {"Win" : 0, "Lose" : 1, "Draw" : 2}):
        """

        :param members:
        :param deltaCoefs:
        :param name:
        :return:
        """
        self.name = name
        self.home  = members[0]
        self.guest = members[1]
        self.result_format = result_format

        self.homeName   = self.home.getName()
        self.homeRating = self.home.getRating()

        self.guestName   = self.guest.getName()
        self.guestRating = self.guest.getRating()
        # print self.homeName, self.guestName

        if self.homeRating >= self.guestRating:
            # mode index multiplier for searching in self.deltaCoefs
            self.mim = 0 # "Favorite" #(Home)
        else:
            # self.mode = "Outsider" #(Home)
            self.mim = 1 #"Outsider" #(Home)

        self.deltaCoefs = deltaCoefs

        self.result = ("not played",)
        self.tie = "Tie"

    def run(self, update = True, mode = "dice original"):
        """
        generate result of match
        :param mode: "dice original" - original game by Gorbachev Arsenii written in 2001 year, played by paper
        :return: result
        """
        if mode == "dice original":
            # throw dice, generate random goals numbers
            homeLuck  = random.randint(1, 6)
            guestLuck = random.randint(1, 6)
            self.homeScore  = homeLuck
            self.guestScore = guestLuck

            # match score logic computation
            # if self.homeRating >= self.guestRating:
            if self.mim == 0:
                self.guestScore += -3
            # elif self.homeRating < self.guestRating:
            else:
                self.homeScore  += -2
                self.guestScore += -1

            # for check positive score
            if self.homeScore < 0:
                self.homeScore = 0
            if self.guestScore < 0:
                self.guestScore = 0

            self.result = (self.homeScore, self.guestScore)

            if update:
                self.updateRatings()

            return self.result
        else:
            raise NotImplementedError, "unknown mode \"%s\"" % (mode)

    def __str__(self):
        return "%s. %s %s %s" % \
               (self.name, self.homeName, str(self.result[0])+ ":" + str(self.result[1]) ,self.guestName)

    def getWinner(self):
        if self.result[0] > self.result[1]:
            # return self.homeName
            # return 0 # Home Wins, Guest Loses
            # return self.home
            return self.result_format["Win"]
        elif self.result[0] < self.result[1]:
            # return self.guestName
            # return 1 # Home Loses, Guest Wins
            return self.result_format["Lose"]
        else:
            # return self.tie
            # return 2 # Tie
            return self.result_format["Draw"]

    def updateRatings(self):
        mimLenght = 6  # coefs in one sector (for favorite at home or otherwise mode) = len(self.deltaCoefs) / 2
        # print "self.deltaCoefs %s lenght of %s" % (self.deltaCoefs, mimLenght)

        # cimpute index for get deltaCoef from list, depending of Favorite or Outsider played home, and Result
        home_delta_ind = mimLenght * self.mim + self.getWinner() * 2 # (2 teams played)
        self.home.setRating (self.homeRating  + self.deltaCoefs[home_delta_ind])
        guest_delta_ind = home_delta_ind + 1
        self.guest.setRating(self.guestRating + self.deltaCoefs[guest_delta_ind])


# TEST
ITERATIONS = 100000
if __name__ == "__main__":
    # v1.1 coefs
    with open(os.path.join("", 'VERSION')) as version_file:
        values_version = version_file.read().strip()
    coefs = C(values_version).getRatingUpdateCoefs("list")
    # v1.0 coefs
    # coefs = C("v1.0").getRatingUpdateCoefs("list")

    print "\nTEST MATCH CLASS\n"
    team1 = Team.Team("Manchester City FC", "ENG", 87.078, "Манчестер Сити", 17)
    team2 = Team.Team("FC Shakhtar Donetsk", "UKR", 85.899, "Шахтер Донецк", 18)
    results = [0,0,0]

    for i in range(ITERATIONS):
        # if i > ITERATIONS*0.5 - 1:
        if not i % 2:
            testMatch = Match((team2, team1), coefs, "testMatch%s" % (i + 1))
        else:
            testMatch = Match((team1, team2), coefs, "testMatch%s" % (i + 1))
        # testMatch = Match((team2, team1), "testMatch%s" % (i + 1))
        testMatch.run()
        # print testMatch.printResult(), "updated ratings", team1.getRating(), team2.getRating()
        if not i % 1000:
            # print every 1000 iterations
            print testMatch, "| updated ratings", team1.getRating(), team2.getRating()
        # results[testMatch.getWinner()] += 1
        # print "updated ratings", team1.getRating(), team2.getRating()
    # # print results
    # for i in range(10):
    #     testMatch = Match((team2, team1), coefs, "testMatch%s" % (i + 11))
    #     testMatch.run()
    #     print testMatch.printResult()


