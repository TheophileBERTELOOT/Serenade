import json
import os
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from joblib import Parallel, delayed


class Scrapper:
    URL_SPECIES = "https://xeno-canto.org/collection/species/all?area=europe"
    BASE_URL = "https://www.xeno-canto.org/api/2/recordings"
    FIELDS_NEEDED = [
        "id",
        "gen",
        "sp",
        "ssp",
        "en",
        "cnt",
        "loc",
        "lat",
        "lng",
        "type",
        "sex",
        "stage",
        "time",
        "date",
        "temperature",
    ]

    def __init__(
        self,
        data_path: Path,
        bird_species_csv: Path,
        species_caracteristics_dir: Path,
        audios_dir: Path,
    ) -> None:
        """
        Initializes the Scrapper object with paths for data storage.

        Args:
            data_path (Path): The base path where data will be stored.
            bird_species_csv (Path, optional): The path to the CSV file containing bird species information. Defaults to "serenade/Dataset/Data/birdSpecies.csv".
            species_caracteristics_dir (Path, optional): The directory where species characteristics will be stored. Defaults to "serenade/Dataset/Data/caracs/".
            audios_dir (Path, optional): The directory where audio files will be stored. Defaults to "serenade/Dataset/Data/audios/".
        """
        self.data_path = data_path
        self.bird_species_csv = bird_species_csv
        self.species_caracteristics_dir = species_caracteristics_dir
        self.audios_dir = audios_dir

        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def download_audio(self, url: str, name: str, i: int) -> None:
        """
        Downloads an audio file from a given URL and saves it to a specified directory.

        Args:
            url (str): The URL of the audio file.
            name (str): The name of the species for directory organization.
            i (int): The index used for naming the downloaded file.
        """
        folder_path = self.audios_dir.joinpath(name.replace(" ", "_"))
        if not folder_path.exists():
            folder_path.mkdir(exist_ok=True)
        file_url = url
        local_filename = folder_path.joinpath(f"{i}.mp3")
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            with open(local_filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Fichier téléchargé et sauvegardé sous : {local_filename}")
        else:
            print(f"Échec du téléchargement. Code HTTP : {response.status_code}")
            
    def _single_scrap_audios_api(self, df: pd.DataFrame, index: int) -> None:
        species = df.loc[index]
        scientific_name = species["scientific_name"]
        print("Download the following species : ")
        print(scientific_name)
        folder_path = self.species_caracteristics_dir.joinpath(
            scientific_name.replace(" ", "_")
        )
        if not folder_path.exists():
            folder_path.mkdir(exist_ok=True)
            query = scientific_name
            response = requests.get(self.BASE_URL, params={"query": query}).json()
            nb_pages = response["numPages"]
            nb_recordings = 0
            for i in range(1, nb_pages + 1):
                print(f"page number {i}")
                for recording in response["recordings"]:
                    filtered_data = {
                        key: recording[key]
                        for key in self.FIELDS_NEEDED
                        if key in recording
                    }
                    file_path = folder_path.joinpath(f"{filtered_data['id']}.json")
                    with open(file_path, "w", encoding="utf-8") as file:
                        json.dump(filtered_data, file, indent=4)
                    self.download_audio(
                        recording["file"], scientific_name, filtered_data["id"]
                    )
                    nb_recordings += 1
                    if nb_recordings > 100:
                        break
                if nb_recordings > 100:
                    break
                response = requests.get(
                    self.BASE_URL, params={"query": query, "page": str(i)}
                ).json()

    def scrap_audios_api(self) -> None:
        """
        Scrapes audio recordings using the Xeno-Canto API based on species information from a CSV file.
        """
        df = pd.read_csv(self.bird_species_csv, index_col=0)
        Parallel(n_jobs=8)(delayed(self._single_scrap_audios_api)(df, index) for index in df.index)

    def scrap_audios(self) -> None:
        """
        Scrapes audio recordings directly from HTML pages of the Xeno-Canto website.
        """
        df = pd.read_csv(self.bird_species_csv, index_col=0)
        next_page_exists = True
        page = 1
        folder_names = [
            p.name
            for p in self.data_path.iterdir()
            if p.is_dir()
        ]
        for index in df.index:
            i = 0
            while next_page_exists:
                species = df.loc[index]
                scientific_name = species["scientific_name"]
                if scientific_name.replace(" ", "_") in folder_names:
                    break
                url = species["link"]
                if page == 1:
                    page_url = url
                response = requests.get(page_url, headers=self._headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    rows = soup.find_all("audio")

                    for row in rows:
                        file_url = row.get("src")
                        self.download_audio(file_url, scientific_name, i)

                        i += 1
                else:
                    next_page_exists = False
                page += 1
                page_url = url + "?pg=" + str(page)

    def scrap_species(self) -> None:
        """
        Scrapes species information from the Xeno-Canto website and saves it to a CSV file.
        """
        response = requests.get(self.URL_SPECIES, headers=self._headers)
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
                link = (
                    row.find("td", recursive=False).find("span").find("a").get("href")
                )
                scientific_name = row.find_all("td")[1].text
                name = row.find("td", recursive=False).find("span").find("a").text
                bird_species.append([name, scientific_name, link])
            print(f"Nombre d'espèces trouvées : {len(bird_species)}")
            df = pd.DataFrame(bird_species, columns=["name", "scientific_name", "link"])
            print(df)
            df.to_csv(self.bird_species_csv)
        else:
            print(f"Échec de la requête. Code HTTP : {response.status_code}")