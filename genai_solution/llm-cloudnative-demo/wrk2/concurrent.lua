-- Max concurrent requests
local maxConcurrent =   3

-- Request body
local reqBody = '{"prompt": "What is AI?", "history": []}'

-- Target URL
local url = "v1/completions"

-- Pending requests counter
local pending = 0

-- Queue for failed requests
local queue = {}

-- Function to send requests
local function sendRequest()
  pending = pending + 1
  local res, err = wrk.format("POST", "/" .. url, nil, reqBody)
  print("after  format")
  return res, err
end

-- Request function
function request()
  print("enter reqeust")
  while true do
    if pending >= maxConcurrent then
      wrk.thread:sleep(0.01) -- Adjust sleep duration as needed
    else
      print("send reqeust")
      local res, err = sendRequest()

      if res then
        print("get res")
        local status = res and res.status
        pending = pending - 1
        return
      elseif err == "SOCKET_ERROR : Connection refused" then
        table.insert(queue, reqBody)
      else
        pending = pending - 1
      end
    end
  end
end

-- Response handler
function response(status, headers, body)
  if status == 502 and #queue > 0 then
    local req = table.remove(queue, 1)
    sendRequest(req)
  end
end
