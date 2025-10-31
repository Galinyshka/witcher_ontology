def sup_decompose(soup):
    for sup in soup.find_all("sup"):
        sup.decompose()
    return soup

def small_decompose(soup):
    for small in soup.find_all("small"):
        small.decompose()
    return soup

def list_pros(soup):
    result = []
    current = []

    # Обходим всех детей, включая текст и теги
    for elem in soup.children:
        if getattr(elem, "name", None) == "br":
            # закончили один блок
            text = " ".join(current).strip()
            if text:
                result.append(text)
            current = []
        else:
            # собираем текст текущего блока
            if hasattr(elem, "get_text"):
                current.append(elem.get_text(" ", strip=True))
            elif isinstance(elem, str):
                current.append(elem.strip())

    # добавляем последний блок
    if current:
        text = " ".join(current).strip()
        if text:
            result.append(text)
    return result

    
def parse_character(soup):
    name = born = nationality = hair_color = eye_color = race = gender = None
    title = profession = affiliation = ability = book_appear = game_appear = None

    infobox = soup.find("aside", class_="portable-infobox")
    infobox = sup_decompose(infobox)
    if not infobox:
        return None  

    name_link = infobox.find("h2", {"data-source": "name"})
    name = name_link.get_text(strip=True) if name_link else None

    born_link = infobox.find("a", {"title": "Timeline"})
    born = int(born_link.get_text(strip=True)) if born_link else None

    nationality_block = infobox.find("div", {"data-source": "nationality"})
    if nationality_block:
        nationality_link = nationality_block.find("a")
        if nationality_link and nationality_link.get("title"):
            nationality = nationality_link["title"]

    hair_color_block = infobox.find("div", {"data-source": "hair_color"})
    if hair_color_block:
        hair_color_link = small_decompose(hair_color_block.find("div"))
        hair_color = hair_color_link.get_text(strip=True) if hair_color_link else None

    eye_color_block = infobox.find("div", {"data-source": "eye_color"})
    if eye_color_block:
        eye_color_link = small_decompose(eye_color_block.find("div"))
        eye_color = eye_color_link.contents[0].get_text(strip=True) if eye_color_link else None

    race_block = infobox.find("div", {"data-source": "race"})
    if race_block:
        race_link = small_decompose(race_block.find("div"))
        race = race_link.contents[0].get_text(strip=True) if race_link else None

    gender_block = infobox.find("div", {"data-source": "gender"})
    if gender_block:
        gender_link = small_decompose(gender_block.find("div"))
        gender = gender_link.contents[0].get_text(strip=True) if gender_link else None

    title_block = infobox.find("div", {"data-source": "titles"})
    if title_block:
        title_link = small_decompose(title_block.find("div"))
        title = list_pros(title_link) if title_link else None

    profession_block = infobox.find("div", {"data-source": "profession"})
    if profession_block:
        profession_link = small_decompose(profession_block.find("div"))
        profession = list_pros(profession_link) if profession_link else None

    affiliation_block = infobox.find("div", {"data-source": "affiliations"})
    if affiliation_block:
        affiliation_link = small_decompose(affiliation_block.find("div"))
        affiliation = list_pros(affiliation_link) if affiliation_link else None

    ability_block = infobox.find("div", {"data-source": "abilities"})
    if ability_block:
        ability_link = small_decompose(ability_block.find("div"))
        ability = list_pros(ability_link) if ability_link else None

    appearance_block = infobox.find("div", {"data-source": "appears_books"})
    if appearance_block:
        appearance_link = small_decompose(appearance_block.find("div"))
        book_appear = list_pros(appearance_link) if appearance_link else None

    appearance_block = infobox.find("div", {"data-source": "appears_games"})
    if appearance_block:
        appearance_link = small_decompose(appearance_block.find("div"))
        game_appear = list_pros(appearance_link) if appearance_link else None

    return {"name": name, "born": born, "nationality": nationality, "hair_color": hair_color, "eye_color": eye_color, "race": race, "gender": gender, "title": title, "profession": profession, "affiliation": affiliation, "abilities": ability, "book_appear": book_appear, "game_appear": game_appear}
