import queue
import time
import threading
import easyocr
from mss import mss
from PIL import Image
import numpy as np
import cv2


class OCREngine(threading.Thread):
    def __init__(
        self, region, lang, fps, text_callback, translate=False, target_lang="PT-BR"
    ):
        super().__init__(daemon=True)

        self.ocr_queue = queue.Queue()
        self._region = region
        self._lang = lang
        self._fps = fps
        self._text_callback = text_callback
        self._translate = translate
        self._target_lang = target_lang
        self._running = False
        self._last_text = ""

        self._ocr_reader = easyocr.Reader(["pt", "en"], gpu=False, verbose=False)
        print("EasyOCR inicializado com sucesso")

    def iniciar_thread_ocr(self):
        self.textbox.insert(
            "end", "\n[INFO] Capturando a tela e iniciando o OCR em segundo plano...\n"
        )
        self.start_button.configure(state="disabled", text="Processando...")

        thread = threading.Thread(
            target=self.worker_ocr_screenshot, args=(self.ocr_queue,)
        )
        thread.daemon = True
        thread.start()

    def worker_ocr_screenshot(self, q):
        print(f"[Thread {threading.get_ident()}] - Iniciando captura de tela e OCR.")
        try:
            with mss.mss() as sct:
                if self.region:
                    monitor = {
                        "left": self.region["left"],
                        "top": self.region["top"],
                        "width": self.region["width"],
                        "height": self.region["height"],
                    }
                else:
                    monitor = sct.monitors[1]

                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                return np.array(img)

            resultado = self.reader.readtext(img, detail=0, paragraph=True)

            if resultado:
                texto_formatado = "\n".join(resultado)
                q.put(texto_formatado)
            else:
                q.put("[AVISO] Nenhum texto foi encontrado na captura de tela.")

        except Exception as e:
            print(f"[Thread {threading.get_ident()}] - ERRO: {e}")
            q.put(f"ERRO DURANTE O PROCESSO: {e}")
        print(f"[Thread {threading.get_ident()}] - Processamento finalizado.")

    
    def verificar_fila(self):
        try:
            resultado = self.ocr_queue.get_nowait()
            self.textbox.delete("1.0", "end")
            self.textbox.insert("0.0", "--- Resultado do OCR ---\n\n" + resultado)

            self.start_button.configure(state="normal", text="Tirar Print e Ler Texto")

        except queue.Empty:
            pass

        self.after(100, self.verificar_fila)
