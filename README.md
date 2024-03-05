# APIManager

平时自己使用多线程调用 OPENAI 的 API，现在只是初略地增加了消息通知工具。时间比较匆忙，代码整体不太完善，后面有时间再继续完善。

## Demo
```
from APIManager import AutoSender, repeat_until_calling_openai_api_successfully, get_account_manager
from typing import Dict, List
import openai
import concurrent.futures
import uuid


@repeat_until_calling_openai_api_successfully
def call_chatgpt(model: str, field: str, example: Dict, **kwargs) -> str:
    messages = [{"role": "user", "content": example["prompt"]}]
    completion = openai.ChatCompletion.create(model=model, messages=messages, temperature=1.1, top_p=1.0, max_tokens=4096)
    ret = completion['choices'][0]['message']['content']
    example[field] = ret


def generate(templates: List[str], api_model: str="gpt-3.5-turbo") -> List[Dict[str, str]]:
    examples = [{"prompt": template} for template in templates]
    
    global account_manager, sender
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for example in examples:
            future = executor.submit(
                call_chatgpt,
                api_model,
                "result",
                example,
                thread_id=uuid.uuid4(),
                sender=sender,
                account_manager=account_manager,
            )
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            future.result()

    return examples


account_manager = get_account_manager('openai_account/available.txt', 'openai_account/used.txt', multi_thread=True)
sender = AutoSender.from_sender_name("lark", webhook_addr="YOUR_WEBHOOK_ADDRESS", description="test_desc")

templates = ["test_case" for _ in range(10)]
examples = generate(templates)
print(examples)

```