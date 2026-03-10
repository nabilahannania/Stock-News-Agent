# from langchain_openai import ChatOpenAI
from openai import OpenAI

from core import APPSetting


# llm_gpt = ChatOpenAI(
#     model="gpt-4.1-mini", temperature=0, api_key=APPSetting.OPENAI_API_KEY
# )

client = OpenAI(api_key=APPSetting.OPENAI_API_KEY)
