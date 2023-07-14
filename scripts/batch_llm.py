import functools
from bigdl.llm.models import Llama
print = functools.partial(print, flush=True)
MDL_NAME = "/home/ansible/yulu/BigDL/bigdl_llm_llama_int4_from_gptq.bin"

# Prompt the user for input
user_input = input("Enter something: ")

# Display the input
print("You entered:", user_input)

# # Shell script snippet
# shell_script_snippet = 'TZ="Asia/Shanghai" date "+%m%d%H%M%S"'
# # Execute the shell script and capture the output
# dt = subprocess.check_output(shell_script_snippet, shell=True, text=True).strip()


thds = [1, 2, 4, 8, 16, 32,40,60,80,120,160]
#thds = [1, 2, 4, 8, 16, 20,24,28,32,36,40,44,48,56,60,80,120,160]

#thds = [1]
iterations = 2

print("Start benchmarking ...")


for num_threads in thds:
    print(f"------- Running iterations with {num_threads} threads: Start -------" )
    for it in range(iterations):
        print(f"--------- Iteration {it + 1} Start ---------")
        llm = Llama(MDL_NAME, n_threads=num_threads)
        result = llm("what is ai")
        print(f"--------- Iteration {it + 1} End ---------")
    print(f"------- Running iterations with {num_threads} threads: End -------" )

print()
print()
print("End benchmarking ...")