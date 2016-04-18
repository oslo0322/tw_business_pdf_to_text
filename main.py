# -*- coding: utf-8 -*-
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.layout import LTContainer
from pdfminer.layout import LTText
from pdfminer.layout import LTTextBox

import sys
import pandas
import re
import json
import os

from group_data import get_model_result


NEED_BUSSINESS_ID = ["F501060", "F501030", "F501990", "F501050", "F203020", "C104020"]


class My(TextConverter):
    word = ""
    group = []
    word_pos_info = {}

    def receive_layout(self, ltpage):
        def render(item):
            if isinstance(item, LTContainer):
                for child in item:
                    render(child)
            elif isinstance(item, LTText):
                if self.word == "":
                    if "x0" in dir(item):
                        self.word_pos_info = {"x0": item.x0, "y1": item.y0}
                if item.get_text() == " ":
                    self.word_pos_info.update({"content": self.word.strip()})
                    self.group.append(self.word_pos_info.copy())
                    self.word_pos_info = {}
                    self.word = ""
                else:
                    self.word += item.get_text()

            if isinstance(item, LTTextBox):
                # self.word_pos_info.update({"x1":item.x1})
                self.word_pos_info.update({"content": self.word.strip()})
                self.group.append(self.word_pos_info.copy())
                self.word_pos_info = {}
                self.word = ""
        render(ltpage)
        return


def find_match_string(string):
    pattern = re.compile(r"(?P<id>[A-Z0-9]{7})", flags=re.MULTILINE)
    try:
        for match in pattern.finditer(string):
            if match.groupdict()["id"] in NEED_BUSSINESS_ID:
                return True
    except:
        return False
    return False


def read_pdf_data(filename):
    fp = open(filename, 'rb')

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    laparams.line_margin = 0.01
    device = My(rsrcmgr, sys.stdout, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    result_data = []
    count = 0
    for page in PDFPage.get_pages(fp, set()):
        # if count == 7:
        interpreter.process_page(page)
        result_data.append(device.group)
        device.word = ""
        device.group = []
        device.word_pos_info = {}
        count += 1
    return result_data


def get_row_group(data, row_name):
    _temp = data[row_name].value_counts()
    group_list = _temp[_temp == 10].index.tolist()
    group_list.sort()
    group_list.insert(0, 0)
    group_list.insert(len(group_list), group_list[-1] + 100)
    return group_list


def main(filename):
    model_data = get_model_result()

    pdf_data_list = read_pdf_data(filename)
    # if os.path.exists("cache.json") is True:
    #     with open("cache.json", "r") as f:
    #         pdf_data_list = json.loads(f.read())
    # else:
    #     pdf_data_list = read_pdf_data(filename)
    #     with open("cache.json", "w") as f:
    #         f.write(json.dumps(pdf_data_list))

    final_data = pandas.DataFrame()
    for pdf_single_data in pdf_data_list:
        pdf_data = pandas.DataFrame(pdf_single_data)
        pdf_data["column"] = -1
        pdf_data["row"] = -1

        group_list = get_row_group(pdf_data, "y1")
        y_group = pdf_data.groupby(pandas.cut(pdf_data["y1"], group_list))
        row_group_list = y_group.groups.values()

        for idx, row_group in enumerate(row_group_list):
            pdf_data.loc[row_group, "row"] = idx

        # predict 可以喂一串list，這邊可以在修正
        for idx in pdf_data.index:
            data_pos = pdf_data.ix[idx][["x0", "y1"]]
            result = model_data.predict([data_pos])[0]
            pdf_data.loc[idx, "column"] = result

        # 產生train的資料
        # pdf_data[["content", "x0", "y1", "column"]].sort(["column"]).to_csv("test.csv", encoding="utf8", index=False)

        pdf_data = pdf_data.drop(["x0", "y1"], axis=1)
        pdf_data["content"] = pdf_data["content"].map(lambda x: "%s" % x)
        gby_data = pdf_data.groupby(["row", "column"]).sum().unstack('column')
        gby_data.columns = range(gby_data.shape[1])
        gby_data.index = range(gby_data.shape[0])
        # gby_data = gby_data.dropna(0)
        gby_data = gby_data[(gby_data[0] != u"序號") & (gby_data[0] != 0)]
        gby_data["is_ok"] = gby_data[7].map(lambda x: find_match_string(x))
        final_data = final_data.append(gby_data)

    # final_data[0] = final_data[0].astype("int")
    final_data = final_data.sort([0])
    final_data = final_data.reset_index(drop=True)
    final_data.to_csv("%s.csv" % filename, encoding="utf8", index=False)
