local cjson = require("cjson")

ngx.log(ngx.INFO, "Starting route.lua execution")

ngx.req.read_body()
local request_body = ngx.req.get_body_data()

if request_body then
    ngx.log(ngx.INFO, "Request body received: ", request_body)

    local data, err = cjson.decode(request_body)
    if not data then
        ngx.log(ngx.ERR, "Failed to decode JSON: ", err)
        ngx.say("Invalid JSON")
        ngx.exit(ngx.HTTP_BAD_REQUEST)
        return
    end

    if data and data.model then
        local model = data.model
        ngx.log(ngx.INFO, "Model from request: ", model)

        if model == "Intel/neural-chat-7b-v3-3" then
            ngx.log(ngx.INFO, "Routing to /upstreamA")
            ngx.var.target = "/upstreamA"
        elseif model == "qianwen" then
            ngx.log(ngx.INFO, "Routing to /upstreamB")
            ngx.var.target = "/upstreamB"
        else
            ngx.log(ngx.INFO, "Unknown model: ", model)
            ngx.say("Unknown model")
            ngx.exit(ngx.HTTP_OK)
            return
        end

        -- Proxy the request to the target location
        ngx.exec(ngx.var.target)
    else
        ngx.log(ngx.INFO, "No model field in request body")
        ngx.say("Invalid request body")
        ngx.exit(ngx.HTTP_OK)
        return
    end
else
    ngx.log(ngx.INFO, "Request body is empty")
    ngx.say("Request body is empty")
    ngx.exit(ngx.HTTP_OK)
    return
end

ngx.log(ngx.INFO, "route.lua execution completed")