-- Declare a table to store latencies
local latencies = {}

-- Function to capture request latency
function capture_latency(request)
    request.start_time = os.clock()  -- Record the start time of the request
end

-- Function to retrieve the latency for a response
function get_latency(response, request)
    local end_time = os.clock()  -- Record the end time of the request
    local latency = end_time - request.start_time  -- Calculate the latency as the difference between end time and start time

    latencies[#latencies + 1] = latency  -- Store the latency in the latencies table
end

-- Function to print the latencies of each request after the benchmark is complete
function print_latencies()
    print("Latencies:")
    for i, latency in ipairs(latencies) do
        print(string.format("Request #%d: %.2f seconds", i, latency))
    end
end

-- Register the request callback function
wrk.request = capture_latency

-- Register the response callback function
wrk.response = get_latency

-- Register the done callback function
wrk.done = print_latencies

-- Define your request function
request =  function ()
    local headers = {}
    headers["Cookie"] = "User1"
    return wrk.format("GET", "/cart", headers)
end

-- -- Register your request function
-- wrk.request = viewCart
wrk.done()