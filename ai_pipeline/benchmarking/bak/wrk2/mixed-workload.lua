require "socket"
local time = socket.gettime()*1000
math.randomseed(time)
math.random(); math.random(); math.random()

local currencies = {"EUR", "USD", "JPY", "CAD"}
local product = {"0PUK6V6EV0", "1YMWWN1N4O", "2ZYFJ3GM2N", "66VCHSJNUP",
  "6E92ZMYYFZ", "9SIQT8TOJO", "L9ECAV7KIM", "LS4PSXUNUM", "OLJCESPC7Z"}

local function productRandom()
  return "/product/" .. product[math.random(1, #product)]
end
local function curRandom()
  return currencies[math.random(1, #currencies)]
end

-- Predefined user requests
local function index()
  return wrk.format("GET", "/")
end

local function setCurrency()
  local headers = {}
  headers["Content-Type"] = "application/x-www-form-urlencoded"
  -- headers["Cookie"] = "User" .. math.random(1, 10)
  headers["Cookie"] = "User1"
  local body
  body = "currency_code=" .. curRandom()
  return wrk.format("POST", "/setCurrency", headers, body)
end

local function browseProduct()
  return wrk.format("GET", productRandom())
end

local function viewCart()
  local headers = {}
  -- headers["Cookie"] = "User" .. math.random(1, 10)
  headers["Cookie"] = "User1"
  return wrk.format("GET", "/cart")
end

local function addToCart()
-- Should first get product, then add to cart, we do the later only
  local headers = {}
  -- headers["Cookie"] = "User" .. math.random(1, 10)
  headers["Cookie"] = "User1"
  headers["Content-Type"] = "application/x-www-form-urlencoded"
  local body
  local body = "product_id=" .. product[math.random(1, #product)] .. "&quantity=" .. math.random(1, 10)
  return wrk.format("POST", "/cart", headers, body)
end

local function checkout()
  local headers = {}
  headers["Content-Type"] = "application/x-www-form-urlencoded"
  -- headers["Cookie"] = "User" .. math.random(1, 10)
  headers["Cookie"] = "User1"
  local body = "email=someone@example.com&street_address=1600AmphitheatreParkway&zip_code=94043&city=MountainView&state=CA&country=USA&credit_card_number=4432-8015-6152-0454&credit_card_expiration_month=1&credit_card_expiration_year=2039&credit_card_cvv=672"
  return wrk.format("POST", "/cart/checkout", headers, body)
end

local function mixed()
    cur_time = math.floor(socket.gettime())
    local browse_ratio = 0.50
    local view_cart_ratio = 0.15
    local set_currency_ratio = 0.10
    local add_cart_ratio = 0.10
    local index_ratio = 0.08
    local checkout_ratio = 0.07
  
    local coin = math.random()
    if coin < browse_ratio then
      return browseProduct()
    elseif coin < view_cart_ratio + browse_ratio then
      return viewCart()
    elseif coin < set_currency_ratio + view_cart_ratio + browse_ratio then
      return setCurrency()
    elseif coin < add_cart_ratio + set_currency_ratio + view_cart_ratio + browse_ratio then
      return addToCart()
    elseif coin < index_ratio + add_cart_ratio + set_currency_ratio + view_cart_ratio + browse_ratio then
      return index()
    else 
      return checkout()
    end
  end

request = function()
  return mixed()
  -- return checkout()
  -- return addToCart()
end
