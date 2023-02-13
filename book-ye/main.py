import logging, collections, csv

import bs4
import requests


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('by')

ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'title',
        'author',
        'genre',
        'book_url',
        'image_url',
    ),
)

HEADERS = [
    'Назва',
    'Автор',
    'Жанр',
    'Посилання на книгу',
    'Посилання на зображення',
]


class Client:

    def __init__(self):
        # Сесія зберігає стан між запитами (записує в себе coocies і тд..).
        # Підвищує вірогідність, що парсер не запідозрять
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
            'Accept-Language': 'uk'
        }

        self.result = []

    def load_page(self, url):
        """Цей метод буде завантажувати сторінку"""
        res = self.session.get(url=url)
        # Перевіряє статус код-відповіді
        res.raise_for_status()
        # Повертаємо текст сторінки в форматі HTML
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.col-xs-6.col-sm-6.col-md-4.col-lg-3.product.product--shadow')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        """Приймає на вхід об'єкт BS"""

        url_book_title_block = block.select_one('a.product__media-wrap')
        if not url_book_title_block:
            logger.error('no url_block')
            return

        book_url = url_book_title_block.get('href')
        if not book_url:
            logger.error('no book_url')
            return

        title = url_book_title_block.get('title')
        if not title:
            logger.error('no title')
            return

        url_img_block = block.select_one('img.product__media')
        if not url_img_block:
            logger.error('no url_img_block')
            return

        url_img = url_img_block.get('data-src')
        if not url_img:
            logger.error('no url_img')
            return

        author_block = block.select_one('div.name-author')
        if not author_block:
            logger.error('no author_block')
            return

        author = author_block.select_one('div.product__author')
        if not author:
            logger.error('no author_div')

        text_author = author.get_text()
        if not text_author:
            logger.error('no text_author')

        self.result.append(ParseResult(
            title=title,
            author=text_author,
            genre='Нехудожня література (нон-фікшн)',
            book_url=book_url,
            image_url='https://book-ye.com.ua/' + url_img
        ))

        logger.debug('%s, %s, %s, %s', title, text_author, url_img, book_url)
        logger.debug('-' * 200)

    def save_results(self):
        path = 'nonfiction.csv'
        with open(path, 'a', encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        number_pages = 639
        url = 'https://book-ye.com.ua/catalog/nekhudozhnya-literatura/'
        for page in range(2, number_pages + 2):
            text = self.load_page(url)
            self.parse_page(text=text)
            self.save_results()
            url = f'https://book-ye.com.ua/catalog/nekhudozhnya-literatura/?PAGEN_1={page}'
            self.result = []
            logger.info(f'Опрацювали {page - 1} сторінку, залишилось {number_pages - (page -1)} сторінок до опрацювання')
            logger.info('#' * (int((page - 1) / number_pages) * 100))


if __name__ == '__main__':
    parser = Client()
    parser.run()
