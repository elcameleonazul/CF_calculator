import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

stl="https://cyclingfantasy.cc/fr/races/cx-world-cup-antwerpen-we-we-2024/startlist"
pattern = r"/races/(.*?)/startlist" # Rechercher avec la regex 
match = re.search(pattern, stl) 
if match: 
    race = match.group(1)
full_Rider=[]
full_Prix=[]
response = requests.get(stl, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:1.0) Gecko/20100101 Firefox/1.0"})
response.raise_for_status()  # Lève une erreur si le statut HTTP est 4xx ou 5xx
soup = BeautifulSoup(response.content, "html.parser")
Rider=soup.find_all("p",style="flex:1;font-size:14px")
Rider_link=soup.find_all("a",style="display:flex;flex:1;gap:4px")
for links in Rider :
    full_Rider.append(links.text)
for links in Rider_link :
    href = links.get('href')
    profil=f"https://cyclingfantasy.cc{href}"
    response = requests.get(profil, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:1.0) Gecko/20100101 Firefox/1.0"})
    response.raise_for_status()  # Lève une erreur si le statut HTTP est 4xx ou 5xx
    soup = BeautifulSoup(response.content, "html.parser")
    #bloc_prix = soup.find('div', class_='rider-container')
    #bloc_prix2= bloc_prix.find('div',class_='frame')
    bloc_prix3= soup.find_all('div', style="display:flex;flex-direction:column;align-items:center")
    for div in bloc_prix3: 
        p_elements = div.find_all('p', style="font-size:14px;font-weight:bold") 
        for p in p_elements: 
            if p.text in ["200","400","600","800","1000","1200"]:
                prix=p.text
                full_Prix.append(prix)
if len(full_Prix) == len(full_Rider) :
    parameters= pd.concat([pd.Series(full_Rider),pd.Series(full_Prix)],axis=1)
    parameters.columns=["Rider","Price"]
    parameters.to_pickle(f"C:/Users/coich/Documents/hugo/A2L/CF_calculator/Race/{race}.pkl")
    

