from time import sleep
import numpy as np
import pandas as pd

from pytrends.request import TrendReq

pytrend = TrendReq()

def get_comp_url(artists):
    base = "https://trends.google.com/trends/explore?geo=US&q="
    max_num_artists = 5
    query = ""
    for artist in artists[:max_num_artists]:
        artist_str = artist.replace(" ","%20")
        query += artist_str
        query += ","
    final = base + query[:-1]
    return final

def comp(comps, comp_val, sleep_time=5, verbose=False):
    
    final = {"comp_val": comp_val, "comps": {}}
    num_iters = (len(comps) // 4) + 1
    for start in range(num_iters):
        if verbose:
            print("{} / {}".format(start,num_iters))
        comps_input = [comp_val] + comps[start*4:start*4+4]
        pytrend.build_payload(kw_list=comps_input)
        results = pytrend.interest_over_time().astype("float64", raise_on_error=False)
        results = results.iloc[-1,:-1]
        results /= results[0]
        for comp, val in results.items():
            final["comps"][comp] = val 
        
        if sleep_time > 0 and start < num_iters - 1:
            if verbose:
                print("sleeping {} seconds...".format(sleep_time))
            sleep(sleep_time)
    return final
