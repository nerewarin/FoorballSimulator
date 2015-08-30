__author__ = 'NereWARin'
# -*- coding: utf-8 -*-
from Team import Teams
from Match import Match, DoubleMatch
from Leagues import League
from Cups import Cup
from UEFA_Champions_League import UEFA_Champions_League
from Season import Season
# import DataParsing
import DataStoring
import sys

class Simulation():
    def __init__(self, ObjectClassName, members = None, iterations = 1):
        if not members:
            # if its first calling of season simulation,
            # create teams instances and get all its data from database
            # Teams contains method setTournResults to quick access to results of current tournament used by cups and UEFA
            self.teams = Teams()
        else:
            # alse we already have Teams object, just use it
            self.teams = members
        # print type(ObjectClassName), ObjectClassName
        self.ObjectClassName = ObjectClassName
        self.iterations = iterations
        # if objectToSim == "Match":
        #     self.object = Match()

    def run(self):
        for iteration in range(self.iterations):
            self.object = getattr(sys.modules[__name__], self.ObjectClassName)(members = self.teams)
            result = self.object.run()
            # print result
            # print self.object


if __name__ == "__main__":
    # create teams list
    teamsL = Teams(members = DataStoring.createTeamsFromExcelTable())
    # for team in teamsL:
    #     print team.getName()
    classes_to_test = ("Season", )
    # classes_to_test = ("Match", "DoubleMatch", "League", "Cup", "UEFA_Champions_League", "Season")
    ITERATIONS  = 2
    for ObjectClassName in classes_to_test:
        print "\nRun Simulation \"%s\"\n" % str(ObjectClassName).split(".")[0]
        sim = Simulation(ObjectClassName, members = teamsL, iterations= ITERATIONS)
        sim.run()

