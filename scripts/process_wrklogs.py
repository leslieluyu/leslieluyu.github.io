import os
import time
import re
import json
import argparse


PATH="memcha_ns4-r6-m1_03"
DIR_PREFIX="memcha_ns4-r6-m1_"
WRK_PREFIX="wrk-result.stdout.ns"
NS=4
OUTPUT="wrk_result.json"


filename="wrk-result.stdout.ns1-client"

#wrk_logs=[]
wrk_datas=[]
wrk_dirs=[]

def time_to_ms(value, unit):
    RATIOS = {
        'us': 0.001,
        'ms': 1,
        's': 1000,
        'm': 60000,
        'h': 3600000,
    }

    if unit not in RATIOS:
        raise ValueError('Invalid unit {}'.format(unit))
    return value * RATIOS[unit]


def prepare():
    files = os.listdir(PATH)
    for f in files:
        #print("f=" + f)
        if f.startswith(WRK_PREFIX):
            print ("Found it! " + f)
            wrk_logs.append(f)
    for w in wrk_logs:
        filename=PATH+"/"+w
        #print("wrk_log="+filename)
        f=open(filename, 'r')
        wrk_datas.append(f.read())

def getDirs_old():
    all_files,all_dirs=[],[]
    for root, dirs, files in os.walk('.'):
        for file in files:
            all_files.append(os.path.join(root,file))
        
        for dir in dirs:
            all_dirs.append(os.path.join(root,dir))
    
    print(all_dirs)


def getDirs(PATH="."):
    files,dirs=[],[]
    #print("PATH=" + PATH)
    for item in os.listdir(PATH):
        #print(item)
        if os.path.isfile(os.path.join(PATH,item)):
            #print(item)
            files.append(item)
        elif os.path.isdir(os.path.join(PATH,item)):
            if item.startswith(DIR_PREFIX):
                print ("Found WRK DIR! " + item)
                wrk_dirs.append(item)
            dirs.append(item)
    #print("all dirs="+''.join(dirs))

    print(wrk_dirs)
    return sorted(wrk_dirs)

def getWRKDatasByDir(dir):
    print("getWRKDatasByDir : " + dir)
    files = os.listdir(dir)
    datas = []
    wrk_logs = []
    for f in files:
        #print("f=" + f)
        if f.startswith(WRK_PREFIX):
            print ("Found it! " + f)
            wrk_logs.append(f)
    for w in sorted(wrk_logs):
        filename=dir+"/"+w
        print("wrk_log="+filename)
        f=open(filename, 'r')
        datas.append(f.read())
    return datas

    
def export(result):
    #print("result is??="+result)
    with open(OUTPUT, 'a') as f:
        #print("json.dumps="+json.dumps(result))
        f.write(json.dumps(result)+"\n")

def run():
    wrk_datas=[]
    #0. get wrk_dirs
    wrk_dirs = getDirs(PATH)
    for dir in wrk_dirs:
        #print("wrk_dirs="+''.join(wrk_dirs));
        #1. get wrk_datas
        wrk_datas = getWRKDatasByDir(PATH+"/"+dir)
        print("wrk_datas.length="+str(len(wrk_datas)))
        #2parse wrk_datas merge to one result
        result = _ParseWrkOutput(wrk_datas,
                                         {'workload': 'mixed-workload_type_1',
                                          'rate': 0,
                                          'namespace_count': 0,
                                          'rate_total': 0,
                                          'duration': 0,
                                          'threads': 0,
                                          'connections': 0,
                                          'connections_total': 0,
                                          }
                                         )
        result["runs"]= os.path.basename(dir)

        #3.export(append) result to  file
        print("Before export runs:" + dir + " to " + OUTPUT)
        print("result is:"+str(result))
        export(result)                    



def _ParseWrkOutput(outputs, metadata):
    request_throughput = 0.0
    results_metadata = metadata.copy()
    percentile_pattern = re.compile(r"^\s*([0-9]{2,3}\.[0-9]{3}\%)\s*([0-9]+\.[0-9]*)(\w+)\s*$", flags=re.MULTILINE)
    counts_pattern = re.compile(r"^\s*([0-9]+)\s*requests\s*in\s([0-9]+\.[0-9]*)(\w),\s*([0-9]+\.[0-9]*)(\w+)\s*read$", flags=re.MULTILINE)
    errors_pattern = re.compile(r"^\s*Socket errors:\s*connect\s*([0-9]+),\s*read\s*([0-9]+),\s*write\s*([0-9]+),\s*timeout\s*([0-9]+)$", flags=re.MULTILINE)
    retcode_pattern = re.compile(r"^\s*Non-2xx or 3xx responses:\s*([0-9]+)$", flags=re.MULTILINE)
    requests_pattern = re.compile(r"^Requests/sec:\s*([0-9]*\.[0-9]*)$", flags=re.MULTILINE)
    wrk_pattern = re.compile(r"^Run wrk with -D exp -T\s*(?P<timeout>[0-9]+)s\s*-t\s*(?P<threads>[0-9]+)\s*-c\s*(?P<connections>[0-9]+).+-d\s*(?P<duration>[0-9]+)\s*-R\s*(?P<rate>[0-9]+).*$", flags=re.MULTILINE)

    


    for output in outputs:
      # percentiles
      def _MetadataPercentile(key, value, unit):
        """ record worst case for each percentile across all clients """
        v = time_to_ms(value, unit)
        try:
          if v > results_metadata[key]:
            results_metadata[key] = v
        except KeyError:
          results_metadata[key] = v
      for match in percentile_pattern.finditer(output):
        _MetadataPercentile(match.group(1), float(match.group(2)), match.group(3))

      # counts
      def _MetadataCount(key, value):
        try:
          results_metadata[key] += value
        except KeyError:
          results_metadata[key] = value
      #print('output='+ output)
      match = counts_pattern.search(output)
      #print('match=',match)
      _MetadataCount("request_count", int(match.group(1)))
      results_metadata["time"] = match.group(2) + match.group(3)  # don't aggregate
      # socket errors
      match = errors_pattern.search(output)
      _MetadataCount("connect_error_count", int(match.group(1)) if match else 0)
      _MetadataCount("read_error_count", int(match.group(2)) if match else 0)
      _MetadataCount("write_error_count", int(match.group(3)) if match else 0)
      _MetadataCount("timeout_error_count", int(match.group(4)) if match else 0)
      # http errors
      match = retcode_pattern.search(output)
      _MetadataCount("http_error_count", int(match.group(1)) if match else 0)
      # throughput in requests (primary metric of interest)
      match = requests_pattern.search(output)
      request_throughput += float(match.group(1))

      # other meta
      match = wrk_pattern.search(output)
      results_metadata["rate"]=match.groupdict()["rate"]
      results_metadata["namespace_count"]=NS
      print("rate_total=" + str(results_metadata["rate_total"] ))
      _MetadataCount("rate_total",int(match.groupdict()["rate"]))
      results_metadata["duration"]=match.groupdict()["duration"]
      results_metadata["threads"]=match.groupdict()["threads"]
      results_metadata["connections"]=match.groupdict()["connections"]
      _MetadataCount("connections_total",int(match.groupdict()["connections"]))

      results_metadata["requests/sec"]=request_throughput;
      
    #print("Result is :"+json.dumps(results_metadata))
    return results_metadata
    #return sample.Sample("Request Throughput", request_throughput, "requests/sec", results_metadata)

def processfile():
        return _ParseWrkOutput(wrk_datas,
                                         {'workload': 'mixed-workload_type_1',
                                          'rate': 0,
                                          'namespace_count': 0,
                                          'rate_total': 0,
                                          'duration': 0,
                                          'threads': 0,
                                          'connections': 0,
                                          'connections_total': 0,
                                          }
                                         )


def test():
    # str = "  2075056 requests in 1.00m, 857.93MB read"
    # counts_pattern = re.compile(r"^\s*([0-9]+)\s*requests\s*in\s([0-9]+\.[0-9]*)(\w),\s*([0-9]+\.[0-9]*)(\w+)\s*read$", flags=re.MULTILINE)
    # match = counts_pattern.search(str)
    # print('match=',match)
    # print('match.group(0)=',match.group(0))
    # print('match.group(1)=',match.group(1))

    str = "Run wrk with -D exp -T 5s -t 24 -c 1920 -s scripts/hotel-reservation/mixed-workload_type_1.lua -d 60 -R 150000"
    f=open("memcha_ns4-r6-m1_03/wrk-result.stdout.ns1-client", 'r')
    str = f.read()
    # print("str="+str)
    errors_pattern = re.compile(r"^\s*Socket errors:\s*connect\s*([0-9]+),\s*read\s*([0-9]+),\s*write\s*([0-9]+),\s*timeout\s*([0-9]+)$", flags=re.MULTILINE)
    #wrk_pattern = re.compile(r"^\s*Run wrk with -D exp -T\s*([0-9]+)s$")
    wrk_pattern = re.compile(r"^Run wrk with -D exp -T\s*(?P<timeout>[0-9]+)s\s*-t\s*(?P<threads>[0-9]+)\s*-c\s*(?P<connections>[0-9]+).+-d\s*(?P<duration>[0-9]+)\s*-R\s*(?P<rate>[0-9]+).*$", flags=re.MULTILINE)
    match = wrk_pattern.search(str)
    # print('match=',match)
    i=0
    # for g in match.groups():
    #     print("match.group" + g )
    # print(match.groupdict())
    # print("timeout="+match.groupdict()["timeout"])
    
    #print('match.group(1)=',match.group(1))
    

def _init():
    parser = argparse.ArgumentParser(description='Test for argparse')
    parser.add_argument('--DIR', '-d', help='path of wrklog folders, Default is .',default=".",required=True)
    parser.add_argument('--namespace', '-n', help='namespace nums, Defualt is 4', default=4,required=True)
    parser.add_argument('--dirprefix', '-r', help='prefix of each runs(Actually is folder name), Default is memcha_ns4-r6-m1_', default="memcha_ns4-r6-m1_")
    parser.add_argument('--wrkprefix', '-w', help='prefix of each wrklog files of each namespace, Default is wrk-result.stdout.ns', default="wrk-result.stdout.ns")
    parser.add_argument('--output', '-o', help='output filename, Default is wrk_result.json', default="wrk_result.json")
    args = parser.parse_args()
    print(args)
    #print("dir:"+args.DIR+" namespace:"+args.namespace+" dirprefix:"+args.dirprefix+" wrkprefix:"+args.wrkprefix+" output:"+args.output)
    global PATH,DIR_PREFIX,WRK_PREFIX,NS,OUTPUT
    PATH=args.DIR
    DIR_PREFIX=args.dirprefix
    WRK_PREFIX=args.wrkprefix
    NS=args.namespace
    OUTPUT=args.output

if __name__=="__main__":
    _init()
    #prepare()
    #result=processfile()
    #result["filename"]="xxxxx"
    #print("result ====="+res)
    #export(result)
    #test()
    #print(getDirs("/home/yulu/yulu/hotel"))
    run()


