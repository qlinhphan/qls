import json
import os
import threading
import unicodedata
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List

import faiss
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from chunking.chunks import load_data
from embedding.embedder import get_embedding
from llm.llama_client import llama_clients, llama_summary_conversation
from llm.llama_review_medical_record import (
    llama_KiemTraCacGiayHoacPhieu,
    llama_check_identity,
    llama_check_medical_logic,
    llama_check_phamarcy,
)
from prompts.prompt_review_medical_record import (
    prompt_CheckNguNghiaGiuaCacFile,
    prompt_GiayRaVien,
    prompt_ThongTinBenhAn,
    prompt_ThongTinRaVien,
    prompt_ThongTinTongKetBenhAn,
    prompt_TomTatBenhAn,
    prompt_check_identity,
    prompt_check_medical_logic,
    prompt_check_pharmacy,
)
from prompts.prompt_temp import llama_clients_prompt, llama_summary_conversation_prompt
from rechieval.rechieval import rechieval_data
from vectordb.postgre import (
    create_table_postgre,
    init_postgre,
    load_knowledge_postgre,
    save_data_into_postgre,
    save_knowledge_postgre,
)
from vectordb.vector_store import vector_stores

load_dotenv()

DEFAULT_MIN_SCORE = float(os.getenv("MIN_SCORE_RECHIEVAL", "0.55"))
API_VERSION = "2026-06-22-cors-5173"
PROMPT_CONFIG_PATH = Path("prompt_config.json")
IDENTITY_ANSWER = "Tôi là trợ lý AI y tế hỗ trợ trích xuất phác đồ điều trị."
CREATOR_ANSWER = (
    "Tôi được tạo ra bởi Phòng CNTT thuộc Bệnh viện Đa khoa Quốc tế Bắc Hà."
)
GREETING_ANSWER = "Xin chào, tôi có thể hỗ trợ bác sĩ tra cứu hướng xử trí từ dữ liệu hiện có."
THANKS_ANSWER = "Rất vui được hỗ trợ bác sĩ."


def _normalize_intent_text(value: str) -> str:
    value = value.lower().strip()
    value = unicodedata.normalize("NFD", value)
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    value = value.replace("đ", "d")
    return " ".join(value.replace("đ", "d").split())


def _quick_answer(question: str) -> str | None:
    normalized = _normalize_intent_text(question)
    compact = normalized.strip(" ?!.:,;")

    if compact in {
        "ban la ai",
        "ban la gi",
        "may la ai",
        "em la ai",
        "chatbot la ai",
        "tro ly la ai",
    }:
        return IDENTITY_ANSWER
    if any(
        keyword in normalized
        for keyword in (
            "ai tao ra ban",
            "ai lam ra ban",
            "ban duoc tao ra boi ai",
            "ban den tu dau",
        )
    ):
        return CREATOR_ANSWER
    if compact in {"xin chao", "chao", "hello", "hi"}:
        return GREETING_ANSWER
    if compact in {"cam on", "thank you", "thanks", "tks"}:
        return THANKS_ANSWER

    identity_questions = {
        "Bạn là ai",
        "Bạn là gì",
        "Mày là ai",
        "Em là ai",
        "Chatbot là ai",
        "Trợ lý là ai",
    }
    creator_keywords = (
        "Ai tạo ra bạn",
        "Ai làm ra bạn",
        "Bạn được tạo ra bởi ai",
        "Bạn đến từ đâu",
    )
    greeting_words = {"Xin chào", "Chào", "Hello", "Hi"}
    thanks_words = {"Cảm ơn", "Thank You", "Thanks", "Tks"}

    if compact in identity_questions:
        return IDENTITY_ANSWER
    if any(keyword in normalized for keyword in creator_keywords):
        return CREATOR_ANSWER
    if compact in greeting_words:
        return GREETING_ANSWER
    if compact in thanks_words:
        return THANKS_ANSWER

    return None


def _stringify_for_history(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _save_thread_history(thread_id: str, question: str, answer: Any) -> None:
    answer_text = _stringify_for_history(answer)
    with app.state.thread_lock:
        history = list(app.state.thread_histories.get(thread_id, []))
        app.state.thread_histories[thread_id] = history + [[question, answer_text]]


def bootstrap_resources(postgre_cursor) -> Dict[str, Any]:
    file_in_docs = os.listdir("ingestion/docs")
    list_path_file = [os.path.join("ingestion/docs", fid) for fid in file_in_docs]

    all_data_in_db = load_knowledge_postgre(postgre_cursor)
    if len(all_data_in_db) == 0:
        save_knowledge_postgre(
            list_path_file=list_path_file,
            load_data=load_data,
            cursor=postgre_cursor,
            get_embedding=get_embedding,
        )
        all_data_in_db = load_knowledge_postgre(postgre_cursor)

    if not os.path.exists("faiss.index"):
        vector_stores(all_data_in_db)

    index_file = faiss.read_index("faiss.index")
    return {
        "knowledge_data": all_data_in_db,
        "index_file": index_file,
    }


class ChatRequest(BaseModel):
    thread_id: str = Field(..., min_length=1, description="ID de ghi nho hoi thoai")
    message: str = Field(..., min_length=1, description="Cau hoi cua nguoi dung")
    top_k: int = Field(default=3, ge=1, le=50)
    min_score: float = Field(default=DEFAULT_MIN_SCORE, ge=0.0, le=1.0)


class SummaryRequest(BaseModel):
    user_id: str = Field(default="user-123", min_length=1, description="ID nguoi dung")


class SystemPromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Prompt he thong")


def _default_system_prompt_template() -> str:
    return llama_clients_prompt("{knowledge}", "{context}", "{q}")


def _load_custom_system_prompt() -> str | None:
    if not PROMPT_CONFIG_PATH.exists():
        return None

    with PROMPT_CONFIG_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    prompt = data.get("llama_clients_prompt")
    if isinstance(prompt, str) and prompt.strip():
        return prompt

    return None


def _save_custom_system_prompt(prompt: str) -> None:
    with PROMPT_CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            {"llama_clients_prompt": prompt},
            file,
            ensure_ascii=False,
            indent=2,
        )


def _render_system_prompt_template(template: str, knowledge, context, q) -> str:
    return (
        template.replace("{knowledge}", str(knowledge))
        .replace("{context}", str(context))
        .replace("{q}", str(q))
    )


def active_llama_clients_prompt(knowledge, context, q):
    template = getattr(app.state, "system_prompt_template", None)
    if not template:
        return llama_clients_prompt(knowledge, context, q)

    return _render_system_prompt_template(template, knowledge, context, q)



def _review_has_error(result: str) -> bool:
    normalized = str(result).upper()
    return "❌" in normalized or "NÊN XEM LẠI" in normalized or "NEN XEM LAI" in normalized


async def _read_json_upload(file: UploadFile) -> Any:
    filename = file.filename or ""
    if filename and not filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Sai định dạng file, bạn phải truyền file JSON")

    if file.content_type and file.content_type not in {"application/json", "text/json"}:
        raise HTTPException(status_code=400, detail="Sai định dạng file, bạn phải truyền file JSON")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File json dang trong")

    try:
        text = content.decode("utf-8-sig")
        return json.loads(text)
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File json phai dung ma hoa UTF-8")
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"File json khong hop le: {exc.msg}",
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    postgre_cursor = init_postgre()
    create_table_postgre(postgre_cursor)
    resources = bootstrap_resources(postgre_cursor)
    app.state.knowledge_data = resources["knowledge_data"]
    app.state.index_file = resources["index_file"]
    app.state.postgre_cursor = postgre_cursor
    app.state.thread_histories: Dict[str, List[List[str]]] = {}
    app.state.thread_lock = threading.Lock()
    app.state.postgre_lock = threading.Lock()
    app.state.prompt_lock = threading.Lock()
    app.state.system_prompt_template = _load_custom_system_prompt()
    yield
    postgre_cursor.close()
    postgre_cursor.connection.close()


app = FastAPI(title="Medical RAG API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # "http://localhost:5173",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {
        "status": "ok",
        "version": API_VERSION,
        "gio": "10:47"
    }


@app.get("/system-prompt")
def get_system_prompt() -> Dict[str, Any]:
    with app.state.prompt_lock:
        prompt = app.state.system_prompt_template

    if prompt:
        return {
            "prompt": prompt,
            "is_default": False,
        }

    return {
        "prompt": _default_system_prompt_template(),
        "is_default": True,
    }


@app.put("/system-prompt")
def update_system_prompt(payload: SystemPromptRequest) -> Dict[str, Any]:
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt không được để trống")

    _save_custom_system_prompt(prompt)

    with app.state.prompt_lock:
        app.state.system_prompt_template = prompt

    return {
        "message": "Đã cập nhật prompt hệ thống",
        "is_default": False,
        "prompt": prompt,
    }


@app.post("/chat")
def chat(payload: ChatRequest) -> Dict[str, Any]:
    question = payload.message.strip()
    if not question:
        raise HTTPException(status_code=400, detail="message khong duoc de trong")

    quick_answer = _quick_answer(question)
    if quick_answer:
        _save_thread_history(payload.thread_id, question, quick_answer)
        return {
            "thread_id": payload.thread_id,
            "question": question,
            "answer": quick_answer,
        }

    question_vector = get_embedding(question)
    if question_vector is None:
        raise HTTPException(status_code=502, detail="Khong tao duoc embedding")

    with app.state.thread_lock:
        history = list(app.state.thread_histories.get(payload.thread_id, []))

    knowledge = rechieval_data(
        question_vector=question_vector,
        index_file=app.state.index_file,
        top_k=payload.top_k,
        mycol=app.state.knowledge_data,
        min_score=payload.min_score,
    )

    try:
        answer = llama_clients(active_llama_clients_prompt, knowledge, history, question)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    _save_thread_history(payload.thread_id, question, answer)

    return {
        "thread_id": payload.thread_id,
        "question": question,
        "answer": answer,
    }


@app.post("/threads/{thread_id}/summary")
def summarize_thread(thread_id: str, payload: SummaryRequest) -> Dict[str, Any]:
    with app.state.thread_lock:
        history = list(app.state.thread_histories.get(thread_id, []))

    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"Khong tim thay hoi thoai cho thread_id={thread_id}",
        )

    summary = llama_summary_conversation(llama_summary_conversation_prompt, history)

    with app.state.postgre_lock:
        save_data_into_postgre(
            cursor=app.state.postgre_cursor,
            sessionId=thread_id,
            userId=payload.user_id,
            content=summary,
        )

    return {
        "thread_id": thread_id,
        "user_id": payload.user_id,
        "turn_count": len(history),
        "summary": summary,
    }


@app.delete("/threads/{thread_id}")
def clear_thread(thread_id: str) -> Dict[str, str]:
    with app.state.thread_lock:
        app.state.thread_histories.pop(thread_id, None)
    return {"message": f"Da xoa history cua thread_id={thread_id}"}


DOCUMENT_CHECKS = {
    "TomTatHoSoBenhAn": prompt_TomTatBenhAn,
    "GiayRaVien": prompt_GiayRaVien,
    "ThongTinTongKetBenhAn": prompt_ThongTinTongKetBenhAn,
    "ThongTinRaVien": prompt_ThongTinRaVien,
    "ThongTinBenhAn": prompt_ThongTinBenhAn,
}


def _invalid_document_type_error() -> HTTPException:
    return HTTPException(
        status_code=400,
        detail="Lỗi check file - kiểm tra xem đã chọn đúng loại giấy tờ chưa",
    )


def _ensure_json_object(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise _invalid_document_type_error()
    return data


def _valid_document_keys(data: Dict[str, Any]) -> List[str]:
    return [key for key in data if key in DOCUMENT_CHECKS]


async def _check_one_medical_document(
    file: UploadFile,
    field_name: str,
    prompt_func,
) -> Dict[str, Any]:
    data = _ensure_json_object(await _read_json_upload(file))

    if len(data.keys()) != 1 or field_name not in data:
        raise _invalid_document_type_error()

    try:
        document_data = data[field_name]
    except Exception:
        raise _invalid_document_type_error()

    result = llama_KiemTraCacGiayHoacPhieu(prompt_func, document_data)
    is_valid = not _review_has_error(result)

    return {
        "filename": file.filename,
        "document_type": field_name,
        "is_valid": is_valid,
        "checks": {
            field_name: is_valid,
        },
        "details": {
            field_name: result,
        },
    }


def _build_cross_document_check_data(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        data_check = {}

        if "TomTatHoSoBenhAn" in data:
            TomTatHoSoBenhAn = data["TomTatHoSoBenhAn"]
            data_check["TTHSBA_ChanDoanVaoVien"] = TomTatHoSoBenhAn["ChanDoanVaoVien"]
            data_check["TTHSBA_ChanDoanRaVien"] = TomTatHoSoBenhAn["ChanDoanRaVien"]
            data_check["TTHSBA_HuongDieuTri"] = TomTatHoSoBenhAn["HuongDieuTri"]
            data_check["TTHSBA_LyDoVaoVien"] = TomTatHoSoBenhAn["LyDoVaoVien"]
            data_check["TTHSBA_TienSuBenh"] = TomTatHoSoBenhAn["TienSuBenh"]
            data_check["TTHSBA_TomTatKetQuaXetNghiemCLS"] = TomTatHoSoBenhAn[
                "TomTatKetQuaXetNghiemCLS"
            ]
            data_check["TTHSBA_TomTatQuaTrinhBenhLy"] = TomTatHoSoBenhAn[
                "TomTatQuaTrinhBenhLy"
            ]

        if "GiayRaVien" in data:
            GiayRaVien = data["GiayRaVien"]
            data_check["GRV_ChanDoan"] = GiayRaVien["ChanDoan"]
            data_check["GRV_GhiChu"] = GiayRaVien["GhiChu"]
            data_check["GRV_PhuongPhapDieuTri"] = GiayRaVien["PhuongPhapDieuTri"]

        if "ThongTinTongKetBenhAn" in data:
            ThongTinTongKetBenhAn = data["ThongTinTongKetBenhAn"]
            data_check["TTTKBA_HuongDieuTri"] = ThongTinTongKetBenhAn["HuongDieuTri"]
            data_check["TTTKBA_LanPhauThuats"] = ThongTinTongKetBenhAn["LanPhauThuats"]
            data_check["TTTKBA_PhuongPhapDieuTri"] = ThongTinTongKetBenhAn[
                "PhuongPhapDieuTri"
            ]
            data_check["TTTKBA_QuaTrinhBenhLy"] = ThongTinTongKetBenhAn["QuaTrinhBenhLy"]
            data_check["TTTKBA_TinhTrangNguoiBenhKhiRaVien"] = ThongTinTongKetBenhAn[
                "TinhTrangNguoiBenhKhiRaVien"
            ]
            data_check["TTTKBA_gridPhauThuatThuThuat"] = ThongTinTongKetBenhAn[
                "gridPhauThuatThuThuat"
            ]

        if "ThongTinRaVien" in data:
            ThongTinRaVien = data["ThongTinRaVien"]
            data_check["TTRV_GhiChuChuanDoanKKBCapCuu"] = ThongTinRaVien[
                "GhiChuChuanDoanKKBCapCuu"
            ]
            data_check["TTRV_GhiChuChuanDoanRaVien"] = ThongTinRaVien[
                "GhiChuChuanDoanRaVien"
            ]
            data_check["TTRV_GhiChuChuanDoanSauPhauThuat"] = ThongTinRaVien[
                "GhiChuChuanDoanSauPhauThuat"
            ]
            data_check["TTRV_GhiChuChuanDoanTruocPhauThuat"] = ThongTinRaVien[
                "GhiChuChuanDoanTruocPhauThuat"
            ]
            data_check["TTRV_GhiChuNoiChuanDoanKhiVaoKhoaDieuTri"] = ThongTinRaVien[
                "GhiChuNoiChuanDoanKhiVaoKhoaDieuTri"
            ]
            data_check["TTRV_GhiChuNoiChuanDoanLucVaoDe"] = ThongTinRaVien[
                "GhiChuNoiChuanDoanLucVaoDe"
            ]

        if "ThongTinBenhAn" in data:
            ThongTinBenhAn = data["ThongTinBenhAn"]
            data_check["TTBA_BoPhanTonThuongs"] = ThongTinBenhAn["BoPhanTonThuongs"]
            data_check["TTBA_CacXetNghiemCanLam"] = ThongTinBenhAn["CacXetNghiemCanLam"]
            data_check["TTBA_ChiSoSinhTons"] = ThongTinBenhAn["ChiSoSinhTons"]
            data_check["TTBA_ChuanDoan"] = ThongTinBenhAn["ChuanDoan"]
            data_check["TTBA_HuongDanDieuTri"] = ThongTinBenhAn["HuongDanDieuTri"]
            data_check["TTBA_HuongXuLyLoiDanBs"] = ThongTinBenhAn["HuongXuLyLoiDanBs"]
            data_check["TTBA_KhamBenhToanThan"] = ThongTinBenhAn["KhamBenhToanThan"]
            data_check["TTBA_LyDoVaoVien"] = ThongTinBenhAn["LyDoVaoVien"]
            data_check["TTBA_Mat"] = ThongTinBenhAn["Mat"]
            data_check["TTBA_QuaTrinhHoiBenh"] = ThongTinBenhAn["QuaTrinhHoiBenh"]
            data_check["TTBA_TaiMuiHong"] = ThongTinBenhAn["TaiMuiHong"]
            data_check["TTBA_ThanKinh"] = ThongTinBenhAn["ThanKinh"]
            data_check["TTBA_ThanTietNieu"] = ThongTinBenhAn["ThanTietNieu"]
            data_check["TTBA_TienSuBenhBanThan"] = ThongTinBenhAn["TienSuBenhBanThan"]
            data_check["TTBA_TieuHoa"] = ThongTinBenhAn["TieuHoa"]
            data_check["TTBA_TomTatBenhAn"] = ThongTinBenhAn["TomTatBenhAn"]
            data_check["TTBA_TuanHoan"] = ThongTinBenhAn["TuanHoan"]

        return data_check
    except Exception:
        raise _invalid_document_type_error()


@app.post("/medical-record/check-json/tom-tat-ho-so-benh-an")
async def check_tom_tat_ho_so_benh_an(file: UploadFile = File(...)) -> Dict[str, Any]:
    return await _check_one_medical_document(file, "TomTatHoSoBenhAn", prompt_TomTatBenhAn)


@app.post("/medical-record/check-json/giay-ra-vien")
async def check_giay_ra_vien(file: UploadFile = File(...)) -> Dict[str, Any]:
    return await _check_one_medical_document(file, "GiayRaVien", prompt_GiayRaVien)


@app.post("/medical-record/check-json/thong-tin-tong-ket-benh-an")
async def check_thong_tin_tong_ket_benh_an(file: UploadFile = File(...)) -> Dict[str, Any]:
    return await _check_one_medical_document(
        file,
        "ThongTinTongKetBenhAn",
        prompt_ThongTinTongKetBenhAn,
    )


@app.post("/medical-record/check-json/thong-tin-ra-vien")
async def check_thong_tin_ra_vien(file: UploadFile = File(...)) -> Dict[str, Any]:
    return await _check_one_medical_document(file, "ThongTinRaVien", prompt_ThongTinRaVien)


@app.post("/medical-record/check-json/thong-tin-benh-an")
async def check_thong_tin_benh_an(file: UploadFile = File(...)) -> Dict[str, Any]:
    return await _check_one_medical_document(file, "ThongTinBenhAn", prompt_ThongTinBenhAn)


@app.post("/medical-record/check-json")
async def check_medical_record_json(file: UploadFile = File(...)) -> Dict[str, Any]:
    data = _ensure_json_object(await _read_json_upload(file))
    missing_keys = [key for key in DOCUMENT_CHECKS if key not in data]
    if missing_keys:
        raise _invalid_document_type_error()

    data_check = _build_cross_document_check_data(data)

    result = llama_KiemTraCacGiayHoacPhieu(prompt_CheckNguNghiaGiuaCacFile, data_check)
    is_valid = not _review_has_error(result)

    return {
        "filename": file.filename,
        "is_valid": is_valid,
        "checks": {
            "KiemTraNguNghiaGiuaCacFile": is_valid,
        },
        "details": {
            "KiemTraNguNghiaGiuaCacFile": result,
        },
    }


# up ca 1 file json lon len va check vai phieu
# @app.post("/medical-record/check-json")
# async def check_medical_record_json(file: UploadFile = File(...)) -> Dict[str, Any]:
#     data = await _read_json_upload(file)

#     required_fields = {
#         "TomTatHoSoBenhAn": prompt_TomTatBenhAn,
#         "GiayRaVien": prompt_GiayRaVien,
#         "ThongTinTongKetBenhAn": prompt_ThongTinTongKetBenhAn,
#         "ThongTinRaVien": prompt_ThongTinRaVien,
#         "ThongTinBenhAn": prompt_ThongTinBenhAn, 
#     }
#     missing_fields = [field for field in required_fields if field not in data]
#     if missing_fields:
#         raise HTTPException(
#             status_code=400,
#             detail=f"File json thieu cac truong: {', '.join(missing_fields)}",
#         )

#     details = {}
#     checks = {}
#     for field, prompt_func in required_fields.items():
#         result = llama_KiemTraCacGiayHoacPhieu(prompt_func, data[field])
#         details[field] = result
#         checks[field] = not _review_has_error(result)

#     return {
#         "filename": file.filename,
#         "is_valid": all(checks.values()),
#         "checks": checks,
#         "details": details,
#     }




# python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
# python -m uvicorn api:app --reload --host 0.0.0.0 --port 8001

# curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d "{\"thread_id\":\"thread-123\",\"message\":\"Bệnh nhân sốt cao và ho kéo dài\",\"top_k\":10,\"min_score\":0.55}"
