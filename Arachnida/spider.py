import argparse
import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
import shutil
import re
import string

parser = argparse.ArgumentParser(description='The spider program allow you to extract all the images from a website, recursively, by providing a url as a parameter.')
parser.add_argument('url', help='The URL of the site to get the images from')
parser.add_argument('-r', action='store_true', default=False, help='recursively downloads the images in a URL received as a parameter.')
parser.add_argument('-l', metavar="[N]", type=int, default=5, help='indicates the maximum depth level of the recursive download. If not indicated, it will be 5.')
parser.add_argument('-p', metavar="[PATH]", default="./data/", help='indicates the path where the downloaded files will be saved. If not specified, ./data/ will be used.')
args = parser.parse_args()

allowed_extensions = r"\.(png|jpg|jpeg|gif|bmp)$"
visited_urls = set()
session = requests.Session()

def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme) or os.path.isfile(url)
 
def process_images(imgs, save_path):
    for img in imgs:
        split_url = img.split("wordpress.")
        if len(split_url) > 1:
            new_url = "https://www." + split_url[1]
            download(new_url, save_path)
        else:
            download(img, save_path)

def get_all_images(url):
    if os.path.isfile(url):
        with open(url, 'r') as f:
            soup = bs(f, "html.parser")
    else:
        soup = bs(requests.get(url).content, "html.parser")

    urls = []
    for img in tqdm(soup.find_all("img"), "Extracting images"):
        img_url = img.attrs.get("src")
        if not img_url:
            continue
        img_url = urljoin(url, img_url)
        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass
        if is_valid(img_url) and re.search(allowed_extensions, img_url, re.IGNORECASE):
            urls.append(img_url)
    return urls

def download(url, pathname):
    if not os.path.isdir(pathname):
        os.makedirs(pathname)

    try:
        if os.path.isfile(url):
            shutil.copy(url, pathname)
        else:
            response = session.get(url)
            file_size = int(response.headers.get("Content-Length", 0))
            filename = os.path.join(pathname, url.split("/")[-1])

            with open(filename, "wb") as f:
                try:
                    progress = tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024,
                                    dynamic_ncols=True, desc=f"Downloading {url}")
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            progress.update(len(chunk))
                finally:
                    progress.close()
    except PermissionError:
        print(f"Failed to download or copy file.")

def recursive_download(url, depth=0):
    if depth > args.l or url in visited_urls:
        return
    visited_urls.add(url)
    imgs = get_all_images(url)
    process_images(imgs, args.p)
    soup = bs(requests.get(url).content, "html.parser")
    links = soup.find_all("a")
    for link in links:
        href = link.get("href")
        if href and not href.startswith("#"):
            absolute_url = urljoin(url, href)
            if is_valid(absolute_url) and absolute_url not in visited_urls:
                recursive_download(absolute_url, depth + 1)

def main():
    if not args.url or not is_valid(args.url):
        print("invalid or missing url")
        return 1
    if args.r:
        recursive_download(args.url)
    else:
        imgs = get_all_images(args.url)
        process_images(imgs, args.p)

if __name__ == "__main__":
    main()
