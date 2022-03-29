from urllib.parse import urlsplit
from bs4 import BeautifulSoup
import requests
import pandas as pd
from requests import get
from tqdm.auto import tqdm


base_url = 'https://www.otomoto.pl/motocykle-i-quady'


def add_marka(marka, model):
    url = ''
    if marka:
        url = url + f'/{marka.lower()}'
        if model:
            url = url + f'/{model.lower()}'
        return url


def add_typ(typ: list):
    url = ''
    if typ:
        typ.sort()
        type_list = ['quad', 'naked', 'cruiser', 'enduro']
        no_type_list = ['chopper', 'krosowy', 'motorower',
                        'skuter', 'sportowy', 'turystyczny']
        type_1 = list(set(typ).intersection(no_type_list))
        type_2 = list(set(typ).intersection(type_list))
        first = True
        for t in type_1:
            if first:
                url = url + f'/{t}'
                first = False
            else:
                url = url + f'--{t}'
        for t in type_2:
            if first:
                url = url + f'/typ-{t}'
                first = False
            else:
                url = url + f'--typ-{t}'
    return url


def add_rok_prod(rok_od, rok_do):
    url_od = url_do = ''
    if rok_od:
        url_od = f'/od-{rok_od}'
    if rok_do:
        url_do = f'search%5Bfilter_float_year%3Ato%5D={rok_do}'
    return url_od, url_do


def add_cena(cena_od, cena_do):
    url_od = url_do = ''
    if cena_od:
        url_od = f'search%5Bfilter_float_price%3Afrom%5D={cena_od}'
    if cena_do:
        url_do = f'search%5Bfilter_float_price%3Ato%5D={cena_do}'
    return url_od, url_do


def add_pojemnosc(poj_od, poj_do):
    url_od = url_do = ''
    if poj_od:
        url_od = f'search%5Bfilter_float_engine_capacity%3Afrom%5D={poj_od}'
    if poj_do:
        url_do = f'search%5Bfilter_float_engine_capacity%3Ato%5D={poj_do}'
    return url_od, url_do


def add_fuel(fuel):
    url = ''
    if fuel:
        url = f'search%5Bfilter_enum_fuel_type%5D={fuel}'
    return url


def make_url(base_url='https://www.otomoto.pl/motocykle-i-quady', typ=None, marka=None,
             model=None, cena_od=None, cena_do=None, rok_od=None, rok_do=None, poj_od=None,
             poj_do=None, paliwo=None):

    url = base_url

    marka_url = add_marka(marka, model)
    typ_url = add_typ(typ)
    cena_od_url, cena_do_url = add_cena(cena_od, cena_do)
    rok_od_url, rok_do_url = add_rok_prod(rok_od, rok_do)
    poj_od_url, poj_do_url = add_pojemnosc(poj_od, poj_do)
    fuel_url = add_fuel(paliwo)
    no_search = [marka_url, typ_url, rok_od_url]
    search_ordered = [rok_do_url, poj_od_url,
                      poj_do_url, cena_od_url, cena_do_url, fuel_url]

    firstsearch = True

    for el in no_search:
        url += el

    for el in search_ordered:
        if el:
            if firstsearch:
                url += '?'
                firstsearch = False
            else:
                url += '&'
            url += el

    return url



def get_site_content(url: str):
    page = get(url, timeout=1000)
    return BeautifulSoup(page.content, "html.parser")


def scrap_page(url):
    source = requests.get(url).content
    soup = BeautifulSoup(source, 'html5lib')
    motors = []

    articles = soup.find_all('article', class_="ooa-wcnchh e1b25f6f18")
    len(articles)

    article = articles[0]

    for article in articles:
        try:
            link = article.find(
                'div', class_="ooa-1nvnpye e1b25f6f5").find('a')['href']
            nazwa = article.find(
                'div', class_="ooa-1nvnpye e1b25f6f5").find('a').text
            motors.append(link)
        except AttributeError as e:
            print(e)
            pass
    return motors


def get_max_page_num(url):
    source = requests.get(url).content
    soup = BeautifulSoup(source, 'html5lib')


    pages = soup.find('div', class_="ooa-1oll9pn e19uumca7")
    ab = pages.findChild('ul', recursive=False).findChildren(
        'li', recursive=False)
    # ab = aa.findChildren('li', recursive=False)

    pages = []
    for item in ab:
        if item['data-testid'] == "pagination-list-item":
            pages.append(item.text)

    max_pages = int(pages[-1])
    return max_pages


def scrap_motors(base_url, max_pages):
    motors = []
    urls = []
    for i in range(max_pages):
        url = base_url + f"?page={i+1}"
        urls.append(url)

    for url in urls:
        motors.extend(scrap_page(url))
    return motors


def scrap_single_offer(url):

    source = requests.get(url).content
    soup = BeautifulSoup(source, 'html5lib')

    table_upper, table_lower = soup.find('div', class_='flex-container-main').find('div',
                                                                                   class_='flex-container-main__left').find('div',
                                                                                                                            class_='offer-content offer-content--secondary').find('div',
                                                                                                                                                                                  class_='offer-content__row om-offer-main').find('div',
                                                                                                                                                                                                                                  class_='offer-content__main-column').find('div',
                                                                                                                                                                                                                                                                            class_='parametersArea').find_all('ul', class_='offer-params__list')

    # table_upper = tables[0]
    # table_lower = tables[1]

    def get_attr(attr_list):

        varname = attr_list[0].strip()
        attval = attr_list[-1].strip()
        return varname, attval

    vars1 = ['Oferta od', 'Kategoria', 'Marka Pojazdu', 'Model pojazdu', 'Rok produkcji',
             'Przebieg', 'Pojemność skokowa', 'Moc', 'Rodzaj napędu', 'Typ silnika', 'Rodzaj paliwa', 'Skrzynia biegów']

    vars2 = ['Typ nadwozia', 'Kolor', 'VAT marża', 'Możliwość finansowania',
             'Rodzaj koloru', 'Zarejestrowany w Polsce', 'Pierwszy właściciel', 'Bezwypadkowy', 'Serwisowany w ASO', 'Stan']

    vars = vars1.copy()
    vars.extend(vars2)

    # ADD CENA, LOKALIZACJA

    price_html = soup.select_one(
        "#siteWrap > main > div.flex-container-main > div.flex-container-main__right > div.offer-content__aside > div.offer-summary > div.price-wrapper > div > span.offer-price__number")
    price = price_html.text.replace(' ', '')[:-4]

    attrs1 = table_upper.find_all('li')
    attrs2 = table_lower.find_all('li', class_='offer-params__item')

    entry_dict = {}
    entry_dict['Cena'] = float(price)

    for i in range(len(attrs1)):
        var, att = get_attr(attrs1[i].text.strip().split('\n'))
        entry_dict[var] = att

    for i in range(len(attrs2)):
        var, att = get_attr(attrs2[i].text.strip().split('\n'))
        entry_dict[var] = att

    address = soup.select_one(
        "#seller-bottom-info > div > section > section.seller-bottom-info__map.collapsible.active > div > article > a")
    location = address.text.strip()
    entry_dict["Adres"] = location

    coordinates = soup.select_one("#adMapData")
    cords = (coordinates['data-map-lat'], coordinates['data-map-lon'])

    entry_dict["Współrzędne"] = cords

    entry_dict["URL"] = url
    return entry_dict


def offers_to_df(urls, filename):

    my_df = []
    for i in tqdm(range(len(urls))):
        d = scrap_single_offer(urls[i])
        my_df.append(d)

    # for i,url in enumerate(urls):
    #     d = scrap_single_offer(url)
    #     my_df.append(d)
    #     print(f"{i+1}/{len(urls)}", flush=True)

    df = pd.DataFrame(my_df)
    df.to_csv(filename, index=False)

    return df


def main():
    base_url = 'https://www.otomoto.pl/motocykle-i-quady'
    typ = ['naked']
    marka = 'Honda'
    model = None
    cena_od = None
    cena_do = 10_000
    rok_od = None
    rok_do = None
    poj_od = None
    poj_do = None
    paliwo = None

    # search_url = make_url(base_url,
    #  typ=typ, marka=marka, model=model, cena_od=cena_od, cena_do=cena_do, rok_od=rok_od,
    #   rok_do=rok_do, poj_od=poj_od, poj_do=poj_do, paliwo=paliwo)

    search_url = make_url(base_url, typ, marka, model, cena_od,
                          cena_do, rok_od, rok_do, poj_od, poj_do, paliwo)

    url_list = scrap_motors(search_url, get_max_page_num(search_url))

    print(
        f"Zakończono poszukiwanie motocykli. Znaleziono {len(url_list)} ofert")
    print(f"Rozpoczęto scrapowanie danych...")

    df = offers_to_df(url_list, 'ex3_motors.csv')


if __name__ == '__main__':
    main()
