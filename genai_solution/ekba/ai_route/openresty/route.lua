local cjson = require("cjson")

ngx.log(ngx.INFO, "Starting route.lua execution")

-- Define upstream servers in Lua
local upstream_servers = {
    ["Intel/neural-chat-7b-v3-3"] = "http://chatqna.benchmark-yulu.svc.cluster.local:8888",
    ["qianwen"] = "http://chatqna.benchmark-yulu2.svc.cluster.local:8888"
}

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

        -- Get the upstream server based on the model
        local upstream = upstream_servers[model]
        if upstream then
            ngx.log(ngx.INFO, "Routing to upstream: ", upstream)
            ngx.var.upstream = upstream
        else
            ngx.log(ngx.INFO, "Unknown model: ", model)
            ngx.say("Unknown model")
            ngx.exit(ngx.HTTP_OK)
            return
        end

        -- Proxy the request to the target upstream while maintaining the URI
        return ngx.exec("@dynamic_proxy")
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