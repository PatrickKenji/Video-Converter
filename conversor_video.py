import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy.editor import VideoFileClip
import os
from queue import Queue
import threading
import time

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, radius=25, **kwargs):
        super().__init__(parent, **kwargs)
        self.command = command
        self.radius = radius
        
        # Cores
        self.bg_color = "#2b2b2b"
        self.hover_color = "#3b3b3b"
        self.text_color = "white"
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        
        self.draw_button(text)
        
    def draw_button(self, text):
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        
        # Desenha o botão arredondado
        self.create_rounded_rect(0, 0, width, height, self.radius, fill=self.bg_color)
        
        # Adiciona o texto
        self.create_text(width/2, height/2, text=text, fill=self.text_color, font=("Segoe UI", 10, "bold"))
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def _on_enter(self, event):
        self.itemconfig(1, fill=self.hover_color)
        
    def _on_leave(self, event):
        self.itemconfig(1, fill=self.bg_color)
        
    def _on_click(self, event):
        if self.command:
            self.command()

class ConversorVideo:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Vídeo")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        
        # Configuração do estilo
        self.style = ttk.Style()
        self.style.configure("Dark.TFrame", background="#1e1e1e")
        self.style.configure("Dark.TLabel", background="#1e1e1e", foreground="white")
        self.style.configure("Dark.TCombobox", background="#2b2b2b", foreground="white")
        self.style.configure("Dark.Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
        self.style.configure("Dark.Treeview.Heading", background="#2b2b2b", foreground="black", font=("Segoe UI", 10, "bold"))
        self.style.map("Dark.Treeview.Heading", background=[("active", "#3b3b3b")])
        self.style.configure("Dark.Horizontal.TProgressbar", background="#00ff00", troughcolor="#2b2b2b")
        
        # Variáveis
        self.caminho_saida = tk.StringVar()
        self.formato_saida = tk.StringVar(value="mp4")
        self.fila_videos = []
        self.conversao_ativa = False
        self.progresso = 0
        self.video_atual = ""
        
        # Frame principal
        self.frame = ttk.Frame(root, style="Dark.TFrame", padding=30)
        self.frame.pack(expand=True, fill='both')
        
        # Widgets
        self.criar_widgets()
        
    def criar_widgets(self):
        # Título
        titulo = ttk.Label(self.frame, text="Conversor de Vídeo", 
                         font=("Segoe UI", 20, "bold"), style="Dark.TLabel")
        titulo.pack(pady=(0, 20))
        
        # Frame para controles
        frame_controles = ttk.Frame(self.frame, style="Dark.TFrame")
        frame_controles.pack(fill='x', pady=10)
        
        # Botão para adicionar vídeos
        btn_adicionar = RoundedButton(frame_controles, "Adicionar Vídeos", 
                                    command=self.adicionar_videos,
                                    width=200, height=40)
        btn_adicionar.pack(side='left', padx=(0, 10))
        
        # Frame para formato de saída
        frame_formato = ttk.Frame(frame_controles, style="Dark.TFrame")
        frame_formato.pack(side='left', padx=10)
        
        lbl_formato = ttk.Label(frame_formato, text="Formato de saída:",
                              style="Dark.TLabel")
        lbl_formato.pack(side='left', padx=(0, 10))
        
        formatos = ["mp4", "avi", "mov", "mkv", "webm"]
        menu_formato = ttk.Combobox(frame_formato, textvariable=self.formato_saida,
                                  values=formatos, state="readonly",
                                  style="Dark.TCombobox")
        menu_formato.pack(side='left')
        
        # Botão para selecionar pasta de saída
        btn_saida = RoundedButton(frame_controles, "Selecionar Pasta de Saída",
                                command=self.selecionar_pasta_saida,
                                width=200, height=40)
        btn_saida.pack(side='left', padx=10)
        
        # Frame para a lista de vídeos
        frame_lista = ttk.Frame(self.frame, style="Dark.TFrame")
        frame_lista.pack(fill='both', expand=True, pady=10)
        
        # Frame para treeview e scrollbar
        frame_tree = ttk.Frame(frame_lista, style="Dark.TFrame")
        frame_tree.pack(fill='both', expand=True)
        
        # Treeview para mostrar a fila de vídeos
        colunas = ("arquivo", "status")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", style="Dark.Treeview")
        self.tree.heading("arquivo", text="Arquivo")
        self.tree.heading("status", text="Status")
        self.tree.column("arquivo", width=400)
        self.tree.column("status", width=200)
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar para a treeview
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Label para mostrar o vídeo atual
        self.lbl_video_atual = ttk.Label(self.frame, text="", style="Dark.TLabel")
        self.lbl_video_atual.pack(pady=(0, 5))
        
        # Frame para botões de controle
        frame_botoes = ttk.Frame(self.frame, style="Dark.TFrame")
        frame_botoes.pack(fill='x', pady=10)
        
        # Botão para remover vídeo selecionado
        btn_remover = RoundedButton(frame_botoes, "Remover Selecionado",
                                  command=self.remover_selecionado,
                                  width=200, height=40)
        btn_remover.pack(side='left', padx=10)
        
        # Botão para limpar fila
        btn_limpar = RoundedButton(frame_botoes, "Limpar Fila",
                                 command=self.limpar_fila,
                                 width=200, height=40)
        btn_limpar.pack(side='left', padx=10)
        
        # Botão de conversão
        btn_converter = RoundedButton(frame_botoes, "Iniciar Conversão",
                                    command=self.iniciar_conversao,
                                    width=200, height=40)
        btn_converter.pack(side='right', padx=10)
        
    def atualizar_progresso(self, progresso):
        self.progresso = progresso
        self.progress_bar["value"] = progresso
        self.root.update_idletasks()
        
    def adicionar_videos(self):
        arquivos = filedialog.askopenfilenames(
            title="Selecione os vídeos",
            filetypes=[
                ("Vídeos", "*.mp4 *.avi *.mov *.mkv *.webm"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if arquivos:
            for arquivo in arquivos:
                self.fila_videos.append({
                    "caminho": arquivo,
                    "status": "Na fila"
                })
                self.tree.insert("", "end", values=(os.path.basename(arquivo), "Na fila"))
                
    def selecionar_pasta_saida(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta de saída")
        if pasta:
            self.caminho_saida.set(pasta)
            
    def remover_selecionado(self):
        selecionado = self.tree.selection()
        if selecionado:
            index = self.tree.index(selecionado[0])
            self.tree.delete(selecionado[0])
            self.fila_videos.pop(index)
            
    def limpar_fila(self):
        self.tree.delete(*self.tree.get_children())
        self.fila_videos.clear()
        
    def atualizar_status(self, index, status):
        self.fila_videos[index]["status"] = status
        self.tree.set(self.tree.get_children()[index], "status", status)
        
    def converter_video(self, index):
        if not self.caminho_saida.get():
            messagebox.showerror("Erro", "Por favor, selecione a pasta de saída")
            return
            
        video_info = self.fila_videos[index]
        try:
            # Atualiza status para "Convertendo"
            self.atualizar_status(index, "Convertendo...")
            self.video_atual = os.path.basename(video_info["caminho"])
            self.lbl_video_atual.config(text=f"Convertendo: {self.video_atual}")
            self.root.update_idletasks()
            
            # Carrega o vídeo
            video = VideoFileClip(video_info["caminho"])
            
            # Define o nome do arquivo de saída
            nome_arquivo = os.path.splitext(os.path.basename(video_info["caminho"]))[0]
            caminho_completo = os.path.join(
                self.caminho_saida.get(),
                f"{nome_arquivo}.{self.formato_saida.get()}"
            )
            
            # Estimar tempo de conversão (simples: assume 1x tempo do vídeo)
            tempo_estimado = int(video.duration)
            inicio = time.time()
            
            def atualizar_tempo():
                while True:
                    decorrido = int(time.time() - inicio)
                    restante = max(0, tempo_estimado - decorrido)
                    mins, secs = divmod(restante, 60)
                    tempo_str = f"{mins:02d}:{secs:02d}"
                    self.atualizar_status(index, f"Convertendo... Tempo estimado: {tempo_str}")
                    self.root.update_idletasks()
                    if restante <= 0 or not self.conversao_ativa:
                        break
                    time.sleep(1)
            
            t = threading.Thread(target=atualizar_tempo, daemon=True)
            t.start()
            
            # Converte o vídeo
            video.write_videofile(
                caminho_completo,
                threads=4,
                preset='fast',
                bitrate='1500k',
                audio_bitrate='128k'
            )
            
            # Atualiza status para "Concluído"
            self.atualizar_status(index, "Concluído")
            self.lbl_video_atual.config(text="")
            
        except Exception as e:
            # Atualiza status para "Erro"
            self.atualizar_status(index, f"Erro: {str(e)}")
            self.lbl_video_atual.config(text="")
            
        finally:
            if 'video' in locals():
                video.close()
                
    def processar_fila(self):
        for i in range(len(self.fila_videos)):
            if self.fila_videos[i]["status"] == "Na fila":
                self.converter_video(i)
        self.conversao_ativa = False
        
    def iniciar_conversao(self):
        if not self.fila_videos:
            messagebox.showwarning("Aviso", "A fila está vazia")
            return
        if not self.caminho_saida.get():
            messagebox.showerror("Erro", "Por favor, selecione a pasta de saída")
            return
        if not self.formato_saida.get() or self.formato_saida.get() not in ["mp4", "avi", "mov", "mkv", "webm"]:
            messagebox.showerror("Erro", "Por favor, selecione o formato de saída antes de converter.")
            return
        if not self.conversao_ativa:
            self.conversao_ativa = True
            threading.Thread(target=self.processar_fila, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConversorVideo(root)
    root.mainloop() 