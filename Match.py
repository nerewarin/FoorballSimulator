__author__ = 'NereWARin'
# -*- coding: utf-8 -*-
import random, Team

# class Result():
#     def __init(self, homeScore, guestScore):
#         self.result = (homeScore, guestScore)
#     def __str(self):
#         return


class Match():
    def __init__(self, members, deltaCoefs, name = "no name match"):
        """

        :param members:
        :param deltaCoefs:
        :param name:
        :return:
        """
        self.name = name
        self.home  = members[0]
        self.guest = members[1]

        self.homeName   = self.home.getName()
        self.homeRating = self.home.getRating()

        self.guestName   = self.guest.getName()
        self.guestRating = self.guest.getRating()
        # print self.homeName, self.guestName

        self.result = ("not played",)
        self.tie = "Tie"

    def run(self, mode = "dice original"):
        """
        generate result of match
        :param mode: "dice original" - original game by Gorbachev Arsenii written in 2001 year, played by paper
        :return: result
        """
        if mode == "dice original":
            homeLuck  = random.randint(1, 6)
            guestLuck = random.randint(1, 6)
            self.homeScore  = homeLuck
            self.guestScore = guestLuck
            # match score logic computation
            if self.homeRating > self.guestRating:
                self.guestScore += -3
            elif self.homeRating < self.guestRating:
                self.homeScore  += -2
                self.guestScore += -1
            # for check positive score
            if self.homeScore < 0:
                self.homeScore = 0
            if self.guestScore < 0:
                self.guestScore = 0

            self.result = (self.homeScore, self.guestScore)
            return self.result
        else:
            raise NotImplementedError, "unknown mode \"%s\"" % (mode)

    def printResult(self):
        return "%s. %s %s %s" % \
               (self.name, self.homeName, str(self.result[0])+ ":" + str(self.result[1]) ,self.guestName)

    def getWinner(self):
        if self.result[0] > self.result[1]:
            # return self.homeName
            return 0 # Home Wins, Guest Loses
        elif self.result[0] < self.result[1]:
            # return self.guestName
            return 1 # Home Loses, Guest Wins
        else:
            # return self.tie
            return 2 # Tie

    def updateRatings(self):

        self.home.setRating (self.homeRating  + homeDelta)
        self.guest.setRating(self.guestRating + guestDelta)

# TEST
ITERATIONS = 10
if __name__ == "__main__":
    print "\nTEST MATCH CLASS\n"
    team1 = Team.Team("Manchester City FC", "ENG", 87.078, "Манчестер Сити", 17)
    team2 = Team.Team("FC Shakhtar Donetsk", "UKR", 85.899, "Шахтер Донецк", 18)
    results = [0,0,0]
    for i in range(ITERATIONS):
        testMatch = Match((team1, team2), "testMatch%s" % (i + 1))
        # testMatch = Match((team2, team1), "testMatch%s" % (i + 1))
        testMatch.run()
        results[testMatch.getWinner()] += 1
        # print testMatch.printResult()
    # print results
    for i in range(10):
        testMatch = Match((team2, team1), "testMatch%s" % (i + 11))
        testMatch.run()
        # print testMatch.printResult()


