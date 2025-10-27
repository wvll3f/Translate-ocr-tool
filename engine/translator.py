import deepl


def translate_text(text, target_lang):
    try:
        deepl_client = deepl.DeepLClient("c8d48173-347f-4722-b2b0-a9bb61e8baa7:fx")
        result = deepl_client.translate_text(text, target_lang="PT-BR")
        return result.text, None
    except deepl.DeepLException as e:
        error_msg = f"Erro da API DeepL: {e}"
        print(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Erro inesperado na tradução: {e}"
        print(error_msg)
        return None, error_msg
