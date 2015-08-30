# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'NereWARin'

"""
HTML parse
"""

import Team
from lxml import html as html # http://habrahabr.ru/post/220125/
import util
import urllib, sys, os

EMBLEMS_STORAGE_FOLDER = "resourses/images/team_emblems/"

def createTeamsFromHTML(season = "2014/2015", mode = "creating"):
    """
    parses UEFA site, stores all data to list of Team object (every object stores tournament, rating, country, uefa_pos)
    :param mode:
    :return:
    """

    if season == "actual":
        UEFA_club_ratingRU = "http://ru.uefa.com/memberassociations/uefarankings/club/"
        UEFA_club_ratingEN = "http://www.uefa.com/memberassociations/uefarankings/club/"

    elif "20" in season:
        last_year = season.split("/")[1]
        UEFA_club_ratingRU = "http://ru.uefa.com/memberassociations/uefarankings/club/season=%s/index.html" % last_year
        UEFA_club_ratingEN = "http://www.uefa.com/memberassociations/uefarankings/club/season=%s/index.html" % last_year
        # for example if season = "2014/2015"
        # UEFA_club_ratingRU = "http://ru.uefa.com/memberassociations/uefarankings/club/season=2015/index.html"
        # UEFA_club_ratingEN = "http://www.uefa.com/memberassociations/uefarankings/club/season=2015/index.html"


    else:
        raise Exception, "season must contains \"20\" like \"2014/2015\" or be \"actual\""

    UEFAsiteEN = html.parse(UEFA_club_ratingEN)
    UEFAsiteRU = html.parse(UEFA_club_ratingRU)
    rows_xpathEN = UEFAsiteEN.xpath("//table[@id=\"clubrank\"]/tbody/tr")
    rows_xpathRU = UEFAsiteRU.xpath("//table[@id=\"clubrank\"]/tbody/tr")
    teams_count = len(rows_xpathEN)
    if mode == "get count":
        return teams_count
    UEFApos_xpath = "td[1]/span[1]"
    team_xpath1 = "td[1]/span[3]/a"
    team_xpath2 = "td[1]/span[3]/span[2]"
    country_xpath = "td[2]"
    UEFArating_xpath = "td[8]"
    td_last_rating = 7 # "td[7]"
    team_emblem_xpath1 = "td[1]/span[3]/span/a/img/@src"
    team_emblem_xpath2 = "td[1]/span[3]/span[1]/img/@src"

    # MAKE DICT OF TEAMS (teamsD)
    teamsD = {}
    teamsL = []

    print "parsing UEFA site"

    for i, tr in enumerate(rows_xpathEN):
        # print i
        try:
            teamName = tr.xpath(team_xpath1).pop().text_content()
            team_emblem_src   = tr.xpath( team_emblem_xpath1 ).pop()
        except IndexError: # special for Betis - is has special format on UEFA site
            teamName = tr.xpath(team_xpath2).pop().text_content()
            team_emblem_src   = tr.xpath( team_emblem_xpath2 ).pop()
        # fix error from site
        if teamName == "1. FSV Mainz 05": teamName = "FSV Mainz 05"
        try:
            ruName   = rows_xpathRU[i].xpath(team_xpath1).pop().text_content()
        except IndexError: # special for Betis
            ruName   = rows_xpathRU[i].xpath(team_xpath2).pop().text_content()

        teamName = teamName.replace("/", "-") # "/" is unsupported symbol for filename in windows
        country = tr.xpath(country_xpath).pop().text_content()
        UEFArating = float(tr.xpath( UEFArating_xpath ).pop().text_content())
        UEFAposition = int(tr.xpath( UEFApos_xpath ).pop().text_content())
        # list of team ratings for last 5 seasons
        UEFAratings   = [float(tr.xpath( "td[%s]" % (td_last_rating - ind) ).pop().text_content()) for ind in range(5)]

        # check sum is actual
        tolerance = 0.1
        assert (UEFArating - tolerance) < sum(UEFAratings) or (UEFArating + tolerance) > sum(UEFAratings), \
            "unequal sum of ratings of last 5 year and actual rating!"


        # save image to disc
        im_filename = util.unicode_to_str(teamName) + ".png"

        if not os.path.isfile(EMBLEMS_STORAGE_FOLDER + im_filename):
            print "image didn't found, creating..."
            print i, im_filename, team_emblem_src
            urllib.urlretrieve(team_emblem_src, EMBLEMS_STORAGE_FOLDER + im_filename)

        else:
            pass
            # print "images found"

            # if site = UEFA_club_ratingEN
            # print str(i + 1) + ". " + unicode_to_str(team) + " " + country + " " + unicode_to_str(score)
        # print str(i + 1) + ". " + teamName + " " + country + " " + UEFArating

        # create teams
        country_ID = None
        # print "UEFArating", UEFArating, type(UEFArating)
        teamObj = Team.Team(0, teamName, country, UEFArating, ruName, UEFAposition, country_ID)
        teamsD[teamName] = teamObj
        teamsL.append(teamObj)

    # # MAKE SORTED LIST OF TEAMS (teamsL)
    # teamsL = sorted(teamsD.items(), key=operator.itemgetter(1))
    # for i, (team, val) in enumerate(teamsL):
    #     # print str(i+1) + ".", team + " (" + val.getRuName() + ")" , val.getCountry(), val.getRating()
    #     pass

    # teamsL = sorted(teamsD.values(), key=operator.getitem())
    return teamsL

def printParsedTable(teamsL):
    for i, team in enumerate(teamsL):
        print str(i+1) + ".", util.unicode_to_str(team.getName()), "(" + team.getRuName() + ")" , team.getCountry(), team.getRating()


def parse_domesticleague_results(country_ABV):
    """
    - IT CANNOT WORKS CAUSE matches_played XPATH IS DIFFERENT FOR ANY COUNTRY

    - CALL IT ONLY IN OFF-SEASON LIKE JUNE!

    parse UEFA site to get list of teams sorted by current position
    http://www.uefa.com/memberassociations/association=ned/domesticleague/index.html
    :country_ABV: country abbreviation like RUS
    :return:
    """
    basic_site = "http://www.uefa.com/memberassociations/association=%s/domesticleague/index.html" % country_ABV
    try:
        l_site = html.parse(basic_site)
        # current matches played in off site by first team
        matches_played = l_site.xpath("//*[@id=\"memberassociations\"]/div[2]/div[3]/div/div[2]/div[1]/div/div/"
                                         "div[2]/div[1]/table/tbody/tr[1]/td[5]").pop().text_content()
                                       # //*[@id=\"memberassociations\"]/div[2]/div[3]/div/div[2]/div[1]/div/div/" \
                                       #          "div[2]/div[1]/table/tbody/tr[1]/td[3]/a
        print "matches_played", matches_played
        if matches_played < 10:
            # not use data from just started league
            return
        # else return all teams sorted by position
        teamnames = []
        pos = 1
        while True:
            try:
                teamname = l_site.xpath("//*[@id=\"memberassociations\"]/div[2]/div[3]/div/div[2]/div[1]/div/div/"
                                        "div[2]/div[1]/table/tbody/tr[%s]/td[3]/a" % pos ).pop().text_content()
                teamnames.append(teamname)
                pos += 1
            except:
                return teamnames
        # //*[@id="memberassociations"]/div[2]/div[3]/div/div[2]/div[1]/div/div/div[2]/div[1]/table/tbody/tr[1]/td[3]/a
        # //*[@id="memberassociations"]/div[2]/div[3]/div/div[2]/div[1]/div/div/div[2]/div[1]/table/tbody/tr[18]/td[3]/a


    except:
        return None

# for key, value in teams.iteritems():
#     print key, value.getCountry(), value.getRating()

# // = найти все элементы
# table - типа таблица
# обладающим атрибутом id = clubrank
# / взять его наследника
# типа tbody
# /tr - взять наследника tr (вложенный элемент)
# /td - первая колонка
# span - штука нужная чтоб раскраситься html - там лежат три разных элемента, значек и т.д. имя команды - в третьем
# a - текст является ссылкой


# короче для твоей цели нужен tree.xpath
# [15:08:57] Артем Александрович Воробьев: xpath
# [15:09:14] Артем Александрович Воробьев: тебе и в браузере вернут XPath путь
# [15:09:23] Артем Александрович Воробьев: и lxml нужно его использовать

# как получить xpath:
# в браузере жмем F12
# выбираем лупу, жмем на объект который хотим
# нас редиректят в правое окно, жмем правой кнопкой мыши - Copy xpath. Можно вставлять

# TODO
# TEST SECTION

if __name__ == "__main__":
    @util.timer
    def Test(*args, **kwargs):
        createTeamsFromHTML()

    Test()