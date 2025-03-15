import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import json


class Scrapper:
    def __init__(self):
        self.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.base_url = "https://www.xeno-canto.org/api/2/recordings"
        
    def dlAudio(self,url,name,i):
        folder_path ="serenade/Dataset/Data/audios/"+name.replace(' ','_')+'/'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_url = url
        local_filename = folder_path+str(i)+'.mp3'
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            with open(local_filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Fichier téléchargé et sauvegardé sous : {local_filename}")
        else:
            print(f"Échec du téléchargement. Code HTTP : {response.status_code}")
        
    def scrapAudiosAPI(self):
        df = pd.read_csv('serenade/Dataset/Data/birdSpecies.csv',index_col=0)
        fieldsNeeded = ['id','gen','sp','ssp','en','cnt','loc','lat','lng','type','sex','stage','time','date','temperature']
        for index in df.index:
            species = df.loc[index]
            scientificName = species['scientificName']
            print('Dl the following species : ')
            print(scientificName)
            folderPath = "serenade/Dataset/Data/caracs/"+scientificName.replace(' ','_')+'/'
            if not os.path.exists(folderPath):
                os.makedirs(folderPath)
                query = scientificName
                response = requests.get(self.base_url, params={"query": query}).json()
                nbPages = response['numPages']
                nbRecordings = 0
                for i in range(1,nbPages+1):
                    print(f'page number {i}')
                    for recording in response['recordings']:
                        filtered_data = {key: recording[key] for key in fieldsNeeded if key in recording}
                        filePath = folderPath+str(filtered_data['id'])+'.json'
                        with open(filePath, "w", encoding="utf-8") as file:
                            json.dump(filtered_data, file, indent=4)
                        self.dlAudio(recording['file'],scientificName,filtered_data['id'])
                        nbRecordings+=1
                        if nbRecordings > 100:
                            break
                    if nbRecordings > 100:
                            break         
                    response = requests.get(self.base_url, params={"query": query,"page":str(i)}).json()
                
        
    def scrapAudios(self):
        df = pd.read_csv('serenade/Dataset/Data/birdSpecies.csv',index_col=0)
        nextPageExist = True
        page = 1
        directory = "serenade/Dataset/Data/"
        folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
        for index in df.index:
            i = 0
            while nextPageExist:
                species = df.loc[index]
                scientificName = species['scientificName']
                if  scientificName.replace(' ','_') in folders:
                    break
                url = species['link']
                if page == 1:
                    pageUrl = url
                response = requests.get(pageUrl, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    rows = soup.find_all("audio")
                    
                    for row in rows:
                        fileUrl = row.get('src')
                        self.dlAudio(fileUrl,scientificName,i)

                        i+=1
                else:
                    nextPageExist = False
                page+=1
                pageUrl = url +'?pg='+str(page)
                
        
    def scrapSpecies(self):
        url = "https://xeno-canto.org/collection/species/all?area=europe"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            bird_species = []
            filtered_rows = []
            rows = soup.find_all("tr")
            for row in rows:
                td = row.find("td", recursive=False)
                if td:
                    span = td.find("span", clas="common-name")
                    if span and span.find("a"):
                        filtered_rows.append(row)
                        
            for row in filtered_rows:
                link = row.find("td", recursive=False).find('span').find('a').get('href')
                scientificName = row.find_all("td")[1].text
                name = row.find("td", recursive=False).find('span').find('a').text
                bird_species.append([name,scientificName,link])
            print(f"Nombre d'espèces trouvées : {len(bird_species)}")
            df = pd.DataFrame(bird_species,columns=['name','scientificName','link'])
            print(df)
            df.to_csv('serenade/Dataset/Data/birdSpecies.csv')
        else:
            print(f"Échec de la requête. Code HTTP : {response.status_code}")

