__author__ = 'GorbachevAA'
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


""" test code """
if __name__ == '__main__':

    def test_roundRobin():
        # pairings =     roundRobin(range(5))
        for team_l in range(20):
            print "\n team_l = %s " % team_l
            for pair in roundRobin(range(team_l)):
                # print "__", pairings
                print pair

    a = [[1,2], [4,3]]
    if 3 in a:
        print "ok"

# The round-robin pairing algorithm can be used in generating a "fair" list of pairings. The algorithm is often used in competitions, where each competitor should be matched against all of the other competitors, once. In such a case, with N competitors (with N a multiple of 2), there will be N-1 sets of pairings.

# If there is an odd number of units in the list, the implementation will add 'None' to the list. The None item will be matched fairly against each of the units. In sports, a competitor paired with 'None', would have a 'bye' for that round.

# syntax error. ..easy fix: change: "pairings.append(units[i], units[count-i-1])", on line 12, to: "pairings.append((units[i], units[count-i-1]))", and it works, fine!