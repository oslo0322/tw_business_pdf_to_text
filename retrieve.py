#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
from bs4 import BeautifulSoup
from main import main
import glob
import pandas


def get_data(is_compay=False):
    if is_compay is False:
        url = "http://gcis.nat.gov.tw/moeadsBF/bms/report.jsp?method=first&agencyCode=allbf&showGcisLocation=true&showBusi=true&showFact=false"
    else:
        url = "http://gcis.nat.gov.tw/pub/cmpy/reportCity.jsp"

    webfile = urllib.urlopen(url)
    webcontext = webfile.read()
    soup = BeautifulSoup(webcontext, "html.parser")
    lis = soup.findAll("td", attrs={"class": "normal"})

    for li in lis:
        test = li.find("a")
        url = test["href"]
        if "bmsItem" in url or "cmpyCityItem" in url:
            if "setup" in url:
                if is_compay is False:
                    real_url = "http://gcis.nat.gov.tw/moeadsBF" + url[2:]
                    print real_url
                    urllib.urlretrieve(real_url, real_url.split("=")[-1])
                else:
                    real_url = "http://gcis.nat.gov.tw/pub" + url[2:]
                    print real_url
                    urllib.urlretrieve(real_url, real_url.split("=")[-1])


def run(is_compay):
    get_data(is_compay)
    for _pdf_name in glob.glob("3*.pdf"):
        main(_pdf_name)


def merge_csv():
    result = pandas.DataFrame([])
    for _csv_name in glob.glob("3*.pdf.csv"):
        result = result.append(pandas.read_csv(_csv_name))

    result.to_csv("%s.csv" % "all", encoding="utf8", index=False)

run(is_compay=True)
# merge_csv()
