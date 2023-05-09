-- Define your request function
request = function()
    local start_time = os.clock() -- Record the start time
    local headers = {}
    headers["Cookie"] = "User1"
    local response = wrk.format("GET", "/cart", headers)
    local latency = (os.clock() - start_time) * 1e9 -- Calculate the latency in nanoseconds
    table.insert(latencies, latency) -- Store the latency in the latencies table
    return response
end

-- Define the report function
local report = function()
    print("Latencies (ns):")
    for _, latency in ipairs(latencies) do
        print(latency)
    end
end

-- Register the request function
wrk.request = request

-- Register the done function
done = function(summary, latency, requests)
    io.write("------------------------------\n")
    for _, p in pairs({ 50, 90, 99, 99.999 }) do
       n = latency:percentile(p)
       io.write(string.format("%g%%,%d\n", p, n))
    end
    print("lens of latency=",#latency)
    for i=0, #latency do
        print("latency is:",latency[i],"requst is:",requests[i])
    end

 end

-- Initialize the latencies table
latencies = {}

-- Call wrk.loop() to start the benchmark
wrk.loop = function()
    return wrk.format(nil, nil, nil, nil)
end





