from scraper import download_pages
from parser import parse_notebooks
from utils import save_to_csv

def main():
    html_pages = download_pages()
    data = parse_notebooks(html_pages)
    save_to_csv(data)

if __name__ == "__main__":
    main()
