-- request_with_unique_id.lua

-- Declare a shared table to store unique IDs
local uniqueIds = {}

-- Function to generate a unique ID for each request
function generate_unique_id()
    local id = os.time() .. "-" .. math.random(10000)
    return id
end

-- Define the callback function to capture request latency and attach unique ID
function capture_latency_with_unique_id(request, response, latency)
    local unique_id = generate_unique_id()
    request.headers["X-Unique-ID"] = unique_id
    uniqueIds[request] = unique_id  -- Store the unique ID in the shared table
    
    
    local headers = {}
    headers["Cookie"] = "User1"
    local response = wrk.format("GET", "/cart", headers)
    return response

end



-- Register the request function
wrk.request = capture_latency_with_unique_id

-- Function to retrieve the unique ID for a response
function get_unique_id(response)
    local request = response.request
    return uniqueIds[request]  -- Retrieve the unique ID from the shared table
end




done = function(summary, latency)
    print("Response Data with Unique IDs:")
    for i = 1, summary.requests do
        local request = summary[i]
        local response = request.response
        local unique_id = get_unique_id(response)
        print(string.format("Request %d: Unique ID: %s, Response: %s", i, unique_id, response.status))
    end
end