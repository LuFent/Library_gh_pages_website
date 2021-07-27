from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from pathlib import Path
import os
import argparse
import requests


def check_for_redirect(response):
    if len(response.history) > 0:
        raise requests.HTTPError


def parse_book_page(book_id):

    url = f"https://tululu.org/b{book_id}/"

    response = requests.get(url)
    check_for_redirect(response)
    response.raise_for_status() 

    book_data = {}

    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('table').find("td", {"class": "ow_px_td"}).find("div", {"id" : "content"}).find("h1")
    title_and_author_string = title_tag.text.split(" :: ")

    book_data["title"] = title_and_author_string[0].strip('  ')

    book_data["author"] = title_and_author_string[1].strip('  ')

    image_tag = soup.find("div", {"class": "bookimage"}).find('img')     

    book_data["cover"] = urljoin(url, image_tag["src"])
                    
    book_data["comments"] = [coment.find("span").text for coment in soup.find_all("div", {"class": "texts"})] 

    book_data["ganres"] = [ganre.text for ganre in soup.find("span", {"class": "d_book"}).find_all("a")]
                
    return book_data


def download_txt(parameters, file_name, folder = 'books/'):
    
    url = f"https://tululu.org/txt.php?"

    response = requests.get(url, params = parameters, allow_redirects = False)  
    response.raise_for_status()                             

    safe_file_name = sanitize_filename(file_name)

    curent_dir = os.getcwdb().decode(encoding='UTF-8')

    Path(f"{curent_dir}\{folder}").mkdir(parents = True, exist_ok = True)
     
    with open(f"{folder}\{safe_file_name}", 'wb') as file:
        file.write(response.text.encode())


def download_img(url, file_name, folder = 'images/'):

    image_response = requests.get(url)

    safe_file_name = sanitize_filename(file_name)

    curent_dir = os.getcwdb().decode(encoding='UTF-8')

    Path(f"{curent_dir}\{folder}").mkdir(parents = True, exist_ok = True)

    with open(f"{folder}\{safe_file_name}", 'wb') as file:
        file.write(image_response.content)



def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--start_id', type = int, help = 'starting id')
    parser.add_argument('--end_id', type = int, help = 'ending id')

    args = parser.parse_args()
         
    for book_id in range(args.start_id, args.end_id):      
        try:

           
            book_data = parse_book_page(book_id)

            for category, info in book_data.items():
                    print(f"{category} - {info}")

            parameters =  {"id": f"{book_id}"}

            download_txt(parameters, f"{str(book_id)}. {book_data['title']}.txt")
            
            download_img(book_data["cover"], f"{str(book_id)}.jpg")

            print("------------------")

        except requests.HTTPError:
            pass
                     


if __name__ == '__main__':
    main()