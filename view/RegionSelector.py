import customtkinter as ctk


class RegionSelector:
    """Permite selecionar uma região da tela"""

    def __init__(self, parent):
        self.parent = parent
        self.region = None
        self.start_x = None
        self.start_y = None

    def select_region(self):
        """Abre uma janela fullscreen transparente para seleção"""
        self.parent.withdraw()  # Esconde a janela principal

        root = ctk.CTkToplevel()
        root.attributes("-fullscreen", True)
        root.attributes("-alpha", 0.4)
        root.configure(bg="black")

        canvas = ctk.CTkCanvas(root, cursor="cross", bg="black", highlightthickness=0)
        canvas.pack(fill=ctk.BOTH, expand=True)

        rect = None

        def on_mouse_down(event):
            nonlocal rect
            self.start_x = event.x
            self.start_y = event.y
            rect = canvas.create_rectangle(
                self.start_x,
                self.start_y,
                self.start_x,
                self.start_y,
                outline="#1dffe5",
                dash=(2, 5),
                width=3,
            )

        def on_mouse_move(event):
            if rect:
                canvas.coords(rect, self.start_x, self.start_y, event.x, event.y)

        def on_mouse_up(event):
            x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
            x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)

            self.region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
            root.quit()
            root.destroy()
            self.parent.deiconify()  # Mostra a janela principal novamente

        canvas.bind("<Button-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_move)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)

        instruction = ctk.CTkLabel(
            root,
            text="Arraste para selecionar a região da tela\nESC para cancelar",
            fg_color="white",
            bg_color="black",
            font=("Arial", 16),
        )
        instruction.place(relx=0.5, rely=0.05, anchor="center")

        def cancel_selection(e):
            self.region = None
            root.destroy()
            self.parent.deiconify()

        root.bind("<Escape>", cancel_selection)
        root.mainloop()

        return self.region
