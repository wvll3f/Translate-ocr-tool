from pydoc import text
import customtkinter as ctk
import easyocr
import mss
from engine.translator import translate_text
from view.RegionSelector import RegionSelector
import queue
import threading
from PIL import Image
import numpy as np
import time


class App(ctk.CTk):
    def __init__(self, root):
        super().__init__()
        self.ocr_engine = None
        self.root = root
        self.lang = "en"
        self.root.reader = easyocr.Reader([self.lang], gpu=False)
        self.root.region = None
        self.ocr_queue = queue.Queue()
        self._running = False
        self.root.title("OCR translate tool")
        self.root.geometry("500x600")
        self.root.maxsize(width=500, height=600)
        self.root.minsize(width=300, height=400)
        self.root.columnconfigure((0, 1, 2), weight=1)
        self.root.rowconfigure((0, 1, 2, 3), weight=1)

        self.root.btn_select = ctk.CTkButton(
            root,
            text="Selecionar Área",
            height=40,
            cursor="hand2",
            command=self.select_region,
        )
        self.root.btn_select.grid(row=0, column=0, padx=5, pady=5)
        self.root.btn_capture = ctk.CTkButton(
            root,
            text="Iniciar",
            height=40,
            cursor="hand2",
            command=self.iniciar_thread_ocr,
            state="disabled",
        )
        self.root.btn_capture.grid(row=0, column=1, padx=5, pady=5)
        self.root.btn_stop = ctk.CTkButton(
            root,
            text="Parar",
            height=40,
            state="disabled",
            command=self.parar_thread_ocr,
        )
        self.root.btn_stop.grid(row=0, column=2, padx=5, pady=5)

        self.root.region_label = ctk.CTkLabel(root, text="Região: Tela inteira")
        self.root.region_label.grid(
            row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew"
        )

        self.root.frame_text = ctk.CTkFrame(root)
        self.root.frame_text.grid(
            row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew"
        )

        self.root.text_captured = ctk.CTkTextbox(self.root.frame_text)
        self.root.text_captured.pack(fill="both", expand=True, padx=5, pady=5)

        self.root.translate = ctk.CTkFrame(root)
        self.root.translate.grid(
            row=3, column=0, columnspan=3, padx=5, pady=5, sticky="nsew"
        )

        self.root.text_translated = ctk.CTkTextbox(self.root.translate)
        self.root.text_translated.pack(fill="both", expand=True, padx=5, pady=5)

        self.verificar_fila()

    def atualizar_texto(self, texto, erro_traducao):
        self.root.text_captured.delete("1.0", "end")
        self.root.text_captured.insert("end", texto)
        if erro_traducao:
            self.root.text_translated.delete("1.0", "end")
            self.root.text_translated.insert(
                "end", f"Erro na tradução: {erro_traducao}"
            )

    def select_region(self):
        selector = RegionSelector(self.root)
        selected = selector.select_region()
        if selected:
            self.region = selected
            self.root.region_label.configure(
                text=f"Região: {self.region['width']}x{self.region['height']} at ({self.region['left']}, {self.region['top']})"
            )
            self.root.btn_capture.configure(state="normal")
        else:
            self.root.region = None
            self.root.region_label.configure(text="Região: Tela inteira")

    def iniciar_thread_ocr(self):
        self._running = True
        self.root.btn_capture.configure(state="disabled", text="Processando...")
        self.root.btn_stop.configure(state="normal")

        thread = threading.Thread(
            target=self.worker_ocr_screenshot, args=(self.ocr_queue,)
        )
        thread.daemon = True
        thread.start()

    def parar_thread_ocr(self):
        self._running = False
        self.root.btn_capture.configure(state="normal", text="Iniciar")
        self.root.btn_stop.configure(state="disabled")

    def worker_ocr_screenshot(self, q):
        while self._running:
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
                    byteImg = np.array(img)

                resultado = self.root.reader.readtext(
                    image=byteImg, detail=0, paragraph=True
                )

                if resultado:
                    texto_formatado = "\n".join(resultado)
                    if not q.full():
                        q.put(texto_formatado)

                time.sleep(0.5)

            except Exception as e:
                print(f"[Thread {threading.get_ident()}] - ERRO: {e}")
                q.put(f"ERRO DURANTE O PROCESSO: {e}")
        print(f"[Thread {threading.get_ident()}] - Processamento finalizado.")

    def verificar_fila(self):
        try:
            resultado = self.ocr_queue.get_nowait()
            self.root.text_captured.delete("1.0", "end")
            self.root.text_captured.insert(
                "0.0",resultado
            )
            self.root.text_translated.delete("1.0", "end")

            texto_traduzido, erro_traducao = translate_text(
                resultado, target_lang="PT-BR"
            )
            self.root.text_translated.delete("1.0", "end")
            self.root.text_translated.insert("1.0", texto_traduzido)
            if erro_traducao:
                self.root.text_translated.insert(
                    "erro ao traduzir o texto: {erro_traducao}"
                )

        except queue.Empty:
            pass

        self.after(100, self.verificar_fila)
