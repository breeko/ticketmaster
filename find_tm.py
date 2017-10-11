import requests
from fake_useragent import UserAgent
import os

tm_key = open("ticketmasterkey.txt").read().strip()
max_pages = 5
ua = UserAgent()

def get_url(params):
    tm_url = "https://app.ticketmaster.com/discovery/v2/events.json?apikey={}".format(tm_key)
    for k,v in params.items():
        tm_url += "&{}={}".format(k,v.replace(" ","%20"))
    tm_url += "&size=200&sort=onSaleStartDate,asc"
    return tm_url
    
def get_event(params):
    tm_url = get_url(params)
    response = requests.get(tm_url).json()
    return response
    
def find_event_id(params,event_ids=None):
    response = get_event(params)
    
    if event_ids is None:
        event_ids = []
    
    if "_embedded" in response:
        events = response["_embedded"]["events"]
        for event in events:
            event_id = event["id"]
            city = event["_embedded"]["venues"][0]["city"]["name"]
            name = event["name"]
            date = event["dates"]["start"]["localDate"]
            event_ids.append({"id": event_id, "city": city, "name": name, "date": date})  
        
        new_page = int(params.get("page",1)) + 1
        if new_page < response["page"]["totalPages"] and new_page < max_pages:
            new_params = dict(params)
            new_params["page"] = str(new_page)
            return find_event_id(new_params, event_ids)
    return event_ids
    
def find_price_ranges(params):
    event_ids = find_event_id(params)
    prices = []
    for event in event_ids:
        event_with_price = dict(event)
        event_id = event["id"]
        tm_url = "https://app.ticketmaster.com/commerce/v2/events/{}/offers.json?apikey={}".format(event_id,tm_key)
        response = requests.get(tm_url).json()
        if "prices" in response:
            price = [data["attributes"]["value"] for data in response["prices"]["data"]]
            event_with_price["price"] = price
            prices.append(event_with_price)
    return prices

def find_stubhub_event_id(search_str):
    sh_url = "https://www.stubhub.com/find/s/?q={}".format(search_str.replace(" ","%20"))
    headers = {"User-Agent": str(ua.random)}
    return requests.get(sh_url,headers=headers)


x=find_stubhub_event_id("seinfeld new york")

x.json()
