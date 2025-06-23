import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import mido
from mido import MidiFile, MetaMessage, Message
import os

class MidiBPMChanger:
    def __init__(self, root):
        self.root = root
        self.root.title("MIDI BPM 修改器")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # 多语言支持
        self.lang = 'zh'
        self.lang_texts = {
            'zh': {
                'menu_language': '语言',
                'menu_about': '关于',
                'about_title': '关于小程序',
                'about_content': 'MIDI BPM 修改器 v1.0\n用于批量导入 MIDI 文件并统一调整 BPM。',
                'load_button': '导入 MIDI 文件',
                'target_bpm_label': '目标 BPM:',
                'convert_button': '开始转换',
                'filename_header': '文件名',
                'original_bpm_header': '原始 BPM',
                'status_header': '状态',
                'converted': '已转换',
                'not_converted': '未转换',
                'select_file_prompt': '请选择 MIDI 文件',
                'success_message': 'BPM 已成功更新！',
                'error_invalid_bpm': '请输入有效的 BPM 数字！',
                'error_no_files': '请先导入 MIDI 文件！',
                'error_no_bpm': '无法读取原始 BPM，请确保 MIDI 文件有效！'
            },
            'en': {
                'menu_language': 'Language',
                'menu_about': 'About',
                'about_title': 'About the App',
                'about_content': 'MIDI BPM Changer v1.0\nUsed to batch import MIDI files and adjust BPM uniformly.',
                'load_button': 'Import MIDI Files',
                'target_bpm_label': 'Target BPM:',
                'convert_button': 'Start Conversion',
                'filename_header': 'Filename',
                'original_bpm_header': 'Original BPM',
                'status_header': 'Status',
                'converted': 'Converted',
                'not_converted': 'Not Converted',
                'select_file_prompt': 'Please select MIDI files',
                'success_message': 'BPM has been successfully updated!',
                'error_invalid_bpm': 'Please enter a valid BPM number!',
                'error_no_files': 'Please import MIDI files first!',
                'error_no_bpm': 'Failed to read original BPM, please ensure the MIDI file is valid!'
            }
        }

        # 创建菜单栏
        menu_bar = tk.Menu(self.root)
        lang_menu = tk.Menu(menu_bar, tearoff=0)
        lang_menu.add_command(label="中文", command=lambda: self.change_language('zh'))
        lang_menu.add_command(label="English", command=lambda: self.change_language('en'))
        menu_bar.add_cascade(label=self.lang_texts[self.lang]['menu_language'], menu=lang_menu)

        about_menu = tk.Menu(menu_bar, tearoff=0)
        about_menu.add_command(label=self.lang_texts[self.lang]['menu_about'], command=self.show_about)
        menu_bar.add_cascade(label=self.lang_texts[self.lang]['menu_about'], menu=about_menu)

        self.root.config(menu=menu_bar)

        # 初始化变量
        self.mid_files = []  # 存储导入的 MIDI 文件路径
        self.midi_objects = []  # 存储解析的 MIDI 对象
        self.target_bpm_entry = tk.Entry(self.root)

        # 创建界面组件
        self.create_widgets()

    def change_language(self, lang):
        self.lang = lang
        self.root.title("MIDI BPM 修改器" if lang == 'zh' else "MIDI BPM Changer")
        self.update_ui_texts()
        self.update_table()

    def update_ui_texts(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Menu):
                continue
        self.load_btn.config(text=self.lang_texts[self.lang]['load_button'])
        self.convert_btn.config(text=self.lang_texts[self.lang]['convert_button'])
        self.target_bpm_label.config(text=self.lang_texts[self.lang]['target_bpm_label'])
        self.filename_header.config(text=self.lang_texts[self.lang]['filename_header'])
        self.original_bpm_header.config(text=self.lang_texts[self.lang]['original_bpm_header'])
        self.status_header.config(text=self.lang_texts[self.lang]['status_header'])

    def show_about(self):
        messagebox.showinfo(self.lang_texts[self.lang]['about_title'], self.lang_texts[self.lang]['about_content'])

    def create_widgets(self):
        # 主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        # Logo 区域
        logo_label = tk.Label(main_frame, text="🎵 MIDI BPM 修改器 🎵", font=("Arial", 16, "bold"))
        logo_label.pack(pady=10)

        # 导入按钮
        self.load_btn = tk.Button(main_frame, text=self.lang_texts[self.lang]['load_button'],
                                  command=self.load_midi_files)
        self.load_btn.pack(pady=10)

        # 目标 BPM 输入框（新增 frame 并使用 pack 布局）
        target_bpm_frame = tk.Frame(main_frame)
        target_bpm_frame.pack(pady=10)

        self.target_bpm_label = tk.Label(target_bpm_frame, text=self.lang_texts[self.lang]['target_bpm_label'])
        self.target_bpm_label.pack(side=tk.LEFT, padx=5)

        self.target_bpm_entry = tk.Entry(target_bpm_frame, width=10)
        self.target_bpm_entry.pack(side=tk.LEFT, padx=5)

        # 开始转换按钮
        self.convert_btn = tk.Button(target_bpm_frame, text=self.lang_texts[self.lang]['convert_button'],
                                     command=self.convert_bpm)
        self.convert_btn.pack(side=tk.LEFT, padx=5)

        # 表格显示 MIDI 文件列表
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(table_frame, columns=("filename", "original_bpm", "status"), show='headings')
        self.tree.heading("filename", text=self.lang_texts[self.lang]['filename_header'])
        self.tree.heading("original_bpm", text=self.lang_texts[self.lang]['original_bpm_header'])
        self.tree.heading("status", text=self.lang_texts[self.lang]['status_header'])
        self.tree.column("filename", width=200)
        self.tree.column("original_bpm", width=100)
        self.tree.column("status", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, (file_path, midi_obj) in enumerate(zip(self.mid_files, self.midi_objects)):
            filename = os.path.basename(file_path)
            original_bpm = self.get_current_bpm(midi_obj)
            status = self.lang_texts[self.lang]['converted'] if getattr(midi_obj, 'converted', False) else self.lang_texts[self.lang]['not_converted']
            self.tree.insert("", tk.END, values=(filename, original_bpm, status))

    def get_current_bpm(self, midi):
        for track in midi.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    return int(60000000 / msg.tempo)
        return 120  # 默认 BPM

    def load_midi_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("MIDI 文件", "*.mid")])
        if not file_paths:
            return
        for file_path in file_paths:
            try:
                mid = MidiFile(file_path)
                self.mid_files.append(file_path)
                self.midi_objects.append(mid)
            except Exception as e:
                messagebox.showerror("错误", f"加载 {file_path} 失败: {str(e)}")
        self.update_table()

    def convert_bpm(self):
        if not self.mid_files:
            messagebox.showwarning("警告", self.lang_texts[self.lang]['error_no_files'])
            return
        try:
            new_bpm = int(self.target_bpm_entry.get())
        except ValueError:
            messagebox.showerror("错误", self.lang_texts[self.lang]['error_invalid_bpm'])
            return

        for i, mid in enumerate(self.midi_objects):
            try:
                old_tempo = None
                for track in mid.tracks:
                    for msg in track:
                        if msg.type == 'set_tempo':
                            old_tempo = msg.tempo
                            break
                    if old_tempo:
                        break
                if not old_tempo:
                    old_tempo = mido.bpm2tempo(120)
                old_bpm = mido.tempo2bpm(old_tempo)
                new_tempo = mido.bpm2tempo(new_bpm)
                scale_factor = new_bpm / old_bpm

                for track in mid.tracks:
                    new_track = mido.MidiTrack()
                    for msg in track:
                        scaled_time = int(round(msg.time * scale_factor))
                        if msg.type == 'set_tempo':
                            new_msg = MetaMessage('set_tempo', tempo=new_tempo, time=scaled_time)
                            new_track.append(new_msg)
                        else:
                            if msg.is_meta:
                                new_track.append(msg.copy(time=scaled_time))
                            else:
                                new_track.append(msg.copy(time=scaled_time))
                    track.clear()
                    track.extend(new_track)

                has_set_tempo = False
                for track in mid.tracks:
                    for msg in track:
                        if msg.type == 'set_tempo':
                            has_set_tempo = True
                            break
                    if has_set_tempo:
                        break
                if not has_set_tempo:
                    mid.tracks[0].insert(0, MetaMessage('set_tempo', tempo=new_tempo))

                mid.save(os.path.splitext(self.mid_files[i])[0] + "_modified.mid")
                mid.converted = True
            except Exception as e:
                messagebox.showerror("错误", f"处理 {self.mid_files[i]} 失败: {str(e)}")
                continue

        self.update_table()
        messagebox.showinfo("成功", self.lang_texts[self.lang]['success_message'])

if __name__ == "__main__":
    root = tk.Tk()
    app = MidiBPMChanger(root)
    root.mainloop()
