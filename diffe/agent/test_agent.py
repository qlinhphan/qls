from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
import os
# tao ra 1 con agent kiem tra tu vung
from langchain_classic.tools import tool
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from pydantic import Field, BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage


class Baseinp(BaseModel):
    exp: str = Field("Câu tiếng anh đầu vào của người dung")
@tool(args_schema=Baseinp)
def toolCheckVocab(exp: str):
    """Tool nhận xét trình độ sử dụng từ vựng tiếng anh của người dùng"""
    if "good" in exp:
        return {
            "result": "Khả năng sử dụng từ vựng tiếng anh của bạn rất tốt"
        }
    elif "bad" in exp:
        return {
            "result": "Trình độ sử dụng tiếng anh của bạn rất tệ"
        }
    else: 
        return {
            "result": "Trình độ sử dụng tiếng anh của bạn bình thường"
        }
    
llm = ChatOpenAI(model = os.getenv("MODEL_CHAT"), api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))

prompt = ChatPromptTemplate.from_messages([
    ("system",
     """Bạn là trợ lý AI học tiếng Anh.

- Nếu người dùng muốn đánh giá tiếng Anh thì BẮT BUỘC dùng tool.
- Nếu không liên quan thì yêu cầu nhập một câu tiếng Anh.
- Luôn trả lời bằng tiếng Việt.
- Cuối cùng luôn nói đây là quy tắc chấm điểm đặt ra bởi {name}
"""),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(
    llm,
    [toolCheckVocab],
    prompt
)

executor = AgentExecutor(
    agent=agent,
    tools=[toolCheckVocab]
)

hisory = []

while True:
    q = input("Ban: ")

    result = executor.invoke({
        "input": q,
        "history": hisory,
        "name": "Dr. Thanh"
    })

    # hisory.append({
    #     HumanMessage(content=q), AIMessage(content=result["output"])
    # })
    hisory.append(HumanMessage(content=q))
    hisory.append(AIMessage(content=result['output']))

    print(result["output"])


