import os
#os.chdir("/home/branko/Documents/tickets/")
import requests
import csv
from collections import OrderedDict
import pandas as pd

api_key = open("ticketmasterkey.txt").read().strip()

req_root = "https://app.ticketmaster.com/discovery/v2/"

def get_req(req_type="events", params={}):
    params_str = ""
    for k,v in params.items():
        params_str += "{}={}&".format(k,v)
    params_str += "apikey={}".format(api_key)
    return "{}{}.json?{}".format(req_root, req_type,params_str)

def get_attrs(row):
    DEFAULT_NUM_ATTRACTIONS = 5
    DEFAULT_NUM_PRESALES = 15
    
    columns = ['numPresales','id','name','date','time','saleStart','saleEnd','numClassifications',
        'segment','genre','subGenre','numPriceRanges','minPrice','maxPrice','numVenues',
        'venueName','city','state','country']
    
    for num in range(DEFAULT_NUM_ATTRACTIONS):
        columns.append("attraction_{}".format(num))
    
    for num in range(DEFAULT_NUM_PRESALES):
        columns.append("presale_{}".format(num))
        columns.append("presaleStart_{}".format(num))
        columns.append("presaleEnd_{}".format(num))
        
    final = pd.DataFrame(index=[0], columns=columns)
    
    final.iloc[0]["id"] = row.get("id")
    final.iloc[0]["name"] = row.get("name")
    final.iloc[0]["date"] = row["dates"]["start"].get("localDate")
    final.iloc[0]["time"] = row["dates"]["start"].get("localTime")
    
    # Attractions
    if "attractions" in row["_embedded"]:
        for num, attraction in enumerate(row["_embedded"]["attractions"]):
            if num >= DEFAULT_NUM_ATTRACTIONS:
                break
            final.iloc[0]["attraction_{}".format(num)] = attraction.get("name")
            
    # Sales
    sales = row["sales"]
    final.iloc[0]["saleStart"] = sales["public"].get("startDateTime")
    final.iloc[0]["saleEnd"] = sales["public"].get("endDateTime")
    
    if "presales" in sales:
        final.iloc[0]["numPresales"] = len(sales["presales"])
        for num, presale in enumerate(sales["presales"]):
            final.iloc[0]["presaleStart_{}".format(num)] = presale.get("startDateTime")
            final.iloc[0]["presaleEnd_{}".format(num)] = presale.get("endDateTime")
            final.iloc[0]["presale_{}".format(num)] = presale.get("name")

    # Classifications
    final.iloc[0]["numClassifications"] = len(row["classifications"])
    classifications = row["classifications"][0]
    final.iloc[0]["segment"] = classifications["segment"].get("name")
    final.iloc[0]["genre"] = classifications["genre"].get("name")
    final.iloc[0]["subGenre"] = classifications["subGenre"].get("name")
    
    # Prices
    if "priceRange" in row:
        final.iloc[0]["numPriceRanges"] = len(row["priceRanges"])
        final.iloc[0]["minPrice"] = row["priceRanges"][0].get("min")
        final.iloc[0]["maxPrice"] = row["priceRanges"][0].get("max")
    
    # Venues
    final.iloc[0]["numVenues"] = len(row["_embedded"]["venues"])
    
    venue = row["_embedded"]["venues"][0]
    final.iloc[0]["venueName"] = venue.get("name")
    final.iloc[0]["city"] = venue["city"].get("name")    
    final.iloc[0]["state"] = venue["state"].get("stateCode")
    final.iloc[0]["country"] = venue["country"].get("countryCode")
    
    return final


def do_all(params = {}, filename="sales.csv", num_pages=10):
    write_headers = False if os.path.exists(filename) else True    
    if write_headers:
        ids = set()
    else:
        ids = set(pd.DataFrame.from_csv(filename)[["id"]].values.flat)
    
    with open(filename, 'a') as f:
        for num in range(num_pages):
            print("Page number: {} / {}".format(num, NUM_PAGES))
            req = get_req(params={**params, **{"size": 200, "page": num})
            response = requests.get(req)
            data = response.json()
            if "_embedded" in data:
                if "events" in data["_embedded"]:
                    rows = data["_embedded"].get("events")
            
                    for row in rows:
                        attrs = get_attrs(row)
                        ID = attrs[["id"]].iloc[0][0]
                        if ID not in ids:
                            attrs.to_csv(f, header=write_headers)
                            write_headers = False
                            ids.add(ID)
            
