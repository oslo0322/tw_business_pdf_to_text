from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from pdfminer.layout import LTContainer
from pdfminer.layout import LTText
from pdfminer.layout import LTTextBox

import sys
import pandas

from group_data import get_model_result

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
                        self.word_pos_info = {"x0":item.x0, "y1":item.y0}
                self.word += item.get_text()

            if isinstance(item, LTTextBox):
                # self.word_pos_info.update({"x1":item.x1})
                self.word_pos_info.update({"content": self.word.strip()})
                self.group.append(self.word_pos_info.copy())
                self.word_pos_info = {}
                self.word = ""
        render(ltpage)
        return

def read_pdf_data():
    fp = open('/Users/oslo/Downloads/test.pdf', 'rb')

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    laparams.line_margin = 0.01
    device = My(rsrcmgr, sys.stdout, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    count = 0
    for page in PDFPage.get_pages(fp, set()):
        interpreter.process_page(page)
        break
        if count > 3:
            break
        count += 1
    return device.group

def get_row_group(data, row_name):
    _temp = data[row_name].value_counts()
    group_list = _temp[_temp == 8].index.tolist()
    group_list.sort()
    group_list.insert(0, 0)
    group_list.insert(len(group_list), group_list[-1]+100)
    return group_list


model_data = get_model_result()
pdf_data = read_pdf_data()
test_data = pandas.DataFrame(pdf_data)
test_data["column"] = -1
test_data["row"] = -1

group_list = get_row_group(test_data, "y1")
y_group = test_data.groupby(pandas.cut(test_data["y1"], group_list))
row_group_list = y_group.groups.values()

for idx, row_group in enumerate(row_group_list):
    test_data.loc[row_group, "row"] = idx

for idx in test_data.index:
    data_pos = test_data.ix[idx][["x0", "y1"]]
    result = model_data.predict([data_pos])[0]
    test_data.loc[idx, "column"] = result

# test_data[["content", "x0", "y1", "column"]].sort("column").to_csv("test.csv", encoding="utf8", index=False)

test_data = test_data.drop(["x0", "y1"], axis=1)
test_data["content"] = test_data["content"].map(lambda x: "%s" % x)
gby_data = test_data.groupby(["row", "column"]).sum()
print gby_data.unstack('column')
