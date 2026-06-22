import json
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
from vectordb.mongodb import mongodb
import os
from embedding.embedder import get_embedding
from main import main
from llm.llama_client import llama_clients, llama_test_semantic
import json
import faiss
from rechieval.rechieval import rechieval_data_for_test, rechieval_data
import pandas as pd
from barh import barhs
from statistics import mean
from prompts.prompt_temp import llama_test_semantic_prompt

def test_chunk(top_k):    # danh gia xem truy van chunk nhu nao
  chunk_predict = [] # du doan
  chunks_actually = [] # thuc te
  mycol = mongodb(address=os.getenv("MONGODB_URI"))
  with open("ingestion/data_test.json", "r", encoding='utf-8') as f:
    data = json.load(f)
    data = data["data"]
    for d in data:
      dau_hieu = d['dau_hieu'] # dau hieu cua nguoi benh
      chunk = d['chunk'] # chunk thuc te

      q = dau_hieu
      q_vector = get_embedding(q)
      response = rechieval_data_for_test(
          question_vector=q_vector,
          index_file=faiss.read_index("faiss.index"),
          top_k=top_k,
          mycol=mycol,   
          min_score=0.55,
      )
      chunk_predict.append(response['chunk_predict'])
      chunks_actually.append(chunk)

  review_chunks = [] 
  for cp, ca in zip(chunk_predict, chunks_actually):
    if ca in cp:
      result = True
    else: result = False
    review_chunks.append(result)

  chunks_true = 0 # mo hinh du doan ra chunk dung
  for rc in review_chunks:
    if rc == True:
      chunks_true += 1
  return chunks_true/len(review_chunks)*100


def test_semantic(): # danh gia ve mat ngu nghia
  mycol = mongodb(address=os.getenv("MONGODB_URI"))
  predict_model = [] # cau tra loi cua model
  ground_true = [] # cau tra loi thuc te
  with open("ingestion/data_test.json", "r", encoding='utf-8') as f:
    data = json.load(f)
    data = data["data"]
    dem = 0
    all_scores = [] # diem so cho moi dau hieu trong file
    name_signal = ['dau_hieu_{}'.format(i) for i in range(len(data))] # ten dau hieu
    for d in data:
      dau_hieu = d['dau_hieu'] # dau hieu cua nguoi benh
      ghi_chu = d['ghi_chu'] # ghi chu ve benh - day la ghi chu that

      ground_true.append(ghi_chu)

      q_vector = get_embedding(dau_hieu)
      response = rechieval_data(
            question_vector=q_vector,
            index_file=faiss.read_index("faiss.index"),
            top_k=10,
            mycol=mycol,   
            min_score=float(os.getenv("MIN_SCORE_RECHIEVAL")),
      )

      
      predict = llama_clients(response, "", dau_hieu)   # se danh gia theo ghi chu
      # print(predict)
      # print(dem)
      # dem = dem + 1
      predict_ghichu = predict['Ghi chú']
      print(predict_ghichu)
      review = llama_test_semantic(llama_test_semantic_prompt, predict_ghichu, ghi_chu)
      all_scores.append(int(review['score']))
  #     predict_model.append(predict_ghichu)
      # break
  # print(predict_model)
  # print(ground_true)
  with open("report/avg_score.txt", "w", encoding="utf-8") as f:
    f.write("điểm trung bình của model {}: {}".format(os.getenv("MODEL_CHAT"), mean(all_scores)))
  barhs(name_signal, all_scores)


if __name__ == "__main__":
  test_semantic()
  # top_k = [1, 25, 50, 75, 100]
  # percent = []
  # for t in top_k:
  #   pc = test(top_k=t)
  #   percent.append(pc)
  #   print(f"=== finish {t} ===")

  # data = {'Top_k': top_k, 'Percent': percent}
  # df = pd.DataFrame(data)

  # df.plot.bar(x='Top_k', y='Percent').get_figure().savefig('report/accuracy_query.png')
  




    
