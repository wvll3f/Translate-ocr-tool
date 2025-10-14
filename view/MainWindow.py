import customtkinter as ctk
import view.RegionSelector as RegionSelector


class App(ctk.CTk):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.root.title("my app")
        self.root.geometry("500x600")
        self.root.maxsize(width=500, height=600)
        self.root.minsize(width=300, height=400)
        self.root.columnconfigure((0, 1, 2), weight=1)
        self.root.rowconfigure((0, 1, 2, 3), weight=1)

        self.root.btn_select = ctk.CTkButton(
            root, text="Selecionar Área", height=40, cursor="hand2", command=self.select_region,
        )
        self.root.btn_select.grid(row=0, column=0, padx=5, pady=5)
        self.root.btn_capture = ctk.CTkButton(
            root, text="Iniciar OCR", height=40, cursor="hand2", state="disabled"
        )
        self.root.btn_capture.grid(row=0, column=1, padx=5, pady=5)
        self.root.btn_stop = ctk.CTkButton(
            root, text="Parar OCR", height=40, cursor="hand2", state="disabled"
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
        self.root.translate = ctk.CTkFrame(root)
        self.root.translate.grid(
            row=3, column=0, columnspan=3, padx=5, pady=5, sticky="nsew"
        )

    def button_callback(self):
        print("button pressed")

    def select_region(self):
        selector = RegionSelector.RegionSelector(self.root)
        selected = selector.select_region()
        if selected:
            self.region = selected
            self.root.region_label.configure(
                text=f"Região: {self.region['width']}x{self.region['height']} at ({self.region['left']}, {self.region['top']})"
            )
        else:
            self.root.region = None
            self.root.region_label.configure(text="Região: Tela inteira")
