# BACHA.AI

BACHA.AI là project trợ lý AI y tế sử dụng kiến trúc RAG (Retrieval-Augmented Generation) để hỗ trợ tra cứu và gợi ý hướng xử trí dựa trên tài liệu chuyên môn nội bộ. Hệ thống nhận câu hỏi từ người dùng, tìm kiếm các nội dung liên quan trong kho tri thức, sau đó dùng mô hình ngôn ngữ lớn để tạo câu trả lời có ngữ cảnh.

Tập trung vào bài toán tham khảo thông tin y tế từ các tài liệu dạng `.docx`. Ngoài luồng hỏi đáp chính, hệ thống còn có lớp guardrail để kiểm tra câu trả lời trước khi trả về cho người dùng.

## Mục tiêu

- Xây dựng API hỏi đáp y tế dựa trên dữ liệu nội bộ.
- Đọc tài liệu chuyên môn, tạo embedding và lưu vào MongoDB.
- Dùng FAISS để tìm kiếm ngữ nghĩa theo câu hỏi của người dùng.
- Kết hợp kết quả truy xuất với LLM để tạo câu trả lời.
- Kiểm tra câu trả lời bằng guardrail trước khi trả về.
- Ghi nhớ lịch sử hội thoại theo `thread_id`.
- Tóm tắt hội thoại và lưu kết quả vào PostgreSQL.

## Luồng hoạt động

1. Tài liệu trong `ingestion/docs` được đọc và trích xuất nội dung.
2. Mỗi đoạn tri thức được tạo embedding và lưu vào MongoDB.
3. FAISS index được tạo từ các vector embedding để phục vụ tìm kiếm nhanh.
4. Khi người dùng gửi câu hỏi, hệ thống tạo embedding cho câu hỏi.
5. FAISS truy xuất các đoạn tri thức có độ tương đồng cao nhất.
6. LLM nhận câu hỏi, lịch sử hội thoại và tri thức truy xuất để sinh câu trả lời.
7. Nếu câu trả lời là dạng dữ liệu y tế có cấu trúc, guardrail sẽ kiểm tra lại với tri thức truy xuất.
8. Nếu guardrail đạt, API trả về câu trả lời; nếu không đạt, API trả về câu thông báo an toàn.
9. Lịch sử hội thoại được lưu theo phiên và có thể tóm tắt để lưu vào PostgreSQL.

## Công nghệ sử dụng

- **FastAPI**: xây dựng REST API.
- **MongoDB**: lưu nội dung tri thức và vector embedding.
- **FAISS**: tìm kiếm vector theo độ tương đồng ngữ nghĩa.
- **PostgreSQL**: lưu tóm tắt lịch sử hội thoại.
- **LLM API / Ollama**: tạo câu trả lời, tóm tắt hội thoại và chạy guardrail.
- **Embedding API**: tạo vector cho tài liệu và câu hỏi.
- **python-docx**: đọc dữ liệu từ tài liệu Word.
- **Docker Compose**: khởi tạo MongoDB, Mongo Express và PostgreSQL.

## Cấu trúc thư mục

```text
BACHA.AI/
|-- api.py                 # FastAPI app và các endpoint chính
|-- main.py                # Chạy thử luồng RAG qua terminal
|-- chunking/              # Đọc và xử lý tài liệu đầu vào
|-- embedding/             # Gọi API tạo embedding
|-- ingestion/             # Dữ liệu đầu vào, dữ liệu test và hồ sơ mẫu
|-- ingestion/docs/        # Tài liệu chuyên môn dạng .docx
|-- llm/                   # Gọi LLM, guardrail và các hàm đánh giá
|-- prompts/               # Prompt cho hỏi đáp, tóm tắt, guardrail
|-- rechieval/             # Truy xuất tri thức bằng FAISS
|-- vectordb/              # MongoDB, PostgreSQL và vector store
|-- report/                # Báo cáo, biểu đồ và kết quả đánh giá
|-- docker-compose.yml     # Cấu hình database bằng Docker
`-- requirements.txt       # Danh sách thư viện Python
```

## API chính

### Kiểm tra trạng thái

```http
GET /health
```

Trả về trạng thái hoạt động của API.

### Hỏi đáp y tế

```http
POST /chat
```

Body mẫu:

```json
{
  "thread_id": "thread-123",
  "message": "Bệnh nhân đau thắt ngực kéo dài và đau lan lên vai trái cần theo dõi gì?",
}
```

Trong đó:

- `thread_id`: ID của phiên hội thoại.
- `message`: câu hỏi của người dùng.
- `top_k`: số lượng kết quả truy xuất tối đa từ FAISS.
- `min_score`: ngưỡng điểm tương đồng tối thiểu để giữ lại tri thức liên quan.

API sẽ trả về câu hỏi, `thread_id` và câu trả lời sau khi đã qua bước truy xuất tri thức và kiểm tra guardrail.

### Tóm tắt hội thoại

```http
POST /threads/{thread_id}/summary
```

Body mẫu:

```json
{
  "user_id": "user-123"
}
```

API sẽ lấy lịch sử hội thoại của `thread_id`, tạo bản tóm tắt bằng LLM và lưu kết quả vào bảng `history` trong PostgreSQL.

### Xóa lịch sử hội thoại

```http
DELETE /threads/{thread_id}
```

Xóa lịch sử hội thoại đang lưu trong bộ nhớ của một phiên cụ thể.

## Cấu hình môi trường

Tạo file `.env` dựa trên `.env.example` và khai báo các biến môi trường cần thiết:

```env
MONGODB_URI=mongodb://admin:supersecretpassword@localhost:27018/
EMBED_API_SERVER=http://localhost:11434/api/embed
CHAT_API_SERVER=http://localhost:11434/api/generate
MODEL_EMB=bge-m3
MODEL_CHAT=llama3
MIN_SCORE_RECHIEVAL=0.55
HOST_POSTGRE=localhost
PORT_POSTGRE=5432
DATABASE_PORTGRE=WikiDB
USER_POSTGRE=admin
PASSWORD_POSTGRE=admin123
```

## Cách chạy project

Khởi động MongoDB và PostgreSQL:

```bash
docker compose up -d
```

Cài đặt thư viện Python:

```bash
pip install -r requirements.txt
```

Chạy API:

```bash
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Sau khi chạy, có thể mở tài liệu API tại:

```text
http://localhost:8000/docs
```

Nếu muốn chạy thử luồng hỏi đáp trực tiếp trên terminal:

```bash
python main.py
```

## Dữ liệu trong project

- `ingestion/docs`: chứa tài liệu chuyên môn dùng để xây dựng kho tri thức.
- `ingestion/data_test.json`: chứa dữ liệu test cho các trường hợp dấu hiệu, phương pháp và ghi chú.
- `ingestion/record.txt`: chứa hồ sơ mẫu để thử nghiệm kiểm tra logic hồ sơ bệnh án.
- `faiss.index`: file index vector được tạo sau khi hệ thống xử lý dữ liệu.

## Ưu điểm

- Câu trả lời bám sát tài liệu nội bộ nhờ kết hợp RAG với kho tri thức đã được xử lý.
- FAISS giúp truy xuất nhanh các đoạn thông tin liên quan theo ngữ nghĩa.
- Guardrail giúp kiểm tra câu trả lời trước khi trả về, tăng độ an toàn cho hệ thống.
- Có cơ chế ghi nhớ lịch sử hội thoại theo từng `thread_id`.
- Có thể tóm tắt hội thoại và lưu vào PostgreSQL để phục vụ tra cứu sau này.
- Dữ liệu tri thức, vector và lịch sử hội thoại được tách rõ bằng MongoDB, FAISS và PostgreSQL.
- Dễ mở rộng bằng cách thêm tài liệu mới vào `ingestion/docs`.
- FastAPI giúp API dễ kiểm thử, dễ tích hợp với frontend hoặc hệ thống nội bộ khác.
