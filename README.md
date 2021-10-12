# Library_parser

 Парсит сайт tululu.org получая основную информацию о книгах жанра  научной фантасти со страниц в определенном диапозоне и рендерит создает сервер с страницами с карточками книг

 &nbsp;

##### Варианты установки:

 &nbsp;

 * Скачать архив с кодом ( "Зеленая кнопка Code" ->  "Download ZIP" ) и распоковать его

 * Скачать репозиторий:
 ```
  cd <Директория установки >

  git clone https://github.com/LuFent/Library.git

 ```


##### Как пользваться (предпологается что python уже скачен)

 ```
  pip install -r requirements.txt

  python parse.py --start_page <...> --end_page <...> --dest_folder <...> --json_path <...> --skip_imgs --skip_txt

```
 * --start_page - Номер страницы с книгами с которой начнется парсинг
 * --end_page - Номер страницы с книгами на которой закончится парсинг


 Например, при параметрах:  

 ```
python parse.py --start_page 1 --end_page 5
 ```

Скрипт скачает все книги с 1ой по 5ую страницу. Чтобы запустить сервер нужно выполнить команду

```
python run.py
```



Готовый сайт находится по ссылке
 https://lufent.github.io/Library/pages/index1.html
