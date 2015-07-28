__author__ = 'GorbachevAA'

import util
# import Team

def roundRobin(units, sets=None):
    """ Generates a schedule of "fair" pairings from a list of units """
    if len(units) % 2:
        units.append(None)
    count    = len(units)
    sets     = sets or (count - 1)
    half     = count / 2
    schedule = []
    for turn in range(sets):
        pairings = []
        for i in range(half):
            # print "i", i
            pair = (units[i], units[count-i-1])
            if not None in pair:
                pairings.append(pair)
            # pairings.append((units[i], units[count-i-1]))
        units.insert(1, units.pop())
        # print "pairings", pairings

        yield pairings
    # return schedule


def test_roundRobin():
    # pairings =     roundRobin(range(5))
    for team_l in range(20):
        print "\n team_l = %s " % team_l
        for pair in roundRobin(range(team_l)):
            # print "__", pairings
            print pair


def TestSortTeamL():
    import Team, random
    team_num = 100
    teams = []
    for i in range(team_num):
        # teamN = i + 1
        teamN = i
        rating = random.randrange(100)
        uefa_pos = teamN
        teams.append(Team.Team("FC team%s" % teamN, "RUS", rating, "team%s" % teamN, uefa_pos, []))
    print [(team.getName(), team.getRating()) for team in teams]
    print "sorting teamsL"
    teams.sort(key=lambda x:-x.getRating())
    print [(team.getName(), team.getRating()) for team in teams]

def TestAddLists():
    a = "qqq"
    b = [1, 2]
    c = [1, 2, 3]
    s =  [a] + b + c
    print s

def testCounter():
    import random
    country_ratings = util.Counter()
    teamsL = [random.randrange(100) for i in range(100)]
    for team in teamsL:
        # sum of all team ratings
        # country_ratings[team] = (country_ratings[team][0] + team, country_ratings[team][1] + 1)
        print country_ratings[team]# = (country_ratings[team][0] + team, country_ratings[team][1] + 1)
    print country_ratings


def testStrings():
    TEAMINFO_TABLENAME = "Team_Info"
    COUNTRIES_TABLENAME = "Countries"
    TOURNAMENTS_TABLENAME = "Tournaments"
    CONSTANT_TABLES = (TEAMINFO_TABLENAME, COUNTRIES_TABLENAME, TOURNAMENTS_TABLENAME)
    SEASONS_TABLENAME = "seasons"
    TEAM_RATINGS_TABLENAME = "team_ratings"
    COUNTRY_RATINGS_TABLENAME = "country_ratings"
    PREDEFINED_TABLES = (SEASONS_TABLENAME, TEAM_RATINGS_TABLENAME, COUNTRY_RATINGS_TABLENAME)
    tables = ""
    for table in (CONSTANT_TABLES + PREDEFINED_TABLES):
        tables += (table + ", ")
    print tables[:-2]


def test_orderedDict():
    _dict = {1:{ "count":1, "toss":"rnd"}, 2 :{ "count":0, }, 0:{ "count":17, "toss":"aaa"}}
    print _dict.items()


def test_iterations(iterations):
    for round in range(1, iterations+1):
        print round

def test_args():
    def foo(*args):
        for arg in args:
            print arg
        print args
    args = [1,2,32,3,2]
    foo(*args)

def test_lists_mul():
    a = [(4, 1), (3, 2), (10, 3), (1, 4), (9, 5), (2, 6), (6, 7), (8, 8), (7, 9), (38, 10), (18, 11), (21, 12), (12, 13), (49, 14), (22, 15), (41, 16), (5, 17), (13, 18), (30, 19), (31, 20), (28, 21), (20, 22), (14, 23), (32, 24), (11, 25), (33, 26), (25, 27), (26, 28), (39, 29), (34, 30), (27, 31), (50, 32), (15, 33), (23, 34), (19, 35), (17, 36), (29, 37), (40, 38), (44, 39), (36, 40), (47, 41), (46, 42), (37, 43), (51, 44), (35, 45), (43, 46), (24, 47), (53, 48), (45, 49), (48, 50), (52, 51), (16, 52), (42, 53), (54, 54)]
    print len(a), a
    a = a * 2
    print len(a), a

""" test code """
if __name__ == '__main__':
    # test_roundRobin()
    # TestSortTeamL()
    # TestAddLists()
    # testCounter()
    # testStrings()
    # test_iterations(10)
    # test_orderedDict()
    # test_args()
    test_lists_mul()

# TestSortTeamL()

# The round-robin pairing algorithm can be used in generating a "fair" list of pairings. The algorithm is often used in competitions, where each competitor should be matched against all of the other competitors, once. In such a case, with N competitors (with N a multiple of 2), there will be N-1 sets of pairings.

# If there is an odd number of units in the list, the implementation will add 'None' to the list. The None item will be matched fairly against each of the units. In sports, a competitor paired with 'None', would have a 'bye' for that round.

# syntax error. ..easy fix: change: "pairings.append(units[i], units[count-i-1])", on line 12, to: "pairings.append((units[i], units[count-i-1]))", and it works, fine!