import json
import os
import requests
import time
from dotenv import load_dotenv
from pprint import pprint
from prompts.prompt_review_medical_record import prompt_TomTatBenhAn, prompt_GiayRaVien, prompt_ThongTinTongKetBenhAn, prompt_ThongTinRaVien, prompt_ThongTinBenhAn
from llm.llama_review_medical_record import llama_KiemTraCacGiayHoacPhieu

load_dotenv()

with open('giay.json', 'r', encoding='utf-8') as fo:
    data = json.load(fo)
    
    keys = list(data.keys())
    print(keys)

    # print("=TÓM TẮT HỒ SƠ BỆNH ÁN========================================")
    # pprint(data['TomTatHoSoBenhAn'])               #'TomTatHoSoBenhAn', 'GiayRaVien', 'ThongTinTongKetBenhAn', 'ThongTinRaVien', 'ThongTinBenhAn'
    # print("=GIẤY RA VIÊN========================================")
    # pprint(data["GiayRaVien"])
    # print("=THÔNG TIN TỔNG KẾT BỆNH ÁN========================================")
    # pprint(data['ThongTinTongKetBenhAn'])
    # print("=TÔNG TIN RA VIỆN========================================")
    # pprint(data['ThongTinRaVien'])
    # print("=THÔNG TIN BỆNH ÁN========================================")
    # pprint(data['ThongTinBenhAn'])


    # start = time.time()
    # res_TomTatHoSoBenhAn = llama_KiemTraCacGiayHoacPhieu(prompt_TomTatBenhAn, data['TomTatHoSoBenhAn'])
    # res_GiayRaVien = llama_KiemTraCacGiayHoacPhieu(prompt_GiayRaVien, data["GiayRaVien"])
    # res_ThongTinTongKetBenhAn = llama_KiemTraCacGiayHoacPhieu(prompt_ThongTinTongKetBenhAn,data['ThongTinTongKetBenhAn'] )
    # res_ThongTinRaVien = llama_KiemTraCacGiayHoacPhieu(prompt_ThongTinRaVien, data['ThongTinRaVien'])
    # res_ThongTinBenhAn = llama_KiemTraCacGiayHoacPhieu(prompt_ThongTinBenhAn, data['ThongTinBenhAn'])

    # print(res_TomTatHoSoBenhAn)
    # print("===========================")
    # print(res_GiayRaVien)
    # print("===========================")
    # print(res_ThongTinTongKetBenhAn)
    # print("===========================")
    # print(res_ThongTinRaVien)
    # print("===========================")
    # print(res_ThongTinBenhAn)

    # end = time.time()
    # print("duting: ", (end - start))


    



    # check giấy ra viện và tóm tắt bệnh án 

    # print(data['BienBanCamKetPhauThuat'])   

    


