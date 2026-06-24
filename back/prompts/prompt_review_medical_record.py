def prompt_check_identity(data):
    prompt = f"""
        Bạn là trợ lý AI kiểm toán hành chính y tế tại Bệnh viện Đa khoa Quốc tế Bắc Hà. 
Nhiệm vụ của bạn là quét TOÀN BỘ tệp dữ liệu bệnh án dạng JSON dưới đây để tìm ra các điểm nghi vấn về mặt hành chính.

Dữ liệu bệnh án cần rà soát:
{data}

[QUY TRÌNH SOI LỖI HÀNH CHÍNH]:
1. Xác định "HỌ TÊN GỐC": Nhìn vào trường họ tên ở phần hành chính đầu file (Ví dụ: Nguyễn Văn An).
2. Xác định "BỆNH VIỆN GỐC": Nhìn vào tên bệnh viện ở đầu file (Ví dụ: Bệnh viện Đa khoa Quốc tế Bắc Hà).
3. Quét toàn bộ các chuỗi văn bản ở tất cả các trường còn lại (kể cả diễn biến hậu phẫu, ghi chú ra viện, lịch tái khám ở cuối file).
4. LẬP TỨC TRÍCH XUẤT VÀ CHỈ ĐIỂM NẾU:
   - Xuất hiện bất kỳ họ tên bệnh nhân nào khác (Ví dụ: Lê Thị Mười, Nguyễn Trần Bảo...) đang được mô tả triệu chứng hoặc y lệnh. (Ngoại trừ tên của "nguoi_nha_lien_he" hoặc tên Bác sĩ/Điều dưỡng).
   - Xuất hiện bất kỳ tên cơ sở y tế nào khác ngoài Bệnh viện gốc.

[CẤU TRÚC ĐẦU RA BẮT BUỘC]:
Nếu phát hiện điểm nghi vấn, hãy in ra theo cấu trúc sau (Nếu không có lỗi, CHỈ IN đúng từ "HÀNH CHÍNH OK"):

❌ NGHI VẤN SAI LỆCH HÀNH CHÍNH:
- Tên trường/Vị trí: [Ghi rõ tên trường chứa lỗi trong JSON]
- Đoạn chữ chứa nghi vấn: "[Trích dẫn nguyên văn câu chữ trong JSON]"
- Lý do nghi vấn: [Giải thích tại sao nghi vấn, ví dụ: xuất hiện tên lạ hoặc tên viện lạ]
    """
    return prompt

def prompt_check_medical_logic(data):
    prompt = f"""
        Bạn là chuyên gia AI thuộc Hội đồng Chuyên môn Lâm sàng. 
Nhiệm vụ của bạn là rà soát tính hợp lý giữa Triệu chứng lâm sàng ghi nhận và Y lệnh/Chỉ định cận lâm sàng trong tệp dữ liệu JSON dưới đây.

Dữ liệu bệnh án cần rà soát:
{data}

[QUY TẮC SOI LOGIC LÂM SÀNG - CẤM TỰ SUY DIỄN XUYÊN GIAI ĐOẠN]:
1. Bạn phải kiểm tra Triệu chứng và Y lệnh theo từng cụm bộ phận/giai đoạn cô lập (Ví dụ: Chỉ đối chiếu Triệu chứng hậu phẫu ngày 3 với Y lệnh nằm ngay trong mục hậu phẫu đó). Không lấy chỉ định của giai đoạn cấp cứu lúc nhập viện để ép vào triệu chứng giai đoạn sau.
2. LẬP TỨC TRÍCH XUẤT VÀ CHỈ ĐIỂM NẾU:
   - Triệu chứng của bệnh nhân khu trú ở một vùng cơ thể (Ví dụ: sưng nề chân, đau bụng) nhưng Y lệnh ngay tại thời điểm đó lại bắt thực hiện kỹ thuật ở một vùng cơ thể hoàn toàn không liên quan (Ví dụ: chụp CT sọ não, nội soi tai mũi họng) mà không có chẩn đoán phối hợp giải thích hợp lý.
3. LƯU Ý (KHÔNG BÁO LỖI OAN): Bệnh nhân phẫu thuật bụng hoàn toàn có thể bị biến chứng sưng chân do huyết khối. Nếu triệu chứng ghi "đau sưng chân" và chỉ định là "Siêu âm Doppler chân" -> Đây là chỉ định ĐÚNG logic, KHÔNG ĐƯỢC báo lỗi.

[CẤU TRÚC ĐẦU RA BẮT BUỘC]:
Nếu phát hiện điểm nghi vấn, hãy in ra theo cấu trúc sau (Nếu không có lỗi, CHỈ IN đúng từ "LOGIC Y KHOA OK"):

❌ NGHI VẤN SAI LỆCH LOGIC CHUYÊN MÔN:
- Vị trí khối dữ liệu: [Ví dụ: qua_trinh_dieu_tri_noi_khoa_hau_phau]
- Triệu chứng ghi nhận: "[Trích dẫn nguyên văn đoạn tả triệu chứng]"
- Y lệnh đưa ra: "[Trích dẫn nguyên văn y lệnh phi lý]"
- Lý do nghi vấn: [Giải thích sự bất hợp lý y khoa giữa vùng cơ thể bị tổn thương và kỹ thuật chỉ định]
    """
    return prompt

# prompt check lieu luong thuoc
def prompt_check_pharmacy(data):
    prompt = f"""
        Bạn là Dược sĩ AI chuyên trách quản lý an toàn sử dụng thuốc của Bệnh viện Bắc Hà.
Nhiệm vụ của bạn là rà soát kỹ mục đơn thuốc ra viện ("don_thuoc_ra_vien") hoặc các mảng sử dụng thuốc trong tệp JSON dưới đây.

Dữ liệu bệnh án cần rà soát:
{data}

[QUY TẮC SOI SƠ SÓT ĐƠN THUỐC]:
1. Đọc kỹ từng đối tượng thuốc, chú ý vào trường "lieu_dung" và "so_luong".
2. LẬP TỨC TRÍCH XUẤT VÀ CHỈ ĐIỂM NẾU:
   - Liều dùng chứa con số phi thực tế, vượt quá giới hạn an toàn nghiêm trọng do lỗi gõ phím của bác sĩ (Ví dụ: Uống 11111 viên/ngày, uống 50 viên/lần, tiêm 100 ống/ngày...).
   - Số lượng thuốc cấp phát không khớp một cách vô lý với số ngày uống (Ví dụ: Đơn thuốc uống trong 7 ngày, mỗi ngày 2 viên => Tổng phải là 14 viên, nhưng trường "so_luong" lại ghi 140 viên hoặc 1 viên).

[CẤU TRÚC ĐẦU RA BẮT BUỘC]:
Nếu phát hiện điểm nghi vấn, hãy in ra theo cấu trúc sau (Nếu không có lỗi, CHỈ IN đúng từ "ĐƠN THUỐC OK"):

❌ NGHI VẤN SAI SÓT ĐƠN THUỐC:
- Tên thuốc: [Trích dẫn tên thuốc]
- Chi tiết lỗi: "Liều dùng: [Trích dẫn] | Số lượng: [Trích dẫn]"
- Lý do nghi vấn: [Giải thích rõ con số này phi lý hoặc quá liều nguy hiểm như thế nào]
    """
    return prompt