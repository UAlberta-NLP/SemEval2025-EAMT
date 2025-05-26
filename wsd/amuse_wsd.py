import json
# import urllib2
from nltk.corpus import wordnet as wn
import babelnet as bn
import csv
import requests


def percent_same_or_similar(sent1bncs, sent2bncs, threshold=0.19):
    """Takes a list of babelnet concepts for each sentence and returns the decimal
    of how many are the same or similar"""
    
    
    sent1bncs = list(sent1bncs)
    print("Sent1", sent1bncs)
    
    sent2bncs = list(sent2bncs)
    print("Sent2", sent2bncs)

    sent1concepts = [wn_from_bn(a) for a in sent1bncs]
    sent2concepts = [wn_from_bn(a) for a in sent2bncs]

    print("sent1concepts", sent1concepts)
    print("sent2concepts", sent2concepts)

    sent1set = set()
    sent2set = set()

    all_concepts = []
    # for item in sent1concepts + sent2concepts:
    #     if item != None or item != "None":
    #         all_concepts.append(item)
    all_concepts = sent1concepts + sent2concepts
    new_all_concepts = all_concepts.copy()

    print("all_concepts", all_concepts)   
    print("new_all_concepts", new_all_concepts)
 
    #Go through all pairs
    for i in range(len(all_concepts)):
        found = False
        closest = None
        closest_score = 0
        for j in range(i + 1, len(all_concepts)):
            conc1 = all_concepts[i]
            conc2 = all_concepts[j]

            #Make sure we're not comparing anything to itself or twice
            assert i < j

            # If a concept is very similar to another concept, replace it with that one. 
            # If it's similar to multiple concepts, replace it with the most similar.
            # if conc2 == None:
            #     print("conc2", conc2)
            #     continue
            similarity = conc1.path_similarity(conc2)
            if similarity > threshold:
                if similarity > closest_score:
                    closest_score = similarity
                    found = True
                    closest = j
                # print(str(conc1) + " as similar as " + str(conc1.path_similarity(conc2)) + " to " + str(conc2))
        if found:
            new_all_concepts[i] = new_all_concepts[closest] 
 
    for k in range(len(new_all_concepts)):
        if k < len(sent1concepts):
            sent1set.add(new_all_concepts[k])
        else:
            sent2set.add(new_all_concepts[k])
    
    intersection_size = len(sent1set & sent2set) 


    union_size = len(sent1set | sent2set)  


    return intersection_size / union_size

# it_concepts = ["bn:00047090n", "bn:00002491n", "bn:00058732n", "bn:00009905n", "bn:00011744n", "bn:00022009n"]
# eng_concepts = ["bn:00115528r", "bn:00082652v", "bn:00040487n", "bn:00058734n", "bn:00083414v", "bn:00011744n", "bn:00116223r", "bn:00085689v"]


# Filter to show only callable functions




def wn_from_bn(bn_id):
    answer = []
    url = "https://babelnet.io/v9/getSynset?id=" + bn_id + "&key=d0a7bbee-08ba-45da-9ae9-4ea965750c32"
    
    response = requests.get(url)

    # Check if the response is successful
    if response.status_code == 200:
        # Parse the JSON response
        synset = response.json()
    # request = urllib2.Request(url)
    # request.add_header('Accept-encoding', 'gzip')
    # response = urllib2.urlopen(request)

    # if response.info().get('Content-Encoding') == 'gzip':
    #     buf = StringIO( response.read())
    #     f = gzip.GzipFile(fileobj=buf)
    #     data = json.loads(f.read())

    #     # retrieving BabelSense data
    #     senses = data['senses']
    #     for result in senses:
    #         lemma = result.get('lemma')
    #         language = result.get('language')
    #         print language.encode('utf-8') + "\t" + str(lemma.encode('utf-8'))
    
    
    # synset = bn.resources.BabelSynsetID(bn_id).to_synset()
    # print(synset)
    # print(synset.keys())
    # print(synset['wnOffsets'])

    if "synsetType" in synset.keys():
        if synset["synsetType"] == "CONCEPT" or synset["synsetType"] == "NAMED_ENTITY":
            if "wnOffsets" in synset.keys():
                for item in synset['wnOffsets']:
                    if item['source'] == 'WN':
                        wn_id = item["id"]

                        offset = wn_id.split(":")[1][:-1] 
                        pos = wn_id[-1]
                        # wordnet_id = f"{pos}.{offset}.01"
                        synset = wn.synset_from_pos_and_offset(pos, int(offset)) # wn.synset(wordnet_id)
                        return synset

    # # if synset._wn_offsets == None:
    # #     assert False
    # if len(synset._wn_offsets) > 0:
    #         if str(synset.type) == "CONCEPT" or str(synset.type) == "NAMED_ENTITY":
    #             s_id = str(synset._wn_offsets[0])
    #             synset = wn.synset_from_pos_and_offset(s_id[-1],int(s_id[-9:-1]))
    #             return synset
    #         else:
    #             print("I expected a concept")
    #             print(synset.type)
    #             print(bn_id)
    #             assert False

# with open('results.tsv', 'r', encoding='utf-8') as file:
#     reader = csv.reader(file, delimiter='\t')
#     for row in reader:
#         first_list = []
#         second_list = []
#         for token in row[1].split():
#             if token != '<unk>':
              
#                 first_list.append(token)
        
#         for token in row[2].split():
#             if token != '<unk>':
             
#                 second_list.append(token)
#         if row[0]  != "Scores":
#             score = percent_same_or_similar(first_list, second_list)
#             print(score)
#             print("up from")
#             print(row[0])
#             print(' ')
        


# print(percent_same_or_similar(eng_concepts, it_concepts))











def calculateOverlap(result, f_out, function_words, overlap_sent):
    tgt_result = result[0]
    # print(tgt_result) 

    src_result = result[1]
    # print(src_result)
    
    # Get all senses src
    src_ids = []
    for d_r in src_result['tokens']:
        id = d_r['bnSynsetId']
        lemma = d_r['lemma']
        # if id != "O":
        src_ids.append(lemma + "_" + id)

    # Get all senses tgt   
    tgt_ids = []
    for d_r in tgt_result['tokens']:
        id = d_r['bnSynsetId']
        lemma = d_r['lemma']
        # if id != "O":
        tgt_ids.append(lemma + "_" + id)
    
    print("src_ids", src_ids)
    print("tgt_ids", tgt_ids)
   
    # print("function words", function_words)
    src_senses = []
    tgt_senses = []
    src_idx = 0
    for pair in overlap_sent:
        print("-----------------------")
        print("pair", pair)
        wrd_1 = pair.split('_')[0]
        wrd_2 = pair.split('_')[1]

        print("wrd_1", wrd_1)
        print("wrd_2", wrd_2)

        print("src_idx", src_idx)
        if wrd_1[:3] == wrd_2[:3]: # cognate
            if src_ids[src_idx].split("_")[1] != 'O':
                src_senses.append(src_ids[src_idx].split("_")[1])
                tgt_senses.append(src_ids[src_idx].split("_")[1])
            src_idx += 1

        elif wrd_1.lower() in function_words: # function word
            src_idx += 1
            continue
        
        else:
            if src_ids[src_idx].split("_")[1] != 'O':
                src_senses.append(src_ids[src_idx].split("_")[1])

            for lemma_sense in tgt_ids:
                if wrd_2 == lemma_sense.split("_")[0]:
                    if lemma_sense.split("_")[1] != "O":
                        tgt_senses.append(lemma_sense.split("_")[1])

            src_idx += 1


    # src_ids = []
    # for d_r in src_result['tokens']:
    #     # if d_r["lemma"] in function_words or d_r["text"] in function_words:
    #     #     continue
    #     id = d_r['bnSynsetId']
    #     if id != "O":
    #         src_ids.append(id)
    # # print(src_ids)
    # src_ids_set = set(src_ids)

    
    # tgt_ids = []
    # for d_r in tgt_result['tokens']:
    #     # print(d_r)
    #     id = d_r['bnSynsetId']
    #     if id != "O":
    #         tgt_ids.append(id)
    # # print(tgt_ids)
    # tgt_ids_set = set(tgt_ids)

    
    
    src_senses = set(src_senses)
    tgt_senses = set(tgt_senses)
    overlap = len(src_senses.intersection(tgt_senses)) / len(src_senses.union(tgt_senses))
    print(overlap)

    # new_overlap = percent_same_or_similar(src_senses, tgt_senses)
    # print(new_overlap)

    # f_out.write(str(src_senses) + '\t' + str(tgt_senses) + "\t" + str(src_senses.intersection(tgt_senses)) + "\t" + str(overlap) +  "\n")
    return overlap

if __name__ == "__main__":
    
    filename = "sample_1_wsd_all_lang.jsonl"
    function_words_filename = "functional_word_list.txt"
    # alignment_filename =  "BabAlign/sample_1.en-it.babelalign.out"
    alignment_filename =  "simalign_sample_1_en_it.txt"

    function_words = []
    lines = open(function_words_filename, "r").readlines()
    for line in lines:
        wrd = line.strip()
        function_words.append(wrd)

    alignment_dict = {}
    lines = open(alignment_filename, "r").readlines()
    for line in lines:
        prts = line.strip().split("\t")
        # k = prts[0].strip().split(".")[1]
        k = prts[0].strip().split(".")[0]
        print(k)

        src_wrd = prts[1]
        tgt_wrd = prts[2]
        # if src_wrd == "NONE" or tgt_wrd == "NONE":
        #     continue
        # else:
        pair = src_wrd + "_" + tgt_wrd
        if k in alignment_dict.keys():
            alignment_dict[k].append(pair)
        else:
            alignment_dict[k] = [pair]


    # print(alignment_dict)

    with open(filename, 'r', encoding="utf-8") as json_file:
        json_list = list(json_file)
    
    filename_out = "refine_overlap_sample_v1.txt"
    f_out = open(filename_out, "w", encoding="utf-8")
    i = 0
    sum_overlap = 0
    cnt_overlap = 0
    for row in json_list:
        entry = json.loads(row)
        if entry[0]['lang'] == "IT" and entry[1]['lang'] == "EN": 
            overlap_sent = alignment_dict['s' + '%03d' % i]
            overlap = calculateOverlap(entry, f_out, function_words, overlap_sent)
            sum_overlap += overlap
            cnt_overlap += 1
            i += 1
    print(sum_overlap/cnt_overlap)
    f_out.close()
