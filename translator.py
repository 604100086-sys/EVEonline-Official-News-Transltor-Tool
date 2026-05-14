import csv
import requests
from pathlib import Path
file_path = 'terms/terms (1).csv'

with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    glossary = {}
    for row in reader:
        glossary[row[0]] = row[1]

class LLMTranslator:

    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def _translate_with_context(self, text, glossary, target_lang='Chinese', max_terms=300):
        """将术语表作为上下文注入"""
        # 如果术语太多，只取最重要的
        if len(glossary) > max_terms:
            glossary = dict(list(glossary.items())[:max_terms])

        # 构建术语表字符串
        glossary_str = "\n".join([f"'{k}' -> '{v}'" for k, v in glossary.items()])

        system_prompt = f"""你是一个游戏本地化专家。以下是本次翻译必须遵守的术语对照表：

{glossary_str}

要求：
1. 严格使用上述术语对照表中的翻译
2. 保持术语翻译的一致性
3. 不添加任何额外解释
4. 只返回翻译结果"""

        user_prompt = f"将以下文本翻译成{target_lang}：\n\n{text}"

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,  # 降低温度以提高一致性
            "top_p": 0.9
        }

        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()["choices"][0]["message"]["content"]
translator = LLMTranslator(api_key="sk-508065e0d2714bebb0a7ea132d4081fb")
text = '''

'''
output = translator._translate_with_context(text=text,glossary=glossary,target_lang='English')
print(output)


