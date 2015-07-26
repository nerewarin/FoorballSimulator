# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'
# import Team, Match, Leagues
import os

# VERSION = "v1.1"
with open(os.path.join("", 'VERSION')) as version_file:
    VALUES_VERSION = version_file.read().strip()

# to store in tournament types names and get in every tournament class name as parameter
UEFA_CL_TYPE_ID = 1
UEFA_EL_TYPE_ID = 2
LEAGUE_TYPE_ID = 3
CUP_TYPE_ID = 4
UEFA_TOURNAMENTS_ID = (UEFA_CL_TYPE_ID, UEFA_EL_TYPE_ID)

TEST_TOURNAMENT_ID = "testTournament"
TEST_LEAGUE_ID = 10 # RUS League
TEST_CUP_ID = 62 # RUS Cup

EUROPEAN_LEAGUES_AND_CUPS = [
    # http://www.uefa.com/memberassociations/leaguesandcups/
    "English Premier League",
    "French Ligue 1",
    "German Bundesliga",
    "Spanish Liga",
    "Romanian First Division",
    "Russian Premier League",
    "Dutch First Division",
    "Ukrainian Premier League",
    "Portuguese First Division",
    "Italian Serie A",
    "Swedish First Division",
    "Swiss Super League",
    "Danish Super League",
    "Croatian First League",
    "Hungarian First League",
    "Welsh Premier League",
    "Finnish First Division",
    "Belgian First League",
    "Georgian Premier League",
    "Belarusian Premier League", # ok
    "Greek Super League",
    "Austrian Bundesliga",
    "Kazakh Premier League",
    "Albanian Super League",
    "Norwegian Premier Division",
    "Serbian Super League",
    "Moldovan First Division", # MDA
    "Israeli Premier League", #28 (30)
    "Icelandic Premier League",
    "Scottish Premiership",
    "Polish First Division",
    "Bulgarian A League",
    "Slovene First League",
    "Slovak First League",
    "Lithuanian First Division",
    "Irish Premier Division",
    "Montenegrin First League",
    "Turkish Super League",
    "Azerbaijani Premier League",
    "Macedonian First League", # 40
    "Cypriot First Division",
    "San Marinese Championship",
    "Estonian First League",
    "Luxembourger First Division",
    "Faroese Premier Division",
    "Latvian First Division",
    "Northern Irish Premiership",
    "Armenian Premier League",
    "Czech First League",
    "Bosnian-Herzegovinian Premier League",
    "Maltese Premier League",
    "Andorran Premier Division",
    "Liechtenstein Super League",   # INTEGRATION TO SWISS WAS NOT REALIZED
    "Gibraltarian Premier League"
]
# print len(EUROPEAN_LEAGUES_AND_CUPS)+2, "\n"


class Coefficients():
    """
    defines coefficients to calculate rating changes after matches
    MAIN FUNC - getRatingUpdateCoefs
                # mode = "Favorite" (home)
                self.FHW - favorite home win
                self.OGL = outsider guest lose
                self.FHL = favorite home lose
                self.OGW = outsider guest win
                self.FHT = favorite home tie (draw)
                self.OGT = outsider guest tie (draw)

                # mode = "Outsider" (home)
                self.OHW = outsider home win
                self.FGL = favorite guest lose
                self.OHL = outsider home lose
                self.FGW = favorite guest win
                self.OHT = outsider home tie (draw)
                self.FGT = favorite guest tie (draw)
    """
    def __init__(self, version):
        # self.version = version
        if version[1] == "1": #"v1.x"

            self.scaler = 0.01 # to scale to rating UEFA format

            if version[3] == "0": # "v1.0"
                # v1.0 original coefficients from 2004 paper game
                self.FHW = +1
                self.OGL = -1
                self.FHL = -3
                self.OGW = +3
                self.FHT = -1
                self.OGT = +1

                self.OHW = +3
                self.FGL = -3
                self.OHL = -1
                self.FGW = +1
                self.OHT = +1
                self.FGT = -1

            elif version[3] == "1": # "v1.1"
                # v1.1 modified coefficients - increased cost of tie for outsider as a guest
                self.FHW = +1
                self.OGL = -1
                self.FHL = -3
                self.OGW = +3
                self.FHT = -2 # powered
                self.OGT = +2 # powered

                self.OHW = +3
                self.FGL = -3
                self.OHL = -1
                self.FGW = +1
                self.OHT = +1
                self.FGT = -1
            else:
                raise ValueError, "unknown subversion %s of %s" % (version[3], version)
        else:
            raise ValueError, "unknown version %s of %s" % (version[1], version)

        # choose dictionary to store coefs
        self.coefs = {}

        # self.coefs[FHW] =
        # print type(self.__dict__.keys())
        instance_variables  = self.__dict__.keys()
        for ind in range(len(instance_variables) - 1): # собрать все коэффициенты из переменных класса,
        # кроме последней переменной - self.coefs - самого словаря, куда собираем переменные.
        # дабы не собирать словарь в себя же, ура рекурсивному словарю  :-)
            # print type(instance_variable)
            self.coefs[instance_variables[ind]] = getattr(self, instance_variables[ind]) * self.scaler
        # for key,val in self.coefs.items():
        #     print key,val
        #     pass
        # print "\n--end--\n"

    def getRatingUpdateCoefs(self, type = "dict"):
        """

        :return: dictionary of coefs (see above)
        """
        if type == "dict":
            return self.coefs
        elif type == "list":
            return [coef * self.scaler for coef in [self.FHW,
                                                    self.OGL,
                                                    self.FHL,
                                                    self.OGW,
                                                    self.FHT,
                                                    self.OGT,

                                                    self.OHW,
                                                    self.FGL,
                                                    self.OHL,
                                                    self.FGW,
                                                    self.OHT,
                                                    self.FGT]
                    ]
        else:
            print "unknown type %s for getRatingUpdateCoefs return data type" % type

    def check(self, version):
        """
        evaluates
        :return:
        """
        # homeRatingKoefs  = [(FHW, OGL), (FHL, OGW), (FHT, OGT)]
        # guestRatingKoefs = [(OHW, FGL), (OHL, FGW), (OHT, FGT)]
        homeRatingKoefs  = [(self.FHW, self.OGL), (self.FHL, self.OGW), (self.FHT, self.OGT)]
        guestRatingKoefs = [(self.OHW, self.FGL), (self.OHL, self.FGW), (self.OHT, self.FGT)]


        procents = 100

        # chancesHomeFavorite
        CHF =  [83.35688, 8.32132, 8.32180] #  % (в процентах)
        assert sum(CHF) == 100, "invalid sum of CHF chances"
        # chancesGuestFavorite
        CGF  =  [27.74954, 55.58041, 16.67005]
        assert sum(CGF) == 100, "invalid sum of CGF chances"

        # CHAOS COEFFICIENTS FOR UPDATE RATING
        # (определяют, как изменится рейтинг команд в зависимости от результата матча)

        # FHW - favorite home win
        # FHW - outsider guest lose
        # print "manualFH", (83.35688 * 1 +  8.32132 * -3 + 8.32180 * -1)/100
        # print "manualFG", (27.74954 * -3 +  55.58041 * +1 + 16.67005 * -1)/100
        # FavoriteHomeDelta of Rating
        FHD = 0
        OGD = 0
        for ind, chance in enumerate(CHF):
            # print homeRatingKoefs[ind]
            FHD += chance * homeRatingKoefs[ind][0]
            OGD += chance * homeRatingKoefs[ind][1]
        OHD = 0
        FGD = 0
        for ind, chance in enumerate(CGF):
            # print homeRatingKoefs[ind]
            OHD += chance * guestRatingKoefs[ind][0]
            # print "chance * homeRatingKoefs[ind][1]", chance, guestRatingKoefs[ind][1]
            FGD += chance * guestRatingKoefs[ind][1]
        # fist is always home
        # print FHD, OGD
        # print OHD, FGD
        # а столько в среднем падает рейтинг у фаворита за один матч

        divergenceFHD =  ( FHD) / procents
        divergenceFGD =  ( FGD ) / procents
        divergenceF =  ( FGD + FHD) / procents

        divergenceOHD =  ( OHD) / procents
        divergenceOGD =  ( OGD ) / procents
        divergenceO =  ( OGD + OHD) / procents

        divs = [divergenceFHD, divergenceFGD, divergenceF, divergenceOHD, divergenceOGD, divergenceO]
        # print divs

        # закон сохранения рейтинга
        # assert divs[2] + divs[5] == 0, "version %s violates the Law of Ranking Conservation" % self.version
        assert divs[2] + divs[5] == 0, "version %s violates the Law of Ranking Conservation" % version

        # закон Энтропии: лидерство не может длиться вечно, для этого divergenceF должен быть отрицательным,
        # обеспечивая тенденцию потери мотивации всяким лидером и как следствие медленным снижением рейтинга
        # if float(self.version[1:]) > 1.0:
        if float(version[1:]) > 1.0:
            # assert divs[2] < 0, "version %s violates the Law of Entropy" % self.version
            assert divs[2] < 0, "version %s violates the Law of Entropy" % version

        # Закон Стабильности сдерживает Энтропию по времени, чтобы лидер терял позиций слишком быстро!
        # assert divs[2] > -0.026, "version %s violates the Law of Stability" % self.version
        assert divs[2] > -0.026, "version %s violates the Law of Stability" % version
        # assert divs[2] > 0, "violate the law of entropy"
        # v1 original
        #[0.5007112, -0.44338260000000007, 0.05732860000000002, 0.44338260000000007, -0.5007112, -0.05732860000000002]
        # главные числа - общая дельта рейтинга фаворита за игру дома+в гостях + 0.05732860000000002
        # нуждо создать условия для догоняющих, чтобы их рейтинг в среднем за игру с фаворитом - рос. они ведь учаться у крутых)
        return divs

# class Tournament_Schemas():
#     """
#     define schemas of all types of tournaments:
#     """
#     def __init__(self):
#         self.sch = {
#             "UEFA_Euro_L" :
#             "UEFA_Champ_L"
#         }

def TournamentSchemas(tournament_id):
    """
    defines how to collect members of UEFA tournaments

    for example
    UEFA_CL = { stage : { tourn_type, pair_mode, list of
    {round of stage : {country_indexes or "CL": pos_of_league_result if int, or "cup winner" or if "CL" round from CL

    to print match, round should include stage+round of stage
    """
    # if tournament_id == UEFA_CL_TYPE_ID:
    raise NotImplementedError

UEFA_CL_SCHEMA = [
            # stage
            {"Qualification" : {
                    # type of tournament and number of sub-tournaments of this type in this stage
                    "classname" : "Cup",
                    "parts" : 1,
                    # 0 - one match in pair, 1 - home & guest but the final , 2 - always home & guest
                    "pair_mode" : 2,
                    # every tour is a row of dict {round tournament : dict{(country indexes)* : team pos of national league**}}
                    # is tuple of int, from country, is stings and == "CL", from
                    # * - if int, pos, if string and == "cupwinner" - so its winner from national cups,

                    "tindx_in_round" : {
                       # 1 round
                       # 6 champions of leagues 49-54
                       1 : {tuple(range(49,55,1)) : 1},
                       # 2 round
                       # 31 champions of leagues 17-48 and 3 winners of prev round # TODO exclude Lichtenstein
                       2 : {tuple(range(17,49,1)) : 1},
                       # 3 round
                       # 3 champions of 14-16, 9 silver of 7-15, 1 bronze of 6 and 17 winners of prev
                       3 : {tuple(range(14,17)) : 1, tuple(range(7,16)) : 2, (6,) : 3},
                       # final of Play-Off round
                       # 2 bronze 4-5, 3 fourth of 1-3, and 15 winners of prev
                       4 : {(4,5) : 3, (1,2,3) : 4}
                    }
                }
            },

            {"Group" : {
                    "classname" : "League",
                    # split members to 8 groups
                    "parts" : 8,
                    "pair_mode" : 2,
                    "tindx_in_round" : {
                        # 13 champions of 1-13, 6 silver 1-6, 3 bronze 1-3   and 10 winners of qualification
                        # no tournament or None -named round (cause its exclusive)
                        1 : {tuple(range(1,14,1)) : 1, tuple(range(1,7,1)) : 2, tuple(range(1,4,1)) : 3 }}
                }
            },

            {"Play-Off" : {
                    "classname" : "Cup",
                    "parts" : 1,
                    "pair_mode" : 1, # one match in final
                    "tindx_in_round" : {1 : {}}
                        # simple cup of 16 winners of groups
                }
            }
        ]

    # elif tournament_id == UEFA_EL_TYPE_ID:
        # 195 members (48 members in groups)
        # return
UEFA_EL_SCHEMA = [
            # stage
            {"Qualification" : {
                    # type of tournament and number of sub-tournaments of this type in this stage
                    "classname" : "Cup",
                    "parts" : 1,
                    # 0 - one match in pair, 1 - home & guest but the final , 2 - always home & guest
                    "pair_mode" : 2,
                    # every tour is a row of dict {round tournament : dict{country ind : team pos of national league}}
                    "tindx_in_round" : {
                        # 1 round
                        # 20 cup winners 35-54, 26 silver of 27-53 # TODO exclude Lichtenstein or not when teams already parsed
                        # 29 bronze 22-51, 3 "FairPlay"
                        # TODO instead of Fairplay we can just get next -rated teams
                        1 : {tuple(range(35,55)) : "cupwinner",  tuple(range(27,53)) : 2, tuple(range(22,52)) : 3, (0,1,2) : "FairPlay"},
                        # 2 round
                         # 15 cup winners 20-34, 11 silver 16-26, 6 bronze 16-21, 6 fourth 10-15, 3 fifth 7-9,
                         # and 38 winners of prev
                        2 : {tuple(range(20,35)) : "cupwinner",  tuple(range(16,27)) : 2, tuple(range(16,22)) : 3,
                               tuple(range(10,16)) : 4,  tuple(range(7,10)) : 3},
                        # 3 round
                         # 3 cup winners 17-19, 6 bronze 10-15, 3 fourth 7-9, 3 fifth 4-6, 3 sixth 1-3,
                        # # TODO if sixth from ENG of FRANCE, use cup winners of special national "League Cup"
                         # and 38 winners of prev
                        3 : {tuple(range(17,20)) : "cupwinner",  tuple(range(10,16)) : 3, tuple(range(7,10)) : 4,
                               tuple(range(4,7)) : 5,  tuple(range(1,4)) : 6}, # or league cup see todo above
                        # Play-Off round
                         # 9 cup winners 8-16, 3 bronze 7-9, 3 fourth 4-6, 3 fifth 1-3,
                         # 15 from 3th qualification round of champions league
                         # and 38 winners of prev
                        4 : {tuple(range(8,17)) : "cupwinner",  tuple(range(7,10)) : 3, tuple(range(4,7)) : 4,
                               tuple(range(1,4)) : 5,   "CL" : 3}
                        # TODO groupUefa support
                        }
            }
            },

            {"Group" : {
                    "classname" : "League",
                    # split members to 12 groups
                    "parts" : 12,
                    "pair_mode" : 2,
                    "tindx_in_round" : {
                        # champion of prev Europe League
                        #  TODO implement shifting rest teams if champion was already qualified to CL or EL
                        # else:
                        # 7 cup winners
                        # 10 from 4th qualification round of champions league
                        # and 31 winners of prev (Qualification)
                        1 : {tuple(range(1,8)) : "cupwinner", "CL" : "Qualification 4"}}

                    }
            },

            {"Play-Off" : {
                    "classname" : "Cup",
                    "parts" : 1,
                    "pair_mode" : 1, # one match in final
                    "tindx_in_round" : {
                        # simple cup of
                        # 24 winners of prev
                        # 8 from Group round of champions league (3th places)
                        1 : {"CL" : "Group"}}

                        }
            }
        ]



# def get_CL_schema():
#     """
#
#     :return: schema of UEFA Champions League Tournament
#     """
#     return TournamentSchemas(UEFA_CL_TYPE_ID)
#
#
# def get_EL_schema():
#     """
#
#     :return: schema of UEFA Champions League Tournament
#     """
#     return TournamentSchemas(UEFA_EL_TYPE_ID)
#
# def get_schema(type_ID):
#     return TournamentSchemas(type_ID)

if __name__ == "__main__":
    def TestCoefficients():
        print "Test Values (coefficients to compute ratings)"
        test_versions = ["v1.0", "v1.1"]
        print                               {tuple(range(49,55,1))  : 0}
                                       # champions of leagues 17-48
        print                               {tuple(range(17,49,1))  : 0}, len(tuple(range(17,49,1)) )
        for version in test_versions:
            test_Coef = Coefficients(version)
            test_Coef.check(version)
            print version
            print test_Coef.getRatingUpdateCoefs()
            print test_Coef.check(version)

    def Test_Tournament_schemas():
        print "Test Tournament Schemas"
        # CL_sch =  get_CL_schema()
        # EL_sch =  get_EL_schema()
        for schema in (UEFA_CL_SCHEMA, UEFA_EL_SCHEMA):
            print "\n"
            for stage in schema:
                # print stage
                for stage_name, stageV in stage.iteritems():
                    print stage_name
                    # print stage_name, stageV
                    for attrK, attrV in stageV.iteritems():
                        if isinstance(attrV, list):
                            print attrK, "... (contains external members, not added from previous round"
                            for round in attrV:
                                # pass
                                for roundname, members_schema in round.iteritems():
                                    print "round = %s" % roundname#, members_schema
                                    for members_source, pos in members_schema.iteritems():
                                        print members_source, pos

                                # print round
                                # for where, pos in round:
                                #     print where, pos
                                # # print roundname #, roundmembers
                        else:
                            print attrK, attrV
                # stage_name = CL_schema[]
            # for stage_name, stageV in CL_schema.iteritems():
            #     print stageK, stageV
            # print schems.get_EL_schema()


    # TestCoefficients()
    Test_Tournament_schemas()