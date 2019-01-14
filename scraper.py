import os
import aiohttp
import asyncio
import async_timeout
import multiprocessing
from bs4 import BeautifulSoup

from good import Good, Specifications, mongo_collection_to_file


class EbayScraping(object):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self,
                 from_page=0, to_page=None,
                 site_url='https://www.ebay.com/b/Cell-Phones-Smartphones/9355',
                 request_timeout=10,
                 result_directory=None):
        self.site_url = site_url
        self.config_file = os.path.join(self.ROOT_DIR, 'configs/ebay/parsing-config.yml')
        self.result_directory = result_directory or os.path.join(self.ROOT_DIR, 'results')
        self.request_timeout = request_timeout
        self.from_page = from_page
        self.to_page = to_page or 10

    async def fetch(self, session, url):
        async with async_timeout.timeout(self.request_timeout):
            async with session.get(url) as response:
                return await response.text()

    @staticmethod
    async def soup_d(html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    async def extract_goods_links(self, html):
        soup = await self.soup_d(html)
        links = soup.find_all("a", {"class": "s-item__link"}, href=True)
        return [link['href'] for link in links]

    async def extract_next_page(self, html):
        soup = await self.soup_d(html)
        selected = soup.find("li", {"class": "ebayui-pagination__li--selected"})
        if selected:
            _next = selected.find_next_sibling("li", {"class": "ebayui-pagination__li"})
            if _next:
                link = _next.find("a", href=True)
                return link['href']

    async def extract_to_good(self, html):
        soup = await self.soup_d(html)
        id_data = soup.find("div", {"id": 'descItemNumber'})
        title_data = soup.find("h1", {"id": 'itemTitle'})
        good = Good(self.result_directory)
        good.id = getattr(id_data, 'text', None)
        good.title = getattr(title_data, 'text', None)
        for key in Specifications().field_keys:
            tag = soup.find(True, {"itemprop": key})
            setattr(good, key, getattr(tag, 'text', None))
        return good

    async def parse_page(self, links):
        async with aiohttp.ClientSession() as session:
            goods = []
            for link_url in links:
                await asyncio.sleep(1)
                good_html = await self.fetch(session, link_url)
                good = await self.extract_to_good(good_html)
                good.to_mongo_db()
                goods.append(good)
            return goods

    async def main(self, url):
        async with aiohttp.ClientSession() as session:
            has_next_page = url
            results = []
            page_count = self.from_page
            while has_next_page and page_count < self.to_page:
                print(has_next_page)
                page = await self.fetch(session, has_next_page)
                links = await self.extract_goods_links(page)
                result = await self.parse_page(links)
                results.extend(result)
                has_next_page = await self.extract_next_page(page)
                page_count += 1

    def execute_parse(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.main(self.site_url))
        except Exception as e:
            print(f'Exception intercepted: {e}')


if __name__ == '__main__':
    pages_gap = 25
    start = 103
    for i in range(multiprocessing.cpu_count()):
        ebay_scraping = EbayScraping(from_page=start,
                                     to_page=start + pages_gap,
                                     site_url=f'https://www.ebay.com/b/Cell-Phones-Smartphones/9355?_pgn={start}',)
        p = multiprocessing.Process(target=ebay_scraping.execute_parse)
        p.start()
        start += pages_gap + 1
    # mongo_collection_to_file('json')
