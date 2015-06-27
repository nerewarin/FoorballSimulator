# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'
# import Team, Match, Leagues

class Coefficients():
    """
    defines coefficients to calculate rating changes after matches
    MAIN FUNC - getRatingUpdateCoefs
                # mode = "Favorite" (home)
                self.FHW - favorite home win
                self.OGL = outsider guest lose
                self.FHL = favorite home lose
                self.OGW = outsider guest win
                self.FHT = favorite home tie
                self.OGT = outsider guest tie

                # mode = "Outsider" (home)
                self.OHW = outsider home win
                self.FGL = favorite guest lose
                self.OHL = outsider home lose
                self.FGW = favorite guest win
                self.OHT = outsider home tie
                self.FGT = favorite guest tie
    """
    def __init__(self, version):
        # self.version = version
        if version[1] == "1": #"v1.x"
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
        self.scaler = 0.001 # to scale to rating UEFA format
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
        assert divs[2] > -0.026, "version %s violates the Law of Stability" % self.version
        # assert divs[2] > 0, "violate the law of entropy"
        # v1 original
        #[0.5007112, -0.44338260000000007, 0.05732860000000002, 0.44338260000000007, -0.5007112, -0.05732860000000002]
        # главные числа - общая дельта рейтинга фаворита за игру дома+в гостях + 0.05732860000000002
        # нуждо создать условия для догоняющих, ятобы их рейтинг в среднем за игру с фаворитом - рос. они ведь учаться у крутых)
        return divs

if __name__ == "__main__":
    print "Test Values (coefficients to compute ratings)"
    test_versions = ["v1.0", "v1.1"]
    for version in test_versions:
        test_Coef = Coefficients(version)
        test_Coef.check(version)
        print version
        print test_Coef.getRatingUpdateCoefs()
        print test_Coef.check(version)