from bs4 import BeautifulSoup, Tag
import curl_cffi

import dataclasses


@dataclasses.dataclass
class FromWord:
    text: str
    definition: str
    pos2: str


@dataclasses.dataclass
class ToWord:
    text: str
    pos2: str
    dsense: str


@dataclasses.dataclass
class Translation:
    from_word: FromWord
    to_word: list[ToWord]


def make_translation_from_trs(trs: list[Tag]) -> Translation:
    primary_tr = trs[0]
    tds = primary_tr.find_all("td", recursive=False)
    assert len(tds) == 3
    for td in tds:
        if not isinstance(td, Tag):
            raise ValueError
    from_td = tds[0]
    from_text = str(from_td.strong.contents[0])
    from_pos2 = str(from_td.em.contents[0])
    definition = tds[1].contents[1]
    print(from_text, from_pos2, definition)

    for tr in trs[1:]:
        # alternative translations
        pass


# response = curl_cffi.get(
#     "https://www.wordreference.com/es/en/translation.asp?spen=hola",
#     impersonate="chrome",
# )
# print(response)
# print(response.content)
# with open("translation.html", "wb") as f:
#     f.write(response.content)
with open("translation.html", "rb") as f:
    response = f.read()
soup = BeautifulSoup(response, "html.parser")
print(len(soup.find_all("table", class_="WRD")))
tables = soup.find_all("table", class_="WRD")
# id_tds = soup.find_all("td", id=["regular", "additional", "compounds"])
id_tds = soup.find_all("td", id=["regular"])
for id_td in id_tds:
    if not isinstance(id_td, Tag):
        raise ValueError("id_td is None or a string")
    print(id_td.get_text())
    parent_table = id_td.find_parent("table")
    if not isinstance(parent_table, Tag):
        raise ValueError("parent_table is None or a string")
    translations: list[list[Tag]] = []
    cur_translation: list[Tag] = []
    for tr in parent_table.find_all("tr"):
        if not isinstance(tr, Tag):
            raise ValueError("tr is None or a string")
        if set(tr.get_attribute_list("class")) & {"wrtopsection", "langHeader"}:
            continue
        id_ = tr.get("id")
        if isinstance(id_, str) and id_.startswith("esen"):
            if cur_translation:
                translations.append(cur_translation)
                cur_translation = []
        cur_translation.append(tr)
    translations.append(cur_translation)
    for translation in translations:
        make_translation_from_trs(translation)
        break
    print("----")
    # print(tr.get_text(separator=" | ", strip=True))


# for table in tables:
#     if not isinstance(table, Tag):
#         raise ValueError("Table is None or a string")
#     assert isinstance(table, Tag)
#     table
#     table_id = table.find("td", id=["regular", "additional", "compounds"])

#     table_rows = table.find_all("tr")
#     print(table_rows)
