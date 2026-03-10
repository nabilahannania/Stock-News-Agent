from openai import OpenAI

from core import APPSetting

client = OpenAI(api_key=APPSetting.OPENAI_API_KEY)
