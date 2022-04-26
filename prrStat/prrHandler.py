import re
import requests as rq
import bs4
from datetime import datetime as dt


def idToURL(ident):
    return "https://journals.aps.org/prresearch/abstract/{}".format(ident)


def idToCitedURL(ident):
    return "https://journals.aps.org/prresearch/cited-by/{}".format(ident)


def getIssues():
    pass


def parsePubInfo(pub):
    try:
        res = " ".join([x.string for x in pub])
    except:
        res = ""
    return res

def parseString(item):
    try:
        res = item.string
    except:
        res = ""
    return res


def queryIssuePaperList(url):
    """
    :param url: the url of the issue
    :return lis: the identifier list of the published papers
    """
    page = bs4.BeautifulSoup(rq.get(url).content, features="lxml").find_all("div", class_="article")
    lis = []
    for z in page:
        if z["data-id"] not in lis:
            lis.append(z["data-id"])
    return lis


def queryCitingListPerPage(url):
    page = bs4.BeautifulSoup(rq.get(url).content, features="lxml").find_all("div", class_="citing")
    lis = []
    for z in page:
        title = parseString(z.find(class_="title"))
        autho = parseString(z.find(class_="authors"))
        pub = parsePubInfo(z.find(class_="pub-info"))
        lis.append({
            "title": title,
            "authors": autho,
            "pubInfo": pub
        })
    return lis


def queryCitingList(ident):
    lis = []
    page = 1
    while True:
        url = idToCitedURL(ident) + "?page={}".format(page)
        res = queryCitingListPerPage(url)
        if len(res) != 0:
            lis += res
        else:
            break
        page += 1
    return lis


def getPapers():
    base = "https://journals.aps.org/prresearch/subjects?page={}"
    pgNum = 1
    lis = []
    while True:
        temp = []
        url = base.format(pgNum)
        page = bs4.BeautifulSoup(rq.get(url).content, features="lxml").find_all("div", class_="article")
        for z in page:
            title = parseString(z.find(class_="title"))
            autho = parseString(z.find(class_="authors"))
            pub = parsePubInfo(z.find(class_="pub-info"))
            ind = z["data-id"]
            temp.append({
                "title": title,
                "authors": autho,
                "pubInfo": pub,
                "identifier": ind
            })
        if len(temp) == 0:
            break
        lis += temp
        if pgNum % 10 == 0:
            print("Page: {} done at {}".format(pgNum, dt.ctime(dt.now())))
        pgNum += 1
    return lis


if __name__ == "__main__":
    import json
    import os
    import progressbar as psb

    # Note here, if prr_pubs in current dir, it would not be updated
    if "prr_pubs" not in os.listdir():
        lis = getPapers()
        with open("./prr_pubs", "w") as f:
            json.dump(lis, f, indent="\t")
    else:
        with open("./prr_pubs", "r") as f:
            lis = json.load(f)

    for item in psb.progressbar(lis):
        citings = queryCitingList(item["identifier"])
        item["cited-by"] = citings
    with open("./prr_pubs_full", "w") as f:
        json.dump(lis, f, indent="\t")