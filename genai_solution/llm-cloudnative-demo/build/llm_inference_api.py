from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModel
import uvicorn
import json
import datetime
import torch
import time
import argparse
import os
import llm_metrics
import threading

# DEVICE = "cpu"
DEFAULT_LLAMA_CPP_THREADS = 40

# class Model():
#     def __init__(self, model_name):
#         self.model_name = model_name
#         self.model = None
#         self.tokenizer = None
#         self.load_model()

app = FastAPI()


@app.get("/v1/models")
async def list_models(request: Request):
    answer = {
        "models": get_supported_models(),
        "status": 200,
        "time": get_time()
    }
    return answer


@app.post("/v1/model/update")
async def load_model(request: Request):
    global model, tokenizer

    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    model_name = json_post_list.get('model_name')
    if model_name == None:
        response = {
            "message": f'Need a model name',
            "status": 400,
            "time": get_time()
        }
        return response
    model_path = json_post_list.get('model_path')
    model_llama_cpp_threads = json_post_list.get('model_llama_cpp_threads')

    if model_name == "llam2-7b":
        from bigdl.llm.models import Llama
        modelclass = Llama
        if model_path == None:
            model_path = "/models/bigdl_llm_llama2_7b_q4_0.bin"
            if os.path.exists(model_path) == False:
                response = {
                    "message": f'Need a model path',
                    "status": 400,
                    "time": get_time()
                }
                return response
        if model_llama_cpp_threads == None:
            n_threads = DEFAULT_LLAMA_CPP_THREADS
        model = modelclass(model_path, n_threads=n_threads)

    elif model_name == "chatglm2-6b":
        # from transformers import AutoTokenizer, AutoModel
        if model_path == "":
            model_path = "/models/chatglm2-6b"
            if os.path.exists(model_path) == False:
                model_path = "THUDM/chatglm2-6b"

        tokenizer = AutoTokenizer.from_pretrained(
            model_path, trust_remote_code=True)
        model = AutoModel.from_pretrained(
            model_path, trust_remote_code=True).float()
        model.eval()
    # https://github.com/huggingface/transformers/blob/main/src/transformers/modeling_utils.py#L1028
    response = {
        "message": f'Successfully load model: {model_name}',
        "status": 200,
        "time": get_time()
    }
    return response


@app.post("/v1/completions")
async def completion(request: Request):
    print("------------------------------------------------------------")
    global model_name, model, tokenizer

    # parse request
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list.get('prompt')
    history = json_post_list.get('history')
    max_length = json_post_list.get('max_length')
    top_p = json_post_list.get('top_p')
    temperature = json_post_list.get('temperature')
    if prompt == None:
        response = {
            "message": f'Need a prompt',
            "status": 400,
            "time": get_time()
        }
        return response
    print(f'Get a prompt: {prompt}')

    # chat completion
    if model_name == "chatglm2-6b":  # use transformers/pytorch to infernece
        st = time.time()
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        ifer_st = time.time()
        output_ids = model.generate(input_ids,
                                    max_new_tokens=max_length if max_length else 2048,
                                    top_p=top_p if top_p else 0.7,
                                    temperature=temperature if temperature else 0.95)
        ifer_end = time.time()
        prompt_tokens = input_ids.shape[1]
        completion_ids = output_ids[0].tolist()[prompt_tokens:]
        completion = tokenizer.decode(completion_ids, skip_special_tokens=True)
        end = time.time()
        completion_tokens = len(completion_ids)
        latency_per_token = (ifer_end-ifer_st)*1000/completion_tokens
    elif model_name == "llama2-7b":  # use bigdl-llm/native/ggml to inference
        st = time.time()
        outputs = model(prompt)
        # todo: get only inference time from llama.cpp
        end = time.time()
        completion = outputs['choices'][0]['text']
        completion_tokens = outputs['usage']['completion_tokens']
        prompt_tokens = outputs['usage']['prompt_tokens']
        latency_per_token = (end-st)*1000/completion_tokens

    # print logs
    now = get_time()
    print("")
    print(now)
    print(f'prompt:\t{prompt}')
    print(f'history:\t{history}')
    print(f'completion:\t{completion}')
    print(f'prompt_tokens:\t{prompt_tokens}')
    print(f'completion_tokens:\t{completion_tokens}')
    print(f'inference duration:\t{end-st:.2f} s')
    print(f'inference latency:\t{latency_per_token:.2f} ms per token')
    print("------------------------------------------------------------")


    # struct response
    response = {
        "status": 200,
        "time": now,
        "prompt": prompt,
        "history": history,
        "completion": completion,
        "total_dur": end-st,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "latency_per_token": latency_per_token
    }
    
    request_metrics = llm_metrics.RequestMetrics(end-st,prompt_tokens,completion_tokens,latency_per_token, "200")
    llm_metrics.process_request_metrics(request_metrics)
    # torch_gc()
    return response


def get_supported_models():
    """
    Returns a list of supported models.
    """
    return ["chatglm2-6b", "llama2-7b"]


def get_time():
    """
    Returns now time(str).
    """
    now = datetime.datetime.now()
    now_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return now_time


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LLM inference service')
    parser.add_argument('-m', '--model-name', type=str, default="chatglm2-6b",
                        choices=["llama2-7b", "chatglm2-6b"],
                        help='LLM to load')
    parser.add_argument('-o', '--model-online', type=bool, default=False,
                        help='Load model online')
    parser.add_argument('-d', '--model-path', type=str, default="",
                        help='Local model path')
    parser.add_argument('-p', '--port', type=int, default=8000,
                        help='Service port')
    parser.add_argument('-e', '--metric_port', type=int, default=8090,
                        help='Metric port')                  
    parser.add_argument('-t', '--model-dtype', type=str, default="fp16",
                        choices=["fp16", "int8", "int4"],
                        help='Model data type')
    parser.add_argument('-q', '--int4', type=bool, default=False,
                        help='Load modal in 4bit, convert relecant layers into INT4 format')
    parser.add_argument('-n', '--llama-cpp-threads', type=int, default=DEFAULT_LLAMA_CPP_THREADS,
                        help='Threads for llama.cpp')
    args = parser.parse_args()

    model_name = os.environ.get('MODEL_NAME')
    model_path = os.environ.get('MODEL_PATH')
    model_dtype = os.environ.get('MODEL_DTYPE')
    svc_port = os.environ.get('SVC_PORT')
    metric_port = os.environ.get('METRIC_PORT')
    llama_cpp_threads = os.environ.get('LLAMA_CPP_THREADS')

    if model_name == None:
        model_name = args.model_name
    if model_path == None:
        model_path = args.model_path
    if model_dtype == None:
        model_dtype = args.model_dtype
    if svc_port == None:
        svc_port = args.port
    else:
        svc_port = int(svc_port)
    if metric_port == None:
        metric_port = args.metric_port
    else:
        metric_port = int(metric_port)   
    model_int4 = args.int4
    model_online = args.model_online

    if model_name not in get_supported_models():
        print(f'Unsupported model: {model_name}')
        exit(1)

    print(f'Loading model ...')
    st = time.time()
    if model_name == "chatglm2-6b":
        if model_dtype == "fp16":
            if model_online == True:
                model_path == "THUDM/chatglm2-6b"
            elif model_path == None:
                model_path = "/models/chatglm2-6b"
        elif model_dtype == "int8":
            if model_online == True:
                model_path == "THUDM/chatglm2-6b-int8"
            elif model_path == None:
                model_path = "/models/chatglm2-6b-int8"
        elif model_dtype == "int4":
            if model_online == True:
                model_path == "THUDM/chatglm2-6b-int4"
            elif model_path == None:
                model_path = "/models/chatglm2-6b-int4"

        tokenizer = AutoTokenizer.from_pretrained(model_path,
                                                  trust_remote_code=True)
        model = AutoModel.from_pretrained(model_path,
                                          trust_remote_code=True).float()
        model.eval()

    elif model_name == "llama2-7b":
        if llama_cpp_threads == None:
            llama_cpp_threads = args.llama_cpp_threads
        else:
            llama_cpp_threads = int(llama_cpp_threads)

        from bigdl.llm.models import Llama

        if model_dtype == "int4":
            if model_online == True:
                # model_path == "meta-llama/Llama-2-7b-hf"
                raise ValueError(
                    "bigdl-llm native int4 need to download and convert model to int4")
            elif model_path == None:
                model_path = "/models/bigdl_llm_llama2_7b.bin"
        else:
            raise ValueError(
                "Bigdl-llm native support int4 format Llama, fp16 format support in progress")

        modelclass = Llama
        model = modelclass(model_path, n_threads=llama_cpp_threads)
        tokenizer = None
    end = time.time()
    print(f'Model loaded from {model_path}, cost {end-st:.2f} s')

    metrics_thread = threading.Thread(target=llm_metrics.start_metrics_server, args=(metric_port,))
    metrics_thread.start()
    uvicorn.run(app, host='0.0.0.0', port=svc_port, workers=1)

