-- request_with_unique_id.lua

-- Declare a shared table to store unique IDs and latencies
local uniqueIds = {}
local latencies = {}

-- Function to generate a unique ID for each request
function generate_unique_id()
    local id = os.time() .. "-" .. math.random(10000)
    return id
end

-- Define the callback function to capture request latency and attach unique ID
function capture_latency_with_unique_id()
    local unique_id = generate_unique_id()
    wrk.request.headers["X-Unique-ID"] = unique_id
    uniqueIds[wrk.request] = unique_id  -- Store the unique ID in the shared table

    local start_time = os.clock()  -- Record the start time of the request
    wrk.event("request-start", unique_id, start_time)  -- Emit a custom event with the unique ID and start time
end

-- Register the request callback function
wrk.request = capture_latency_with_unique_id

-- Function to retrieve the unique ID and latency for a response
function get_unique_id_and_latency(response)
    local request = response.request
    local unique_id = uniqueIds[request]  -- Retrieve the unique ID from the shared table

    local end_time = os.clock()  -- Record the end time of the request
    local latency = end_time - response.request.start_time  -- Calculate the latency as the difference between end time and start time

    latencies[unique_id] = latency  -- Store the latency in the shared table
    return unique_id, latency
end

-- Function to modify the response data to include the unique ID and latency
function modify_response_data(response)
    local unique_id, latency = get_unique_id_and_latency(response)
    local original_response_data = response.body
    local modified_response_data = string.format("%s, Unique ID: %s, Latency: %.2f seconds", original_response_data, unique_id, latency)
    response.body = modified_response_data
end

-- Register the response callback function
wrk.response = modify_response_data

-- Function to print the unique ID and latency of each request after the benchmark is complete
function print_latencies()
    for unique_id, latency in pairs(latencies) do
        print(string.format("Unique ID: %s, Latency: %.2f seconds", unique_id, latency))
    end
end

-- Register the done callback function
wrk.done = print_latencies
