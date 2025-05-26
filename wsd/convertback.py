import csv
import re
from simalign import SentenceAligner
import babelnet as bn
from babelnet import Language
from babelnet.pos import POS
from itertools import zip_longest
import pandas as pd
from nltk.corpus.reader.wordnet import WordNetError
from jellyfish import jaro_similarity
import ast

STRING_SIMILARITY_THRESHOLD = 0.7

pos_tags = {"VERB": POS.VERB, "NOUN": POS.NOUN, "ADV": POS.ADV, "ADJ": POS.ADJ}
langs = {"TR": Language.TR, "es": Language.ES, "it": Language.IT, "AR": Language.AR, "de": Language.DE,
         "fr": Language.FR, "en": Language.EN, "ja": Language.JA, "zh": Language.ZH}

# LANGUAGES = {'it': Language.IT, 'es': Language.ES, 'fr': Language.FR}

from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
BROWN_IC = wordnet_ic.ic('ic-brown.dat')

PUNCTUATION = {'.', ',', '!', '?', '.', ':', ';', '*', ' ', " "}

class TokenDictionary:
    def __init__(self, file_to_read):
        ans = {}
        self.function_words = self.read_function_words('/home/dbasil1/misc/WList.pm')
        with open(file_to_read, mode='r', encoding='utf-8') as reader:
            for line in reader:
                pattern = r'id="([^"]+)"\s+lemma="([^"]+)"\s+pos="([^"]+)"'
                match = re.search(pattern, line)
                if match:
                    id_value = match.group(1)  # First capture group
                    lemma_value = match.group(2)  # Second capture group
                    pos_value = match.group(3)
                    assert id_value not in ans.keys()
                    ans[id_value] = [lemma_value, pos_value]
        self.dictionary = ans


    def find(self, arg):
        return self.dictionary[arg][0]
    
    def find_pos(self, arg):
        return self.dictionary[arg][1]

    def read_function_words(self, file):
        ans = set()
        with open(file, mode='r', encoding='latin-1') as reader:
            for a, line in enumerate(reader):
                if a > 3:
                    if len(line.split()) < 1:
                        break
                    word = line.split()[0].strip()
                    ans.add(word.replace('"', ''))
        return ans

SET_CACHE_KEYS = set()
SET_CACHE_DICT = {}

def cachable_to_synset(x):
    if x in SET_CACHE_KEYS:
        return SET_CACHE_DICT[x]
    else:
        SET_CACHE_KEYS.add(x)
        SET_CACHE_DICT[x] = bn.resources.BabelSynsetID(x).to_synset()
        return SET_CACHE_DICT[x]
    

def wn_from_bn(bn_id):
    answer = []

    synset = cachable_to_synset(bn_id)
    
    
    if len(synset._wn_offsets) > 0:
            if str(synset.type) == "CONCEPT" or str(synset.type) == "NAMED_ENTITY":
                s_id = str(synset._wn_offsets[0])
                synset = wn.synset_from_pos_and_offset(s_id[-1],int(s_id[-9:-1]))
                return synset
            else:
                print("I expected a concept")
                print(synset.type)
                print(bn_id)
                assert False


def highest_sentence(address):
    curr_ans = -1
    # TODO could make this more robust BUT who cares
    with open(address, 'r', encoding='utf-8') as file_one:
        for line in file_one:
            s_num = line[7:11]
            if int(s_num) > curr_ans:
                curr_ans = int(s_num)
    assert curr_ans > -1
    return curr_ans + 1


def replace_val_in_dict(d, v, nv):
    for key, value in d.items():
        if value == v:
            d[key] = nv


def percent_same_or_similar(sent1bncs, sent2bncs, threshold=0.19):
    """Takes a list of babelnet concepts for each sentence and returns the decimal
    of how many are the same or similar"""

    reps = {}

    sent1concepts = [wn_from_bn(a) for a in sent1bncs if a != '<pad>']
    sent2concepts = [wn_from_bn(a) for a in sent2bncs if a != '<pad>']

    sent1set = set()
    sent2set = set()

    all_concepts = sent1concepts + sent2concepts
    new_all_concepts = all_concepts.copy()

    all_bn_tags = sent1bncs + sent2bncs


    #Go through all pairs
    for i in range(len(all_concepts)):
        found = False
        closest = None
        closest_score = 0
        for j in range(0, i):
            conc1 = all_concepts[i]
            conc2 = all_concepts[j]

            #Make sure we're not comparing anything to itself or twice
            assert i > j

            # If a concept is very similar to another concept, replace it with that one.
            # If it's similar to multiple concepts, replace it with the most similar.
            try:
                similarity = conc1.jcn_similarity(conc2, BROWN_IC)
            except WordNetError:
                similarity = 0
            if similarity > threshold:
                if similarity > closest_score:
                    closest_score = similarity
                    found = True
                    closest = j
                # print(str(conc1) + " as similar as " + str(conc1.path_similarity(conc2)) + " to " + str(conc2))
        if found:
            new_all_concepts[i] = new_all_concepts[closest]
            reps[all_bn_tags[i]] = all_bn_tags[closest]
            if all_bn_tags[i] in reps.values():
                replace_val_in_dict(reps, all_bn_tags[i], all_bn_tags[closest])

    for k in range(len(new_all_concepts)):
        if k < len(sent1concepts):
            sent1set.add(new_all_concepts[k])
        else:
            sent2set.add(new_all_concepts[k])

    intersection_size = len(sent1set & sent2set)


    union_size = len(sent1set | sent2set)


    # return intersection_size / union_size, reps TODO testing not this for now
    try:
        return intersection_size / len(sent1set), reps
    except ZeroDivisionError:
        return 0, reps


def compare(file_one_addr, file_two_addr, lang, tar_xml, eng_xml, ne_file):
    print()
    print(lang)
    t_d = TokenDictionary(tar_xml)
    e_d = TokenDictionary(eng_xml)
    align_boy = SentenceAligner(model="bert", token_type="bpe", matching_methods="mai")
    scores = []
    eng_concepts = []
    tar_concepts = []
    num_sentences = highest_sentence(file_one_addr)
    original = ["Original"]
    b_answer = ["Best Translation"]
    g_answer = ["GPT Translation"]
    c_answer = ["Cloud Translation"]
    gold_answer = ["Gold Translation"]
    d_answer = ["DeepL Translation"]
    translator = ["Translator of Output"]
    
    df = pd.read_csv(ne_file, sep='\t')
    list_of_en_nes = df["Named_Entity"]
    list_of_tar_nes = df["All Translations"]

    assert len(list_of_en_nes) == len(list_of_tar_nes)
    
    list_of_nes = list(zip(list_of_en_nes, list_of_tar_nes))
    list_of_nes = list_of_nes + list_of_nes + list_of_nes
   
    with open(f"valid{lang}.tsv", 'r', newline='', encoding='utf-8') as csvfile:

        csvreader = csv.DictReader(csvfile, delimiter="\t")
        sentencesgold = [(ast.literal_eval(row["targets"])[0]['translation'], row["source"]) for row in csvreader]
    with open(f"valid{lang}.tsv", 'r', newline='', encoding='utf-8') as csvfile:

        csvreader = csv.DictReader(csvfile, delimiter="\t")
        sentencesgpt = [(row["Our GPT Translation"], row["source"]) for row in csvreader]
    with open(f"valid{lang}.tsv", 'r', newline='', encoding='utf-8') as csvfile:

        csvreader = csv.DictReader(csvfile, delimiter="\t")
        sentencescloud = [(row["Google Translate"], row["source"]) for row in csvreader]
    with open(f"valid{lang}.tsv", 'r', newline='', encoding='utf-8') as csvfile:

        csvreader = csv.DictReader(csvfile, delimiter="\t")
        sentencesdeep = [(row["DeepL"], row["source"]) for row in csvreader]

    for i in range(num_sentences):
        print(f'\r{(i * 10000 // num_sentences) / 100}%', end='')
        curr_ans = compare_sentence(file_one_addr, file_two_addr, i, e_d, t_d, align_boy, lang, list_of_nes)
        if len(curr_ans) == 0:
            break
        scores.append(curr_ans[0])
        eng_concepts.append(" ".join(curr_ans[1]))
        tar_concepts.append(" ".join(curr_ans[2]))
    scoresgold = scores[0: len(scores) // 4]
    scoresgpt = scores[len(scores) // 4: 2*len(scores) // 4]
    scorescloud = scores[len(scores)*2 // 4: 3*len(scores) // 4]
    scoresdeep = scores[3 * len(scores) // 4:]
    true_tokens = tar_concepts[0: len(tar_concepts) // 4]
    e_tokens = eng_concepts[0: len(eng_concepts) // 4]
    g_tokens = tar_concepts[len(tar_concepts) // 4: 2*len(tar_concepts) // 4]
    c_tokens = tar_concepts[len(tar_concepts)*2 // 4: 2*len(tar_concepts) // 4]
    d_tokens = tar_concepts[3*len(tar_concepts) // 4 :]
    e_tokens = ["English Tokens"] + e_tokens
    g_tokens = ["GPT Tokens"] + g_tokens
    c_tokens = ["Cloud Tokens"] + c_tokens
    d_tokens = ["DeepL Tokens"] + d_tokens
    assert len(d_tokens) == len(c_tokens) and len(c_tokens) == len(g_tokens) == len(true_tokens)
    with open('results' + lang + '.tsv', encoding="utf-8", mode='w', newline="") as outfile:
        # print(len(scores))

        for j in range(len(scorescloud)):
            original.append(sentencescloud[j][1])
            gold_answer.append(sentencesgold[j][0])
            g_answer.append(sentencesgpt[j][0])
            c_answer.append(sentencescloud[j][0])
            d_answer.append(sentencesdeep[j][0])
            if scoresgpt[j] >= scorescloud[j] and scoresgpt[j] >= scoresdeep[j]:
                translator.append("Our GPT Translation")
                b_answer.append(g_answer[j+1])
            elif scorescloud[j] >= scoresdeep[j] and scorescloud[j] >= scoresgpt[j]:
                translator.append("Google Translate")
                b_answer.append(c_answer[j+1])
            else:
                translator.append("DeepL")
                b_answer.append(d_answer[j+1])
        tsv_writer = csv.writer(outfile, delimiter="\t")
        scorescloud = ["Google Score"] + scorescloud
        scoresgpt = ["GPT Score"] + scoresgpt
        scoresdeep = ["DeepL Score"] + scoresdeep
        scoresgold = ["Gold Score"] + scoresgold
        lists = [b_answer, scoresgold, original, translator, scoresgpt, g_answer, scorescloud, c_answer, 
         scoresdeep, d_answer, e_tokens, g_tokens, c_tokens, d_tokens]

        lengths = [len(lst) for lst in lists]
        assert len(set(lengths)) == 1, f"Length mismatch: {lengths}"
        for row in zip_longest(original, b_answer, gold_answer, scoresgold, true_tokens, translator, scoresgpt, g_answer, scorescloud, c_answer, scoresdeep, d_answer,  e_tokens, g_tokens, c_tokens, d_tokens, fillvalue="NONE"):
            tsv_writer.writerow(row)


SYNSET_CACHED_KEYS = set()
SYNSET_CACHED_DICT = {}

def get_synsets_cachable(word, lang, pos):
    index = word + lang + pos
    if index in SYNSET_CACHED_KEYS:
        return SYNSET_CACHED_DICT[index]
    else:
        SYNSET_CACHED_KEYS.add(index)
        SYNSET_CACHED_DICT[index] = set([s.id for s in bn.get_synsets(word, from_langs=[langs[lang]], poses=[POS[pos]])])
        return SYNSET_CACHED_DICT[index]

def are_synonyms_or_cognates(word1, word2, pos1, pos2, lang2, lang1="en"):
    if jaro_similarity(word1, word2) > STRING_SIMILARITY_THRESHOLD:
        return True
    if pos1 == 'X' or pos2 == 'X':
        return False
    synsets1 = get_synsets_cachable(word1, lang1, pos1)
    synsets2 = get_synsets_cachable(word2, lang2, pos2)

    intersection = set.intersection(synsets1, synsets2)
    
    if len(intersection) > 0:
        # print(word1, word2, intersection)
        return True
    
    
    return False

def foreign_function_word(alignments, num, token, s1, repo):
    relevant_pairs = [tup for tup in alignments if tup[1] == num]

    for pair in relevant_pairs:
        if s1[pair[0]] in repo.function_words:

            return True
    return False


def position_of_entity_in_sentence(sublist, main_list):
    len_sublist = len(sublist)
    len_main = len(main_list)
    # Iterate over the main list and check for contiguous sublist match
    for i in range(len_main - len_sublist + 1):
        if main_list[i:i+len_sublist] == sublist:
            return i
    return -1


def part_of_ne(token, index, all_tokens, entities, is_list):
    
        
    if is_list:
        entities = entities.split(';')
    else:
        entities = [entities]
    for entity in entities:
        try:
            entity_tokens = entity.lower().split()
        except AttributeError:

            return False # sometimes no named entity and this is how it happens
        a = position_of_entity_in_sentence(entity_tokens, all_tokens)
        if a > -1:
            if a <= index < a + len(entity_tokens):
                # print(token + " part of " + str(entities))
                return True
    # print(token + " not part of " + str(entities))
    return False


def compare_sentence(f1, f2, x, en_d, ta_d, aligner, langcode, entities):
    found1 = False
    found2 = False

    with open(f1, 'r', encoding='utf-8') as file_one:
        with open(f2, 'r', encoding='utf-8') as file_two:
            s1_concepts = set()
            s2_concepts = set()
            s1_conlist = []
            s1_tokenlist = []
            s2_tokenlist = []
            s1_poslist = []
            s2_poslist = []
            s2_conlist = []
            for line in file_one:
                s_num = line[7:11]

                if int(s_num) == x:
                    found1 = True
                    s1_conlist.append(line[16:].strip().replace('\n', ''))
                    s1_tokenlist.append(en_d.find(line[:16]))
                    s1_poslist.append(en_d.find_pos(line[:16]))
                    # s1_concepts.add(line[16:])
            for line in file_two:

                s_num = line[7:11]
                if int(s_num) == x:
                    s2_conlist.append(line[16:].strip().replace('\n', ''))
                    s2_tokenlist.append(ta_d.find(line[:16]))
                    s2_poslist.append(ta_d.find_pos(line[:16]))
                    # s2_concepts.add(line[16:])
                    found2 = True

            alignments = aligner.get_word_aligns(s1_tokenlist, s2_tokenlist)
            for i, token in enumerate(s1_tokenlist):
                pos = s1_poslist[i]
                # print(token)
                try:
                    if token not in en_d.function_words:
                        if token not in PUNCTUATION:
                            if not part_of_ne(token, i, s1_tokenlist, entities[x][0], False):
                                try:
                                    other_token = s2_tokenlist[alignments['mwmf'][i][1]]
                                    other_pos = s2_poslist[alignments['mwmf'][i][1]]
                                    same = are_synonyms_or_cognates(token, other_token, pos, other_pos, langcode)
                                except IndexError:
                                    same = False
                                if same:
                                    s1_concepts.add(s2_conlist[alignments['mwmf'][i][1]])
                                else:
                                    s1_concepts.add(s1_conlist[i])
                except IndexError:
                    print(token)
                    print(en_d.function_words)
            for i, token in enumerate(s2_tokenlist):
                if token not in en_d.function_words and not foreign_function_word(alignments['mwmf'], i, token, s1_tokenlist, en_d):
                    if not part_of_ne(token, i, s2_tokenlist, entities[x][1], True):
                        if token not in PUNCTUATION:
                            s2_concepts.add(s2_conlist[i])


            try:
                s1_concepts.remove('<unk>')
            except KeyError:
               
                pass
            try:
                s2_concepts.remove('<unk>')
            except KeyError:
                
                pass
            if not found1 or not found2:

                return []
            score = percent_same_or_similar(list(s1_concepts), list(s2_concepts))
            try:
                return score[0], list(s1_concepts), list(s2_concepts)
            except ZeroDivisionError:
                return 0, list(s1_concepts), list(s2_concepts)


# compare('/home/dbasil1/TED/overlap/xl-wsd-code/testresults/takenine/enes.predictions.txt', '/home/dbasil1/TED/overlap/xl-wsd-code/testresults/takenine/test-es.predictions.txt', 'es', "test-es.data.xml", "enes.data.xml", "es_valid_ne.tsv")

compare('/home/dbasil1/TED/overlap/xl-wsd-code/testresults/taketen/enit.predictions.txt', '/home/dbasil1/TED/overlap/xl-wsd-code/testresults/taketen/test-it.predictions.txt', 'it', "test-it.data.xml", "enit.data.xml", "it_valid_ne.tsv")

compare('/home/dbasil1/TED/overlap/xl-wsd-code/testresults/taketen/enfr.predictions.txt', '/home/dbasil1/TED/overlap/xl-wsd-code/testresults/taketen/test-fr.predictions.txt', 'fr', "test-fr.data.xml", "enfr.data.xml", "fr_valid_ne.tsv")
