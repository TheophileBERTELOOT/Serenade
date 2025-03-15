from serenade.Dataset.Scrapper import Scrapper



def cli():
    scrapper = Scrapper()
    # scrapper.scrapSpecies()
    scrapper.scrapAudiosAPI()

if __name__ == '__main__':
    cli()