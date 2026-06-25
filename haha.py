import json
import requests
from jsonpath_ng import parse

# 1. DỮ LIỆU JSON ĐỘNG
raw_json_data = {
  "thong_tin_benh_vien": {
    "ten_benh_vien": "Bệnh viện Đa khoa Quốc tế Bắc Hà",
    "ma_co_so_y_te": "HA-042",
    "phong_system": "Phòng CNTT & Quản lý Chất lượng"
  },
  "hanh_chinh": {
    "ma_benh_nhan": "BN-1980-AN",
    "ho_ten": "Nguyễn Văn An",
    "nam_sinh": 1980,
    "gioi_tinh": "Nam",
    "quoc_tich": "Việt Nam",
    "nghe_nghiep": "Lao động tự do (Khuân vác kho bãi)",
    "dia_chi": "Số 15, Ngõ 210, Đường Nguyễn Văn Cừ, Quận Long Biên, Hà Nội",
    "so_dien_thoai": "0912345xxx",
    "nguoi_nha_lien_he": {
      "ho_ten": "Trần Thị Bình",
      "quan_he": "Vợ",
      "so_dien_thoai": "0987654xxx"
    }
  },
  "thong_tin_nhap_vien": {
    "ma_luot_kham": "DOT2026-KHAM-001",
    "so_vao_vien": "VV-26-08942",
    "ngay_gio_vao_vien": "2026-06-23T08:15:00+07:00",
    "loai_hinh_vao_vien": "Cấp cứu",
    "ly_do_vao_vien": "Đau bụng dữ dội vùng hạ sườn phải và quanh rốn sau tai nạn giao thông giờ thứ 2"
  },
  "qua_trinh_cap_cuu_va_sang_loc": {
    "khoa_tiep_nhan": "Khoa Khám Cấp Cứu",
    "ten_file_nguon_he_thong": "PHÂN LOẠI KHÁM CẤP CỨU.2025.docx",
    "dau_hieu_sinh_ton_luc_vao": {
      "mach": 115,
      "don_vi_mach": "lần/phút",
      "huyen_ap_tam_thu": 90,
      "huyen_ap_tam_truong": 55,
      "don_vi_huyen_ap": "mmHg",
      "nhiet_do": 37.2,
      "don_vi_nhiet_do": "°C",
      "nhip_tho": 24,
      "don_vi_nhip_tho": "lần/phút",
      "spo2": 94,
      "don_vi_spo2": "%"
    },
    "trieu_chung_lam_sang_ghi_nhan": "Bệnh nhân tỉnh táo, tiếp xúc chậm, kích thích do đau. Phản ứng đau dữ dội và bất ngờ ở toàn bộ vùng bụng, tập trung nhiều ở hạ sườn phải. Bụng chướng nề nhẹ, có dấu hiệu bầm tím xây xát nông vùng thượng vị do va đập vào tay lái xe máy. Nôn mửa liên tục 2 lần ra dịch dạ dày trong quá trình thăm khám. Da niêm mạc nhợt nhạt, vã mồ hôi lạnh, đầu chi lạnh.",
    "chan_doan_tai_cap_cuu": "Theo dõi Chấn thương bụng kín / Sốc mất máu cấp do xuất huyết nội giờ thứ 2 sau Tai nạn giao thông",
    "xu_tri_cap_cuu_khan_cap": [
      "Lập 2 đường truyền tĩnh mạch ngoại vi lớn với Kim 18G",
      "Xả nhanh 1000ml dung dịch NaCl 0.9% và 500ml HES 130/0.4",
      "Thở oxy qua gọng kính 3 lít/phút",
      "Lấy máu làm xét nghiệm khẩn cấp tại giường (Công thức máu, Nhóm máu, Đông máu toàn bộ)",
      "Mời hội chẩn khẩn cấp liên khoa: Khoa Ngoại Tổng hợp và Khoa Gây mê hồi sức"
    ]
  },
  "ket_qua_can_lam_sang_ghi_nhan": {
    "xet_nghiem_mau": {
      "hong_cau": 3.1,
      "don_vi_hong_cau": "T/L",
      "hemoglobin": 85,
      "don_vi_hemoglobin": "g/L",
      "hematocrit": 0.26,
      "don_vi_hematocrit": "L/L",
      "bach_cau": 14.2,
      "don_vi_bach_cau": "G/L",
      "tieu_cau": 185,
      "don_vi_tieu_cau": "G/L"
    },
    "sieu_am_tai_giuong_FAST": "Dịch tự do ổ bụng lượng nhiều, dịch thuần nhất nghi máu tụ. Phát hiện đường mất liên tục nhu mô gan hạ phân thùy VI-VII kích thước ~4cm.",
    "chup_ct_scan_o_bung_co_can_quang": "Hình ảnh rách bao gan, tổn thương vỡ nhu mô gan hạ phân thùy VI, VII mức độ phức tạp (Phân độ chấn thương gan: Độ III), kèm khối máu tụ bao quanh gan và dịch máu tự do ngập hố chậu hai bên, khoang Douglas. Rách nhẹ bao lách gây rỉ máu nhẹ. Các tạng rỗng chưa thấy dấu hiệu khí tự do ổ bụng."
  },
  "qua_trinh_phau_thuat_va_dieu_tri_ngoai_khoa": {
    "khoa_chuyen_den": "Khoa Ngoại",
    "ten_file_nguon_he_thong": "PHÂN LOẠI SÀNG LỌC K. NGOẠI 2025 -.docx",
    "thoi_gian_phau_thuat": "2026-06-23T09:30:00+07:00",
    "phuong_phap_phau_thuat": "Phẫu thuật nội soi ổ bụng xử trí chấn thương (Khâu cầm máu nhu mô gan, dẫn lưu ổ bụng)",
    "phuong_phap_vo_cam": "Gây mê nội khí quản",
    "luoc_do_phau_thuat": "Vào ổ bụng bằng 3 Trocar. Thấy có khoảng 1200ml máu đặc and máu cục tập trung ở khoang gan và hố chậu. Tiến hành hút sạch máu tụ. Kiểm tra thấy gan phải hạ phân thùy VI-VII có vết rách nhu mô dài 4.5cm, sâu 1.5cm đang rỉ máu dầm dề. Tiến hành khâu ép cầm máu nhu mô gan bằng chỉ tiêu chậm số 1. Kiểm tra lách thấy rách nhẹ bao lách đã tự cầm máu, tiến hành đắp gạc xốp cầm máu. Đặt 2 ống dẫn lưu (1 ở hố gan, 1 ở Douglas). Đóng các lỗ Trocar.",
    "chan_doan_hau_phau": "Chấn thương bụng kín: Vỡ gan độ III, rách bao lách đã xử trí khâu cầm máu giờ thứ 1"
  },
  "qua_trinh_dieu_tri_noi_khoa_hau_phau": {
    "khoa_chuyen_den": "Khoa Nội",
    "ten_file_nguon_he_thong": "PHÂN LOẠI SÀNG LỌC K. NỘI.2025.docx",
    "ngay_chuyen_khoa": "2026-06-25T14:00:00+07:00",
    "tinh_trang_lam_sang_ngay_hau_phau_thu_3": "Bản ghi nhận thông tin lâm sàng đối với bệnh nhân Lê Văn Minh. Người bệnh tỉnh táo hoàn toàn, không sốt, bụng mềm, vết mổ khô. Tuy nhiên xuất hiện triệu chứng đau nhức dữ dội lan tỏa dọc toàn bộ vùng đùi và bắp chân trái, cẳng chân sưng nề to căng bóng, sờ vào nóng đỏ, hạn chế vận động chi dưới nghiêm trọng.",
    "chan_doan_noi_khoa_phoi_hop": "Theo dõi Viêm tắc huyết khối tĩnh mạch sâu chân trái / Biến chứng sưng nề phần mềm chi dưới sau chấn thương lớn",
    "che_do_cham_soc_noi_khoa": [
      "Bệnh nhân bị đau chân, Chỉ định chụp não",
      "Nâng cao thể trạng bằng dinh dưỡng hỗ trợ đường tĩnh mạch",
      "Sử dụng thuốc kháng viêm, giảm đau hạ sốt, bất động tạm thời chân trái",
      "Theo dõi sát chu vi vòng chân trái và các dấu hiệu sinh tồn"
    ]
  },
  "thong_tin_ra_vien": {
    "ngay_gio_ra_vien": "2026-06-30T09:00:00+07:00",
    "tinh_trang_ra_vien": "Bệnh nhân ổn định, đi lại nhẹ nhàng được, chân trái giảm sưng nề rõ rệt, da dẻ hồng hào trở lại, vết mổ bụng liền sẹo tốt.",
    "huong_dan_dieu_tri_ngoai_tru": {
      "che_do_nghi_ngoi": "Nghỉ ngơi tuyệt đối tại nhà từ 2-4 tuần, không khuân vác, làm việc nặng, kê cao chân trái khi nằm.",
      "che_do_dinh_duong": "Ăn thức ăn mềm, giàu đạm, nhiều rau xanh, hạn chế tối đa dầu mỡ và tuyệt đối không sử dụng rượu bia.",
      "don_thuoc_ra_vien": [
        {
          "ten_thuoc": "Augmentin 1g (Amoxicillin/Clavulanic acid)",
          "lieu_dung": "Uống 2 viên/ngày, chia 2 lần sáng - tối sau ăn",
          "so_luong": 14,
          "don_vi": "Viên"
        },
        {
          "ten_thuoc": "Tardyferon B9 (Sắt + Acid Folic)",
          "lieu_dung": "Uống 1 viên/ngày, uống vào buổi sáng trước ăn 30 phút",
          "so_luong": 3000000000,
          "don_vi": "Viên"
        }
      ],
      "lich_tai_kham": "Tái khám sau 1 tuần tại chuyên khoa Ngoại tổng hợp và chuyên khoa Nội mạch máu để siêu âm doppler mạch máu kiểm tra lại chân trái."
    }
  }
}

# =====================================================================
# SYSTEM TOOLS DEFINITION
# =====================================================================

def tool_get_identity_data(path_ho_ten: str, path_ten_vien: str):
    try:
        jsonpath_name = parse(path_ho_ten)
        jsonpath_hospital = parse(path_ten_vien)
        
        name_matches = [match.value for match in jsonpath_name.find(raw_json_data)]
        hospital_matches = [match.value for match in jsonpath_hospital.find(raw_json_data)]
        
        return {
            "ten_benh_nhan_goc": name_matches[0] if name_matches else "THIẾU",
            "ten_benh_vien_goc": hospital_matches[0] if hospital_matches else "THIẾU",
            "toan_bo_text_he_thong": json.dumps(raw_json_data, ensure_ascii=False)
        }
    except Exception as e:
        return {"error": f"Lỗi thực thi JsonPath: {str(e)}"}

def tool_get_clinical_data(path_trieu_chung: str, path_y_lenh: str):
    try:
        jsonpath_symptom = parse(path_trieu_chung)
        jsonpath_order = parse(path_y_lenh)
        
        symptom_matches = [match.value for match in jsonpath_symptom.find(raw_json_data)]
        order_matches = [match.value for match in jsonpath_order.find(raw_json_data)]
        
        return {
            "triieu_chung_lam_sang": symptom_matches[0] if symptom_matches else "THIẾU",
            "y_lenh_chi_dinh": order_matches[0] if order_matches else "THIẾU"
        }
    except Exception as e:
        return {"error": f"Lỗi thực thi JsonPath: {str(e)}"}

available_tools = {
    'tool_get_identity_data': tool_get_identity_data,
    'tool_get_clinical_data': tool_get_clinical_data
}

# =====================================================================
# LUỒNG REQUESTS THUẦN GỌI OLLAMA API
# =====================================================================

def run_audit_agent():
    url = "http://10.10.61.29:11434/api/chat"
    headers = {"Content-Type": "application/json"}
    
    # Bước 1: Thiết lập danh sách hội thoại ban đầu
    messages = [
        {
            'role': 'system',
            'content': """Bạn là Agent AI kiểm toán lâm sàng tối cao. Nhiệm vụ của bạn là phát hiện lỗi hành chính hoặc sai logic y khoa.
            Bạn không được tự bịa dữ liệu, bắt buộc phải gọi công cụ để lấy dữ liệu thực tế.
            Hãy nhìn vào cấu trúc JSON thô được cung cấp, tự tìm xem các thông tin quan trọng nằm ở Key nào để trích xuất đường dẫn JsonPath (Ví dụ: 'profile.full_name')."""
        },
        {
            'role': 'user',
            'content': f"Tài liệu JSON thô cần kiểm toán hệ thống:\n{json.dumps(raw_json_data, ensure_ascii=False, indent=2)}"
        }
    ]
    
    # Định nghĩa cấu trúc Tools dạng chuẩn JSON Schema phục vụ qua HTTP POST
    tools_spec = [
        {
            'type': 'function',
            'function': {
                'name': 'tool_get_identity_data',
                'description': 'Lấy dữ liệu hành chính bằng cách tự dò tìm đường dẫn trường tên và trường viện.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'path_ho_ten': {'type': 'string', 'description': 'Đường dẫn JsonPath tới họ tên bệnh nhân. Ví dụ: profile.full_name'},
                        'path_ten_vien': {'type': 'string', 'description': 'Đường dẫn JsonPath tới tên bệnh viện.'},
                    },
                    'required': ['path_ho_ten', 'path_ten_vien'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'tool_get_clinical_data',
                'description': 'Lấy dữ liệu lâm sàng để đối chiếu logic triệu chứng và y lệnh chỉ định.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'path_trieu_chung': {'type': 'string', 'description': 'Đường dẫn JsonPath tới chuỗi mô tả triệu chứng.'},
                        'path_y_lenh': {'type': 'string', 'description': 'Đường dẫn JsonPath tới mảng hoặc chuỗi y lệnh/chỉ định.'},
                    },
                    'required': ['path_trieu_chung', 'path_y_lenh'],
                },
            },
        }
    ]

    # Khởi tạo payload lượt 1 (Thám thính tìm key)
    payload_1 = {
        "model": "qwen2.5:14b",
        "messages": messages,
        "tools": tools_spec,
        "stream": False,
        "options": {"temperature": 0.0}
    }

    print("🤖 Agent đang thám thính cấu trúc JSON để tìm Key...")
    response = requests.post(url, data=json.dumps(payload_1), headers=headers)
    response_json = response.json()
    
    message_result = response_json.get('message', {})
    
    # Bước 2: Kiểm tra và xử lý Vòng lặp gọi Tool (Tool Calling)
    if 'tool_calls' in message_result:
        # Lưu lại phản hồi chứa ý định gọi tool của AI vào lịch sử hội thoại
        messages.append(message_result)
        
        for tool in message_result['tool_calls']:
            tool_name = tool['function']['name']
            tool_args = tool['function']['arguments']
            
            print(f"⚙️ Python kích hoạt Tool: {tool_name} với tham số động: {tool_args}")
            
            # Thực thi hàm Python cục bộ
            tool_output = available_tools[tool_name](**tool_args)
            
            # Đóng gói và đẩy kết quả trả về của Tool vào lịch sử hội thoại
            messages.append({
                'role': 'tool',
                'content': json.dumps(tool_output, ensure_ascii=False)
            })
            
        # Bước 3: Đóng gói toàn bộ lịch sử và gửi yêu cầu lượt cuối để AI xuất báo cáo
        payload_2 = {
            "model": "qwen2.5:14b",
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.0}
        }
        
        print("📝 Agent đang đối chiếu dữ liệu sạch và xuất báo cáo...")
        final_response = requests.post(url, data=json.dumps(payload_2), headers=headers)
        final_json = final_response.json()
        
        print("\n======= KẾT QUẢ KIỂM TOÁN LÂM SÀNG =======")
        print(final_json['message']['content'])
    else:
        print("Bot không gọi Tool nào. Kết quả:", message_result.get('content'))

if __name__ == "__main__":
    run_audit_agent()