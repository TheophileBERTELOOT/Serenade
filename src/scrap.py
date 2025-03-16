from pathlib import Path

import click

from serenade.dataset.scrapper import Scrapper


# NOTE: Vérifier si le click.Path converti la chaîne de caractères donnée en default
@click.command()
@click.option(
    "-d",
    "--data-path",
    type=click.Path(exists=True),
    default=Path("C:\\Users\\baske\\projects\\Serenade\\data"),
)
@click.option(
    "-bird-csv",
    "--bird-species-csv",
    type=click.Path(exists=False),
    default=Path("C:\\Users\\baske\\projects\\Serenade\\data\\bird_species.csv"),
)
@click.option(
    "-caracteristics-dir",
    "--species-caracteristics-dir",
    type=click.Path(exists=True),
    default=Path("C:\\Users\\baske\\projects\\Serenade\\data\\caracs"),
)
@click.option(
    "-audios-dir",
    "--audios-dir",
    type=click.Path(exists=True),
    default=Path("C:\\Users\\baske\\projects\\Serenade\\data\\audios"),
)
@click.option(
    "--scrap-species", is_flag=True, show_default=True, default=False, type=bool
)
def scrap(
    data_path: Path,
    bird_species_csv: Path,
    species_caracteristics_dir: Path,
    audios_dir: Path,
    scrap_species: bool,
):
    scrapper = Scrapper(
        data_path=data_path,
        bird_species_csv=bird_species_csv,
        species_caracteristics_dir=species_caracteristics_dir,
        audios_dir=audios_dir,
    )

    if scrap_species:
        scrapper.scrap_species()

    scrapper.scrap_audios_api()


if __name__ == "__main__":
    scrap()
