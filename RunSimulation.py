__author__ = 'NereWARin'
# -*- coding: utf-8 -*-
import Team, Match, Leagues

class Simulation():
    def __init__(self, teams, ObjectClassName, iterations):
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
            print self.object.printResult()


if __name__ == "__main__":
    teamsL = Team.createTeamsFromExcelTable()
    # for team in teamsL:
    #     print team.getName()
    ObjectClassName = Match.Match
    iterations  = 1
    sim = Simulation((teamsL[0], teamsL[1]), ObjectClassName, iterations).run()

