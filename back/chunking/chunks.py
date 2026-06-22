from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredWordDocumentLoader

# file_name = "job.txt"
from docx import Document


def load_data(file_name):
    doc = Document(file_name)
    data = []
    for table in doc.tables:
        # print("=== TABLE ===")
        for row in table.rows:
            data.append([cell.text for cell in row.cells])
    final = []
    for dt in data:
        dt = [d.replace("\n", "") for d in dt]
        final.append(dt)
    return final