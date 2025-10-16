import deepl


def translate_text(text, target_lang):
    print(f"Traduzindo texto: '{text}' para {target_lang}")
    try:
        # translator = deepl.DeepLClient(DEEPL_API_KEY)
        deepl_client = deepl.DeepLClient("c8d48173-347f-4722-b2b0-a9bb61e8baa7:fx")
        result = deepl_client.translate_text(text, target_lang=target_lang)
        print(f"Texto traduzido: '{result.text}'")
        return result.text, None
    except deepl.DeepLException as e:
        error_msg = f"Erro da API DeepL: {e}"
        print(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Erro inesperado na tradução: {e}"
        print(error_msg)
        return None, error_msg
