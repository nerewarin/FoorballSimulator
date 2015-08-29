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

            team_rank  = db.select(what = ["rating", "position"], table_names=db.TEAM_RATINGS_TABLENAME,
                                      where = " WHERE ", columns="id", sign = " = ", values=self.id,
                                      fetch="all", suffix=" ORDER BY id DESC LIMIT 1")
            self.rating, self.uefaPos = team_rank
            # print "self.rating, self.uefaPos", self.rating, self.uefaPos
            self.country = db.select(what = "name", table_names=db.COUNTRIES_TABLE, where = " WHERE ", columns="id",
                                     sign = " = ",  values=self.countryID, fetch="one")
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


class Teams():
    """
    all teams container - used for store all team data in RAM to quick access instead of get from database every time
    """
    def __init__(self, season, year, nations):
        # self.season = season # id
        # self.year = year # id
        # self.nations = nations
        # self.setTeams()

        # create list of ALL TEAMS OBJECTS
        teams_num = db.select(what="id", table_names=db.TEAMINFO_TABLE, suffix=" ORDER BY id DESC LIMIT 1", fetch="one")
        # print "teams_num = %s" % teams_num
        self.teams = [Team(ind) for ind in xrange(1, teams_num + 1)]
        # self.teams = {}

        # dictionary of teams sorted by tournament ID
        self.tourn_teams = {}

    def str(self):
        """
        string representation of dict
        :return:
        """
        representation = "\n print Teams"
        # for k, teams in self.teams.iteritems():
        for k, teams in self.tourn_teams.iteritems():
            representation += "\nid_tourn = %s" % k
            for i, team in enumerate(teams):
                representation += "\n%s. %s" % (str(i), str(team))
        return representation

    def get_team(self, ind="all"):
        if ind=="all":
            return self.teams
        return self.teams[ind]

    def setTournResults(self, tournament_id, teams_indexes):
        """
        set prev tournament result as a list of teams sorted by position
        :param tournament_id:
        :param teams:
        :return:
        """
        self.tourn_teams[tournament_id] = teams_indexes

    def getTournResults(self, tournament_id):
        """

        :param tournament_id:
        :return: list of teams sorted by results in last played tournament (which id is given_
        """
        if tournament_id in self.tourn_teams.keys():
            # teams = []
            # for pos, team_ind in enumerate(self.tourn_teams[tournament_id]):
            #     teams.append(self.teams[team_ind - 1])
            # return teams
            # return self.teams[self.tourn_teams[tournament_id] - 1]

            return [self.teams[ind-1] for ind in self.tourn_teams[tournament_id]]
            return self.tourn_teams[tournament_id]
        else:
            raise KeyError, "no data for getTournResults tournament_tournament_id = %s" %tournament_id

    def sorted_by_rating(self):
        """
        :return: list of teams sorted by current rating
        """
        teamsL = sorted(self.teams, key=lambda x: x.getRating(), reverse = True)
        return teamsL

    def sortedByCountryPos(self, season_id):
        """
        :season_id: id of current season (but we will use id of previous season)
        :country_positions: list of country_positions (national tournaments) positions
        :return: dict of teams where keys are sorted in
        """

        # get country ratings for this season - list of tuples [(country_id, position), ...]
        # country_positions = db.select(what="id_country, position", table_names=db.COUNTRY_RATINGS_TABLE, where=" WHERE ",
        #                             columns="id_season", sign=" = ", values=(self.season_id-1), fetch="all", ind="all")
        country_positions = db.select(what="id_country", table_names=db.COUNTRY_RATINGS_TABLE, where=" WHERE ",
                                    columns="id_season", sign=" = ", values=(season_id-1), fetch="all", ind="all")
        country_positions = [country[0] for country in country_positions]
        # print "country_positions", country_positions

        # national_tournaments_positions
        # twice - for leagues and cups
        ntp = country_positions + [cup_id + len(country_positions) for cup_id in country_positions]
        # in other words,
        # ntp = ntp_leagues + ntp_cups    where
        # ntp_leagues = [league_teams for league_teams in ntp_leagues]
        # ntp_cups = [(cup_teams + shift) for cup_teams in ntp_leagues] where shift = len(country_positions)

        # ntp teams - list of teams, sorted by ntp
        # self.ntp_teams = [self.tourn_teams[tournament_id + 2] for tournament_id in  ntp]
        # print "self.ntp_teams v1", len(self.ntp_teams), self.ntp_teams
        # for ntp_team in self.ntp_teams:
        #     print ntp_team


        self.ntp_teams = []
        for tournament_id in ntp:
            tourn_teams = []
            teams_indexes = self.tourn_teams[tournament_id + 2]
            if isinstance(teams_indexes, list):
                # for every pos in League
                for ind in teams_indexes:
                    tourn_teams.append(self.teams[ind - 1])
                self.ntp_teams.append(tourn_teams)
            elif isinstance(teams_indexes, int):
                # cup winner
                self.ntp_teams.append(self.teams[teams_indexes - 1])
        # self.ntp_teams = [[self.teams[ind - 1] for ind in self.tourn_teams[tournament_id + 2]] for tournament_id in ntp]
        # print "self.ntp_teams v2", self.ntp_teams
        return self.ntp_teams

    def getNTPteams(self, ntp_index = None):
        """
        return list of teams of tournament - all the same as getTournResults but ntp is list, sorted by nation rating
        instead of just country_id
        :param ntp: index (position of tournament in ntp_list)
        :return:
        """
        if not ntp_index:
            return self.ntp_teams
        else:
            return self.ntp_teams[ntp_index]

    def sortedByID(self):
        return [tourn_id for tourn_id in self.teams]

    def setTeams(self):
        """
        get ALL teams sorted by rating - not realised by me, use individual setting for country and tournament
        :return:
        """
        raise NotImplementedError

    def sortTeamsByPos(self):
        """
        sort all lists of teams (for every country or champ
        :return:
        """
        raise NotImplementedError
        # print "new_team_info", new_team_info
        # teams_info = db.select(what = "id_season, id_team, position", table_names=db.TEAMINFO_TABLE, fetch="all")
        # db.select()

    def getCupWinner(self, id_country):
        """

        :return: team object - winner cup of a given id
        """
        raise NotImplementedError


def Test():
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
    Test()
    print "time = ", time.time() - start_time
    # # print to console all teams
    # DataParsing.printParsedTable(teamsL)





