import re

s='https://rozetka.com.ua/notebooks/c80004/filter/page=100/'


import requests
from bs4 import BeautifulSoup


BASE_URL = 'https://rozetka.com.ua/notebooks/c80004/filter/'


def get_html(url=BASE_URL):
    req = requests.get(url)
    return req.text


def get_count_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    pages_anc = soup.find('nav', class_ = 'paginator-catalog pos-fix').find_all('a',
                            class_ = 'blacklink paginator-catalog-l-link')[-1].get('href')
    total = pages_anc.split('/')[-2].split('=')[1] or re.search(r'1\d{2}',pages_anc)[0]
    return int(total)


def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    product_catalog = soup.find('div', class_ = 'g-i-tile-l g-i-tile-catalog-hover-left-side clearfix').find_all('div',
                                class_='g-i-tile g-i-tile-catalog')

    dct_data={}

    for item, product in enumerate(product_catalog, 1):
        dct_data.setdefault(item,{})['title']=product.find('div', 
                            class_ = 'g-i-tile-i-title clearfix').find('a').next.strip()
        dct_data.setdefault(item, {})['url']=product.find('a').get('href')
        #price = product.find('div').find('g-price-uah').next or product.find('div', class_ = 'g-price g-price-cheaper').next

    return dct_data


def main():
    html = get_html(BASE_URL)
    total_pages = get_count_pages(html)

    for page in range(1,total_pages):
        url = f'{BASE_URL}page={int(page)}/'
        try:
            html_page = get_html(url)
            dct_data=get_page_data(html_page)
        except requests.exceptions.ConnectionError:
            print('Rozetka is unavailable')
            return

        print(f'\n\t\t\t\tPage: {page} ', end='\n\n')

        for item, value in dct_data.items():
            #print(f'\n{key}. {value[]} \n\turl: {value[1]}\n\tprice: None')
            print(''.join('\n{}. {} \n\turl: {}\n\tprice: None'.format(item, value['title'], value['url'])))


if __name__=='__main__':
    main()
