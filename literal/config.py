import spacy
from spacy.lang.th import Thai
from spacy.lang.ja import Japanese
from spacy.lang.ar import Arabic
from spacy.lang.tr import Turkish


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
    'it': spacy.load("it_core_news_sm"),    # Italian
    'es': spacy.load("es_core_news_sm"),    # Spanish
    'fr': spacy.load("fr_core_news_sm"),    # French
    'ja': spacy.load("xx_ent_wiki_sm"),    # Japanese
    'ko': spacy.load("ko_core_news_sm"),    # Korean
    'zh': spacy.load("zh_core_web_sm"),     # Chinese (simplified)
    'de': spacy.load("de_core_news_sm"),    # German
    'ar': Arabic(),    # Arabic
    'tr': Turkish(),    # Turkish
    'th': spacy.load("xx_ent_wiki_sm")     # Thai (no dedicated SpaCy model, using multi-language model) '''
}

def read_function_words(filename):
    func_wrds = []
    lines = open(filename, "r").readlines()
    for line in lines:
        func_wrds.append(line.strip().lower())
    func_wrds = func_wrds + list(PUNCTUATION)
    return func_wrds
    
PUNCTUATION = {'.', ',', '!', '?', '.', ':', ';', '*', ' ', " ", '-', '؟'}

def is_punctuation(word):
    return word in PUNCTUATION
    
FUNCTION_WORDS = read_function_words('functional_word_list.txt')

USE_SPACES = ['de', 'fr', 'it', 'es', 'tr']