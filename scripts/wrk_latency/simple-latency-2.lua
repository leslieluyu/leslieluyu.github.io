local socket = require("socket")

latencies = {}

-- Define your request function
request = function()
    local start_time = os.time() -- Record the start time
    local headers = {}
    headers["Cookie"] = "User1"
    local response = wrk.format("GET", "/cart", headers)
    -- local latency = os.time() - start_time -- Calculate the latency in seconds
    -- local latency = (os.clock() - start_time) * 1e6 -- Calculate the latency in nanoseconds
    local latency = (socket.gettime() * 1e6) - start_time -- Calculate the latency in microseconds
    print("latency is " , latency, " μs")
    table.insert(latencies, latency) -- Store the latency in the latencies table
    -- print("lens of latencies=",#latencies)
    return response
end

-- Define the report function
report = function(latencies)
    print("Latencies (s): the length is ",#latencies)
    for _, latency in ipairs(latencies) do
        print(latency)
    end
end

-- Register the request and done functions
wrk.request = request
wrk.done = function()
    report(latencies) -- Call the report function when wrk is done
end

wrk.done() -- Call wrk.done() explicitly to trigger the printing of latencies
