
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from tqdm import tqdm
from pathlib import Path
from urllib.parse import quote


import os
import argparse
import requests
import json


json_dicts = []


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_pages_amount(url):
    response = requests.get(url)
    check_for_redirect(response)
    response.raise_for_status() 

    soup = BeautifulSoup(response.text, 'lxml')  
    selector = "table.tabs td.ow_px_td div#content p.center a.npage:last-child"
    
    last_page_number = soup.select_one(selector)
    
    return last_page_number.text


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
    
    book_data["comments"] = [coment.select_one("span").text for coment in soup.select("div.texts")]
            
    book_data["ganres"] = [ganre.text for ganre in soup.select("span.d_book a")]

    return book_data


def if_text_exist(parameters):   
    url = "https://tululu.org/txt.php"

    response = requests.get(url, params=parameters, allow_redirects=False)
    if response.text:
        return True
    else:
        return False


def download_txt(parameters, file_name, directory):
    url = "https://tululu.org/txt.php"

    response = requests.get(url, params=parameters, allow_redirects=False)
    response.raise_for_status()                             
           
    file_path = os.path.join(directory, "books", file_name)

    Path(os.path.join(directory, "books")).mkdir(parents=True, exist_ok=True)

    with open(file_path, 'wb') as file:
        file.write(response.text.encode())

     
def download_img(url, file_name, directory):

    image_response = requests.get(url)

    safe_file_name = sanitize_filename(file_name).replace(" ", "_")
    file_path = os.path.join(directory, "images", safe_file_name)
    Path(os.path.join(directory, "images")).mkdir(parents=True, exist_ok=True)

    with open(file_path, 'wb') as file:
        file.write(image_response.content)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--start_page', type=int, default=1, help='starting page')
    parser.add_argument('--end_page', type=int, default=get_pages_amount("https://tululu.org/l55/1/"),
                        help='ending page')
    parser.add_argument('--dest_folder', default=os.path.join(os.path.abspath(os.curdir)), help='books and imgs dir')
    parser.add_argument('--json_path', default=os.path.join(os.path.abspath(os.curdir)), help='json-file dir')

    parser.add_argument('--skip_imgs', action="store_true", help='skip img download')
    parser.add_argument('--skip_txt', action="store_true",  help='skip txt download')

    args = parser.parse_args()

    json_path = os.path.join(args.json_path, "data.json")
    pbar = tqdm(total=args.end_page - args.start_page + 1)

    for page_id in range(args.start_page, args.end_page):
        pbar.update(1)
        url = f"https://tululu.org/l55/{page_id}"
        response = requests.get(url)
        response.raise_for_status() 

        soup = BeautifulSoup(response.text, 'lxml')
        
        book_cards_selector = "div#content"

        book_cards = soup.select_one(book_cards_selector).select("table")
        
        for book_card in book_cards:                  
            
            book_url = urljoin(url, book_card.select_one("a")["href"])
            book_id = book_url.split('/b')[-1]         
            
            book_data = parse_book_page(book_url)       

            parameters = {"id": book_id}

            if if_text_exist(parameters):

                if not args.skip_txt:
                    file_name = sanitize_filename(f"book_{book_id}_{book_data['title']}.txt").replace(" ", "_")
                    book_data['text_path'] = ".." + "/" + "books" + "/" + file_name
                    download_txt(parameters,  sanitize_filename(f"book_{book_id}_{book_data['title']}.txt")
                                 .replace(" ", "_"), args.dest_folder)

                if not args.skip_imgs:
                    file_name = sanitize_filename(f"book_cover_{book_id}_{book_data['title']}.png").replace(" ", "_")
                    book_data['cover_path'] = ".." + "/" + "images" + "/" + file_name
                    download_img(book_data['cover'], f"book_cover_{book_id}_{book_data['title']}.png", args.dest_folder)

                json_dicts.append(book_data)
    pbar.close()
    with open(json_path, 'a+') as file:
        json.dump(json_dicts, file, ensure_ascii=False, sort_keys=True, indent=4)    
    

if __name__ == '__main__':
    main()
