from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="kimi-k2-0711-preview",
    base_url="https://api.moonshot.cn/v1",
    api_key=os.getenv("MOONSHOT_API_KEY")
)

response = llm.invoke("Responda apenas: teste OK")
print(response.content)
