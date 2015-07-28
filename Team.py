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
                                      columns="id", values=self.id,
                                      where = " WHERE ", sign = " = ", fetch="all")
            self.rating, self.uefaPos = team_rank
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


class Teams():
    """
    all teams container - used for store all team data in RAM to quick access instead of get from database every time
    """
    def __init__(self, season, year):
        self.season = season # id
        self.year = year # id
        # self.setTeams()
        self.teams = {}

    def str(self):
        """
        string representation of dict
        :return:
        """
        representation = "\n print Teams"
        for k, teams in self.teams.iteritems():
            representation += "\nid_tourn = %s" % k
            for i, team in enumerate(teams):
                representation += "\n%s. %s" % (str(i), str(team))
        return representation

    def setTournResults(self, tournament_id, teams):
        """
        set prev tournament result as a list of teams sorted by position
        :param tournament_id:
        :param teams:
        :return:
        """
        self.teams[tournament_id] = teams

    def getTournResults(self, tournament_id):
        """

        :param tournament_id:
        :return: list of teams sorted by results in last played tournament (which id is given_
        """
        if tournament_id in self.teams.keys():
            return self.teams[tournament_id]
        else:
            raise KeyError, "no data for getTournResults tournament_tournament_id = %s" %tournament_id

    def sortedByCountryPos(self, country_positions):
        """
        :country_positions: list of country_positions (national tournaments) positions
        :return: dict of teams where keys are sorted in
        """
        # national_tournaments_positions
        # twice - for leagues and cups
        ntp = country_positions + [cup_id + len(country_positions) for cup_id in country_positions]
        # in other words,
        # ntp = ntp_leagues + ntp_cups    where
        # ntp_leagues = [league_teams for league_teams in ntp_leagues]
        # ntp_cups = [(cup_teams + shift) for cup_teams in ntp_leagues] where shift = len(country_positions)

        # ntp teams - list of teams, sorted by ntp
        self.ntp_teams = [self.teams[tournament_id + 2] for tournament_id in  ntp]
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

    def setTeams(self):
        """
        get ALL teams sorted by rating - not realised by me, use individual setting for country and tournament
        :return:
        """
        raise NotImplementedError
        if self.year <= db.START_SIM_SEASON:
            # print "setMembers by rating for first season"
            # get all team ids from defined country id - like they ordered by default in team_info table
            # print "self.country_id=", self.country_id
            teams_tuples = db.select(what="id", table_names=db.TEAMINFO_TABLE, where=" WHERE ", columns="id_country ",
                              sign=" = ", values=self.country_id, fetch="all", ind="all")
            teams_indexes = [team[0] for team in teams_tuples]
            self.teams = [Team(ind) for ind in teams_indexes]
            print "self.teams", self.teams
            # if it already sorted, comment all block below

            # another sort variants
            # teams_info = db.select(what = "id, name, runame, id_country", table_names=db.TEAMINFO_TABLE, fetch="all")
            teams_info = db.select(what = "id", table_names=db.TEAMINFO_TABLE, fetch="all")
            self.teams = [Team(team_info[0]) for team_info in teams_info] # make teams by id
            print "self.teams", self.teams
            self.teams = db.select(what="id_team", table_names=db.TEAM_RATINGS_TABLENAME, where=" WHERE ",
                                   columns="id_season", values=self.season, suffix="ORDER BY position", fetch="all")
            print "self.sorted_teams", self.teams

        else:
            print "setMembers by position from previous league"
            # raise NotImplementedError
            teams_tuples = db.select(what="id", table_names=db.TEAMINFO_TABLE, where=" WHERE ", columns="id_country ",
                              sign=" = ", values=self.country_id, fetch="all", ind="all")
            # sort by position in league





        # TODO see below
        # convert self.teams to form convenient to extract by tournaments
        # form = { tournament_id : [pos1, pos2...] if League

        # countries id sorted by rating
        countries_ids =  db.select(what="id_country", table_names=db.COUNTRY_RATINGS_TABLE, where=" WHERE ",
                               columns="id_season", values=self.season, suffix="ORDER BY position", fetch="all")
        print "countries_ids", countries_ids
        countries_ids = [id[0] for id in countries_ids]
        print "countries_ids", countries_ids

        # fill self.teams to form
        # {id_country1 : {pos1..posN of League : team_id, "cupwinner":team_id} ... id_countryN,
        # "CL" : {"Qualification 3, 4, Group" : team_id }
        for country_id in countries_ids:
            self.teams[country_id] = {}
            # get leagues

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





