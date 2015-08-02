# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

from Team import Team
from Cups import Cup
import DataStoring as db
import util
from Leagues import League, TeamResult
import Match as M
from values import Coefficients as C, TournamentSchemas as schemas, UEFA_CL_TYPE_ID, \
    UEFA_EL_TYPE_ID, VALUES_VERSION, UEFA_TOURNAMENTS_ID, UEFA_CL_SCHEMA, UEFA_EL_SCHEMA, RESERVED_EL_TEAMS
import values as v

from operator import attrgetter, itemgetter
import random
import time
import os
import sys
import warnings

# TODO func here avoid importing - delete it if DB is installed on executable env
# def trySQLquery(a,b,c):
#     return a
#
# def connectDB(a="",b="",c="",d=""):
#     return a,cur()
#
# class cur():
#     def execute(self):
#         return None

class UEFA_Champions_League(Cup):
    def __init__(self,
                 name = UEFA_CL_TYPE_ID, # id from Tournaments
                 season = None,
                 year = None,
                 members = None,
                 delta_coefs = C(VALUES_VERSION).getRatingUpdateCoefs("list"),
                 pair_mode = 1,
                 seeding = UEFA_CL_SCHEMA,
                 state_params = ("final_stage", ),
                 save_to_db = True,
                 prefix = "UEFA",
                 type_id = UEFA_CL_TYPE_ID, # id from tournaments_types_names
                 country_id = None
                 ):
        """
        UEFA_Champ_L is a tournament, implemented as three tournaments:
        Qualification Cup, Group League, Play-Off Cup.

        Num of rounds and pairs in every tournament defined by schema

        :param name:
        :param season:
        :param members:
        :param delta_coefs:
        :param schema:
        :param pair_mode:
        :param state_params:
        :return:
        """
        if country_id:
            warnings.warn("UEFA not uses country as parameter - its international!")

        super(UEFA_Champions_League, self).__init__(**{par:val for par,val in locals().iteritems()
                                                       if par != "self" })
                                                        # if par not in ("self", "ntp_teams", "nations")})
        print "\nWELCOME TO UEFA LEAGUE *** id = %s season_id = %s ***" % (name, season.getID())


    def setMembers(self):
        """
        defines members for every round
        convert indexes of countries, from what championships members are getting, to indexes of self.members for every team

        :return:
        """
        ntp_teams = self.season.get_ntp()
        nations = self.season.getNations()

        def shift_tourn(ntp_teams, nations, tourn_id):
            """
            shift seeding source, if current team is already seeded in this or higher UEFA tournament
            """

             # get next league - stay in the same half
            # ifcup, reminder =  divmod(tourn_id, self.nations)
            # tourn_id = ifcup * self.nations + (reminder + 1) % self.nations

            # get from next-ranked LEAGUE (even if CUP was empty)            # shift
            tourn_id = (tourn_id + 1) % nations
            # get again
            ntt = ntp_teams[tourn_id]
            return tourn_id, ntt

        # shift_seed is used to shift indexes of seeded members in cases - if some country has'n got so many counties
        # to pass them to UEFA cup, so shift nation
        shift_nation = 0
        # or if member seeded to UEFA_EL by Cup was already seeded to UEFA_CL - so get team from next pos of national
        # league
        shift_team = 0

        # self.members = []
        # list of seeded members ordered by sub-tournament from qual to play-off
        self.sub_schems = []
        # parsing stored in schema values
        stages = []

        # winners of every sub-tournament will be added to next sub-tournament
        winners = []

        # UEFA tournament consists of sub_tournemants - Qualification, Group, Pla-off which are played in order
        for sub_tourn in self.seeding: # schema - list of dicts
            # print stage
            sub_tourn_members = []
            classname, round_num, parts, seeding, round_num, sub_tourn_name, pair_mode = \
                None, None, None, None, None, None, None
            rounds_info = {}
            # parts = None
            # pair_mode = None
            # tourn_class = None
            # classname = None

            assert len(sub_tourn.keys()) == 1, "unexpected sub_tourn keys (%s) > 1 " % len(sub_tourn.keys())
            # v1 the same as
            # sub_tourn_name = sub_tourn.keys()[0]
            # sub_tourn_info = sub_tourn[sub_tourn_name]
            # v2
            for sub_tourn_name, sub_tourn_info in sub_tourn.iteritems():
                # print "sub_tourn_name %s" % sub_tourn_name
                classname = sub_tourn_info["classname"]
                # tourn_class = getattr(sys.modules[__name__], classname)

                parts = sub_tourn_info["parts"] # for Groups
                pair_mode = sub_tourn_info["pair_mode"]
                rounds_info = sub_tourn_info["tindx_in_round"]
                # borders = {}
                for round_num, seeded_sources in rounds_info.items():
                    # print "round_num = %s" % round_num#, members_schema
                    rounds_info[round_num] = {}
                    round_members = []
                    if round_num == 4: # TODO for test
                        pass

                    for source, pos in seeded_sources.iteritems():
                        print "sourcse, pos = ", source, pos

                        # # if individual toss for round is defined
                        # if source == "toss":
                        #     seeding[round_num]["toss"] = pos

                        if isinstance(source, tuple):
                            # getting teams from source
                            if isinstance(pos, int):
                                # print "seed from national League"
                                # shift if cup is references to orders Leagues and Cups are stored in ntp, see Teams
                                shift_ifcup = 0
                                position = pos
                            elif pos == "cupwinner":
                                # print "seed from national Cup"
                                shift_ifcup = nations
                                position = 1
                            else:
                                raise Exception, "unknown pos %s type %s" % (pos, type(pos))

                            # tourn_pos is a index of self.ntp, it is stored in schema (see values.py) and points to ntp
                            for tourn_pos in source:
                                # -1 cause torn_id start from 1 in db, but index of ntp_teams starts from 0
                                tourn_id = tourn_pos + shift_ifcup + shift_nation - 1 # index of list ntp_teams
                                # national tournament teams list
                                ntt = ntp_teams[tourn_id] # list of teams for league or cup winner for cup
                                # index of ntt list
                                # -1 cause position start from 1 in db, but index of teams in ntp_teams starts from 0
                                team_index = (position - 1) + shift_team
                                # check national tournament has this position (ntp exists)
                                # while len(ntt) < team_index:
                                #     # if not, next tournament fills vacant position
                                #     self.shift_nation += 1
                                #     warnings.warn("national tournament_id %s has not position %s to qualify it to UEFA!" % (
                                #         tourn_id, team_index )
                                #     raise NotImplemented
                                while team_index > (len(ntt) - 1): # league is too small!
                                    # if tournament has not got more unseeded teams, tourn will be shifted to next
                                    warnings.warn("national tournament_id %s has not position %s to qualify it to UEFA!"
                                                  % (tourn_id, team_index))
                                    # TODO there may be a problem
                                    tourn_id, ntt = shift_tourn(ntp_teams, nations, tourn_id)

                                seeded_team = ntt[team_index]
                                # seeded_team = ntt.pop(0)

                                def check_already_seeded_in_UEFA(type, season, seeded_team):
                                    # look at current lists
                                    if (seeded_team in round_members) or (seeded_team in sub_tourn_members) or \
                                            (seeded_team in [other_sub[2] for other_sub in  self.sub_schems]):
                                        return True

                                    if type == UEFA_EL_TYPE_ID:
                                        # additionally see in members CL stored in Season
                                        return season.check_seed_in_CL(seeded_team)
                                    # not found - ok, team is ready to be seeded
                                    return False

                                    # if type == UEFA_CL_TYPE_ID:
                                    #     # see in self members
                                    #     if seeded_team in round_members:
                                    #         return True
                                    #     elif seeded_team in sub_tourn_members:
                                    #         return True
                                    #     elif seeded_team in [other_sub[2] for other_sub in  self.sub_schems]:
                                    #         return True
                                    #     return False
                                    # elif type == UEFA_EL_TYPE_ID: # if EL
                                    #     # see in members CL stored in Season
                                    #     is_in_CL = season.check_seed_in_CL(seeded_team)
                                    #     # see in current members EL
                                    #     is_in_EL = season.check_seed_in_EL(seeded_team)
                                    #     return (is_in_CL or is_in_EL)

                                # if source == (35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54):
                                #     pass
                                #     # for debug
                                # # check team was already seeded in UEFA by another source
                                # # TODO useful only when seed UEFA_EL - we can skip it for UEFA_CL
                                while check_already_seeded_in_UEFA(self.type_id, self.season, seeded_team):
                                    # self.shift_team += 1
                                    # get team of lower position of the same league

                                    # print "seed_in_CL, shift_tourn!"
                                    team_index += 1
                                    if team_index > (len(ntt) - 1):
                                        # if tournament has ot got more unseeded teams, tourn will be shifted to next
                                        tourn_id, ntt = shift_tourn(ntp_teams, nations, tourn_id)
                                        # TODO we check one tournament but not others!  we can make "reserve" tag in schema for additional list of teams and pop from it
                                    seeded_team = ntt[team_index]#.pop()
                                round_members.append(seeded_team)

                        elif source == "toss":
                            rounds_info[round_num]["toss"] = pos

                        elif source == "CL":
                            round_members += self.season.get_CL_EL_seeding(pos)
                            # print "seed_from_CL", team
                            # # its good for checking
                            # cl_members = self.season.get_UEFA_CL_members()
                            # print "cl_members", len(cl_members), cl_members

                    sub_tourn_members += reversed(round_members)
                    rounds_info[round_num]["count"] = len(round_members) # TODO round_members = 8 but group_winners = 24! count should be 0!
                    if sub_tourn_name == "Play-Off":
                        pass
                        rounds_info[round_num]["count"] = 0

            self.sub_schems.append((classname, sub_tourn_name, sub_tourn_members[::-1], rounds_info, parts, pair_mode))

        # common list of members used for quick search by another tournament (UEFA_EL) - maybe it will be unused
        self.members = []
        for members in reversed(self.sub_schems):
            # get sub_tourn_members   from  sub_schems and add them to the common list
            self.members += members[2]
        # reverse back - now its from favorite to outsider
        self.members = self.members[::-1]
        print "ok UEFA setMembers"
        return self.members


    def run(self, print_matches = False):
        """
        run sub-tournaments
        :param print_matches:
        :return:
        """
        # register ID of tournament if unregistered yet
        self.name_id = self.saveTounramentPlayed()

        # fot Matches (not use cause id_tournament column references to tourn_type_name through tournaments_played)
        # tourn_type_name = db.select(what="name", table_names=db.TOURNAMENTS_TYPES_TABLE, where=" WHERE ", columns="id",
        #                             sign=" = ", values=self.type_id)
        # print "tourn_type_name: %s" %  tourn_type_name

        # dict of CL loosers that will be transferred to EL seeding
        self.CL_EL_seeding = {"Qualification 3" : [], "Qualification 4" : [], "Group 3th places" : []}

        # parse schema
        pre_winners = []
        for sub_schema in self.sub_schems:
            # tourn_class, sub_tourn_name, members, rounds_info, parts, pair_mode = sub_schema
            classname, sub_tourn_name, members, rounds_info, parts, pair_mode = sub_schema
            tourn_class = getattr(sys.modules[__name__], classname)
            print "classname %s, sub_tourn_name %s, seeded_members %s, rounds_info %s, parts %s, pair_mode %s" % (
            classname, sub_tourn_name, members, rounds_info, parts, pair_mode)

            if not parts:
                warnings.warn("empty round!")
                # go to next round
                continue

            if not sub_tourn_name:
                warnings.warn("no name sub-tournament!")
                continue

            if not pair_mode:
                warnings.warn("no pair mode!")

            if not rounds_info:
                warnings.warn("no rounds_info collected!")

            # sourcse, pos =  = sub_tourn_name
            # seeding = {round_num : {"count": len(sub_tourn_members)}  }  # - already defined
            # members = sub_tourn_members
            # pair_mode = pair_mode


            # for multiple groups
            sub_winners = []
            # add winners from previous sub-tournament
            members = pre_winners + members
            # members = pre_winners + self.members_by_sub

            # split members by parts
            # if sub-tournament has classname = "League"
            if classname == "League": # or prefix == "Group" (or starts from group)
                # sort teams by rating
                members = sort_by_ratings(members)
                pass
                # split by 4 baskets
                baskets_count = 4
                assert len(members) % baskets_count == 0, "teams in baskets cannot be equal!"
                basket_len = len(members) / baskets_count
                baskets = []
                for basket_num in xrange(baskets_count):
                    basket = members[basket_len*basket_num : basket_len*(basket_num+1)]
                    baskets.append(basket) # TODO APPEND

                # define group members Group
                group_members = [[] for part in xrange(parts)]
                attempts = 1000
                while members and attempts:
                    for part in xrange(parts):
                        for basket in baskets:
                            unchecked_candidates = list(basket)
                            if not unchecked_candidates:
                                print  "groups_seeded_successfully"
                                break
                            candidate = random.choice(unchecked_candidates)
                            checked = False
                            # check no same country in the group
                            # there can be case that only thow teams with same nation are the rest of baskets
                            # and check will never be True - so we constraint this case with a fixed num of attempts
                            check_attempts = 100
                            while not checked and check_attempts:
                                checked = True
                                # если не встретилась команда с той же страной -то Тру закрепляется, иначе выст.флаг Фолс
                                for member in group_members[part]:
                                    if member.getCountry() == candidate.getCountry():
                                        checked = False
                                        # unchecked_candidates.remove(candidate)
                                        new_candidate = random.choice(unchecked_candidates)
                                        while candidate == new_candidate and check_attempts:
                                            check_attempts -= 1
                                            new_candidate = random.choice(unchecked_candidates)
                                        candidate = new_candidate
                                        break
                                # if not checked:
                                #     if not unchecked_candidates:
                                #         # unlucky! but no way
                                #         print "cannot found candidate with the different country for %s" % candidate
                                #         break
                                #     candidate = random.choice(unchecked_candidates)

                            group_members[part].append(candidate)
                            basket.remove(candidate)
                            members.remove(candidate)
                print "TOSS group_members is ok!\n" % group_members
                self.set_group_members(group_members)

            # RUN SUB_TOURNAMENTS
            for part in xrange(parts):
                part_num = part + 1
                # if parts > 1, so its groups
                print "run UEFA part_num=%s" % part_num, "sub_tourn_name = %s" % sub_tourn_name
                if classname == "League":
                    # members = group_members[baskets_count*part : baskets_count*(part+1)]
                    members = group_members[part]
                    # prefix = tourn_type_name + " " + sub_tourn_name + " %s" % part_num
                    prefix = sub_tourn_name + " %s " % part_num
                else:
                    # prefix = tourn_type_name + " " + sub_tourn_name
                    prefix = sub_tourn_name + " "

                if classname == "Cup":
                    pass # catching problem (debug breakpoint)
                sub_tournament = tourn_class(name = self.name_id,
                                     season = self.season,
                                     year = self.year,
                                     members = members,
                                     pair_mode = pair_mode,
                                     seeding = rounds_info,
                                     # save_to_db = True, # by default
                                     prefix = prefix,
                                     type_id = self.type_id) # TODO !!!
                if classname == "League":
                    # filter two first teams
                    group_results = sub_tournament.run()
                    first_place = group_results[0]["Team"]
                    second_place = group_results[1]["Team"]
                    # if its CL, if will be used used for EL
                    third_place = group_results[2]["Team"]
                    sub_winners = [first_place] + sub_winners + [second_place]
                    self.CL_EL_seeding["Group 3th places"].append(third_place)
                else:
                    # classname == "Cup"
                    sub_results = sub_tournament.run()
                    sub_winners += sub_results
            pre_winners = sub_winners
        return

    def get_group3(self):
        """
        :return: dict {"Qualification 3" : [Team...Team], "Qualification 4" : [], "Group 3th places" : []}
        """
        return self.CL_EL_seeding

    def set_group_members(self, members):
        """

        :param members: list of lists_of_teams, combinated by played in Group
        :return:
        """
        self.group_members = members

    def test(self, print_matches = False, print_ratings = False):
        print "\nTEST CUP CLASS\n"
        print "pair_mode = %s\nseeding = %s\n" % (self.pair_mode, self.seeding)
        print "initial Net:"
        print self#.printTable()
        if print_matches:
            print "\nMatches:"
        self.run(print_matches)
        print "\nWinner:\n%s" % self.getWinner()
        # print "\nresults:\n%s" % [(k, [team.getName() for team in self.results[k]] ) for k in self.results.keys()]
        print "\nresults:"
        for k in self.results.keys():
            # TODO sort results ny round (maybe store them in list)
            print k, [team.getName() for team in self.results[k]]
        print "\nFinal Net:\n", str(self), "\n"

        # ratings after league
        # print "print_ratings = %s" % print_ratings
        # print "self.getMember() %s" % self.getMember()
        if print_ratings:
            for team in self.getMember():
                print team.getName(), team.getRating()



def sort_by_ratings(teams):
    """
    sort list of teams by ratings and return in descending order [favorite ... outsider]
    :param teams:
    :return:
    """
    # return teams.sort(key=lambda x: x.getUefaPos(), reverse=False)
    return sorted(teams, key=lambda x: x.getUefaPos())


@util.timer
def Test(*args, **kwargs):
    # test sort_by_ratings
    teams_unsorted = [Team(1), Team(15), Team(20), Team(2)]
    teams_sorted = sort_by_ratings(teams_unsorted)
    assert (teams_sorted == [teams_unsorted[ind] for ind in (0,3,1,2)]), "test sort_by_ratings fails!"

    # TEST CUP CLASS
    if "ids" in kwargs:
        for id in  kwargs["ids"]:
            tstcp = UEFA_Champions_League(name=id)

# TEST
if __name__ == "__main__":
    Test(ids = UEFA_TOURNAMENTS_ID)
    # print v.get_schema(UEFA_CL_TYPE_ID)




