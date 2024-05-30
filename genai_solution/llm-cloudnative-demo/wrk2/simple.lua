local http = require("socket.http")
local url = "http://llm.intel.com/v1/completions"
local body = '{"prompt": "What is AI?", "history": []}'

local res, code, headers, status = http.request{
   url = url,
   method = "POST", 
   headers = {
      ["Content-Type"] = "application/json"
   },
   source = ltn12.source.string(body),
   sink = ltn12.sink.table(table)
}

if code ~= 200 then
   error('HTTP request failed: ' .. code)
end

print(table.concat(res))