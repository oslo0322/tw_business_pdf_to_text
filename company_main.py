# -*- coding: utf-8 -*-
import os
import re
import sys

import pandas
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.layout import LTContainer
from pdfminer.layout import LTText
from pdfminer.layout import LTTextBox
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
# from matplotlib import pyplot as plt

NEED_BUSINESS_ID = ["F501060", "F501030", "F501990", "F501050", "F203020", "C104020"]


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
                if item.get_text() == " ":  # 將空白也判斷成下一個句子
                    self.word_pos_info.update({"content": self.word.strip()})
                    self.group.append(self.word_pos_info.copy())
                    self.word_pos_info = {}
                    self.word = ""
                else:
                    self.word += item.get_text()

            if isinstance(item, LTTextBox):
                self.word_pos_info.update({"content": self.word.strip()})
                self.group.append(self.word_pos_info.copy())
                self.word_pos_info = {}
                self.word = ""
        render(ltpage)
        return

    def reset(self):
        self.word = ""
        self.group = []
        self.word_pos_info = {}


def find_match_string(string):
    pattern = re.compile(r"(?P<id>[A-Z0-9]{7})", flags=re.MULTILINE)
    # try:
    for match in pattern.finditer(string):
        if match.groupdict()["id"] in NEED_BUSINESS_ID:
            return True
    # except:
    #     return False
    return False


def read_pdf_data(filename):
    fp = open(filename, 'rb')

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    laparams.line_margin = 0.01
    device = My(rsrcmgr, sys.stdout, laparams=laparams)
    device.reset()
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    result_data = []
    count = 0
    for page in PDFPage.get_pages(fp, set()):
        interpreter.process_page(page)
        result_data.append(device.group)
        device.word = ""
        device.group = []
        device.word_pos_info = {}
        count += 1
        # break
    fp.close()
    return result_data


def get_row_group(data, row_name):
    _temp = data[row_name].value_counts()
    # 將大於10的list，當作是正常的，有可能因為名字或者其他因素造成多切
    group_list = _temp[_temp >= 7].index.tolist()
    group_list.sort()
    group_list.insert(0, 0)
    group_list.insert(len(group_list), group_list[-1] + 100)
    return group_list


def get_column_groups():
    return [0, 40.00, 90.0, 175.0, 295.0, 360.0, 520.0, 600.0, 655.0, 800]


def main(filename):
    pdf_data_list = read_pdf_data(filename)
    final_data = pandas.DataFrame()
    for pdf_single_data in pdf_data_list[:1]:
        pdf_data = pandas.DataFrame(pdf_single_data)
        # parsing enter alphabet
        pdf_data["content"] = pdf_data["content"].str.replace("\n", "")
        # y must be 24.412 <= y1 <= 522.309
        pdf_data = pdf_data[ (pdf_data.y1>24.412) & (pdf_data.y1<=522.309) ]
        pdf_data = pdf_data.reset_index(drop=True)
        pdf_data["column"] = -1
        pdf_data["row"] = -1

        # it can validate your condition
        # plt.plot(pdf_data.x0, pdf_data.y1, "bo")
        # for i in get_column_groups():
        #     plt.axvline(i)
        # plt.show()

        x_group = pdf_data.groupby(pandas.cut(pdf_data["x0"], get_column_groups()))
        column_group_list = x_group.groups.values()

        for idx, column_group in enumerate(column_group_list):
            pdf_data.loc[column_group, "column"] = idx

        group_list = get_row_group(pdf_data, "y1")
        y_group = pdf_data.groupby(pandas.cut(pdf_data["y1"], group_list))
        row_group_list = y_group.groups.values()

        for idx, row_group in enumerate(row_group_list):
            pdf_data.loc[row_group, "row"] = idx

        pdf_data = pdf_data[pdf_data["column"] < 100]
        pdf_data = pdf_data.drop(["x0", "y1"], axis=1)
        pdf_data["content"] = pdf_data["content"].map(lambda x: "%s" % x)
        gby_data = pdf_data.groupby(["row", "column"]).sum().unstack('column')
        gby_data.columns = range(gby_data.shape[1])
        gby_data.index = range(gby_data.shape[0])
        gby_data = gby_data.dropna()
        gby_data = gby_data[(gby_data[0] != u"序號") & (gby_data[0] != 0)]
        # print gby_data
    #
        gby_data["is_ok"] = gby_data[8].map(lambda x: find_match_string(x))
        final_data = final_data.append(gby_data)
    #
    final_data[0] = pandas.to_numeric(final_data[0], errors="ignore")
    final_data = final_data.sort_values([0])
    final_data = final_data.reset_index(drop=True)
    # print final_data
    final_data.to_csv("%s.csv" % filename, encoding="utf8", index=False)

if __name__ == "__main__":
    main("376570000Asetup10505.pdf")
