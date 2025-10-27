import os
import deepl
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPL_API_KEY")


def translate_text(text, target_lang):
    if not api_key:
        raise ValueError("Chave da API DeepL não encontrada. Verifique o arquivo .env")

    try:
        deepl_client = deepl.DeepLClient(api_key)
        result = deepl_client.translate_text(text, target_lang=target_lang)
        return result.text, None
    except deepl.DeepLException as e:
        error_msg = f"Erro da API DeepL: {e}"
        print(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Erro inesperado na tradução: {e}"
        print(error_msg)
        return None, error_msg
