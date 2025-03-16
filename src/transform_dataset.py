from serenade.dataset.data_transformer import DataTransformer


def cli():
    dt = DataTransformer()
    dt.transformData()

if __name__ == '__main__':
    cli()