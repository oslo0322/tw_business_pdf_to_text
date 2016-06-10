# -*- coding: utf-8 -*-
import business_main
import company_main


def main(pdf_filename, is_company):
    if is_company is True:
        company_main.main(pdf_filename)
    else:
        business_main.main(pdf_filename)
