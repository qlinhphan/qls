# from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
import requests
import json


def get_embedding(text_input):
    url = os.getenv("EMBED_API_SERVER")
    
    payload = {
        "model": os.getenv("MODEL_EMB"),
        "input": text_input
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        vector = data.get("embeddings")[0]
        
        return vector

    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối đến Ollama: {e}")
        return None