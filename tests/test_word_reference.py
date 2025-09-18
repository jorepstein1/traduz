from tradu import word_reference


def test_hola():
    with open("./tests/html_translation_samples/hola.html") as f:
        response_content = f.read()
    translations = word_reference.make_translations(response_content)
    assert len(translations) == 2


def test_guau():
    with open("./tests/html_translation_samples/guau.html", "r") as f:
        response_content = f.read()
    translations = word_reference.make_translations(response_content)
    assert len(translations) == 1


def test_ball():
    # TODO add support for compound forms
    with open("./tests/html_translation_samples/ball.html", "r") as f:
        response_content = f.read()
    translations = word_reference.make_translations(response_content)
    assert len(translations) == 3


def test_cool():
    with open("./tests/html_translation_samples/cool.html", "r") as f:
        response_content = f.read()
    translations = word_reference.make_translations(response_content)
    # print(translations)
    for translation in translations:
        print(translation)
    assert len(translations) == 5
