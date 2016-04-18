#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
from bs4 import BeautifulSoup
from main import main
import glob
import pandas


def get_data():
    url = "http://gcis.nat.gov.tw/moeadsBF/bms/report.jsp?method=first&agencyCode=allbf&showGcisLocation=true&showBusi=true&showFact=false"

    webfile = urllib.urlopen(url)
    webcontext = webfile.read()
    soup = BeautifulSoup(webcontext, "html.parser")
    lis = soup.findAll("td", attrs={"class": "normal"})

    for li in lis:
        test = li.find("a")
        url = test["href"]
        if "bmsItem" in url and "setup" in url:
            real_url = "http://gcis.nat.gov.tw/moeadsBF" + url[2:]
            print real_url
            urllib.urlretrieve(real_url, real_url.split("=")[-1])


def run():
    get_data()
    for _pdf_name in glob.glob("3*.pdf"):
        main(_pdf_name)


def merge_csv():
    result = pandas.DataFrame([])
    for _csv_name in glob.glob("3*.pdf.csv"):
        result = result.append(pandas.read_csv(_csv_name))

    result.to_csv("%s.csv" % "all", encoding="utf8", index=False)

# run()
merge_csv()
