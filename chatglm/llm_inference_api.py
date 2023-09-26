from fastapi import FastAPI, Request
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
DEFAULT_LLAMA_CPP_THREADS = 80
DEFAULT_SVC_PORT = 8000


class ModelWorker():
    def __init__(self, model_name, framework, dtype):
        self.model_name = model_name
        self.framework = framework
        self.dtype = dtype
        self.model = None
        self.tokenizer = None
        load_model()

    def load_model(self):
        return

    def generation(self):
        return

    def heart(self):
        return


class LlamaModel():
    def __init__(self):
        return


class ChatglmModel():
    def __init__(self):
        return


app = FastAPI()


@app.get("/v1/models")
async def list_models():
    resp = {
        "models": get_model_list(),
        "status": 200,
        "time": get_time()
    }
    return resp


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
        from transformers import AutoTokenizer, AutoModel
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
        CHATGLM_V2_PROMPT_FORMAT = "问：{question}\n\n答："
        with torch.inference_mode():
            st = time.time()
            prompt = CHATGLM_V2_PROMPT_FORMAT.format(question=prompt)
            input_ids = tokenizer.encode(prompt, return_tensors="pt")

            ifer_st = time.time()

            output_ids = model.generate(input_ids,
                                        max_new_tokens=max_length if max_length else 2048,
                                        top_p=top_p if top_p else 0.7,
                                        temperature=temperature if temperature else 0.95)
            ifer_end = time.time()
            prompt_tokens = input_ids.shape[1]
            completion_ids = output_ids[0].tolist()[prompt_tokens:]
            completion = tokenizer.decode(
                completion_ids, skip_special_tokens=True)
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


def get_model_list():
    """
    Returns a list of supported models.
    """
    model_list = {
        "llama2-7b": {
            "framework": {
                "bigdl-llm": {
                    "dtype": ["int4"],
                },
                "transformers": {
                    "dtype": ["fp16", "int8", "int4"],
                }
            },
            "dtype": ["fp16", "int8", "int4"],
        },
        "chatglm2-6b": {
            "framework": {
                "bigdl-llm": {
                    "dtype": ["int4"],
                },
                "transformers": {
                    "dtype": ["fp16"],
                }
            },
            "dtype": ["fp16", "int4"],
        }
    }
    return model_list


def get_time():
    """
    Returns now time(str).
    """
    now = datetime.datetime.now()
    now_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return now_time


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LLM inference service')
    parser.add_argument('-m', '--model-name', type=str,
                        choices=["llama2-7b", "chatglm2-6b"],
                        help='LLM to load')
    parser.add_argument('-o', '--model-online', action="store_true",
                        help='Load model online')
    parser.add_argument('-d', '--model-path', type=str, default="",
                        help='Local model path')
    parser.add_argument('-p', '--port', type=int,
                        help='Service port')
    parser.add_argument('-f', '--framework', type=str,
                        choices=["transformers", "bigdl-llm"],
                        help='Inference framework')
    parser.add_argument('-t', '--model-dtype', type=str,
                        choices=["fp16", "int8", "int4"],
                        help='Model data type')
    parser.add_argument('-i', '--ipex', action="store_true",
                        help='Use IPEX(intel-extension-for-pytorch)')
    parser.add_argument('-n', '--llama-cpp-threads', type=int, default=DEFAULT_LLAMA_CPP_THREADS,
                        help='Threads for llama.cpp')
    args = parser.parse_args()

    # get env variables
    model_name = os.environ.get('MODEL_NAME')
    model_path = os.environ.get('MODEL_PATH')
    model_dtype = os.environ.get('MODEL_DTYPE')
    framework = os.environ.get('FRAMEWORK')
    ipex = os.environ.get('IPEX')
    if ipex is not None:
        ipex = ipex.lower() == "true"
    else:
        ipex = False
    model_online = os.environ.get('MODEL_ONLINE')
    if model_online is not None:
        model_online = model_online.lower() == "true"
    else:
        model_online = False

    llama_cpp_threads = os.environ.get('LLAMA_CPP_THREADS')
    if llama_cpp_threads is not None:
        llama_cpp_threads = int(llama_cpp_threads)
    else:
        llama_cpp_threads = DEFAULT_LLAMA_CPP_THREADS

    svc_port = os.environ.get('SVC_PORT')
    if svc_port is not None:
        svc_port = int(svc_port)
    else:
        svc_port = DEFAULT_SVC_PORT

    # priority: command line args > env variables
    if args.model_name:
        model_name = args.model_name
    if args.model_path:
        model_path = args.model_path
    if args.model_dtype != model_dtype:
        model_dtype = args.model_dtype
    if args.framework:
        framework = args.framework
    if args.ipex:
        ipex = args.ipex
    if args.model_online:
        model_online = args.model_online
    if args.llama_cpp_threads:
        llama_cpp_threads = args.llama_cpp_threads
    if args.port:
        svc_port = args.port

    # verify parameters
    model_dict = get_model_list()
    if model_name not in model_dict:
        raise ValueError(f'Not supported model {model_name}')
    elif framework not in model_dict[model_name]["framework"]:
        raise ValueError(
            f'Not supported framework {framework} for {model_name}')
    elif model_dtype not in model_dict[model_name]["framework"][framework]["dtype"]:
        raise ValueError(
            f'Not supported dtype {model_dtype} for {model_name} inference with {framework}')

    # load model and tokenizer
    print(f'Loading {model_name}/{model_dtype} using {framework}')
    st = time.time()
    if model_name == "chatglm2-6b":
        if model_path == "":
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

        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path,
                                                  trust_remote_code=True)
        if framework == "transformers":  # use pytorch
            from transformers import AutoTokenizer, AutoModel
            # tokenizer = AutoTokenizer.from_pretrained(model_path,
            #                                           trust_remote_code=True)
            model = AutoModel.from_pretrained(model_path,
                                              trust_remote_code=True).float()
            model.eval()

            if args.ipex:
                print("Use IPEX to accelerate inference")
                import intel_extension_for_pytorch as ipex
                model = ipex.optimize(model)
                # todo: amp error in pytorch

                # if model_dtype == "fp16":
                #     model = ipex.optimize(model, dtype=torch.bfloat16)
                # with torch.no_grad(), torch.cpu.amp.autocast():
                #     input_example = tokenizer.encode(
                #         "what is ai?", return_tensors="pt")
                #     data = torch.randint(64794, size=[1, 100])
                #     model = torch.jit.trace(model)
                #     model = torch.jit.freeze(model)
        elif framework == "bigdl-llm":  # use bigdl
            from bigdl.llm.transformers import AutoModel

            # Normal format
            # model = AutoModel.from_pretrained(model_path,
            #                                   trust_remote_code=True)
            # INT4
            if model_dtype == "int4":
                model = AutoModel.from_pretrained(model_path,
                                                  load_in_4bit=True,
                                                  trust_remote_code=True)
    elif model_name == "llama2-7b":
        if llama_cpp_threads == None:
            llama_cpp_threads = args.llama_cpp_threads
        else:
            llama_cpp_threads = int(llama_cpp_threads)
        # todo: need re-struct
        if model_dtype == "int4":
            if model_online == True:
                # model_path == "meta-llama/Llama-2-7b-chat-hf"
                raise ValueError(
                    "bigdl-llm native int4 need to download and convert model to int4")
            elif model_path == None:
                model_path = "/models/bigdl_llm_llama2_7b_chat_q4_0.bin"
        else:
            raise ValueError(
                "Bigdl-llm native supports int4 format Llama")

        if framework == "bigdl-llm":
            from bigdl.llm.models import Llama
            modelclass = Llama
            if model_dtype == "int4":
                model = modelclass(model_path, n_threads=llama_cpp_threads)
                tokenizer = None
            else:
                raise ValueError(f'Not supported model dtype for {framework}')
    else:
        raise ValueError("Not supported model")
    end = time.time()
    print(f'Model loaded from {model_path}, cost {end-st:.2f} s')

    metrics_thread = threading.Thread(target=llm_metrics.start_metrics_server, args=(metric_port,))
    metrics_thread.start()
    uvicorn.run(app, host='0.0.0.0', port=svc_port, workers=1)
