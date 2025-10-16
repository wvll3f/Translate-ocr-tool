import time
import threading
import easyocr
from mss import mss
from PIL import Image
import numpy as np
import cv2
from engine.translator import translate_text

class OCREngine(threading.Thread):
    """Motor de OCR em tempo real que também pode traduzir o texto."""
    def __init__(self, region, lang, fps, text_callback, translate=False, target_lang='PT-BR'):
        super().__init__(daemon=True)
        
        # Armazena os parâmetros com nomes protegidos
        self._region = region
        self._lang = lang
        self._fps = fps
        self._text_callback = text_callback
        self._translate = translate
        self._target_lang = target_lang
        self._running = False
        self._last_text = ""
        
        # Inicializa o EasyOCR (isso pode levar alguns segundos na primeira vez)
        lang_code = self._convert_lang_code(lang)
        print(f"Inicializando EasyOCR com idioma: {lang_code}")
        self._ocr_reader = easyocr.Reader([lang_code], gpu=False, verbose=False)
        print("EasyOCR inicializado com sucesso")
    
    def _convert_lang_code(self, tesseract_lang):
        """
        Converte códigos de idioma do Tesseract para EasyOCR.
        EasyOCR usa códigos ISO 639-1 (2 letras).
        """
        lang_map = {
            'eng': 'en',
            'por': 'pt',
            'spa': 'es',
            'fra': 'fr',
            'deu': 'de',
            'ita': 'it',
            'jpn': 'ja',
            'kor': 'ko',
            'chi_sim': 'ch_sim',
            'chi_tra': 'ch_tra',
            'rus': 'ru',
            'ara': 'ar',
        }
        return lang_map.get(tesseract_lang, 'en')
    
    def run(self):
        self._running = True
        sct = mss()
        
        while self._running:
            start_time = time.time()
            try:
                # Captura de tela
                if self._region:
                    # Responsável pela seleção da área de captura
                    screenshot = sct.grab(self._region)
                else:
                    screenshot = sct.grab(sct.monitors[1])
               
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                img_np = np.array(img)
                
                # Converte a imagem em preto e branco (binária)
                gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
                binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                               cv2.THRESH_BINARY, 11, 2)
                
                # OCR com EasyOCR
                # readtext retorna lista de tuplas: (bbox, text, confidence)
                results = self._ocr_reader.readtext(binary)
                
                text_parts = []
                confidences = []
                
                for result in results:
                    bbox, text, conf = result
                    # EasyOCR retorna confiança entre 0 e 1, converte para 0-100
                    confidence = int(conf * 100)
                    if confidence > 30:
                        text = text.strip()
                        if text:
                            text_parts.append(text)
                            confidences.append(confidence)
               
                original_text = ' '.join(text_parts).strip()
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                # Verifica se o texto mudou
                if original_text and original_text != self._last_text:
                    self._last_text = original_text
                    final_text = original_text
                    translation_error = None
                    
                    # Tradução, se ativada
                    if self._translate:
                        translated_text, error = translate_text(original_text, self._target_lang)
                        if error:
                            translation_error = error
                        elif translated_text:
                            final_text = translated_text
                    
                    # Envia o resultado para a UI
                    if self._text_callback:
                        self._text_callback(original_text, final_text, avg_confidence, translation_error)
           
            except Exception as e:
                print(f"Erro no loop de OCR: {e}")
                import traceback
                traceback.print_exc()
           
            # Controle de FPS
            elapsed = time.time() - start_time
            interval = 1.0 / self._fps
            if elapsed < interval:
                time.sleep(interval - elapsed)
    
    def stop(self):
        self._running = False