"""
Test harness cho BACHA.AI.

Chạy:
    python aitest.py

File này để test do AI
logic chính mà không cần gọi MongoDB, PostgreSQL, Ollama hoặc embedding server thật.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np


class FakeCollection:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.inserted = []

    def find(self):
        return list(self.rows)

    def insert_one(self, row):
        self.inserted.append(row)


class FakeIndex:
    def __init__(self, distances, indices):
        self.distances = np.array([distances], dtype=np.float32)
        self.indices = np.array([indices], dtype=np.int64)

    def search(self, question, top_k):
        return self.distances[:, :top_k], self.indices[:, :top_k]


class ApiState:
    pass


class DummyLock:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class MedicalRagUnitTests(unittest.TestCase):
    def test_extract_json_from_markdown_block(self):
        from llm.llama_client import extract_json

        raw = '```json\n{"score": 9, "reason": "đúng"}\n```'
        self.assertEqual(extract_json(raw), {"score": 9, "reason": "đúng"})

    def test_retrieval_filters_by_min_score(self):
        from rechieval.rechieval import rechieval_data

        mycol = FakeCollection(
            [
                {"name_doc": "doc-a", "content": "chunk A"},
                {"name_doc": "doc-b", "content": "chunk B"},
                {"name_doc": "doc-c", "content": "chunk C"},
            ]
        )
        index = FakeIndex(distances=[0.95, 0.70, 0.30], indices=[0, 1, 2])

        result = rechieval_data(
            question_vector=[1.0, 0.0, 0.0],
            index_file=index,
            top_k=3,
            mycol=mycol,
            min_score=0.6,
        )

        self.assertEqual(result, {"response": ["chunk A", "chunk B"]})

    def test_load_data_reads_docx_tables(self):
        from docx import Document
        from chunking.chunks import load_data

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "sample.docx"
            doc = Document()
            table = doc.add_table(rows=2, cols=4)
            table.rows[0].cells[0].text = "STT"
            table.rows[0].cells[1].text = "Dấu hiệu"
            table.rows[0].cells[2].text = "Phương pháp"
            table.rows[0].cells[3].text = "Ghi chú"
            table.rows[1].cells[0].text = "1"
            table.rows[1].cells[1].text = "Đau ngực\nkhó thở"
            table.rows[1].cells[2].text = "Hỏi nhanh"
            table.rows[1].cells[3].text = "Theo dõi"
            doc.save(file_path)

            result = load_data(str(file_path))

        self.assertEqual(result[1][1], "Đau ngựckhó thở")
        self.assertEqual(result[1][2], "Hỏi nhanh")
        self.assertEqual(result[1][3], "Theo dõi")

    def test_save_data_mongodb_builds_expected_schema(self):
        from vectordb.mongodb import save_data_mongodb

        rows = [
            ["Tiêu đề", "", "", ""],
            ["Header", "Dấu hiệu", "Phương pháp", "Ghi chú"],
            ["1", "Đau ngực", "Hỏi nhanh", "Theo dõi NMCT"],
            ["Lưu ý cấp cứu", "", "", ""],
        ]
        mycol = FakeCollection()

        save_data_mongodb(
            list_path_file=["ingestion/docs/test.docx"],
            load_data=lambda file_name: rows,
            mycol=mycol,
            get_embedding=lambda text: [0.1, 0.2, 0.3],
        )

        self.assertEqual(len(mycol.inserted), 1)
        saved = mycol.inserted[0]
        self.assertEqual(saved["name_doc"], "test.docx")
        self.assertEqual(saved["vector"], [0.1, 0.2, 0.3])
        self.assertIn("DẤU HIỆU LÂM SÀNG GỢI Ý: Đau ngực", saved["content"])
        self.assertIn("PHƯƠNG PHÁP: Hỏi nhanh", saved["content"])
        self.assertIn("GHI CHÚ: Theo dõi NMCT", saved["content"])
        self.assertIn("LƯU Ý: Lưu ý cấp cứu", saved["content"])

    def test_api_guardrail_pass_returns_model_answer(self):
        import api

        state = ApiState()
        state.thread_histories = {}
        state.thread_lock = DummyLock()
        state.mycol = FakeCollection([{"name_doc": "doc-a", "content": "knowledge"}])
        state.index_file = FakeIndex(distances=[0.9], indices=[0])

        with patch.object(api.app, "state", state), \
            patch.object(api, "get_embedding", return_value=[1.0, 0.0, 0.0]), \
            patch.object(api, "llama_clients", return_value={"Phương pháp": "Hỏi nhanh"}), \
            patch.object(api, "llama_guardrail", return_value='{"check": "pass", "reason": "ok"}'):
            result = api.chat(
                api.ChatRequest(
                    thread_id="thread-test",
                    message="Đau ngực cần làm gì?",
                    top_k=1,
                    min_score=0.5,
                )
            )

        self.assertEqual(result["answer"], {"Phương pháp": "Hỏi nhanh"})
        self.assertEqual(len(state.thread_histories["thread-test"]), 1)

    def test_api_guardrail_fail_returns_safe_fallback(self):
        import api

        state = ApiState()
        state.thread_histories = {}
        state.thread_lock = DummyLock()
        state.mycol = FakeCollection([{"name_doc": "doc-a", "content": "knowledge"}])
        state.index_file = FakeIndex(distances=[0.9], indices=[0])

        with patch.object(api.app, "state", state), \
            patch.object(api, "get_embedding", return_value=[1.0, 0.0, 0.0]), \
            patch.object(api, "llama_clients", return_value={"Phương pháp": "Sai dữ liệu"}), \
            patch.object(api, "llama_guardrail", return_value='{"check": "fail", "reason": "không khớp"}'):
            result = api.chat(
                api.ChatRequest(
                    thread_id="thread-test",
                    message="Đau ngực cần làm gì?",
                    top_k=1,
                    min_score=0.5,
                )
            )

        self.assertEqual(result["answer"], api.GUARDRAIL_FALLBACK_ANSWER)
        self.assertEqual(state.thread_histories["thread-test"][0][1], api.GUARDRAIL_FALLBACK_ANSWER)

    def test_api_summary_saves_to_postgre(self):
        import api

        saved = {}

        state = ApiState()
        state.thread_histories = {"thread-test": [["Q1", "A1"], ["Q2", "A2"]]}
        state.thread_lock = DummyLock()
        state.postgre_lock = DummyLock()
        state.postgre_cursor = object()

        def fake_save(cursor, sessionId, userId, content):
            saved.update(
                {
                    "cursor": cursor,
                    "sessionId": sessionId,
                    "userId": userId,
                    "content": content,
                }
            )

        with patch.object(api.app, "state", state), \
            patch.object(api, "llama_summary_conversation", return_value="Tóm tắt phiên"), \
            patch.object(api, "save_data_into_postgre", side_effect=fake_save):
            result = api.summarize_thread("thread-test", api.SummaryRequest(user_id="user-1"))

        self.assertEqual(result["summary"], "Tóm tắt phiên")
        self.assertEqual(result["turn_count"], 2)
        self.assertEqual(saved["sessionId"], "thread-test")
        self.assertEqual(saved["userId"], "user-1")


class MedicalRagScenarioChecklist(unittest.TestCase):
    def test_production_scenarios_to_run_manually(self):
        scenarios = [
            "Hỏi đúng triệu chứng có trong tài liệu và kiểm tra câu trả lời có Phương pháp/Ghi chú/Lưu ý.",
            "Hỏi triệu chứng gần nghĩa với tài liệu để kiểm tra retrieval ngữ nghĩa.",
            "Hỏi ngoài phạm vi y tế để kiểm tra prompt/guardrail không trả lời lan man.",
            "Hỏi y tế nhưng không có trong knowledge để kiểm tra câu fallback an toàn.",
            "Hỏi tiếp trong cùng thread_id để kiểm tra context hội thoại.",
            "Gọi summary sau nhiều lượt chat để kiểm tra lưu PostgreSQL.",
            "Nạp lại dữ liệu khi MongoDB rỗng và faiss.index chưa tồn tại.",
            "Thử tài liệu bảng sai cấu trúc để phát hiện điểm parser đang fix cứng.",
            "Tắt embedding server để kiểm tra API trả 502.",
            "Cho guardrail fail để kiểm tra API không trả câu trả lời nguy hiểm.",
        ]

        self.assertEqual(len(scenarios), 10)
        print("\nKịch bản test thủ công nên chạy thêm:")
        for index, scenario in enumerate(scenarios, start=1):
            print(f"{index}. {scenario}")


if __name__ == "__main__":
    os.environ.setdefault("MIN_SCORE_RECHIEVAL", "0.55")
    unittest.main(verbosity=2)
