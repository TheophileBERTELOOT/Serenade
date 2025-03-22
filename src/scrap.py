from pathlib import Path

import click

from serenade.dataset.scrapper import Scrapper


# NOTE: Vérifier si le click.Path converti la chaîne de caractères donnée en default
@click.command()
@click.option(
    "-d",
    "--data-dir",
    type=click.Path(exists=True),
    default=Path("C:\\Users\\baske\\projects\\Serenade\\data"),
)
@click.option(
    "-rec-csv",
    "--recordings-csv",
    type=click.Path(exists=False),
    default=Path("C:\\Users\\baske\\projects\\Serenade\\data\\recordings.csv"),
)
@click.option(
    "-audios-dir",
    "--audios-dir",
    type=click.Path(exists=True),
    default=Path("C:\\Users\\baske\\projects\\Serenade\\data\\audios"),
)
@click.option(
    "--scrap-recordings", is_flag=True, show_default=True, default=False, type=bool
)
def scrap(
    data_dir: Path,
    recordings_csv: Path,
    audios_dir: Path,
    scrap_recordings: bool,
):
    scrapper = Scrapper(
        data_dir=data_dir,
        recordings_csv=recordings_csv,
        audios_dir=audios_dir,
    )

    if scrap_recordings:
        scrapper.scrap_species_api()

    scrapper.download_audios()


if __name__ == "__main__":
    scrap()
