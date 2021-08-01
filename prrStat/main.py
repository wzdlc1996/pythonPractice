import numpy as np
import matplotlib.pyplot as plt
import json
import re


def parseYear(paper):
    info = paper["pubInfo"]
    mat = re.match(r".*\(([0-9]*?)\).*", info)
    if mat:
        year = int(mat.group(1))
    else:
        year = -1
    return year


def getByYears(papers, years):
    return [x for x in papers if parseYear(x) in years]


def getCitingNumByYears(paper, years):
    return len([x for x in paper["cited-by"] if parseYear(x) in years])


class dataInterface:
    def __init__(self):
        with open("./prr_pubs_full", "r") as f:
            self.body = json.load(f)

    def __getitem__(self, k):
        return self.body[k]

    def __len__(self):
        return len(self.body)

    def getPapersByYears(self, years):
        return getByYears(self.body, years)


if __name__ == "__main__":
    dat = dataInterface()
    publishedInPastTwoYears = dat.getPapersByYears([2020, 2019])
    citedInThisYear = []
    for x in publishedInPastTwoYears:
        citedInThisYear.append(getCitingNumByYears(x, [2021]))
    print("Predicted Impact Factor in 2021(up to now) is: %.3f" % (sum(citedInThisYear) / len(publishedInPastTwoYears)))
