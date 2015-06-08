__author__ = '130315'
# -*- coding: utf-8 -*-

# from lxml import etree as ET
# import xml.dom.minidom as ET
# import json, os, time#, sys
# from HTMLParser import HTMLParser
import operator

# http://habrahabr.ru/post/220125/
# import lxml
from lxml import html as html
# import lxml.html as html
# from pandas import DataFrame

class Team():
    """
    represents team
    """
    def __init__(self, name, country, rating, ruName):
        self.name = name
        self.country = country
        self.rating = rating
        self.ruName = ruName

    def getName(self):
        return self.name

    def getCountry(self):
        return self.country

    def getRating(self):
        return self.rating

    def getRuName(self):
        return self.ruName

    def setRating(self, rating):
        self.rating = rating

Spartak = Team("Spartak Moscow", "RUS", 1, "Спартак Москва")
teams = {}
# print "ok"

def parseXML(link):
    xml_tree = ET.parse(link)
    root = xml_tree.getroot()
    print type(root)
    for child in root:
        print child

        # barter_obt_item_lst = [int(barter_obtain_item.text) for barter_obtain_item in child.iter(interested_tag)]
        # if request_id in barter_obt_item_lst:
        #     answer_ways_count += 1
        #     answer += str(answer_ways_count) + message + str(child.tag) + "\n"

# print dir(ET)
UEFA_club_ratingRU = "http://ru.uefa.com/memberassociations/uefarankings/club/"
UEFA_club_ratingEN = "http://www.uefa.com/memberassociations/uefarankings/club/season=2015/index.html"


def unicode_to_str(string):
    """
    helper function to convert unicode to string.
    :param unicode: unicode
    :return: string
    """
    try:
        string.encode('utf8')
    except AttributeError:
        # print "type of entry of func <unicode_to_str> is not unicode! "
        answer = str(string)
    else:
        answer = string.encode('utf8')
    return answer

# print type(site.xpath("//table[@id=\"clubrank\"]/tbody/tr")), site.xpath("//table[@id=\"clubrank\"]/tbody/tr")
# HTML parse
UEFAsiteEN = html.parse(UEFA_club_ratingEN)
UEFAsiteRU = html.parse(UEFA_club_ratingRU)
rows_xpathEN = UEFAsiteEN.xpath("//table[@id=\"clubrank\"]/tbody/tr")
rows_xpathRU = UEFAsiteRU.xpath("//table[@id=\"clubrank\"]/tbody/tr")
print "teams count =", len(rows_xpathEN)
team_xpath1 = "td[1]/span[3]/a"
team_xpath2 = "td[1]/span[3]/span[2]"
country_xpath = "td[2]"
UEFArating_xpath = "td[8]"
# print rows_xpathRU[0].xpath(team_xpath1).pop().text_content()
for i, tr in enumerate(rows_xpathEN):
    # print i
    try:
        teamName = tr.xpath(team_xpath1).pop().text_content()
    except IndexError: # special for Betis
        teamName = tr.xpath(team_xpath2).pop().text_content()
    try:
        ruName   = rows_xpathRU[i].xpath(team_xpath1).pop().text_content()
    except IndexError: # special for Betis
        ruName   = rows_xpathRU[i].xpath(team_xpath2).pop().text_content()
    country = tr.xpath(country_xpath).pop().text_content()
    UEFArating   = tr.xpath( UEFArating_xpath ).pop().text_content()

        # if site = UEFA_club_ratingEN
        # print str(i + 1) + ". " + unicode_to_str(team) + " " + country + " " + unicode_to_str(score)
    # print str(i + 1) + ". " + teamName + " " + country + " " + UEFArating

    # create teams
    teams[teamName] = Team(teamName, country, UEFArating, ruName)

sorted_x = sorted(teams.items(), key=operator.itemgetter(1))
for i, (team, val) in enumerate(sorted_x):
    print str(i+1) + ".", team + " (" + val.getRuName() + ")" , val.getCountry(), val.getRating()

# for key, value in teams.iteritems():
#     print key, value.getCountry(), value.getRating()

# // = найти все элементы
# table - типа таблица
# обладающим атрибутом id = clubrank
# / взять его наследника
# типа tbody
# /tr - взять наследника tr (вложенный элемент)
# /td - первая колонка
# span - хуйня чтоб раскраситься html - там лежат три элемента разных, значек и т.д. имя команды - в третьем
# a - текст является ссылкой





# print td.pop()['class]']#.keys()
# короче для твоей цели нужен tree.xpath
# [15:08:57] Артем Александрович Воробьев: xpath
# [15:09:14] Артем Александрович Воробьев: тебе и в браузере вернут XPath путь
# [15:09:23] Артем Александрович Воробьев: и lxml нужно его использовать
