import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests
from joblib import Parallel, delayed
from tqdm import tqdm


class Scrapper:
    BASE_URL = "https://xeno-canto.org/api/2/recordings?query=cnt:france+grp:birds"

    def __init__(
        self,
        data_dir: Path,
        recordings_csv: Path,
        audios_dir: Path,
    ) -> None:
        """
        Initializes the Scrapper object with paths for data storage.

        Args:
            data_dir (Path): The base path where data will be stored.
            recordings_csv (Path): The path to the CSV file containing every data recordings.
            audios_dir (Path): The directory where audio files will be stored. Defaults to "serenade/Dataset/Data/audios/".
        """
        self.data_dir = data_dir
        self.recordings_csv = recordings_csv
        self.audios_dir = audios_dir

        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def download_single_audio(self, recordings_dataframe: pd.DataFrame, i: int) -> None:
        """
        Downloads an audio file from a given URL and saves it to a specified directory.

        Args:
            recordings_dataframe (pd.DataFrame): DataFrame containing the recording information.
            i (int): Index of the row in the DataFrame corresponding to the audio file to be downloaded.
        """
        target_path = Path(recordings_dataframe.loc[i, "audio_file_path"])
        download_link = recordings_dataframe.loc[i, "file"]
        
        if target_path.exists():
            print(f"Fichier {target_path} déjà existant")
        else:
            response = requests.get(download_link, stream=True)
            if response.status_code == 200:
                with open(target_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"Fichier téléchargé et sauvegardé sous : {target_path}")
            else:
                print(f"Échec du téléchargement. Code HTTP : {response.status_code}")

    def download_audios(self) -> None:
        """
        Download audio recordings using the Xeno-Canto API based on species information from a CSV file.
        """
        recordings_dataframe = pd.read_csv(self.recordings_csv)
        Parallel(n_jobs=8)(
            delayed(self.download_single_audio)(recordings_dataframe, index)
            for index in recordings_dataframe.index
        )

    def _extract_recordings(
        self, response: requests.models.Response
    ) -> List[Dict[str, Any]] | list:
        """
        Extracts recording information from the API response.

        Args:
            response (requests.models.Response): The API response containing the recordings data.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the recording information.
        """
        if response.status_code == 200:
            response_dict = json.loads(response.text)

            recordings_list = []
            for recordings in response_dict["recordings"]:
                recordings["file-name"] = re.sub(r"[\\\/\[\]\{\}\(\)\^\$|\?\*\+&:]", "", recordings["file-name"])
                recordings["file-name"] = re.sub(r"[- ]", "_", recordings["file-name"])
                
                recordings["audio_file_path"] = str(
                    self.audios_dir.joinpath(recordings["file-name"])
                )
                recordings_list.append(recordings)

            return recordings_list
        else:
            return []

    def scrap_species_api(self) -> None:
        """
        Scrapes the Xeno-Canto API to retrieve recording information for bird species in France.
        """
        response = requests.get(self.BASE_URL, headers=self._headers)
        time.sleep(1.0)

        every_recordings = []
        if response.status_code == 200:
            response_dict = json.loads(response.text)

            pbar = tqdm(
                range(response_dict["numPages"]),
                desc="Progression scrapping des enregistrements",
                total=response_dict["numPages"],
            )
            for i in pbar:
                recordings_url = self.BASE_URL + f"&page={i + 1}"

                response = requests.get(recordings_url)
                every_recordings += self._extract_recordings(response)

                time.sleep(1.0)

        df = pd.DataFrame(every_recordings)
        df.to_csv(self.data_dir.joinpath("recordings.csv"), index=None)
