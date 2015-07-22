# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

"""
represents Match Class
"""

import Team
import util
from values import Coefficients as C
import random, os, warnings
import DataStoring as db


class Match(object):
    def __init__(self, members, deltaCoefs, tournament = 0, round = "no round", playoff = False,
        result_format = [0,1,2], mode = "dice original", save_to_db = True):
        # result_format = {"Win" : 0, "Lose" : 1, "Draw" : 2}, mode = "dice original"):
        """

        :param members: tuple of 2 teams objects
        :param deltaCoefs: coefficients to compute tearing changes after match
        :param tournament: tournament id
        :param round: string (qualification 1....final)
        :param playoff: Draw result available (for league) or not (for Cup play-offs and finals)
        :param result_format: what getWinner will return
        :param mode: computing match result logic

        :return:
        """
        self.tournament = tournament
        self.round = str(round)
        self.name = str(self.tournament) + " " + self.round

        self.members = members
        self.playoff = playoff
        self.deltaCoefs = deltaCoefs
        self.result_format = result_format
        self.mode = mode
        self.save_to_db = save_to_db

        self.home  = self.members[0]
        self.guest = self.members[1]

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

        self.result = "not played"
        self.winner = "not played" # or not updated in run() method - debug it!
        self.looser = "not played"
        self.outcome = "not played"

    def __str__(self):
        return "%s. %s %s %s" % \
               (self.name, self.homeName, str(self.getResult())[1:-1].replace(",", ":").replace(" ", "") ,self.guestName)
               # (self.name, self.homeName, str(self.getResult())[1:-1].replace(",", ":").replace(" ", "") ,self.guestName)
               # (self.name, self.homeName, str(self.result[0])+ ":" + str(self.result[1]) ,self.guestName)

    def getName(self):
        return self.tournament

    def getResultFormats(self):
        """
        what formats class provides
        :return: by default [0,1,2] where 0 = Win (of home team), Lose = 1, Draw = 2
        """
        return {"Win" : self.result_format[0], "Lose" : self.result_format[1], "Draw" : self.result_format[2]}

    def getModes(self):
        return ("dice original")

    def run(self, update = True):
        """
        generate result of match
        :param mode: "dice original" - original game by Gorbachev Arsenii written in 2001 year, played by paper
        :return: result
        """
        if self.mode == "dice original":
            # throw dice, generate random goals numbers
            homeLuck  = random.randint(1, 6)
            guestLuck = random.randint(1, 6)
            homeScore  = homeLuck
            guestScore = guestLuck

            # match score logic computation
            # if self.homeRating >= self.guestRating:
            if self.mim == 0:
                guestScore += -3
            # elif self.homeRating < self.guestRating:
            else:
                homeScore  += -2
                guestScore += -1

            # for check positive score
            if homeScore < 0:
                homeScore = 0
            if guestScore < 0:
                guestScore = 0

            self.result = [homeScore, guestScore]

            if self.playoff and homeScore == guestScore:
                self.result[self.penalty_sequence()] += 1

            # set winner for getWinner
            if self.result[0] > self.result[1]:
                # return self.homeName
                # return 0 # Home Wins, Guest Loses
                # return self.home
                # return self.result_format["Win"]
                # self.winner = self.home
                # self.looser = self.guest
                # self.winner = self.result_format[0]
                # self.looser = self.result_format[1]
                self.outcome = self.result_format[0]

            elif self.result[0] < self.result[1]:
                # return self.guestName
                # return 1 # Home Loses, Guest Wins
                # return self.result_format["Lose"]
                # self.winner = self.guest
                # self.looser = self.home
                # self.winner = self.result_format[1]
                # self.looser = self.result_format[0]
                self.outcome = self.result_format[1]
            else:
                # return self.tie
                # return 2 # Tie
                # return self.result_format["Draw"]
                self.outcome = self.result_format[2]
                # self.winner = self.result_format[2]
                # self.looser = self.winner

            if update:
                self.updateRatings()


            if self.save_to_db:
                self.saveToDB()
            return self.result
        else:
            raise NotImplementedError, "unknown mode \"%s\"" % (self.mode)


    def penalty_sequence(self):
        """
        returns index of winner in pair
        """
        # honest version...
        # homeLuck  = random.randint(1, 6)
        # guestLuck = random.randint(1, 6)
        # self.homeScore  = homeLuck
        # self.guestScore = guestLuck

        # simplified version
        # index of losed team
        pair_winner = random.randint(0,1)
        # print "penalty i", i
        # print "penalty sequence!", [match2_score[1], match2_score[0]], pair_score
        # return pair_winner, match_score[(pair_winner + 1) % 2] + 1, pair_score[pair_winner] + 1
        return pair_winner

    def getWinner(self):
        """
        return index of team in pair who had won. if Draw, returns self.result_format[2]
        """

        # return self.winner
        if not self.playoff: # Draw allows!
            warnings.warn("getWinner Depricated!!! Use getOutcome to get value of self.result_format[winner]")
            if self.outcome == self.result_format[2]:
                warnings.warn("Call getWinner but return Draw")
                return "Draw" # or None
                # raise FutureWarning, "Call getWinner but return Tie"
            # return self.members[self.winner]
        # return self.winner
        # print "getWinner self.playoff %s" % self.playoff
        return self.members[self.outcome]

    def getResult(self, *args, **kwargs):
        """

        :return: tuple match result for Match, tuple DoubleMatch result for DoubleMatch
        """
        return tuple(self.result)
        # return tuple(self.result, )

    def getLooser(self):
        """
        return index of team in pair who had loosed. if Draw, returns self.result_format[2]
        """
        if not self.playoff: # Draw allows!
            warnings.warn("getLooser Depricated!!! Use gewOutcome to get value of self.result_format[winner]")
            if self.outcome == self.result_format[2]:
                warnings.warn("Call getLooser but return Tie")
        # return self.members[self.looser]
        # return self.looser
        return self.members[(self.outcome + 1) %2]

    def getOutcome(self):
        """
        best way to know winner/looser/draw (supports draw)
        :return: self.result_format[winner] that can be one of getResultFormats() values
        """
        return self.outcome

    def isDraw(self):
        """
        return True if match result is Draw (False otherwise)
        """
        return self.winner == self.result_format[2]

    def updateRatings(self):


        # winner = self.getWinner()
        if type(self.result) == str:
            warnings.warn("Can't call updateRatings cause match result is %s. Ratings will state the same" % self.result)
            raise FutureWarning
        else:
            # winner = self.getWinner()
            outcome = self.getOutcome()
        if type(outcome) == int:
            # coefs in one sector (for favorite at home or otherwise mode) = len(self.deltaCoefs) / 2
            mimLenght = 6
            # print "self.deltaCoefs %s lenght of %s" % (self.deltaCoefs, mimLenght)
            #  compute index for get deltaCoef from list, depending of Favorite or Outsider played home, and Result
            home_delta_ind = mimLenght * self.mim + outcome * 2 # (2 teams played)
            self.home.setRating (self.homeRating  + self.deltaCoefs[home_delta_ind])
            guest_delta_ind = home_delta_ind + 1
            self.guest.setRating(self.guestRating + self.deltaCoefs[guest_delta_ind])
        else:
            raise FutureWarning, "Error in updateRatings! self.result = %s, self.getWinner() = %s" % (self.result, self.getWinner())


    def saveToDB(self):
        """
        saving match result to database
        :return:
        """
        self.homeID = self.home.getID()
        self.guestID = self.guest.getID()
        # columns = db.trySQLquery(CUR.execute())"id" "SELECT * FROM %s LIMIT 0" % db.MATCHES_TABLE
        columns = db.select(table_names=db.MATCHES_TABLE, fetch="colnames", suffix = " LIMIT 0")
        # print "Matches columns are ", columns
        columns = columns[1:]
        # print "Matches columns (exclusive id) are ", columns
        values = [self.tournament, self.round, self.homeID, self.guestID, self.getResult()[0], self.getResult()[1]]
        # print "values are ", values
        db.insert(db.MATCHES_TABLE, columns, values)
       #  return "%s. %s %s %s" % \
       # (self.tournament, self.homeName, str(self.getResult())[1:-1].replace(",", ":").replace(" ", "") ,self.guestName)
       # # (self.tournament, self.homeName, str(self.result[0])+ ":" + str(self.result[1]) ,self.guestName)
        print


class DoubleMatch(Match):
    """
    represents two matches (home - guest) for pair (useful in Cups)
    """
    def __init__(self, members, deltaCoefs, tournament = 0,  round = "no round", playoff = False, result_format = [0, 1, 2], mode = "dice original", save_to_db = True):
        """
         :param members: tuple of 2 teams objects
         :param deltaCoefs: coefficients to compute tearing changes after match
         :param tournament: string match tournament (league/cup, season, round, etc)
         :param playoff: Draw result available (for league) or not (for Cup play-offs and finals)
         :param result_format: what getWinner will return
         :return:
        """

        super(DoubleMatch, self).__init__(members, deltaCoefs, tournament, round, playoff, result_format, mode, save_to_db)
        self.playoff = playoff
        self.result = ("not played",)#, ("not played",)
        self.matches_results = ("not played","not played"), ("not played","not played")

    def __str__(self, casted_m2 = True):
        # print "AAA", str(self.getResult(0))[1:-1].replace(",", ":").replace(" ", "")
        # print "AAA", str(self.getResult(0))
        cast_m2 = True
        return "%s. %s %s %s" % \
                     (self.tournament,
                      self.homeName,
                      # str(self.getResult())[1:-1].replace(",", ":").replace(" ", "")
                      str(self.getResult(0))[1:-1].replace(",", ":").replace(" ", "")
                      + " (" + str(self.getFirstMatchResult())[1:-1].replace(",", ":").replace(" ", "") + ", "
                      + str(self.getSecondMatchResult(cast_m2))[1:-1].replace(",", ":").replace(" ", "") + ")"
                     ,self.guestName)

               # (self.tournament, self.homeName, str(self.result[0][0])+ ":" + str(self.result[0][1]) ,self.guestName)
               #  (self.tournament, self.homeName, str(self.getResult()).replace(",", ":") ,self.guestName)
    def run(self, update = True):
        # first digit - team1 goals, second - team2 goals
        # forward: 1 - team1 , 2 - team2
        match1_score = list(Match((self.home, self.guest), self.deltaCoefs, self.tournament, self.round + " m1", False,
                                  self.result_format, self.mode, save_to_db = self.save_to_db).run())

        # reversed: 1 - team2 , 2 - team1
        match2_score = list(Match((self.guest, self.home), self.deltaCoefs, self.tournament, self.round + " m2", False,
                                  self.result_format, self.mode, save_to_db = self.save_to_db).run())

        # like in match1_score, first digit - team1 goals, second - team2 result
        # 1 - team1 , 2 - team2
        # casted_match2 = list(reversed(match2_score))
        # print match2_score, casted_match2
        pair_score =  [match1_score[0] + match2_score[1],  match1_score[1] + match2_score[0]]
        # print "match1_score %s, match2_score* %s, pair_score %s" % (match1_score, [match2_score[1], match2_score[0]], pair_score)

        # pair_winner - index in self.results  of result for favorite (win, soole or draw)
        #  return pair_winner, match_score[(pair_winner + 1) % 2] + 1, pair_score[pair_winner] + 1
        if pair_score[0] > pair_score[1]:
            # pair_winner = 0
            # self.winner = self.result_format[0]
            # self.looser = self.result_format[1]
            self.outcome  = self.result_format[0]
        elif pair_score[0] < pair_score[1]:
            # pair_winner = 1
            # self.winner = self.result_format[1]
            # self.looser = self.result_format[0]
            self.outcome  = self.result_format[1]
        else: # sum of goals is equal

            # rule of guest goal
            if match2_score[1] > match1_score[1]: # first team wins guest goal rule
                # pair_winner = 0
                # self.winner = self.result_format[0]
                # self.looser = self.result_format[1]
                self.outcome  = self.result_format[0]
            elif match2_score[1] < match1_score[1]:
                # pair_winner = 1
                # self.winner = self.result_format[1]
                # self.looser = self.result_format[0]
                self.outcome  = self.result_format[1]
            else: # scores of 2 match are absolutely equal
                # print "self.playoff", self.playoff
                if self.playoff:

                    # penalty sequence
                    penalty_winner = self.penalty_sequence()
                    # update score for second match
                    match2_score[penalty_winner] += 1
                    # if penalty_winner = 0, so guest wins, witch is [0] in match2_score
                    # but [1] in pair_score
                    pair_score[(penalty_winner + 1) % 2] += 1
                    pair_winner = (penalty_winner + 1) % 2
                    # cause match2 wasn't casted to favorite...
                    # self.winner = self.result_format[pair_winner]
                    # self.looser = self.result_format[penalty_winner]
                    self.outcome  = self.result_format[pair_winner]
                    # print "Penalty sequence! update match2_score %s" % match2_score
                else:
                    # self.winner = self.result_format[2]
                    # self.looser = self.winner
                    self.outcome  = self.result_format[2]
                    # raise FutureWarning, "Incorrect \'Draw\' result in mode play-off!"
                    # raise FutureWarning, "SENYA! Where did you see play-off double match with a Draw as result?? no winner - no play-off!"
                    warnings.warn("SENYA! Where did you see play-off double match with a Draw as result?? no winner - no play-off!")
                # self.winner = self.result_format[2]
                # self.looser = self.winner
        # self.winner = list(self.result_format)[pair_winner]
        # print "pair_score", pair_score, "pair_winner", self.winner
        self.result = pair_score #match1_score, match2_score
        self.matches_results = match1_score, match2_score
        # for getWinner
        self.casted_match2 = [match2_score[1], match2_score[0]]
        # return self.result, match1_score, casted_match2
        return self.result#, match1_score, casted_match2


    # def getResult(self, match = "all", casted = True):
    def getResult(self, *args, **kwargs):
        # for printing to net
        # print "RESULTTT", self.result

        # print "casted", casted
        res = []
        if "casted" in kwargs:
            casted = kwargs["casted"]
        else:
            casted = True

        results = (self.result, self.getFirstMatchResult(), self.getSecondMatchResult(casted))

        if args:
            if len(args) == 1:
                return results[args[0]]

            for index in args:
                res.append(results[index])
                # if res:
                #     res.append(results[index])
                # else:
                #     res = results[index]
                # # print "\nBBB", index, res, "\n"
            return res
        else:
            return results
        # return res
        # if match == "all":
        #     return results
        # else: # if match = 0, return pair result, 1 - FirstMatchResult, 2 - SecondMatchResult
        #     return results[match]

    def getMatchesResults(self):
        """

        :return: tuple (pair_score, match1_score, match2_score
        """
        return self.matches_results

    def getFirstMatchResult(self):
        return tuple(self.matches_results[0])

    def getSecondMatchResult(self, casted = False):
        """
         put in casted = True for nice printing format (team1:team2, team1:team2)
         if casted = False, home-guest match results will be like (team1:team2, team2:team1)
        :param casted:
        :return:
        """
        if casted:
            return tuple(self.casted_match2)
        return tuple(self.matches_results[1])



# TEST
if __name__ == "__main__":
    # v1.1 coefs
    with open(os.path.join("", 'VERSION')) as version_file:
        values_version = version_file.read().strip()
    coefs = C(values_version).getRatingUpdateCoefs("list")
    # v1.0 coefs
    # coefs = C("v1.0").getRatingUpdateCoefs("list")

    @util.timer
    def Test(iterations, pre_truncate, post_truncate, save_to_db, *args, **kwargs):
        """

        run matches and store in database (if new-styled)

        :param iterations:
        :param args:
        :param kwargs:
        :return:
        """

        # # old-styled
        # team1 = Team.Team("Manchester City FC", "ENG", 87.078, "Манчестер Сити", 17)
        # team2 = Team.Team("FC Shakhtar Donetsk", "UKR", 85.899, "Шахтер Донецк", 18)

        if pre_truncate:
            db.truncate(db.MATCHES_TABLE)

        print "self.save_to_db", save_to_db
        if "Match" in args:
            print "\nTEST MATCH CLASS\n"
            for i in range(iterations):
                # new-styled
                team1_id = random.randint(1, 454)
                team1 = Team.Team(team1_id)
                team2_id = random.randint(1, 454)
                while team2_id == team1_id:
                     team2_id = random.randint(1, 454)
                team2 = Team.Team(team2_id)


                # if i > ITERATIONS*0.5 - 1:
                if not i % 2:
                    pair = (team2, team1)
                else:
                    pair = (team1, team2)
                # testMatch = Match(pair, coefs, "testMatch%s" % (i + 1))
                testMatch = Match(pair, coefs, round = "friendly%s" % (i + 1), save_to_db = save_to_db)

                testMatch.run()
                # print testMatch.printResult(), "updated ratings", team1.getRating(), team2.getRating()
                # if not i % 1000:
                # or print every iteration
                outcome = testMatch.getOutcome()
                if outcome == testMatch.getResultFormats()["Draw"]:
                    winner = "Draw"
                else:
                    winner = pair[outcome]
                # try:
                #     winner = pair[testMatch.getWinner()]
                # except:
                #     winner = "Draw"
                # print testMatch, "winner = %s" % winner,"| updated ratings", team1.getRating(), team2.getRating()
                print testMatch#, "winner = %s" % winner,"| updated ratings", team1.getRating(), team2.getRating()
                    # print "%s: %s : %s, outcome = %s, pair_score %s m1 %s m2 %s" % \
                    #       (test_DoubleMatch1.getName(), pair[0], pair[1], test_DoubleMatch1.getOutcome(), pair_result,
                    #        test_DoubleMatch1.getFirstMatchResult(), test_DoubleMatch1.getSecondMatchResult())

                # results[testMatch.getWinner()] += 1
                # print "updated ratings", team1.getRating(), team2.getRating()

        if "DoubleMatch" in args:
            print "\nTEST DoubleMatch CLASS\n"
            for playoff in (True, False):
                print ("playoff = %s") % playoff
                for i in range(iterations):
                    # playoff = False # ERROR WILL BE RISEN cause DoubleMatch made only for playoff stages!
                    # playoff = True

                    pair = (team1, team2)
                    test_DoubleMatch1 = DoubleMatch(pair, coefs, tournament = 1, round = "_m%s" % (2*i+1), playoff = playoff, save_to_db = save_to_db)
                    pair_result = test_DoubleMatch1.run()
                    # print "test_DoubleMatch%s: pair_score %s m1 %s m2 %s" % (i, result[0], result[1], result[2])

                    print test_DoubleMatch1, " [winner = %s]" % test_DoubleMatch1.getWinner()
                    # return "%s. %s %s %s" % \
                    # (self.tournament, self.homeName, str(self.getResult()).replace(",", ":") ,self.guestName)
                    # print "%s: %s : %s, outcome = %s, pair_score %s m1 %s m2 %s" % \
                    #       (test_DoubleMatch1.getName(), pair[0], pair[1], test_DoubleMatch1.getOutcome(), pair_result,
                    #        test_DoubleMatch1.getFirstMatchResult(), test_DoubleMatch1.getSecondMatchResult())

        if post_truncate:
            db.truncate(db.MATCHES_TABLE)


    # for every iteration will be played 1 match and 1 double-matches
    ITERATIONS = 100

    # Test(ITERATIONS, "Match")
    # Test(int(ITERATIONS*0.001), "DoubleMatch")

    # RESET ALL MATCHES DATA BEFORE TEST
    PRE_TRUNCATE = False
    PRE_TRUNCATE = True
    # RESET ALL MATCHES DATA AFTER TEST
    POST_TRUNCATE = False
    POST_TRUNCATE = True
    # SAVE TO DB - to avoid data integrity (if important data in table exists), turn it off
    SAVE_TO_DB = False
    SAVE_TO_DB = True
    Test(ITERATIONS, PRE_TRUNCATE, POST_TRUNCATE, SAVE_TO_DB, "Match", "DoubleMatch")
