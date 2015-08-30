__author__ = 'NereWARin'
# -*- coding: utf-8 -*-
from Team import Teams
import Match
# import Leagues
# import DataParsing
import DataStoring

class Simulation():
    def __init__(self, ObjectClassName, iterations, teams = None):
        if not teams:
            # if its first calling of season simulation,
            # create teams instances and get all its data from database
            # Teams contains method setTournResults to quick access to results of current tournament used by cups and UEFA
            self.teams = Teams()
        else:
            # alse we already have Teams object, just use it
            self.teams = teams
        # print type(ObjectClassName), ObjectClassName
        self.ObjectClassName = ObjectClassName
        self.iterations = iterations
        # if objectToSim == "Match":
        #     self.object = Match()

    def run(self):
        for iteration in range(self.iterations):
            self.object = self.ObjectClassName(self.teams, "testSimulation")
            result = self.object.run()
            # print result
            print self.object


if __name__ == "__main__":
    # create teams list
    teamsL = DataStoring.createTeamsFromExcelTable()
    # for team in teamsL:
    #     print team.getName()
    ObjectClassName = Match.Match
    print "\nRun Simulation \"%s\"\n" % str(ObjectClassName).split(".")[0]
    iterations  = 1
    sim = Simulation((teamsL[0], teamsL[1]), ObjectClassName, iterations).run()

