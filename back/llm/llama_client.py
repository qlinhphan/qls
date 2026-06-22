# import requests
import requests
import re
import json
from dotenv import load_dotenv
load_dotenv()
import os


def _read_ollama_response(response):
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "application/x-ndjson" not in content_type:
        try:
            return response.json().get("response", "")
        except json.JSONDecodeError:
            pass

    parts = []
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue

        data = json.loads(line)
        parts.append(data.get("response", ""))

        if data.get("done"):
            break

    return "".join(parts)


def extract_json(text):
    match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if match:
        text = match.group(1)

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "score": None,
            "reason": "Invalid JSON",
            "raw": text
        }


# llm chính để trả lời câu hỏi
def llama_clients(llama_clients_prompt, knowledge, context, q):
    prompt = llama_clients_prompt(knowledge, context, q)
    response = requests.post(
        os.getenv("CHAT_API_SERVER"),
        json={
            'model': os.getenv("MODEL_CHAT"),
            'prompt': prompt,
            'stream': True,
            'options': {
                'num_predict': 256,
                'temperature': 0
            }
        },
        stream=True,
    )
    res = _read_ollama_response(response)

    
    if '{' in res and '}' in res:
        return extract_json(res)
    else:
        return res


# tóm tắt cuộc hội thoại trong 1 phiên
def llama_summary_conversation(llama_summary_conversation_prompt, context):
    prompt = llama_summary_conversation_prompt(context)
    response = requests.post(
        os.getenv("CHAT_API_SERVER"),
        json={
            'model': os.getenv("MODEL_CHAT"),
            'prompt': prompt,
            'stream': False  
        }
    )
    res  = response.json()['response']
    return res


# llm check đầu ra trước khi trả về câu trả lời cho user
def llama_guardrail(guardrail_prompt, answer, ground_truth):
    prompt = guardrail_prompt(answer, ground_truth)
    response = requests.post(
        os.getenv("CHAT_API_SERVER"),
        json={
            'model': os.getenv("MODEL_CHAT"),
            'prompt': prompt,
            'stream': False  
        }
    )
    res  = response.json()['response']
    return res

# llm kiểm tra lỗi hồ sơ bệnh án
def llama_check_record(check_medical_record_logic_prompt, medical_record):
    prompt = check_medical_record_logic_prompt(medical_record)
    response = requests.post(
        os.getenv("CHAT_API_SERVER"),
        json={
            'model': os.getenv("MODEL_CHAT"),
            'prompt': prompt,
            'stream': False  
        }
    )
    res  = response.json()['response']
    return res



# đánh giá ngữ nghĩa
def llama_test_semantic(llama_test_semantic_prompt, answer, ground_truth):
    prompt = llama_test_semantic_prompt(answer, ground_truth)
    response = requests.post(
        os.getenv("CHAT_API_SERVER"),
        json={
            'model': os.getenv("MODEL_CHAT"),
            'prompt': prompt,

            'stream': False
        }
    )
    return extract_json(response.json()['response'])

if __name__ == "__main__":

    answer = "tôi nghĩ là con chó"
    ground_truth = "con chó"
    res = llama_test_semantic(answer, ground_truth)
    print(res)
