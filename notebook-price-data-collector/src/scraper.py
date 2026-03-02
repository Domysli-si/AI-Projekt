import requests

def download_pages():
    pages = []
    urls = [
        # sem prijdou URL
    ]

    for url in urls:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            pages.append(response.text)

    return pages
