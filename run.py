# -*- coding: utf-8 -*-
from pathlib import Path
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked

import json

with open('data.json', 'r', encoding='cp1251') as fh:
    json_dicts = json.load(fh)


def on_reload():

    env = Environment(loader=FileSystemLoader('.'), autoescape=select_autoescape(['html', 'xml']))

    size_of_packages = 10

    template = env.get_template('template.html')

    Path("pages").mkdir(parents=True, exist_ok=True)
    
    pages_at_all = len(list(chunked(json_dicts, size_of_packages)))

    for index, books_packages in enumerate(list(chunked(json_dicts, size_of_packages))):

        rendered_page = template.render(books_data=list(chunked(list(books_packages), 2)), page_number=index + 1,
                                        pages_at_all=pages_at_all)

        with open(f"pages/index{index + 1}.html", 'w', encoding="utf8") as file:
            file.write(rendered_page)

    print("Site rebuilt")


def main():

    on_reload()

    server = Server()

    server.watch('template.html', on_reload)

    server.serve(root='.')


if __name__ == '__main__':
    main()
