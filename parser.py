import requests
from bs4 import BeautifulSoup
from collections import defaultdict

BASE_URL = "https://witcher.fandom.com/api.php"
API_PARAMS = {
    "action": "parse",
    "prop": "text", 
    "format": "json"
}

def get_html(page_name:str):
    ''' Получение HTML по названию'''

    params = API_PARAMS.copy()
    params["page"] = page_name

    r = requests.get(BASE_URL, params=params)
    data = r.json()
    if 'error' in data:
        print(f"'{page_name}' error: {data['error']['info']}")
        return None
    
    html = data["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")

    redirect_block = soup.find("div", class_="redirectMsg")
    if redirect_block:
        link = redirect_block.find("a")
        if link and link.get("title"):
            new_page = link["title"]
            print(f"Redirected from '{page_name}' → '{new_page}'")
            return get_html(new_page)
        
    print(f"Page '{page_name}' parsed.")
    return soup

def remove_tags(soup, name:str):
    for tag in soup.find_all(name):
        tag.decompose()
    return soup

def extract_text(soup):
    if not soup:
        return None
    inner = soup.find("div") or soup
    remove_tags(inner, "small")
    text = inner.contents[0].get_text(strip=True)
    return text if text else None

def extract_list(soup, remove=True):
    if not soup or not soup.contents:
        return None
    inner = soup.find("div") or soup
    if remove:
        remove_tags(inner, "small")
    items = []
    current = []
    for elem in inner.children:
        if getattr(elem, "name", None) == "br":
            text = " ".join(current).strip()
            if text:
                items.append(text)
            current = []
        else:
            if hasattr(elem, "get_text"):
                current.append(elem.get_text(" ", strip=True))
            elif isinstance(elem, str):
                current.append(elem.strip())
    if current:
        text = " ".join(current).strip()
        if text:
            items.append(text)
    return items if items else None

def parse_characters_list(books:list):
    ''' Парсинг списка персонажей по основным персонажам книг'''

    characters = []

    for book in books:
        soup = get_html(book)
        if not soup:
            continue

        inner = soup.find('span', id='Characters')
        if inner:
            inner = inner.parent.find_next_sibling('div', {'class':'listfix'}) or inner.parent.find_next_sibling('ul')
        if not inner:
            continue

        for el in inner.find_all('li'):
            character = el.get_text(strip=True)
            if character not in characters:
                characters.append(character)
                
    return characters

def parse_character(characters:list) -> list:
    ''' Парсинг подробной информации для персонажа'''

    characters_info = []
    for character in characters:
        data = {}
        data['character'] = character
        soup = get_html(character)
        if not soup:
            continue

        infobox = soup.find("aside", class_="portable-infobox")
        if not infobox:
            continue
        remove_tags(infobox, ["sup"])

        name_tag = infobox.find("h2", {"data-source": "name"})
        data["full name"] = name_tag.get_text(strip=True) if name_tag else None

        born_tag = infobox.find("a", {"title": "Timeline"})
        data["born"] = int(born_tag.get_text(strip=True)) if born_tag else None

        nationality_block = infobox.find("div", {"data-source": "nationality"})
        if nationality_block:
            nationality_link = nationality_block.find("a")
            if nationality_link and nationality_link.get("title"):
                data['nationality'] = nationality_link["title"]
            else:
                data['nationality'] = None
        else: 
            data['nationality'] = None

        for key in ["hair_color", "eye_color", "race", "gender", "status"]:
            data[key] = extract_text(infobox.find("div", {"data-source": key}))

        for key in ["titles", "profession", "affiliations", "abilities", "appears_books", "appears_games"]:
            data[key] = extract_list(infobox.find("div", {"data-source": key}))

        characters_info.append(data)

    return characters_info


def parse_organisation(organisations:list):
    ''' Парсинг подробной информации для организации'''

    organisations_info = []
    for organisation in organisations:
        data = {}
        data['organisation'] = organisation
        soup = get_html(organisation)
        if not soup:
            continue

        infobox = soup.find("aside", class_="portable-infobox")
        if not infobox:
            continue
        remove_tags(infobox, ["sup"])

        name_tag = infobox.find("h2", {"data-source": "name"})
        data["full name"] = name_tag.get_text(strip=True) if name_tag else None

        for key in ["gender", "status", "area served", "country"]:
            data[key] = extract_text(infobox.find("div", {"data-source": key}))

        for key in ["type", "purpose", "founder", "leader", "members", "headquarters", "appears_books", "appears_games"]:
            data[key] = extract_list(infobox.find("div", {"data-source": key}))

        if not data['gender']:
            organisations_info.append(data)

    return organisations_info