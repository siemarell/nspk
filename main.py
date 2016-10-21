from dataloader import DataLoader
from dataloader import CsvSource

def load_from_csv():
    dataLoader = DataLoader()
    dataLoader.load_metadata()
    dataLoader.load_data(CsvSource())

if __name__ == '__main__':
    load_from_csv()

