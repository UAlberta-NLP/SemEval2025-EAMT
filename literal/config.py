import spacy


SUPPORTED_LANGUAGES = {
    'ar',  # Arabic
    'de',  # German
    'es',  # Spanish
    'fr',  # French
    'it',  # Italian
    'ja',  # Japanese
    'ko',  # Korean
    'th',  # Thai
    'tr',  # Turkish
    'zh',  # Chinese
}

TOKENIZERS = {
    'en': spacy.load("en_core_web_sm"),
    'it': spacy.load("it_core_news_sm"),
    'es': spacy.load("es_core_news_sm"),
    'fr': spacy.load("fr_core_news_sm"),
    'ja': spacy.load("xx_ent_wiki_sm"),
    'ko': spacy.load("ko_core_news_sm"),
    'zh': spacy.load("zh_core_web_sm"),
    'de': spacy.load("de_core_news_sm"),
    'ar': spacy.blank("ar"),
    'tr': spacy.blank("tr"),
    'th': spacy.load("xx_ent_wiki_sm"),  # no dedicated SpaCy model; using multilingual
}

PUNCTUATION = {'.', ',', '!', '?', ':', ';', '*', ' ', ' ', '-', '؟'}


def is_punctuation(word):
    return word in PUNCTUATION


def read_function_words(filename):
    with open(filename, "r") as f:
        func_wrds = [line.strip().lower() for line in f]
    return func_wrds + list(PUNCTUATION)


FUNCTION_WORDS = read_function_words('functional_word_list.txt')

USE_SPACES = ['de', 'fr', 'it', 'es', 'tr']
