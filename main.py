from dataloader import DataLoader
from data_sources import CsvSource, PgSource

def load_from_csv():
    dataLoader = DataLoader()
    dataLoader.load_metadata()
    dataLoader.load_data(CsvSource())

def load_from_pg():
    dataLoader = DataLoader()
    #dataLoader.load_metadata()
    dataLoader.load_data(PgSource())


if __name__ == '__main__':
    load_from_pg()

