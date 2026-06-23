# Medic AI - Hệ thống RAG hỗ trợ phân loại người bệnh

Medic AI là hệ thống trợ lý AI y tế hỗ trợ bác sĩ tra cứu nhanh hướng xử trí, phân loại và theo dõi người bệnh dựa trên bộ tài liệu chuyên môn nội bộ. Dự án sử dụng kiến trúc RAG: đọc tài liệu Word, tạo embedding, lưu tri thức vào PostgreSQL, xây dựng chỉ mục FAISS và dùng mô hình ngôn ngữ để sinh câu trả lời theo ngữ cảnh.

## Tính năng chính

- Giao diện chat web đơn giản, dễ sử dụng cho bác sĩ.
- API backend bằng FastAPI, hỗ trợ hỏi đáp theo từng phiên hội thoại.
- Tự nạp dữ liệu từ các file `.docx` trong thư mục `back/ingestion/docs`.
- Lưu tri thức và lịch sử tóm tắt hội thoại bằng PostgreSQL.
- Tìm kiếm ngữ nghĩa nhanh bằng FAISS.
- Gọi mô hình chat và embedding qua Ollama/API nội bộ.
- Có trả lời nhanh cho các câu hỏi xã giao hoặc câu hỏi danh tính để phản hồi tức thì.
- Có endpoint tóm tắt hội thoại và lưu kết quả vào bảng `history`.
- Triển khai thuận tiện bằng Docker Compose gồm frontend, backend và PostgreSQL.

## Công nghệ sử dụng

- Frontend: React, Vite, lucide-react.
- Backend: FastAPI, Uvicorn, Pydantic.
- Cơ sở dữ liệu: PostgreSQL 16.
- Vector search: FAISS.
- Embedding và LLM: Ollama/API tương thích.
- Xử lý tài liệu: python-docx.
- Đóng gói triển khai: Docker Compose.

## Cấu trúc thư mục

```text
.
├── back
│   ├── api.py                  # FastAPI backend chính
│   ├── main.py                 # Chạy thử luồng RAG qua terminal
│   ├── requirements.txt        # Thư viện Python
│   ├── chunking
│   │   └── chunks.py           # Đọc bảng trong file Word và làm sạch nội dung
│   ├── embedding
│   │   └── embedder.py         # Gọi API tạo embedding
│   ├── ingestion
│   │   └── docs                # Tài liệu Word nguồn
│   ├── llm
│   │   └── llama_client.py     # Gọi model chat, đọc phản hồi stream
│   ├── prompts
│   │   └── prompt_temp.py      # Prompt cho trả lời, tóm tắt, kiểm tra
│   ├── rechieval
│   │   └── rechieval.py        # Tìm kiếm chunk liên quan bằng FAISS
│   └── vectordb
│       ├── postgre.py          # Lưu và đọc dữ liệu PostgreSQL
│       └── vector_store.py     # Tạo file chỉ mục FAISS
├── front
│   ├── src
│   │   ├── App.jsx             # Giao diện chat
│   │   └── styles.css          # Giao diện ứng dụng
│   └── package.json
├── docker-compose.yml          # Cấu hình chạy toàn bộ hệ thống
└── .env                        # Biến môi trường
```

## Luồng hoạt động

1. Backend khởi động và kết nối PostgreSQL.
2. Hệ thống tạo bảng `knowledge` và `history` nếu chưa có.
3. Nếu bảng `knowledge` đang trống, hệ thống đọc các file `.docx` trong `back/ingestion/docs`.
4. Mỗi dòng tri thức được chuẩn hóa, tạo embedding và lưu vào PostgreSQL.
5. FAISS index được tạo từ vector trong bảng `knowledge`.
6. Khi người dùng đặt câu hỏi, backend tạo embedding cho câu hỏi.
7. FAISS tìm các chunk tri thức liên quan nhất.
8. Prompt được ghép từ câu hỏi, tri thức liên quan và lịch sử hội thoại.
9. Model chat sinh câu trả lời và API trả kết quả về giao diện web.

## Biến môi trường

Các biến chính được dùng trong `.env` hoặc `docker-compose.yml`:

```env
MODEL_CHAT="qwen2.5:14b"
MODEL_EMB="bge-m3"

CHAT_API_SERVER="http://10.10.61.29:11434/api/generate"
EMBED_API_SERVER="http://10.10.61.29:11434/api/embed"

MIN_SCORE_RECHIEVAL="0.55"

HOST_POSTGRE="postgres_wiki_db"
PORT_POSTGRE="5432"
DATABASE_PORTGRE="postgres"
USER_POSTGRE="admin"
PASSWORD_POSTGRE="admin123"
```

Khi chạy bằng Docker Compose hiện tại, backend kết nối tới PostgreSQL container tên `postgres_wiki_db`.

## Chạy bằng Docker Compose

Từ thư mục gốc của dự án:

```bash
docker compose up -d --build
```

Kiểm tra container:

```bash
docker ps
```

Các container chính:

```text
bacha_api
bacha_front
postgres_wiki_db
```

Truy cập ứng dụng:

```text
http://localhost:4173
```

API backend:

```text
http://localhost:8001
```

Kiểm tra trạng thái API:

```bash
curl http://localhost:8001/health
```

## Các API chính

### Health check

```http
GET /health
```

Kết quả mẫu:

```json
{
  "status": "ok",
  "version": "2026-06-22-cors-5173",
  "gio": "10:47"
}
```

### Chat

```http
POST /chat
```

Body:

```json
{
  "thread_id": "thread-123",
  "message": "Người bệnh đau thắt ngực kéo dài, đau lan vai trái",
  "top_k": 3,
  "min_score": 0.55
}
```

Ý nghĩa trường:

- `thread_id`: ID phiên hội thoại để lưu ngữ cảnh.
- `message`: câu hỏi hoặc mô tả triệu chứng.
- `top_k`: số lượng chunk tri thức lấy từ FAISS.
- `min_score`: ngưỡng điểm tương đồng tối thiểu.

### Tóm tắt hội thoại

```http
POST /threads/{thread_id}/summary
```

Body:

```json
{
  "user_id": "user-123"
}
```

API sẽ tóm tắt lịch sử hội thoại theo `thread_id` và lưu vào bảng `history`.

### Xóa lịch sử một thread

```http
DELETE /threads/{thread_id}
```

API xóa lịch sử hội thoại đang lưu trong bộ nhớ của backend cho `thread_id` tương ứng.

## Làm việc với PostgreSQL

Vào PostgreSQL container:

```bash
docker exec -it postgres_wiki_db psql -U admin -d postgres
```

Xem danh sách bảng:

```sql
\dt
```

Xem dữ liệu tri thức:

```sql
SELECT id, name_doc, left(content, 300) AS content_preview
FROM knowledge
LIMIT 20;
```

Xem lịch sử tóm tắt:

```sql
SELECT *
FROM history
ORDER BY id DESC
LIMIT 20;
```

Thoát PostgreSQL:

```sql
\q
```

## Nạp lại dữ liệu tri thức

Tài liệu nguồn đặt trong:

```text
back/ingestion/docs
```

Khi backend khởi động, nếu bảng `knowledge` trống thì hệ thống sẽ đọc tài liệu, tạo embedding và lưu dữ liệu vào PostgreSQL. File `faiss.index` được tạo để phục vụ tìm kiếm ngữ nghĩa nhanh.

Nếu cần nạp lại toàn bộ dữ liệu từ đầu trong môi trường Docker, có thể xóa dữ liệu PostgreSQL local và khởi động lại:

```bash
docker compose down -v
docker compose up -d --build
```

Lệnh trên tạo lại volume PostgreSQL và nạp lại tri thức từ thư mục tài liệu nguồn.

## Chạy backend thủ công

Cài thư viện Python:

```bash
cd back
pip install -r requirements.txt
```

Chạy API:

```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8001 --reload
```

Chạy thử luồng hỏi đáp qua terminal:

```bash
python main.py
```

## Chạy frontend thủ công

```bash
cd front
npm install
npm run dev -- --host 0.0.0.0
```

Mở trình duyệt:

```text
http://localhost:5173
```

Khi chạy bằng Docker Compose, frontend được publish ra cổng:

```text
http://localhost:4173
```

## Triển khai trên Ubuntu server

Cài Docker và Docker Compose plugin, sau đó đưa source code lên server.

Chạy hệ thống:

```bash
cd /duong-dan-toi-project
docker compose up -d --build
```

Kiểm tra log backend:

```bash
docker logs -f bacha_api
```

Kiểm tra log frontend:

```bash
docker logs -f bacha_front
```

Kiểm tra log PostgreSQL:

```bash
docker logs -f postgres_wiki_db
```

Truy cập từ máy khác trong cùng mạng:

```text
http://<IP-server>:4173
```

API:

```text
http://<IP-server>:8001
```

## Ghi chú vận hành

- Model chat mặc định là `qwen2.5:14b`.
- Model embedding mặc định là `bge-m3`.
- Backend dùng `top_k` mặc định là `3` để lấy các chunk liên quan nhất.
- Câu hỏi xã giao, lời chào, cảm ơn và câu hỏi danh tính có phản hồi nhanh ngay trong API.
- Nội dung trong file Word được làm sạch khoảng trắng để tránh dính từ khi đọc bảng.
- Câu trả lời từ model được giới hạn bằng `num_predict` và `temperature` thấp để ưu tiên phản hồi gọn, ổn định.

## Một số lệnh hữu ích

Khởi động lại API:

```bash
docker compose restart api
```

Khởi động lại toàn bộ:

```bash
docker compose restart
```

Dừng hệ thống:

```bash
docker compose down
```

Xem container đang chạy:

```bash
docker ps
```

Xem biến môi trường trong container API:

```bash
docker exec -it bacha_api printenv MODEL_CHAT
```

Kiểm tra API chat bằng `curl`:

```bash
curl -X POST "http://localhost:8001/chat" \
  -H "Content-Type: application/json" \
  -d "{\"thread_id\":\"test\",\"message\":\"bạn là ai?\"}"
```
