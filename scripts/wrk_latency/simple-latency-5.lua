-- Load the LuaSocket library
local socket = require("socket")

-- Define a table to store ID and latency information
local requests_info = {}

-- Function to generate a unique ID
function generate_id()
    return string.format("%s_%d", os.date("%Y%m%d%H%M%S"), counter)
end

-- Define a global counter to generate unique IDs
counter = 0

-- Function to initialize the script
function setup(thread)
    -- Initialize the counter for each thread
    thread:set("counter", 0)
end

-- Function to handle each request
function request()
    local thread = wrk.thread
    -- Increment the counter for each request
    counter = counter + 1

    -- Generate a unique ID for this request
    local id = generate_id()

    -- Set the unique ID as a custom header in the request
    wrk.headers["X-Request-ID"] = id

    -- Send the request and record the start time
    local start_time = socket.gettime()
    local response = wrk.format("GET", "/cart", headers)

   -- Record the end time and calculate the latency in milliseconds
   local end_time = socket.gettime()
   local latency = (end_time - start_time) * 1000 * 1000


    -- Store the request ID and its latency in the global requests_info table
    table.insert(requests_info, {id = id, latency = latency})
    -- Store the request ID and latency in the thread's local storage
    thread:set("id", id)
    thread:set("latency", latency)
    _G[id] = latency
    print("id:",id," latency:", latency)
    return response
end

-- Function to handle the response after all requests have been completed
done = function (summary, latency, requests)
    -- Print the request ID and latency information for all requests
    print("Print the request ID and latency information for all requests")
    print("length of requests_info is :",#requests_info)
    for id, latency in pairs(_G) do
        print(string.format("Request ID:",id, " latency:",latency))
    end
    for i, info in ipairs(requests_info) do
        print(string.format("Request ID: %s, Latency: %d seconds", info.id, info.latency))
    end
end
