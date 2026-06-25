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











def prompt_TomTatBenhAn(data_TomTatHoSoBenhAn):
    prompt = f"""
    Bạn là chuyên gia kiểm toán dữ liệu lâm sàng. Hãy rà soát block dữ liệu Tóm tắt hồ sơ bệnh án dưới đây:

DỮ LIỆU:
{data_TomTatHoSoBenhAn}

QUY TẮC PHÁT HIỆN LỖI:
1. Xem xét mục 'Thông Tin Hành chính': Trích xuất và ghi lại Họ tên, Giới tính, Ngày vào viện, Ngày ra viện.
2. Kiểm tra tính đồng nhất lâm sàng: So sánh trường 'Chẩn đoán vào viện', 'Chẩn đoán ra viện', 'Lý do vào viện', và 'Tiền sử bệnh'. Ghi nhận bộ phận cơ thể bị tổn thương (Trái hay Phải).

YÊU CẦU: Trả ra kết quả kiểm toán ngắn gọn:
- Chỉ in ra Tiếng Việt có dấu, Chỗ nào chứa ký tự không dấu viết liền thì chuyển thành tiếng việt chuẩn, ví dụ: BoPhanTonThuongs -> "Bộ Phận Tổn Thương"
- Thông tin hành chính bóc được: ...
- Chẩn đoán bộ phận (Trái/Phải): ...
- Điểm bất thường trong phiếu này (nếu có): ...
- Cuối cùng kết luận là "Nên Xem Lại" hoặc "ĐẠT"
"""
    return prompt

def prompt_GiayRaVien(data_GiayRaVien):
    prompt = f"""
    Bạn là chuyên gia kiểm toán hồ sơ pháp lý y tế. Hãy rà soát block dữ liệu Giấy ra viện dưới đây:

DỮ LIỆU:
{data_GiayRaVien}

QUY TẮC PHÁT HIỆN LỖI:
1. Ghi lại chẩn đoán bệnh tại trường 'Chẩn đoán'. Đặc biệt chú ý từ khóa chỉ định vị trí bộ phận cơ thể (Trái hay Phải).
2. Kiểm tra mục 'Phương pháp điều trị': Phương pháp phẫu thuật thực tế tác động vào bên nào (Trái hay Phải)? Có mâu thuẫn với trường 'Chẩn đoán' của chính phiếu này không?

YÊU CẦU: Trả ra kết quả kiểm toán ngắn gọn:
- Chỉ in ra Tiếng Việt có dấu, Chỗ nào chứa ký tự không dấu viết liền thì chuyển thành tiếng việt chuẩn, ví dụ: BoPhanTonThuongs -> "Bộ Phận Tổn Thương"
- Chẩn đoán ra viện ghi nhận: ...
- Bên cơ thể phẫu thuật điều trị: ...
- Điểm mâu thuẫn nội tại của phiếu (nếu có): ...
- Cuối cùng kết luận là "Nên Xem Lại" hoặc "ĐẠT"
"""
    return prompt

def prompt_ThongTinTongKetBenhAn(data_ThongTinTongKetBenhAn):
    prompt = f"""
    Bạn là chuyên gia giám định hồ sơ điều trị. Hãy rà soát block dữ liệu Tổng kết bệnh án dưới đây:

DỮ LIỆU:
{data_ThongTinTongKetBenhAn}

QUY TẮC PHÁT HIỆN LỖI:
1. Vào mục "Lần Phẫu Thuật" hoặc "Lưới Phẫu Thuật Thủ Thuật": Trích xuất thời gian làm phẫu thuật ("Phẫu Thuật Thủ Thuật Ngày Giờ"), phương pháp phẫu thuật ("Phẫu Thuật Thủ Thuật Phương Pháp"), và phương pháp vô cảm ("Vô Cảm").
2. Đối chiếu logic: Kiểm tra xem thông tin can thiệp thực tế ở các trường này có đồng nhất và logic với mục "Phương Pháp Điều Trị" và "Tình Trạng Người Bệnh Khi Ra Viện" hay không.

YÊU CẦU: Trả ra kết quả kiểm toán ngắn gọn:
- Chỉ in ra Tiếng Việt có dấu, Chỗ nào chứa ký tự không dấu viết liền thì chuyển thành tiếng việt chuẩn, ví dụ: BoPhanTonThuongs -> "Bộ Phận Tổn Thương"
- Thông tin phẫu thuật thực tế: ...
- Điểm bất thường trong phiếu này (nếu có): ...
- Cuối cùng kết luận là "Nên Xem Lại" hoặc "ĐẠT"
"""
    return prompt

def prompt_ThongTinRaVien(data_ThongTinRaVien):
    prompt = f"""
Bạn là giám định viên chi phí Bảo hiểm y tế. Hãy rà soát block dữ liệu Thông tin ra viện dưới đây:

DỮ LIỆU:
{data_ThongTinRaVien}

QUY TẮC PHÁT HIỆN LỖI:
1. Làm toán thời gian: Kiểm tra trường 'Ngày Lập Phiếu', 'Thời Gian Ra Viện'. 
2. Đối chiếu logic số số liệu: Trích xuất trường 'Tổng Số Ngày Điệu Trị'. Kiểm tra xem con số này có dấu hiệu bất thường, quá tải hoặc sai lệch phi lý hay không.
3. Ghi lại trường 'Ghi Chú Chẩn Đoán Ra Viện' để phục vụ đối chiếu chéo sau này.

YÊU CẦU: Trả ra kết quả kiểm toán ngắn gọn:
- Chỉ in ra Tiếng Việt có dấu, Chỗ nào chứa ký tự không dấu viết liền thì chuyển thành tiếng việt chuẩn, ví dụ: BoPhanTonThuongs -> "Bộ Phận Tổn Thương"
- Số ngày điều trị hệ thống ghi: ...
- Ghi chú chẩn đoán ra viện: ...
- Điểm bất thường số liệu (nếu có): ...
- Cuối cùng kết luận là "Nên Xem Lại" hoặc "ĐẠT"
    """
    return prompt

def prompt_ThongTinBenhAn(data_ThongTinBenhAn):
    prompt = f"""
    Bạn là chuyên gia kiểm soát nhiễm khuẩn và an toàn lâm sàng. Hãy rà soát block dữ liệu Thông tin bệnh án dưới đây:

DỮ LIỆU:
{data_ThongTinBenhAn}

QUY TẮC PHÁT HIỆN LỖI:
1. Kiểm tra mục 'Bộ Phận Tổn Thương': Trích xuất mô tả tổn thương và liên kết hình ảnh chứng minh.
2. Kiểm tra thông tin hành chính: Trích xuất 'Họ Tên' và 'Năm Sinh' để chuẩn bị đối chiếu chéo.
3. Rà soát các trường chẩn đoán và ghi nhận triệu chứng cơ xương khớp tại đây.

YÊU CẦU: Trả ra kết quả kiểm toán ngắn gọn:
- Chỉ in ra Tiếng Việt có dấu, Chỗ nào chứa ký tự không dấu viết liền thì chuyển thành tiếng việt chuẩn, ví dụ: BoPhanTonThuongs -> "Bộ Phận Tổn Thương"
- Danh tính và Chẩn đoán ghi nhận: ...
- Mô tả bộ phận tổn thương gốc: ...
- Điểm bất thường (nếu có): ...
- Cuối cùng kết luận là "Nên Xem Lại" hoặc "ĐẠT"

"""
    return prompt 

def prompt_CheckNguNghiaGiuaCacFile(data):
    prompt = f"""
    Bạn là Trưởng phòng Kiểm toán Lâm sàng AI tối cao tại hệ thống y tế. 
Nhiệm vụ của bạn là thực hiện SIÊU KIỂM TOÁN CHÉO (Super Cross-matching) giữa các phân mục dữ liệu của cùng một hồ sơ bệnh án dưới đây nhằm phát hiện ra các sai sót logic mâu thuẫn nghiêm trọng.

DỮ LIỆU HỒ SƠ BỆNH ÁN THỰC TẾ:
=========================================
{data}
=========================================

HƯỚNG DẪN CHIẾN LƯỢC KIỂM TOÁN CHÉO (AI BẮT BUỘC PHẢI QUÉT):
1. ĐỐI CHIẾU ĐỊNH VỊ GIẢI PHẪU VÀ VỊ TRÍ TỔN THƯƠNG:
   Rà soát chéo các trường chẩn đoán và xử lý: "Bộ phận tổn thương" (ở THÔNG TIN BỆNH ÁN), "Chẩn đoán vào viện/ra viện" (ở TÓM TẮT HỒ SƠ BỆNH ÁN), "Chẩn đoán" (ở GIẤY RA VIỆN), và các trường "Ghi chú chẩn đoán trước/sau phẫu thuật" (ở THÔNG TIN RA VIỆN).
   👉 Bắt lỗi ngay nếu có sự tráo đổi hoặc mâu thuẫn vị trí cơ thể giải phẫu (Ví dụ: Lúc vào viện ghi tổn thương bên TRÁI hoặc chi TRÊN, nhưng lúc phẫu thuật và làm Giấy ra viện bác sĩ lại gõ nhầm thành bên PHẢI hoặc chi DƯỚI).

2. ĐỐI CHIẾU TƯƠNG THÍCH GIỮA LÂM SÀNG VÀ ĐIỀU TRỊ:
   So khớp các trường "Lý do vào viện", "Quá trình hỏi bệnh" với các trường "Phương pháp điều trị", "Lưới phẫu thuật thủ thuật" (ở THÔNG TIN TỔNG KẾT BỆNH ÁN) và "Hướng dẫn điều trị".
   👉 Kiểm tra xem phương pháp phẫu thuật hay y lệnh dùng thuốc thực tế có phù hợp logic với bệnh danh chẩn đoán hay không.

3. ĐỐI CHIẾU TIỀN SỬ VÀ DIỄN BIẾN LÂM SÀNG:
   So sánh "Tiền sử bệnh bản thân" với "Tóm tắt quá trình bệnh lý" và "Tình trạng người bệnh khi ra viện" xem diễn biến qua các mốc thời gian ghi nhận có bị xung đột logic hay không.

BẮT BUỘC xuất báo cáo kiểm toán chi tiết bằng tiếng Việt có dấu theo đúng định dạng Markdown nghiêm ngặt dưới đây (Tuyệt đối không tự bịa thông tin nằm ngoài tệp dữ liệu được cung cấp):

### ❌ PHÁT HIỆN ĐIỂM NGHI VẤN TRÊN BỆNH ÁN
- **Sai lệch về Chẩn đoán & Vị trí giải phẫu:** [Chỉ rõ trường nào, phiếu nào ghi mâu thuẫn vị trí tổn thương hoặc sai lệch bệnh danh, nếu không có ghi "Không phát hiện bất thường"]
- **Sai lệch về Quy trình & Phương pháp điều trị:** [Ghi rõ nếu phương pháp phẫu thuật, thủ thuật hoặc lời dặn điều trị không tương thích với lý do vào viện và chẩn đoán lâm sàng, nếu không có ghi "Không phát hiện bất thường"]
- **Mâu thuẫn về Diễn biến & Tiền sử:** [Ghi rõ mâu thuẫn logic giữa tiền sử bệnh án cũ và bệnh lý đợt này nếu có, nếu không có ghi "Không phát hiện bất thường"]
- **Rủi ro Pháp lý & Nguy cơ xuất toán Bảo hiểm (BHYT):** [Phân tích cụ thể xem các lỗi lệch pha dữ liệu ở trên sẽ khiến hồ sơ này bị cơ quan giám định Bảo hiểm từ chối thanh toán ở những điểm nào]
"""
    return prompt