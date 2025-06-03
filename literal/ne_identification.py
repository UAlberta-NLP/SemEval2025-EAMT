def part_of_ne(token, index, all_tokens, all_tokens_text, entities, is_list):
    """
    Determines whether a token is part of a named entity.
    """
    token = token.lower()
    
    if is_list:
        answer = any(is_in_this_ne(token, index, all_tokens_text, entity) 
                   for entity in entities.split(';'))
    else:
        answer = is_in_this_ne(token, index, all_tokens_text, entities)
    return answer


def punc_count(text):
    """
    Counts occurrences of common punctuation marks in the text.
    """
    return sum(text.count(p) for p in ['?', '¿', ',', '.'])


def remove_punct_except_hyphen_for_item(tokens):
    """
    Removes selected punctuation (?, ¿, ,, .) and lowercases all tokens.
    Keeps hyphens and removes empty entries.
    """
    return [token.replace('?', '')
                 .replace('¿', '')
                 .replace(',', '')
                 .replace('.', '')
                 .lower()
            for token in tokens if token.strip()]


def position_of_entity_in_sentence(sublist, main_list):
    """
    Returns the index of the first occurrence of a contiguous sublist in a list.
    Returns -1 if the sublist is not found.
    """
    len_sub = len(sublist)
    for i in range(len(main_list) - len_sub + 1):
        if main_list[i:i + len_sub] == sublist:
            return i
    return -1


def is_in_this_ne(token, index, all_tokens_text, entity):
    """
    Checks if a token is within the span of the entity in the context of a tokenized sentence.
    """
    tokens_orig = remove_punct_except_hyphen_for_item(all_tokens_text.split())
    tokens_entity = remove_punct_except_hyphen_for_item(entity.split())
    entity_text = ' '.join(tokens_entity)
    sentence_text = ' '.join(tokens_orig)

    # Simple case: token occurs once, just check text inclusion
    if entity.lower() in sentence_text and sentence_text.count(token) <= 1:
        return token in entity_text

    # Fallback to positional logic
    entity_start = position_of_entity_in_sentence(tokens_entity, tokens_orig)
    if entity_start != -1:
        in_direct_span = entity_start <= index < entity_start + len(tokens_entity)
        in_offset_span = entity_start + len(tokens_entity) + punc_count(' '.join(all_tokens_text.split()[:index])) - 1 == index
        return in_direct_span or in_offset_span

    return False
