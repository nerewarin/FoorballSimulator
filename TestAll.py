# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

import DataStoring
import Team
import Match
import Leagues
import Cups

import util
import DataStoring as db
from Leagues import League, TeamResult

import values as v
from values import Coefficients as C
from operator import attrgetter, itemgetter
import random
import time
import os
import warnings
import copy

@util.timer
def run(models):
    names = [model.__name__ for model in models]
    print "TEST ALL:", ", ".join(name for name in names)
    for ind, model in enumerate(models):
        testname = "TEST %s:%s" % (ind+1, names[ind])
        print "\n%s" % testname
        model.Test()
        print "%s PASSED\n===================================================" % testname

if __name__ == "__main__":
    models = [DataStoring, Team, Match, Leagues, Cups]
    # models = [Leagues]
    run(models)