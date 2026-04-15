from openai import OpenAI
import json
import time
import base64


def query_qwen(messages, base_url="http://60.12.233.42:6001/qwen25-32b/v1", model="Qwen2.5-32B-Instruct", stream=False):
    """
    调用大模型
    """
    client = OpenAI(
        api_key="1b12fe14-4f59-412f-b372-fa06f7fdcc9c",
        base_url=base_url
    )
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        stream=stream,
        extra_body={
            "top_k": 20,
            "chat_template_kwargs": {"enable_thinking": False},
        },
    )
    if stream:
        result_str = ""
        for item in completion:
            choice = item.choices
            # print(choice)
            if choice:
                content = choice[0].delta.content
                if content:
                    result_str += content
                    print(content, end='')
        return result_str
    else:
        # print(completion.choices[0].message.content)
        return completion.choices[0].message.content


qwen3_32b_url = "http://llm.a800.prod-ai.cai-inc.com/v1"
qwen3_32b_lora = "Qwen3.5-27B"

messages = [
    {
        "role": "user",
        "content": "你是谁"
    }
]
print()
resp = query_qwen(messages, base_url=qwen3_32b_url, model=qwen3_32b_lora, stream=True)