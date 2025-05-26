from xml.dom import minidom
import csv
import xml.etree.ElementTree as ET
import re
from simalign import SentenceAligner
import spacy
import ast

import pandas as pd

FOREIGNLANGUAGES = {
    'it': spacy.load("it_core_news_sm"),    # Italian
    'es': spacy.load("es_core_news_sm"),    # Spanish
    'fr': spacy.load("fr_core_news_sm"),    # French
    'ja': spacy.load("ja_core_news_sm"),    # Japanese
    'ko': spacy.load("ko_core_news_sm"),    # Korean
    'zh': spacy.load("zh_core_web_sm"),     # Chinese (simplified)
    'de': spacy.load("de_core_news_sm"),    # German
    'ar': spacy.load("xx_ent_wiki_sm"),    # Arabic
    'tr': spacy.load("xx_ent_wiki_sm"),    # Turkish
    'th': spacy.load("xx_ent_wiki_sm"),     # Thai (no dedicated SpaCy model, using multi-language model)
}

eng_p = spacy.load("en_core_web_sm")



# pos_tags = {}
pos_tags = {
    "NN": "NOUN",
    "NR": "NOUN",
    "NT": "NOUN",
    "VV": "VERB",
    "VC": "VERB", "X": "X", "R": "ADV", "N": "NOUN", "A": "ADJ",
    "ADP": "X",
    "CCONJ": "X",
    "NUM": "X",
    "SYM": "X",
    "DET": "X",
    "AUX": "X",
    "PRON": "NOUN",
    "NOUN": "NOUN",
    "VERB": "VERB",
    "ADJ": "ADJ",
    "ADV": "ADV",

    "VE": "VERB",
    "VR": "VERB",
    "ETC": "VERB",
    "VA": "ADJ",  # Or "ADJ" depending on classification preference
    "JJ": "ADJ",
    "AD": "ADV",
    "DEV": "ADV",
    "DT": "X",
    "PU": "X",
    "PN": "X",
    "MSP": "X",
    "AS": "X",
    "DEC": "X",
    "P": "X",
    "SCONJ": "X",
    "CS": "X",
    "CD": "X",
    "M": "X",
    "CC": "X",
    "DEG": "X",
    "LC": "X",
    "SB": "X",
    "SP": "X",
    "EM": "X",
    "NOI": "X",
    "BA": "X",
    "OD": "X",
    "V": "VERB",
    "PROPN": "NOUN",
    "PUNCT": "X",
}


def get_id_column(csv_file_path):
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter="\t")
        a = [row["text"] for row in csvreader]
        b = []
        document = 1
        sentence = 1
        token = 1
        for entry in a:

            if entry == '...':
                sentence += 1
                token = 1
                b.append("GAPTOKEN")
            else:
                b.append(f"d{document:03d}.s{sentence:04d}.t{token:03d}")
                token += 1
        return b


def get_num_doc(csv_file_path):
    # print(get_column(csv_file_path,"Token ID"))
    return 1


def get_num_sentences(csv_file_path, doc_num):
    with open(csv_file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter='\t')
        ans = sum(1 for _ in reader) - 1  # Counts the rows in the file
    return ans


def add_tokens(sentence_id, input_file, object, root):
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter="\t")
        token_num = 0
        sentence_num = int(sentence_id[6:])
        # print(sentence_num)
        # print(sentence_num)
        # dockey = int(sentence_id[1:4])
        # print(sentence_id)
        sentence_cur = 1
        t = 1

        for row in csvreader:
            # print(row)
            
            if (sentence_num == sentence_cur) :
                # print(row["Token ID"])
                if "nan" != "nan":
                    token = root.createElement("wf")
                    # if row["Lemma"] != "":
                    #     token.setAttribute("lemma", row["Lemma"].split("#")[0])
                    # else:
                    token.setAttribute("lemma", row["text"])
                    pos = pos_tags[row["pos"]]
                    token.setAttribute("pos", pos)
                    x = root.createTextNode(row["text"])
                    token.appendChild(x)
                    object.appendChild(token)
                else:
                    token = root.createElement("instance")
                    if token_num % 10 == token_num and token_num != 10:
                        
                        token.setAttribute("id",
                                           f"d000{1}.s{sentence_cur:04d}.t00{token_num}")
                    elif token_num % 100 == token_num and token_num != 100:
                        token.setAttribute("id",
                                           f"d000{1}.s{sentence_cur:04d}.t0{token_num}")
                    else:
                        token.setAttribute("id",
                                           f"d000{1}.s{sentence_cur:04d}.t{token_num}")
                 
                    token_num += 1
                    # if row["Lemma"] != "":
                    #     token.setAttribute("lemma", row["Lemma"].split("#")[0])
                    # else:
                    token.setAttribute("lemma", row["text"])
                    if row["pos"] in pos_tags.keys():
                        pos = pos_tags[row["pos"]]
                    else:
                        pos = "X"
                    if row["text"] != "...":
                        token.setAttribute("pos", pos)
                        x = root.createTextNode(row["text"])
                        token.appendChild(x)
                        object.appendChild(token)
            elif sentence_num < sentence_cur:
                return
            if row["text"] == "...":
                sentence_cur += 1


def GenerateXML(input_file, other_file, output_file, lang):
    root = minidom.Document()
    xml = root.createElement("corpus")
    xml.setAttribute('lang', lang)
    root.appendChild(xml)
    if 1 == 1:
        
        # add more here if we want to be general
        document = root.createElement('text')
        document.setAttribute('id', "0001")
        xml.appendChild(document)
        num_sen = get_num_sentences(other_file, "0001")
        print(input_file)
        for y in range(1, num_sen*3 + 1):
            
            
            
            if y % 10 == y:
                senId = f"s0000{y}"
            elif y % 100 == y:
                senId = f"s000{y}"
            elif y % 1000 == y:
                senId = f"s00{y}"
            elif y % 10000 == y:
                senId = f"s0{y}"
            else: 
                senId = f"s{y}"
            
            sentence = root.createElement("sentence")
            sentence.setAttribute('id', f"d00{1}.{senId}")
            sentence.setAttribute('source', "semeval2024-en")
            document.appendChild(sentence)
            add_tokens(f"d00{1}.{senId}", input_file, sentence, root)
    xml_str = root.toprettyxml(indent="\t")
    with open(output_file, "w",  encoding="utf-8") as f:
        f.write(xml_str)


def fix_key_ids(input_key, output_key):
    with open(input_key, 'r', encoding='utf-8') as infile, \
            open(output_key, 'w', encoding='utf-8') as outfile:

        reader = csv.reader(infile, delimiter=' ')
        writer = csv.writer(outfile, delimiter=' ')
        token_num = 0
        sent_num = 0
        current_sent = "d000.s000"
        current_token = "d000.s000.t000"
        for row in reader:
            # print(row[0])
            # print(row[0],row[1])
            # if current_token == "d001.s001.t001":
            
            if current_token != row[0] and current_token != "d000.s000.t000":
                writer.writerow(d)
                token_num += 1
            if row[0][0:9] != current_sent:
                current_sent = row[0][0:9]
                current_token = row[0]
                token_num = 0
                # print(int(row[0]))
                sent_num = int(row[0][6:9]) - 1
                doc_num = int(row[0][2:5] )
            if token_num % 10 == token_num and token_num != 10:
                tok = f"t00{token_num}"
            else:
                tok = f"t0{token_num}"
            if sent_num % 10 == sent_num and sent_num != 10:
                sent = f"s00{sent_num}"
            elif sent_num % 100 == sent_num and sent_num != 100:
                sent = f"s0{sent_num}"
            else:
                sent = f"s{sent_num}"

            token_id = f"d{doc_num}.{sent}.{tok}"
           
            bn_synset = row[1:]

            d = [token_id]
            for a in bn_synset:
                d.append(a)
            # for x in range(len(bn_synset)):
            #     d[f"Sense {x}"] = bn_synset[x]

            current_token = row[0]
            # sent_num+=1


def decrement_sentence_ids(input_file, output_file):
    # Parse the XML file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Regex pattern to match the id format and capture the parts
    pattern = re.compile(r"(d\d{2,})\.(s\d{4})\.(t\d{3})")
    sentence_pattern = re.compile(r"(d\d{2,})\.(s\d{4})")

    # Iterate through all elements with an 'id' attribute
    for elem in root.findall(".//*[@id]"):
        original_id = elem.get('id')

        # Handle token-level IDs (e.g., d00a.s00b.t00c)
        match = pattern.match(original_id)
        if match:
            doc_part, sentence_part, token_part = match.groups()
            # Decrement the sentence number by 1
            sentence_num = int(sentence_part[1:])
            new_sentence_num = sentence_num - 1
            new_sentence_part = f"s{new_sentence_num:04d}"

            # Form the new id and update the element
            new_id = f"{doc_part}.{new_sentence_part}.{token_part}"
            elem.set('id', new_id)

        # Handle sentence-level IDs (e.g., d00a.s00b)
        match_sentence = sentence_pattern.match(original_id)
        if match_sentence and not pattern.match(original_id):
            doc_part, sentence_part = match_sentence.groups()
            # Decrement the sentence number by 1
            sentence_num = int(sentence_part[1:])
            new_sentence_num = sentence_num - 1
            new_sentence_part = f"s{new_sentence_num:04d}"

            # Form the new id and update the element
            new_id = f"{doc_part}.{new_sentence_part}"
            elem.set('id', new_id)

    # Write the modified XML to the output file
    tree.write(output_file, encoding='utf-8', xml_declaration=True)


def do_key_files(keyfile, referencefile):
    with open(referencefile, 'r', encoding='utf-8') as readfile:
        with open(keyfile, 'w', encoding='utf-8') as writefile:
            for line in readfile:

                if line[3:12] == "<instance":
                    code = line[17:33]

                    to_write = code + ' ' + 'bn:00024586n' + '\n'
                    writefile.write(to_write)



def tag_for_aligning(input_file, outfile_tar, lancode):
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter="\t")
        sentences1 = [(ast.literal_eval(row["targets"])[0]['translation']) for row in csvreader ]
        print(sentences1)
        sentences = sentences1 
        doc = ''
        for sentence in sentences:
            #parsed = ast.literal_eval(sentence[0])
            parsed = sentence
            doc += parsed + ' ... '

        target_doc = FOREIGNLANGUAGES[lancode](doc)
        
        tar_text = []
        tar_pos = []
        tar_tag = []
        
        for token in target_doc:
            tar_text.append(token.text.lower())
            tar_pos.append(token.pos_)
            tar_tag.append(token.tag)

        tar_ans = pd.DataFrame(
            {"text": tar_text, "pos": tar_pos, "tag": tar_tag})
        tar_ans.to_csv(outfile_tar, sep="\t", index=False)


def tag(input_file, outfile_en, outfile_tar, lancode):
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter="\t")
        sentences1 = [(row["Our GPT Translation"], row["source"]) for row in csvreader ]
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter="\t")
        sentences2 = [(row["Google Translate"], row["source"]) for row in csvreader]
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter="\t")
        sentences3 = [(row["DeepL"], row["source"]) for row in csvreader]

        sentences = sentences1 + sentences2 + sentences3
        assert len(sentences1) == len(sentences2) and len(sentences2) == len(sentences3)
        doc = ''
        for sentence in sentences:
            #parsed = ast.literal_eval(sentence[0])
            parsed = sentence
            doc += parsed[0] + ' ... '

        target_doc = FOREIGNLANGUAGES[lancode](doc)
        doc = ''
        for sentence in sentences:
            parsed = sentence
            doc += parsed[1].strip() + ' ... '

        english_doc = eng_p(doc)
        en_text = []
        en_pos = []
        en_tag = []
        tar_text = []
        tar_pos = []
        tar_tag = []
        for token in english_doc:
            
            en_text.append(token.text.lower())
            en_pos.append(token.pos_)
            en_tag.append(token.tag)
        for token in target_doc:
            
            tar_text.append(token.text.lower())
            tar_pos.append(token.pos_)
            tar_tag.append(token.tag)

        en_ans = pd.DataFrame({"text": en_text, "pos": en_pos, "tag": en_tag})
        tar_ans = pd.DataFrame(
            {"text": tar_text, "pos": tar_pos, "tag": tar_tag})
        en_ans.to_csv(outfile_en, sep="\t", index=False)
        tar_ans.to_csv(outfile_tar, sep="\t", index=False)


def align_and_add(tar_file, eng_file, lang_code):
    aligner = SentenceAligner(model="bert", token_type="bpe", matching_methods="mai")
    with open(tar_file, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter="\t")
        tar_words = [(row["text"]) for row in csvreader ]
    with open(eng_file, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter="\t")
        eng_words = [(row["text"]) for row in csvreader ]
    print(tar_words)
    print(eng_words)
    eng_sentences = []
    tar_sentences = []
    current_sublist = []
    for item in eng_words:
        if item == '...': 
            if current_sublist:  
                eng_sentences.append(current_sublist)
                current_sublist = []  # Reset the sublist
        else:
            current_sublist.append(item) 
    current_sublist = []
    eng_sentences = eng_sentences[: len(eng_sentences) // 3]
    for item in tar_words:
        if item == '...': 
            if current_sublist:  
                tar_sentences.append(current_sublist)
                current_sublist = []  # Reset the sublist
        else:
            current_sublist.append(item)
    assert len(tar_sentences) == len(eng_sentences) 
    for j in range(len(eng_sentences)):
        print(eng_sentences[j])
        print(tar_sentences[j])
        if len(eng_sentences[j]) == len(tar_sentences[j]):
            alignments = aligner.get_word_aligns(eng_sentences[j], tar_sentences[j])
            print(alignments)
            for matching_method in alignments:
                print(matching_method, ":", alignments[matching_method])
    

language_list = [['it', 'italian'], ['es', 'spanish'], ['fr', 'french'], ['ar', 'arabic'], ['de', 'german'], ['ja', 'japanese'], ['ko', 'korean'], ['th', 'thai'], ['tr', 'turkish'], ['zh', 'chinese']]
# language_list = [['es', 'spanish'], ['fr', 'french']]
for [lang, language] in language_list:
    print(language)
    input_xml = f"test{lang}.tsv"
    # input_xml = "italiansamples.tsv"
    tagged_file = f"taggedgold.tsv"
    eng_tagged_file = f"taggedenglish.tsv"
    output_xml = f"test-{lang}.data.xml"
    tag_for_align_file = f"taggedalign.tsv"
    output_other = f"en{lang}.data.xml"
    print("Tag starting")
    # tag_for_aligning(input_xml, tag_for_align_file, lang)
    tag(input_xml, eng_tagged_file, tagged_file, lang)
    # align_and_add(tag_for_align_file, eng_tagged_file, lang)
    
    print("XML starting")
    GenerateXML(tagged_file, input_xml, output_xml, lang)
    GenerateXML(eng_tagged_file, input_xml, output_other, 'eng')
    print("Decrementing")
    decrement_sentence_ids(output_xml, output_xml)
    decrement_sentence_ids(output_other, output_other)
    print("Key ing")
    do_key_files(f'en{lang}.gold.key.txt', output_other)
    do_key_files(f'test-{lang}.gold.key.txt', output_xml)
