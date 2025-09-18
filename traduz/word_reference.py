from bs4 import BeautifulSoup, Tag
import curl_cffi

import dataclasses


@dataclasses.dataclass
class FromWord:
    text: str
    definition: str
    pos2: str
    fr2: str


@dataclasses.dataclass
class ToWord:
    text: str
    pos2: str
    dsense: str


@dataclasses.dataclass
class Translation:
    from_word: FromWord
    to_words: list[ToWord]


from parsel import Selector


def _sanitize_string(text: str) -> str:
    text = text.strip()
    if text:
        if text[0] == "(":
            text = text[1:]
        if text[-1] == ")":
            text = text[:-1]
    return text


def make_translation_from_trs(trs: list[Selector]) -> Translation:
    print("this many trs", len(trs))
    from_word = None
    to_words = []
    for tr in trs:
        tds = tr.css("td")
        if len(tds) == 3:
            # translation row
            if tds[0].css(".FrWrd"):
                # first row (e.g. with from text + definition)
                from_text = tds[0].css("strong::text").get()  # e.g.hello
                if from_text is None:
                    raise ValueError("From Word should not be None")
                from_pos2 = tds[0].css("em::text").get() or ""
                # e.g. interj (interjection)
                # Definition can take a few forms including a definition
                # and optionally a fr2 and a dsense
                # fr2 qualifies the definitioin
                # dsense qualifiies the translation
                # definition iis not wrapped in a tag, and contains text in parantheses
                # fr2 is in <i class="Fr2">
                # dsense is in <span class="dsense">  => () => <span /> => Val
                definition = tds[1]  # e.g. greeting
                definition_td = tds[1]

                if fr2_i := definition_td.css("i::text"):
                    fr2_text = fr2_i.get() or ""  # e.g. informal
                else:
                    fr2_text = ""
                definition.css("i").drop()

                if (definition := definition_td.css("::text").get()) is None:
                    raise ValueError("Definition should not be None")
                else:
                    definition = definition.strip()
                from_word = FromWord(
                    text=from_text,
                    definition=_sanitize_string(definition),
                    pos2=from_pos2,
                    fr2=fr2_text,
                )
            to_word = create_to_word(tds[1], tds[2])
            to_words.append(to_word)
            # to = tds[0].css("strong::text").get()  # e.g.hello
            # if from_text is None:
            #     raise ValueError("From Word should not be None")
            # from_pos2 = tds[0].css("em::text").get() or ""
            # # e.g. interj (interjection)
            # print(from_text)
            # print(from_pos2)
        elif len(tds) == 2:
            # phrase translation
            pass
        elif len(tds) == 1:
            # Notes (Uncommon)
            pass
        else:
            raise ValueError("Unrecognized tr")

    if from_word is None:
        raise ValueError("from_word should not be None")

    return Translation(from_word=from_word, to_words=to_words)


def create_to_word(td1, td2) -> ToWord:
    dsense_text = td1.css("span span::text").get() or ""
    to_td = td2
    if not to_td.attrib.get("class") == "ToWrd":
        raise ValueError("Third td should have ToWrd class")
    to_pos2 = td2.css(".POS2")
    if to_pos2 := td2.css(".POS2"):
        to_pos2_text = to_pos2.css("::text").get() or ""
        to_pos2.drop()  # to isolate the to text
    else:
        to_pos2_text = ""
    to_text = to_td.css("::text").get()
    if not to_text:
        raise ValueError("To Text should not be None")
    to_word = ToWord(
        text=_sanitize_string(to_text),
        pos2=_sanitize_string(to_pos2_text),
        dsense=_sanitize_string(dsense_text),
    )
    return to_word


# response = curl_cffi.get(
#     "https://www.wordreference.com/es/en/translation.asp?spen=hola",
#     impersonate="chrome",
# )
# print(response)
# print(response.content)
# with open("translation.html", "wb") as f:
#     f.write(response.content)
# with open("translation.html", "rb") as f:
#     response = f.read()
# response = curl_cffi.get(
#     "https://www.wordreference.com/es/en/translation.asp?spen=guau",
#     impersonate="chrome",
# )
# with open("guau.html", "wb") as f:
#     f.write(response.content)
# response = curl_cffi.get(
#     "https://www.wordreference.com/es/translation.asp?tranword=cool",
#     impersonate="chrome",
# )


# with open("cool.html", "wb") as f:
#     f.write(response.content)
def make_translations(html_content):
    # soup = BeautifulSoup(html_content, "html.parser")
    selector = Selector(html_content)
    # print(len(soup.find_all("table", class_="WRD")))
    tables = selector.css("table .WRD")
    translation_objs = []
    for table in tables:
        print("new table")
        if not table.css("td#regular"):
            continue
        translations: list[list[Selector]] = []
        cur_translation: list[Selector] = []
        trs = table.css("tr")
        for tr in trs:
            if tr.css(".langHeader") or tr.css(".wrtopsection"):
                continue
            tr_id = tr.attrib.get("id")
            if tr_id and (tr_id.startswith("enes") or tr_id.startswith("esen")):
                print("new translation")
                if cur_translation:
                    translations.append(cur_translation)
                    cur_translation = []
            cur_translation.append(tr)
        translations.append(cur_translation)
        print(f"there are {len(translations)} translations")
        for translation in translations:
            translation_objs.append(make_translation_from_trs(translation))
        print("----")
        # for td in tds:
        # print(td)
        # print(table.css("table::has(td#regular)"))
    return translation_objs
    # ids can be regular, phrasal, additional, compounds
    # I've found an example where there can be two regular tables but I will just
    # take the first because the second didn't seem as important
