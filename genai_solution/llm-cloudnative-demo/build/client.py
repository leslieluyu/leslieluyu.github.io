import argparse


def test_llama_bigdl(prompt):
    import requests
    url = "http://127.0.0.1:8000/v1/completions"
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt,
            "history": []}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Request successful:")
        print(response.json())
    else:
        print("Request failed with status code:", response.status_code)


def test_chatglm2_6b(prompt):
    import requests
    url = "http://172.16.3.21:30021/v1/completions"
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt,
            "history": []}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Request successful:")
        print(response.json())
    else:
        print("Request failed with status code:", response.status_code)


def test_chatglm_openaiapi(prompt):
    import openai
    openai.api_base = "http://localhost:8080/v1"
    openai.api_key = "none"
    question = "Generate markdown documentation for this code. This documentation is meant to summarize the purpose and technical details of this operator. Use headings to breakdown the documentation into the following sections. Summary: a one sentence summary of this operators functionality. Inputs: briefly describe the inputs and their purpose. Parameters: briefly describe params and their purpose. Outputs: briefly describe outputs. Functionality: this section summarizes the run_step and the helper functions supporting it."
    question = f'{question} Answer in markdown and English, no Chinese.'

    # print(f'read')
    with open('./test2.txt', 'r', encoding='utf-8') as f:
        file = f.read()
        content = f'Given the context: {file}, answer the question or complete the following task: {question}'
        # print(content)

    for chunk in openai.ChatCompletion.create(
        model="chatglm2-6b",
        messages=[
            # {"role": "user", "content": "随便说句话"}
            # {
            #     "role": "system",
            #     "content": "You are a helpful assistant."
            # },
            {
                "role": "user",
                "content": content
            }
        ],
        stream=True
    ):
        if hasattr(chunk.choices[0].delta, "content"):
            print(chunk.choices[0].delta.content, end="", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='client to test service api')
    parser.add_argument('-m', '--model', type=str, default="chatglm2-6b",
                        help='model to test')
    parser.add_argument('-a', '--api', type=str, default="chat",
                        help='api to test')
    parser.add_argument('-p', '--prompt', type=str, default="what is ai?",
                        help='prompt')

    args = parser.parse_args()
    model = args.model
    api = args.api
    prompt = args.prompt

    if model == "llama2-7b":
        if api == "chat":
            test_llama_bigdl(prompt)
    elif model == "chatglm2-6b":
        if api == "chat":
            test_chatglm2_6b(prompt)
        elif api == "stream":
            test_chatglm_openaiapi(prompt)
