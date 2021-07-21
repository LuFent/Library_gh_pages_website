# -*- coding: cp1251 -*-

import argparse
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.status_code == 302:
        raise requests.HTTPError


def parse_book_page(url):
    try:

        response = requests.get(url, allow_redirects = False)
        check_for_redirect(response)
        response.raise_for_status() 

        soup = BeautifulSoup(response.text, 'lxml')

        title_tag = soup.find('table').find("td", {"class": "ow_px_td"}).find("div", {"id" : "content"}).find("h1")
        

        title = title_tag.text.split(" :: ")[0].strip('  ')
        author = title_tag.text.split(" :: ")[1].strip('  ')

        image_tag = soup.find("div", {"class": "bookimage"}).find('img')
        
        image = urljoin(url, image_tag["src"])
                  
        coments = []

        for coment in soup.findAll("div", {"class": "texts"}):
            coments.append(coment.find("span").text)

        janres = []

        for janre in soup.find("span", {"class": "d_book"}).find_all("a"):
            janres.append(janre.text)

        print("Жанры : " + str(janres))
        print("Коментарии : " + str(coments))
        print("Название : " + title)
        print("Автор : " + author)
        print("Обложка : " + image)
        print("-------------------")
        

        #file_name = sanitize_filename(book_id + ". "  + title_tag.text.split(" :: ")[0].strip('  ') + ".txt")

    except requests.HTTPError:
        print("Error")


def download_txt(url, file_name, folder='books/'):
    try:
        response = requests.get(url, allow_redirects = False)
        check_for_redirect(response)
        response.raise_for_status() 
                           

        with open(folder + file_name, 'wb') as file:
            file.write(response.text.encode())

    except requests.HTTPError:
        print("Error")
        


def main():
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--start_id', help='starting id')
    parser.add_argument('--end_id', help='ending id')

    args = parser.parse_args()

    print(args.start_id)
    print(args.end_id)
    url_ = "https://tululu.org/b9/"
    

    for book_id in range(int(args.start_id),int(args.end_id)):
        url = f"https://tululu.org/b{book_id}/"
        parse_book_page(url)



if __name__ == '__main__':
    main()