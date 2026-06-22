# -*- coding: utf-8 -*-

import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


def init_postgre():
    conn = psycopg2.connect(
        host=os.getenv("HOST_POSTGRE"),
        port=os.getenv("PORT_POSTGRE"),
        database=os.getenv("DATABASE_PORTGRE"),
        user=os.getenv("USER_POSTGRE"),
        password=os.getenv("PASSWORD_POSTGRE"),
    )
    return conn.cursor()


def create_table_postgre(cursor):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS history (
            id SERIAL PRIMARY KEY,
            sessionId VARCHAR(100) NOT NULL,
            userId VARCHAR(100) NOT NULL,
            content TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS knowledge (
            id SERIAL PRIMARY KEY,
            name_doc TEXT NOT NULL,
            content TEXT NOT NULL,
            vector JSONB NOT NULL
        );
    """
    cursor.execute(create_table_query)
    cursor.connection.commit()


def save_data_into_postgre(cursor, sessionId, userId, content):
    insert_query = """
        INSERT INTO history (sessionId, userId, content)
        VALUES (%s, %s, %s);
    """
    cursor.execute(insert_query, (sessionId, userId, content))
    cursor.connection.commit()


def load_knowledge_postgre(cursor):
    cursor.execute(
        """
            SELECT name_doc, content, vector
            FROM knowledge
            ORDER BY id ASC;
        """
    )
    rows = cursor.fetchall()
    return [
        {
            "name_doc": name_doc,
            "content": content,
            "vector": vector,
        }
        for name_doc, content, vector in rows
    ]


def save_knowledge_postgre(list_path_file, load_data, cursor, get_embedding):
    name_docs = []
    attentions = []
    content_table = []

    for file_path in list_path_file:
        chunks = load_data(file_name=file_path)
        chunks = [chunk for chunk in chunks if len(chunk[0]) > 0]
        name_docs.append(os.path.basename(file_path))
        attentions.append(chunks[-1][0])

        data_need = []
        for row in chunks[2 : len(chunks) - 1]:
            data_need.append(
                {
                    "dau_hieu_lam_sang_goi_y": row[1],
                    "phuong_phap": row[2],
                    "ghi_chu": row[3],
                }
            )
        content_table.append(data_need)

    insert_query = """
        INSERT INTO knowledge (name_doc, content, vector)
        VALUES (%s, %s, %s);
    """
    for name_doc, attention, rows in zip(name_docs, attentions, content_table):
        for row in rows:
            content = (
                "DẤU HIỆU LÂM SÀNG GỢI Ý: "
                + row["dau_hieu_lam_sang_goi_y"]
                + ", "
                + "PHƯƠNG PHÁP: "
                + row["phuong_phap"]
                + ", "
                + "GHI CHÚ: "
                + row["ghi_chu"]
                + ", "
                + "LƯU Ý: "
                + attention
            )
            vector = get_embedding(content)
            if not isinstance(vector, list) or len(vector) == 0:
                raise RuntimeError("Không tạo được embedding, không lưu knowledge vào PostgreSQL")

            cursor.execute(
                insert_query,
                (name_doc, content, psycopg2.extras.Json(vector)),
            )

    cursor.connection.commit()
    print("saved knowledge into postgre successfully!!!")
