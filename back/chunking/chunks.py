from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredWordDocumentLoader

# file_name = "job.txt"
from docx import Document


def clean_cell_text(text):
    return " ".join(text.split())


def load_data(file_name):
    doc = Document(file_name)
    data = []
    for table in doc.tables:
        # print("=== TABLE ===")
        for row in table.rows:
            data.append([cell.text for cell in row.cells])
    final = []
    for dt in data:
        dt = [clean_cell_text(d) for d in dt]
        final.append(dt)
    return final

if __name__ == "__main__":
    rs = load_data("PHÂN LOẠI  KHÁM CẤP CỨU.2025.docx")
    print(rs)
