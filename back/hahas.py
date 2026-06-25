import json
import os
import requests
import time
from dotenv import load_dotenv
from pprint import pprint
from prompts.prompt_review_medical_record import prompt_TomTatBenhAn, prompt_GiayRaVien, prompt_ThongTinTongKetBenhAn, prompt_ThongTinRaVien, prompt_ThongTinBenhAn
from llm.llama_review_medical_record import llama_KiemTraCacGiayHoacPhieu

load_dotenv()

with open('5_to.json', 'r', encoding='utf-8') as fo:
    data = json.load(fo)
    
    keys = list(data.keys())
    # print(keys)

    # print("=TÓM TẮT HỒ SƠ BỆNH ÁN========================================")
    pprint(data['TomTatHoSoBenhAn'])               #'TomTatHoSoBenhAn', 'GiayRaVien', 'ThongTinTongKetBenhAn', 'ThongTinRaVien', 'ThongTinBenhAn'


    # start = time.time()
    # res_TomTatHoSoBenhAn = llama_KiemTraCacGiayHoacPhieu(prompt_TomTatBenhAn, data['TomTatHoSoBenhAn'])
    # res_GiayRaVien = llama_KiemTraCacGiayHoacPhieu(prompt_GiayRaVien, data["GiayRaVien"])
    # res_ThongTinTongKetBenhAn = llama_KiemTraCacGiayHoacPhieu(prompt_ThongTinTongKetBenhAn,data['ThongTinTongKetBenhAn'] )
    # res_ThongTinRaVien = llama_KiemTraCacGiayHoacPhieu(prompt_ThongTinRaVien, data['ThongTinRaVien'])
    # res_ThongTinBenhAn = llama_KiemTraCacGiayHoacPhieu(prompt_ThongTinBenhAn, data['ThongTinBenhAn'])


