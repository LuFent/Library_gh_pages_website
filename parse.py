from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from pathlib import Path

import os
import argparse
import requests
import json


def get_id_from_url(url):   
    id = ""
    for symbol in reversed(url.strip("/")):
         
        if symbol == "b":
            break
        id += symbol
    
    id = id[::-1]    
    return id

def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError

def parse_book_page(url):
    response = requests.get(url)
    check_for_redirect(response)
    response.raise_for_status() 

    book_data = {}

    soup = BeautifulSoup(response.text, 'lxml')

    title_tag_selector = "table td.ow_px_td div#content h1"
    title_tag = soup.select_one(title_tag_selector)
    title_and_author = title_tag.text.split(" :: ")

    book_data["title"] = title_and_author[0].strip('\xa0').strip(' ')

    book_data["author"] = title_and_author[1].strip('\xa0').strip(' ')

    image_selector = "div.bookimage img"
    image_tag = soup.select_one(image_selector)

    book_data["cover"] = urljoin(url, image_tag["src"])
    
    book_data["comments"] = [coment.select_one("span").text for coment in soup.select("div.texts") ] 
            
    book_data["ganres"] = [ganre.text for ganre in soup.select("span.d_book a")]

    return book_data

def download_txt(parameters, file_name, dir):   
    url = "https://tululu.org/txt.php"

    response = requests.get(url, params = parameters, allow_redirects = False)  
    response.raise_for_status()                             

    safe_file_name = sanitize_filename(file_name)
    
    file_path = os.path.join(dir, "books" , safe_file_name)

    Path(os.path.join(dir, "books")).mkdir(parents = True, exist_ok = True)

    with open(file_path, 'wb') as file:
        file.write(response.text.encode())
     
def download_img(url, file_name, dir):

    image_response = requests.get(url)

    safe_file_name = sanitize_filename(file_name)
    file_path = os.path.join(dir, "images" , safe_file_name)
    Path(os.path.join(dir, "images")).mkdir(parents = True, exist_ok = True)

    with open(file_path, 'wb') as file:
        file.write(image_response.content)

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--start_page', type = int, default = 1, help = 'starting page')
    parser.add_argument('--end_page', type = int, default = 2, help = 'ending page')
    parser.add_argument('--dest_folder', default = os.path.join(os.path.abspath(os.curdir)) , help = 'books and imgs dir')
    parser.add_argument('--json_path', default = os.path.join(os.path.abspath(os.curdir)), help = 'json-file dir')

    parser.add_argument('--skip_imgs', action="store_true", help = 'skip img download')
    parser.add_argument('--skip_txt', action="store_true",  help = 'skip txt download')

    args = parser.parse_args()

    dir = args.dest_folder

    json_dir = args.json_path

    json_path = os.path.join(json_dir, "data.json" )
        
    json_dicts = []

    for page_id in range(args.start_page, args.end_page):

        url = f"https://tululu.org/l55/{page_id}"
        response = requests.get(url)
        response.raise_for_status() 

        soup = BeautifulSoup(response.text, 'lxml')
        
        book_cards_selector = "div#content"

        book_cards_list = soup.select_one(book_cards_selector).find_all("table")
        
        for book_card in book_cards_list:                  
            
            book_url = urljoin(url, book_card.find("a")["href"])
            book_id = book_url.split('/b')[-1]         
            
            book_data = parse_book_page(book_url)
         
            json_dicts.append(book_data)

            parameters =  {"id": book_id}

            if not args.skip_txt:
                download_txt(parameters, f"Книга {book_id} {book_data['title']}.txt", dir)

            if not args.skip_imgs:
                download_img(book_data['cover'],  f"Обложка книги {book_id} {book_data['title']}.png", dir)       

        with open (json_path, 'a+') as file:
                json.dump(json_dicts, file, ensure_ascii=False, sort_keys=True, indent=4)         


if __name__ == '__main__':
    main()