import json
import os
import requests
import time
from dotenv import load_dotenv
from pprint import pprint
from prompts.prompt_review_medical_record import prompt_TomTatBenhAn, prompt_GiayRaVien, prompt_ThongTinTongKetBenhAn, prompt_ThongTinRaVien, prompt_ThongTinBenhAn, prompt_CheckNguNghiaGiuaCacFile
from llm.llama_review_medical_record import llama_KiemTraCacGiayHoacPhieu
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv()
              #'TomTatHoSoBenhAn', 'GiayRaVien', 'ThongTinTongKetBenhAn', 'ThongTinRaVien', 'ThongTinBenhAn'


llm = ChatOpenAI(model = os.getenv("MODEL_CHAT"), api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))



# try:
#     data_check = {}
#     with open('5_to.json', 'r', encoding='utf-8') as fo:
#         data = json.load(fo)
#         TomTatHoSoBenhAn = data['TomTatHoSoBenhAn']
#         GiayRaVien = data['GiayRaVien']
#         ThongTinTongKetBenhAn = data['ThongTinTongKetBenhAn']
#         ThongTinRaVien = data['ThongTinRaVien']
#         ThongTinBenhAn = data['ThongTinBenhAn']

#         data_check['TTHSBA_ChanDoanVaoVien'] = TomTatHoSoBenhAn['ChanDoanVaoVien']
#         data_check['TTHSBA_ChanDoanRaVien'] = TomTatHoSoBenhAn['ChanDoanRaVien']
#         data_check['TTHSBA_HuongDieuTri'] = TomTatHoSoBenhAn['HuongDieuTri']
#         data_check['TTHSBA_LyDoVaoVien'] = TomTatHoSoBenhAn['LyDoVaoVien']
#         data_check['TTHSBA_TienSuBenh'] = TomTatHoSoBenhAn['TienSuBenh']
#         data_check['TTHSBA_TomTatKetQuaXetNghiemCLS'] = TomTatHoSoBenhAn['TomTatKetQuaXetNghiemCLS']
#         data_check['TTHSBA_TomTatQuaTrinhBenhLy'] = TomTatHoSoBenhAn['TomTatQuaTrinhBenhLy']

#         data_check['GRV_ChanDoan'] = GiayRaVien['ChanDoan']
#         data_check['GRV_GhiChu'] = GiayRaVien['GhiChu']
#         data_check['GRV_PhuongPhapDieuTri'] = GiayRaVien['PhuongPhapDieuTri']

#         data_check['TTTKBA_HuongDieuTri'] = ThongTinTongKetBenhAn['HuongDieuTri']
#         data_check['TTTKBA_LanPhauThuats'] = ThongTinTongKetBenhAn['LanPhauThuats']
#         data_check['TTTKBA_PhuongPhapDieuTri'] = ThongTinTongKetBenhAn['PhuongPhapDieuTri']
#         data_check['TTTKBA_QuaTrinhBenhLy'] = ThongTinTongKetBenhAn['QuaTrinhBenhLy']
#         data_check['TTTKBA_TinhTrangNguoiBenhKhiRaVien'] = ThongTinTongKetBenhAn['TinhTrangNguoiBenhKhiRaVien']
#         data_check['TTTKBA_gridPhauThuatThuThuat'] = ThongTinTongKetBenhAn['gridPhauThuatThuThuat']

#         data_check['TTRV_GhiChuChuanDoanKKBCapCuu'] = ThongTinRaVien['GhiChuChuanDoanKKBCapCuu']
#         data_check['TTRV_GhiChuChuanDoanRaVien'] = ThongTinRaVien['GhiChuChuanDoanRaVien']
#         data_check['TTRV_GhiChuChuanDoanSauPhauThuat'] = ThongTinRaVien['GhiChuChuanDoanSauPhauThuat']
#         data_check['TTRV_GhiChuChuanDoanTruocPhauThuat'] = ThongTinRaVien['GhiChuChuanDoanTruocPhauThuat']
#         data_check['TTRV_GhiChuNoiChuanDoanKhiVaoKhoaDieuTri'] = ThongTinRaVien['GhiChuNoiChuanDoanKhiVaoKhoaDieuTri']
#         data_check['TTRV_GhiChuNoiChuanDoanLucVaoDe'] = ThongTinRaVien['GhiChuNoiChuanDoanLucVaoDe']

#         data_check['TTBA_BoPhanTonThuongs'] = ThongTinBenhAn['BoPhanTonThuongs'] 
#         data_check['TTBA_CacXetNghiemCanLam'] = ThongTinBenhAn['CacXetNghiemCanLam'] 
#         data_check['TTBA_ChiSoSinhTons'] = ThongTinBenhAn['ChiSoSinhTons'] 
#         data_check['TTBA_ChuanDoan'] = ThongTinBenhAn['ChuanDoan'] 
#         data_check['TTBA_HuongDanDieuTri'] = ThongTinBenhAn['HuongDanDieuTri'] 
#         data_check['TTBA_HuongXuLyLoiDanBs'] = ThongTinBenhAn['HuongXuLyLoiDanBs'] 
#         data_check['TTBA_KhamBenhToanThan'] = ThongTinBenhAn['KhamBenhToanThan'] 
#         data_check['TTBA_LyDoVaoVien'] = ThongTinBenhAn['LyDoVaoVien'] 
#         data_check['TTBA_Mat'] = ThongTinBenhAn['Mat'] 
#         data_check['TTBA_QuaTrinhHoiBenh'] = ThongTinBenhAn['QuaTrinhHoiBenh'] 
#         data_check['TTBA_TaiMuiHong'] = ThongTinBenhAn['TaiMuiHong'] 
#         data_check['TTBA_ThanKinh'] = ThongTinBenhAn['ThanKinh'] 
#         data_check['TTBA_ThanTietNieu'] = ThongTinBenhAn['ThanTietNieu'] 
#         data_check['TTBA_TienSuBenhBanThan'] = ThongTinBenhAn['TienSuBenhBanThan'] 
#         data_check['TTBA_TieuHoa'] = ThongTinBenhAn['TieuHoa'] 
#         data_check['TTBA_TomTatBenhAn'] = ThongTinBenhAn['TomTatBenhAn'] 
#         data_check['TTBA_TuanHoan'] = ThongTinBenhAn['TuanHoan'] 

#     pprint(data_check)
#     res = llama_KiemTraCacGiayHoacPhieu(prompt_CheckNguNghiaGiuaCacFile, data_check)
#     print(res)
# except:
#     print("ERROR")


    # start = time.time()
# with open('tom_tat_ho_so_benh_an.json', 'r', encoding='utf-8') as fo:
#     try:
#         data = json.load(fo)
#         res_TomTatHoSoBenhAn = llama_KiemTraCacGiayHoacPhieu(prompt_TomTatBenhAn, data['TomTatHoSoBenhAn'])
#         print(res_TomTatHoSoBenhAn)
#     except:
#         print("SAI LOAI PHIEU")
# print("========================================================================================================")
# with open('giay_ra_vien.json', 'r', encoding='utf-8') as fo:
#     try:
#         data = json.load(fo)
#         res_GiayRaVien = llama_KiemTraCacGiayHoacPhieu(prompt_GiayRaVien, data["GiayRaVien"])
#         print(res_GiayRaVien)
#     except:
#         print("SAI LOAI PHIEU")
# print("========================================================================================================")
# with open('thong_tin_tong_ket_benh_an.json', 'r', encoding='utf-8') as fo:
#     try:
#         data = json.load(fo)
#         res_ThongTinTongKetBenhAn = llama_KiemTraCacGiayHoacPhieu(prompt_ThongTinTongKetBenhAn,data['ThongTinTongKetBenhAn'] )
#         print(res_ThongTinTongKetBenhAn)
#     except:
#         print("SAI LOAI PHIEU")
# print("========================================================================================================")
# with open('thong_tin_ra_vien.json', 'r', encoding='utf-8') as fo:
#     try:
#         data = json.load(fo)
#         res_ThongTinRaVien = llama_KiemTraCacGiayHoacPhieu(prompt_ThongTinRaVien, data['ThongTinRaVien'])
#         print(res_ThongTinRaVien)
#     except:
#         print("SAI LOAI PHIEU")
# print("========================================================================================================")
# with open('thong_tin_benh_an.json', 'r', encoding='utf-8') as fo:
#     try:
#         data = json.load(fo)
#         res_ThongTinBenhAn = llama_KiemTraCacGiayHoacPhieu(prompt_ThongTinBenhAn, data['ThongTinBenhAn'])
#         print(res_ThongTinBenhAn)
#     except:
#         print("SAI LOAI PHIEU")
# 
# 
# 
# 


