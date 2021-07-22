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

        book_data = {}

        soup = BeautifulSoup(response.text, 'lxml')\

        title_tag = soup.find('table').find("td", {"class": "ow_px_td"}).find("div", {"id" : "content"}).find("h1")
 
 
        book_data["Íàçâàíèå"] = title_tag.text.split(" :: ")[0].strip('  ')
        book_data["Àâòîð"] = title_tag.text.split(" :: ")[1].strip('  ')

        image_tag = soup.find("div", {"class": "bookimage"}).find('img')     
        book_data["Îáëîæêà"] = urljoin(url, image_tag["src"])
                 
        
        book_data["Êîìåíòàðèè"] = []
        for coment in soup.findAll("div", {"class": "texts"}):
            book_data["Êîìåíòàðèè"].append(coment.find("span").text)

        book_data["Æàíðû"] = []
        for janre in soup.find("span", {"class": "d_book"}).find_all("a"):
            book_data["Æàíðû"].append(janre.text)
           
        return book_data

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
        
    
    for book_id in range(int(args.start_id),int(args.end_id)):
        url = f"https://tululu.org/b{book_id}/"

        for category, info in parse_book_page(url).items():
            print(f"{category} - {info}")
            
        print("--------------------")    



if __name__ == '__main__':
    main()
