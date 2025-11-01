import requests
from bs4 import BeautifulSoup
from collections import defaultdict

def get_html(page_name:str):
    url = "https://witcher.fandom.com/api.php"
    params = {
        "action": "parse",
        "page": page_name,
        "prop": "text",
        "format": "json"
    }
    r = requests.get(url, params=params)
    data = r.json()
    html = data["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")
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
    if not soup:
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

def parse_characters_dict(books):
    characters_dict = defaultdict(list)

    for book in books:
        soup = get_html(book)
        if not soup:
            continue

        inner = soup.find('span', id='Characters')
        if inner:
            inner = inner.parent.find_next_sibling('div', {'class':'listfix'})
        if not inner:
            continue

        for el in inner.find_all('li'):
            character = el.get_text(strip=True)
            if character:
                if book not in characters_dict[character]:
                    characters_dict[character].append(book)

    return dict(characters_dict)


def parse_character(soup):
    infobox = soup.find("aside", class_="portable-infobox")
    if not infobox:
        return None
    remove_tags(infobox, ["sup"])

    data = {}

    name_tag = infobox.find("h2", {"data-source": "name"})
    data["name"] = name_tag.get_text(strip=True) if name_tag else None

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

    for key in ["titles", "profession", "affiliation", "abilities", "appears_books", "appears_games"]:
        data[key] = extract_list(infobox.find("div", {"data-source": key}))
    

    return data
