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

""" test code """
if __name__ == '__main__':
    # test_roundRobin()
    # TestSortTeamL()
    # TestAddLists()
    # testCounter()
    # testStrings()
    # test_iterations(10)
    test_orderedDict()

# TestSortTeamL()

# The round-robin pairing algorithm can be used in generating a "fair" list of pairings. The algorithm is often used in competitions, where each competitor should be matched against all of the other competitors, once. In such a case, with N competitors (with N a multiple of 2), there will be N-1 sets of pairings.

# If there is an odd number of units in the list, the implementation will add 'None' to the list. The None item will be matched fairly against each of the units. In sports, a competitor paired with 'None', would have a 'bye' for that round.

# syntax error. ..easy fix: change: "pairings.append(units[i], units[count-i-1])", on line 12, to: "pairings.append((units[i], units[count-i-1]))", and it works, fine!

