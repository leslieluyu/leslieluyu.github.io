









local function viewCart()
  local headers = {}
  headers["Cookie"] = "User1"
  return wrk.format("GET", "/cart")
end


request = function()
  return viewCart1()
end
