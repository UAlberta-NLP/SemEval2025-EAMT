import opencc

# simplified to traditional
cc = opencc.OpenCC("s2t.json")


def prompts(
    prompt_version,
    source_language,
    target_language,
    src_sent,
    tgt_sent,
    ne_translation=None,
    named_entity=None,
    all_translations=None,
    entity_info=None,
):
    prompt = None

    match prompt_version:
        case "GPT_Official":
            prompt = (
                f"You are an expert translator."
                f"Translate from {source_language} to {target_language}."
                f"Provide only the translated text without explanations."
            )

        case "Entity_Emphasis":
            prompt = (
                f"You are an expert translator."
                f"Translate from {source_language} to {target_language} while preserving meaning and proper entity translation."
                f"Identify the named entity in the {source_language} sentence and search for its translations in {target_language} from Wikidata, and use the named entity translation in the translated sentence."
                f"Provide only the translated text without explanations."
            )

        case "One_Shot":
            prompt = (
                f"You are an expert translator."
                f"Translate from {source_language} to {target_language} while preserving meaning and proper entity translation."
                f"Refer to the example translation for consistency:\n\n"
                f"Source: {src_sent}\nTarget: {tgt_sent}\n\n"
                f"Provide only the translated text without explanations."
            )

        case "Entity_Emphasis_BN":
            ne_translation = (
                ne_translation
                if target_language != "Chinese (Traditional)"
                else cc.convert(ne_translation)
            )
            prompt = (
                f"You are an expert translator."
                f"Translate from {source_language} to {target_language} while preserving meaning and proper entity translation."
                f"Identify the named entity in the {source_language} sentence and translate it accurately as {ne_translation} in {target_language}."
                f"Then, provide a full translation of the sentence into {target_language}, ensuring the named entity is translated exactly as specified."
                f"Provide only the translated text without explanations."
            )

        case "One_Shot_BN":
            ne_translation = (
                entity_info["Label"]
                if target_language != "Chinese (Traditional)"
                else cc.convert(entity_info["Label"])
            )
            prompt = (
                f"You are an expert translator. "
                f"Translate from {source_language} to {target_language} while preserving meaning and proper entity translation. "
                f"Identify the named entity in the {source_language} sentence and translate it accurately as {ne_translation} in {target_language}."
                f"Then, provide a full translation of the sentence into {target_language}, ensuring the named entity is translated exactly as specified. "
                f"Refer to the example translation for consistency:\n\n"
                f"Source: {src_sent}\nTarget: {tgt_sent}\n\n"
                f"Provide only the translated text without explanations."
            )

        case "Soft_NETs_BN":
            ne_translation = (
                ne_translation
                if target_language != "Chinese (Traditional)"
                else cc.convert(ne_translation)
            )
            prompt = (
                f"You are an expert translator. "
                f"Translate from {source_language} to {target_language} while preserving meaning and proper entity translation. "
                f"A possible translation for the entity in the sentence is '{ne_translation}'. Use this if you think it is correct."
                f"Refer to the example translation for consistency:\n\n"
                f"Source: {src_sent}\nTarget: {tgt_sent}\n\n"
                f"Provide only the translated text without explanations."
            )

        case "Soft_NETs_WD":
            all_translations = (
                all_translations
                if target_language != "Chinese (Traditional)"
                else cc.convert(all_translations)
            )
            prompt = (
                f"You are an expert translator. Translate from {source_language} to {target_language} while preserving meaning and proper entity translation. "
                f"The named entity '{named_entity}' should be translated appropriately, considering the best contextual translation. "
                f"Use the most suitable translation from: '{all_translations}', with the first one being the most likely. "
                f"Refer to the example translation for consistency:\n\n"
                f"Source: {src_sent}\nTarget: {tgt_sent}\n\n"
                f"Provide only the translated text without explanations."
            )

        case "Missing_WD":
            prompt = (
                f"You are an expert translator. Translate from {source_language} to {target_language} while preserving meaning and proper entity translation. "
                f"The named entity '{named_entity}' should be translated appropriately, considering the best contextual translation. "
                f"Refer to the example translation for consistency:\n\n"
                f"Source: {src_sent}\nTarget: {tgt_sent}\n\n"
                f"Provide only the translated text without explanations."
            )

    return prompt
