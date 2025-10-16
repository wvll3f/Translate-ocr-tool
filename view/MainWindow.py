import customtkinter as ctk
import view.RegionSelector as RegionSelector
import engine.OCREngine as ocr


class App(ctk.CTk):
    def __init__(self, root):
        super().__init__()
        self.root = root
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
            command=self.start_ocr,
            state="disabled",
        )
        self.root.btn_capture.grid(row=0, column=1, padx=5, pady=5)
        self.root.btn_stop = ctk.CTkButton(
            root,
            text="Parar",
            height=40,
            cursor="hand2",
            command=self.stop_ocr,
            state="disabled",
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

    def start_ocr(self):
        ocr.OCREngine(
            region =self.region,
            fps=2,
            lang="eng",
            translate=True,
            target_lang="PT-BR",
            text_callback=lambda text: print(f"Texto detectado: {text}"),
        )

        ocr.OCREngine.start(self)
        self.root.btn_capture.configure(state="disabled")
        self.root.btn_select.configure(state="disabled")
        self.root.btn_stop.configure(state="normal")

    def stop_ocr(self):
        ocr.OCREngine.stop(self)
        self.root.btn_capture.configure(state="normal")
        self.root.btn_select.configure(state="normal")

    def select_region(self):
        selector = RegionSelector.RegionSelector(self.root)
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
