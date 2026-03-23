import tkinter as tk
from tkinter import font as tkfont
from functools import partial
import random


class ScratchCardGame:
    def __init__(self, root):
        self.root = root
        self.root.title("刮刮乐游戏")
        self.root.geometry("800x650")
        self.root.configure(bg="#8A2BE2")

        self.penalties = [
            "表演一段舞蹈",
            "唱一首歌",
            "喝一杯水",
            "做10个俯卧撑",
            "讲一个笑话",
            "模仿动物叫声",
            "给大家发红包",
            "说一句绕口令",
            "跳一段街舞"
        ]

        self.cards = []
        self.card_states = [False] * 9
        self.is_zoomed = False
        self.zoomed_index = -1

        self.main_frame = tk.Frame(root, bg="#8A2BE2")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        title_label = tk.Label(
            self.main_frame,
            text="刮刮乐",
            font=tkfont.Font(family="微软雅黑", size=28, weight="bold"),
            bg="#8A2BE2",
            fg="white"
        )
        title_label.pack(pady=(0, 15))

        self.card_frame = tk.Frame(self.main_frame, bg="#8A2BE2")
        self.card_frame.pack(expand=True)

        self.back_button = tk.Button(
            self.main_frame,
            text="返回",
            font=tkfont.Font(family="微软雅黑", size=12, weight="bold"),
            bg="#FF6347",
            fg="white",
            relief=tk.FLAT,
            width=8,
            height=1,
            command=self.back_to_grid
        )
        self.back_button.pack_forget()

        self.refresh_button = tk.Button(
            root,
            text="刷新",
            font=tkfont.Font(family="微软雅黑", size=12, weight="bold"),
            bg="#FF6347",
            fg="white",
            relief=tk.FLAT,
            width=8,
            height=1,
            command=self.refresh_game
        )
        self.refresh_button.place(x=700, y=20)

        self.init_cards()

    def init_cards(self):
        self.refresh_button.place_forget()

        for widget in self.card_frame.winfo_children():
            widget.destroy()

        random.shuffle(self.penalties)

        self.cards = []
        self.card_states = [False] * 9

        card_size = 150

        for i in range(3):
            for j in range(3):
                idx = i * 3 + j

                # 创建卡片容器Frame
                card_frame = tk.Frame(
                    self.card_frame,
                    width=card_size,
                    height=card_size,
                    bg="#FF6347",
                    cursor="hand2"
                )
                card_frame.grid(row=i, column=j, padx=10, pady=10)
                card_frame.grid_propagate(False)

                # 底层Canvas - 显示惩罚内容
                content_canvas = tk.Canvas(
                    card_frame,
                    width=card_size,
                    height=card_size,
                    bg="#FF6347",
                    highlightthickness=0
                )
                content_canvas.place(x=0, y=0)

                content_canvas.create_rectangle(0, 0, card_size, card_size, fill="#FF6347", outline="")
                content_canvas.create_text(
                    card_size / 2, card_size / 2,
                    text=self.penalties[idx],
                    font=tkfont.Font(family="微软雅黑", size=12, weight="bold"),
                    fill="white",
                    width=card_size - 30,
                    justify="center"
                )

                # 上层Canvas - 遮罩层
                mask_canvas = tk.Canvas(
                    card_frame,
                    width=card_size,
                    height=card_size,
                    bg="#D3D3D3",
                    highlightthickness=2,
                    highlightbackground="#FF4500"
                )
                mask_canvas.place(x=0, y=0)

                mask_canvas.create_text(
                    card_size / 2, card_size / 2,
                    text="刮一刮",
                    font=tkfont.Font(family="微软雅黑", size=16, weight="bold"),
                    fill="#666666"
                )

                card_info = {
                    'frame': card_frame,
                    'content_canvas': content_canvas,
                    'mask_canvas': mask_canvas,
                    'penalty': self.penalties[idx],
                    'scratched': False,
                    'size': card_size,
                    'scratch_count': 0,
                    'index': idx,
                    'row': i,
                    'col': j
                }
                self.cards.append(card_info)

                # 绑定点击事件到遮罩Canvas
                mask_canvas.bind("<Button-1>", partial(self._on_click, idx))

    def _on_click(self, idx, event):
        if not self.is_zoomed:
            self.zoom_card(idx)

    def zoom_card(self, idx):
        self.is_zoomed = True
        self.zoomed_index = idx

        for i, c in enumerate(self.cards):
            if i != idx:
                c['frame'].grid_forget()

        card_info = self.cards[idx]
        frame = card_info['frame']

        frame.grid(row=0, column=0, padx=50, pady=30)

        self.animate_zoom(idx, 150, 400, 0)

        self.back_button.pack(pady=10)

    def animate_zoom(self, idx, start_size, end_size, step):
        card_info = self.cards[idx]

        if step < 12:
            current_size = int(start_size + (end_size - start_size) * step / 12)

            card_info['frame'].configure(width=current_size, height=current_size)
            card_info['content_canvas'].configure(width=current_size, height=current_size)
            card_info['mask_canvas'].configure(width=current_size, height=current_size)

            # 重绘底层内容
            card_info['content_canvas'].delete("all")
            card_info['content_canvas'].create_rectangle(0, 0, current_size, current_size, fill="#FF6347", outline="")
            font_size = 14 if current_size < 250 else 18
            card_info['content_canvas'].create_text(
                current_size / 2, current_size / 2,
                text=card_info['penalty'],
                font=tkfont.Font(family="微软雅黑", size=font_size, weight="bold"),
                fill="white",
                width=current_size - 30,
                justify="center"
            )

            # 重绘遮罩层
            if not card_info['scratched']:
                card_info['mask_canvas'].delete("all")
                card_info['mask_canvas'].create_rectangle(0, 0, current_size, current_size, fill="#D3D3D3", outline="")
                mask_size_font = 16 if current_size < 250 else 20
                card_info['mask_canvas'].create_text(
                    current_size / 2, current_size / 2,
                    text="刮一刮",
                    font=tkfont.Font(family="微软雅黑", size=mask_size_font, weight="bold"),
                    fill="#666666"
                )

                # 绑定刮刮事件
                card_info['mask_canvas'].bind("<B1-Motion>", partial(self.scratch, idx))
                card_info['mask_canvas'].bind("<Button-1>", partial(self.scratch, idx))

            card_info['size'] = current_size

            self.root.after(25, lambda: self.animate_zoom(idx, start_size, end_size, step + 1))

    def scratch(self, idx, event):
        card_info = self.cards[idx]
        mask_canvas = card_info['mask_canvas']
        size = card_info['size']

        x, y = event.x, event.y

        if x < 0 or x > size or y < 0 or y > size:
            return

        r = 25
        # 刮开效果 - 绘制透明椭圆，露出底层内容
        mask_canvas.create_oval(x - r, y - r, x + r, y + r, fill="", outline="", tags="scratch")

        card_info['scratch_count'] += 1

        # 刮到一定次数后显示结果
        if card_info['scratch_count'] > 8:
            self.reveal_card(idx)

    def reveal_card(self, idx):
        card_info = self.cards[idx]

        # 隐藏遮罩Canvas，显示底层内容
        card_info['mask_canvas'].place_forget()
        card_info['scratched'] = True

        self.card_states[idx] = True

        if all(self.card_states):
            self.refresh_button.lift()
            self.refresh_button.place(x=700, y=20)

    def back_to_grid(self):
        self.is_zoomed = False

        self.back_button.pack_forget()

        idx = self.zoomed_index
        card_info = self.cards[idx]

        self.animate_shrink(idx, 400, 150, 0)

    def animate_shrink(self, idx, start_size, end_size, step):
        card_info = self.cards[idx]

        if step < 12:
            current_size = int(start_size - (start_size - end_size) * step / 12)

            card_info['frame'].configure(width=current_size, height=current_size)
            card_info['content_canvas'].configure(width=current_size, height=current_size)

            # 重绘底层内容
            card_info['content_canvas'].delete("all")
            card_info['content_canvas'].create_rectangle(0, 0, current_size, current_size, fill="#FF6347", outline="")
            font_size = 14 if current_size < 250 else 18
            card_info['content_canvas'].create_text(
                current_size / 2, current_size / 2,
                text=card_info['penalty'],
                font=tkfont.Font(family="微软雅黑", size=font_size, weight="bold"),
                fill="white",
                width=current_size - 30,
                justify="center"
            )

            # 重绘遮罩层（如果未刮开）
            if not card_info['scratched']:
                card_info['mask_canvas'].configure(width=current_size, height=current_size)
                card_info['mask_canvas'].delete("all")
                card_info['mask_canvas'].create_rectangle(0, 0, current_size, current_size, fill="#D3D3D3", outline="")
                mask_size_font = 16 if current_size < 250 else 20
                card_info['mask_canvas'].create_text(
                    current_size / 2, current_size / 2,
                    text="刮一刮",
                    font=tkfont.Font(family="微软雅黑", size=mask_size_font, weight="bold"),
                    fill="#666666"
                )

            card_info['size'] = current_size

            self.root.after(25, lambda: self.animate_shrink(idx, start_size, end_size, step + 1))
        else:
            # 恢复所有卡片
            for card_info in self.cards:
                idx = card_info['index']
                row, col = card_info['row'], card_info['col']
                card_info['frame'].grid(row=row, column=col, padx=10, pady=10)
                card_info['frame'].configure(width=150, height=150)
                card_info['content_canvas'].configure(width=150, height=150)

                # 重绘底层内容
                card_info['content_canvas'].delete("all")
                card_info['content_canvas'].create_rectangle(0, 0, 150, 150, fill="#FF6347", outline="")
                card_info['content_canvas'].create_text(
                    75, 75,
                    text=card_info['penalty'],
                    font=tkfont.Font(family="微软雅黑", size=12, weight="bold"),
                    fill="white",
                    width=120,
                    justify="center"
                )

                # 重绘遮罩层（如果未刮开）
                if not card_info['scratched']:
                    card_info['mask_canvas'].configure(width=150, height=150)
                    card_info['mask_canvas'].delete("all")
                    card_info['mask_canvas'].create_rectangle(0, 0, 150, 150, fill="#D3D3D3", outline="")
                    card_info['mask_canvas'].create_text(
                        75, 75,
                        text="刮一刮",
                        font=tkfont.Font(family="微软雅黑", size=16, weight="bold"),
                        fill="#666666"
                    )
                    card_info['mask_canvas'].place(x=0, y=0)
                    card_info['mask_canvas'].bind("<Button-1>", partial(self._on_click, card_info['index']))

                card_info['size'] = 150

            # 重新绑定所有未刮开卡片的点击事件
            for card_info in self.cards:
                if not card_info['scratched']:
                    card_info['mask_canvas'].bind("<Button-1>", partial(self._on_click, card_info['index']))

            if all(self.card_states):
                self.refresh_button.lift()
                self.refresh_button.place(x=700, y=20)

    def refresh_game(self):
        self.refresh_button.place_forget()
        self.is_zoomed = False
        self.zoomed_index = -1
        self.init_cards()


if __name__ == "__main__":
    root = tk.Tk()
    game = ScratchCardGame(root)
    root.mainloop()
