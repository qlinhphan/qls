import json
import os
import requests
import time
from dotenv import load_dotenv
from pprint import pprint
from prompts.prompt_review_medical_record import prompt_TomTatBenhAn, prompt_GiayRaVien, prompt_ThongTinTongKetBenhAn, prompt_ThongTinRaVien, prompt_ThongTinBenhAn
from llm.llama_review_medical_record import llama_KiemTraCacGiayHoacPhieu

load_dotenv()
              #'TomTatHoSoBenhAn', 'GiayRaVien', 'ThongTinTongKetBenhAn', 'ThongTinRaVien', 'ThongTinBenhAn'


    # start = time.time()
with open('tom_tat_ho_so_benh_an.json', 'r', encoding='utf-8') as fo:
    try:
        data = json.load(fo)
        res_TomTatHoSoBenhAn = llama_KiemTraCacGiayHoacPhieu(prompt_TomTatBenhAn, data['TomTatHoSoBenhAn'])
        print(res_TomTatHoSoBenhAn)
    except:
        print("SAI LOAI PHIEU")
print("========================================================================================================")
with open('giay_ra_vien.json', 'r', encoding='utf-8') as fo:
    try:
        data = json.load(fo)
        res_GiayRaVien = llama_KiemTraCacGiayHoacPhieu(prompt_GiayRaVien, data["GiayRaVien"])
        print(res_GiayRaVien)
    except:
        print("SAI LOAI PHIEU")
print("========================================================================================================")
with open('thong_tin_tong_ket_benh_an.json', 'r', encoding='utf-8') as fo:
    try:
        data = json.load(fo)
        res_ThongTinTongKetBenhAn = llama_KiemTraCacGiayHoacPhieu(prompt_ThongTinTongKetBenhAn,data['ThongTinTongKetBenhAn'] )
        print(res_ThongTinTongKetBenhAn)
    except:
        print("SAI LOAI PHIEU")
print("========================================================================================================")
with open('thong_tin_ra_vien.json', 'r', encoding='utf-8') as fo:
    try:
        data = json.load(fo)
        res_ThongTinRaVien = llama_KiemTraCacGiayHoacPhieu(prompt_ThongTinRaVien, data['ThongTinRaVien'])
        print(res_ThongTinRaVien)
    except:
        print("SAI LOAI PHIEU")
print("========================================================================================================")
with open('thong_tin_benh_an.json', 'r', encoding='utf-8') as fo:
    try:
        data = json.load(fo)
        res_ThongTinBenhAn = llama_KiemTraCacGiayHoacPhieu(prompt_ThongTinBenhAn, data['ThongTinBenhAn'])
        print(res_ThongTinBenhAn)
    except:
        print("SAI LOAI PHIEU")
# 
# 
# 
# 


