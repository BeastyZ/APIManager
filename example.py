from APIManager import AutoSender, openai_error_wrapper, get_account_manager
from typing import Dict, List
from openai import OpenAI
import concurrent.futures
import uuid


@openai_error_wrapper
def call_chatgpt(index: int, model: str, prompt: str, **kwargs) -> str:
    global client

    temperature = kwargs.pop('temperature', 1.0)
    top_p = kwargs.pop('top_p', 1.0)
    max_tokens = kwargs.pop('max_tokens', 4096)
    messages = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(model=model, 
                                                messages=messages, 
                                                temperature=temperature, 
                                                top_p=top_p, 
                                                max_tokens=max_tokens)
    ret = completion.choices[0].message.content
    return index, ret


def generate(prompts: List[str], api_model: str="gpt-3.5-turbo") -> List[Dict[str, str]]:
    examples = [{"prompt": prompt} for prompt in prompts]
    
    global account_manager, sender
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for index, example in enumerate(examples):
            future = executor.submit(
                call_chatgpt,
                index,
                api_model,
                example['prompt'],
                thread_id=uuid.uuid4(),
                sender=sender,
                account_manager=account_manager,
            )
            futures.append(future)

        results = []
        for future in concurrent.futures.as_completed(futures):
            index, ret = future.result()
            results.append((index, ret))
        results = sorted([result for result in results], key=lambda x: x[0])

    for i in range(len(results)):
        examples[i]['response'] = results[i][1]
    return examples


account_manager = get_account_manager('openai_account/available.txt', 'openai_account/used.txt', multi_thread=True)
sender = AutoSender.from_sender_name("lark", webhook_addr="YOUR_WEBHOOK_ADDRESS", description="test_desc")
client = OpenAI(
    api_key="sk-xxxx",
)

prompts = [f"你好呀~[{_}]" for _ in range(20)]
examples = generate(prompts)
print(examples)
