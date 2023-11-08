# import ctypes
from threading import Thread
from tkinter import *
from tkinter.ttk import *
# from PIL import Image, ImageTk  # 导入PIL库用于图像处理，会导致打包后体积过大
from Back_end import main


class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        # 加载并缩放图片
        # self.image = ImageTk.PhotoImage(Image.open("log.png").resize((25, 25), Image.LANCZOS))  # 创建PhotoImage对象
        self.image = PhotoImage(file="log.png").subsample(3)
        self.tk_button_log = self.__tk_button_log(self)
        self.tk_text_input_message = self.__tk_text_input_message(self)
        self.tk_label_input = self.__tk_label_input(self)
        self.tk_label_output = self.__tk_label_output(self)
        self.tk_button_submit = self.__tk_button_submit(self)
        self.tk_text_output_message = self.__tk_text_output_message(self)
        self.tk_label_mac = self.__tk_label_mac(self)
        self.tk_text_mac_message = self.__tk_text_mac_message(self)
        self.tk_label_lojw60bv = self.__tk_label_lojw60bv(self)

    def __win(self):
        self.title("IP冲突扫描器")
        # 设置窗口大小、居中
        width = 568
        height = 462
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

        self.resizable(width=False, height=False)

    def scrollbar_autohide(self, vbar, hbar, widget):
        """自动隐藏滚动条"""

        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)

        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)

        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())

    def v_scrollbar(self, vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')

    def h_scrollbar(self, hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')

    def create_bar(self, master, widget, is_vbar, is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)

    def show_message(self):
        popup = Toplevel(self)
        popup.title("更新日志")
        popup.geometry("460x410")  # 设置窗口尺寸

        # 从文本文件中读取消息内容，使用UTF-8编码
        with open("README.md", "r", encoding="utf-8") as file:
            content = file.read()

        # 移除文本中的 '#' 字符
        content = content.replace("#", "")
        content = content.replace(". ", ".")

        # 创建一个Label，并将文本内容设置为README.md的内容
        message_label = Label(popup, text=content, anchor="w", compound="top", justify="left", wraplength=435)
        message_label.pack(expand=True, fill="both", padx=10, pady=(10, 0))

        close_button = Button(popup, text="关闭", command=popup.destroy)
        close_button.pack(side="bottom", pady=10)  # 调整关闭按钮位置

    def __tk_text_input_message(self, parent):  # 环境地址
        text = Text(parent)
        text.place(x=160, y=90, width=346, height=75)
        text.insert("end", "192.168.1.100，172.168.1.101-172.168.1.105,10.10.10.0/28，111")
        return text

    def __tk_label_input(self, parent):
        label = Label(parent, text="环境地址：", anchor="center", )
        label.place(x=30, y=90, width=84, height=30)
        return label

    def __tk_label_output(self, parent):
        label = Label(parent, text="输出结果：", anchor="center", )
        label.place(x=30, y=190, width=85, height=30)
        return label

    def __tk_button_submit(self, parent):
        btn = Button(parent, text="开始扫描", takefocus=False, )
        btn.place(x=250, y=400, width=65, height=35)
        return btn

    def __tk_text_output_message(self, parent):
        text = Text(parent)
        text.place(x=160, y=190, width=346, height=173)
        self.create_bar(parent, text, True, False, 160, 190, 346, 173, 568, 462)
        return text

    def __tk_label_mac(self, parent):
        label = Label(parent, text="MAC地址：", anchor="center", )
        label.place(x=30, y=30, width=84, height=30)
        return label

    def __tk_text_mac_message(self, parent):  # Mac地址
        text = Text(parent)
        text.place(x=160, y=30, width=346, height=30)
        text.insert("end", 'DC:21:5C:84:9B:26')
        return text

    def __tk_label_lojw60bv(self, parent):
        label = Label(parent, text="(多地址用逗号分割)", anchor="center", )
        label.place(x=30, y=110, width=113, height=30)
        return label

    def __tk_button_log(self, parent):
        log_button = Button(parent, image=self.image, command=self.show_message)
        log_button.place(x=526, y=420)
        return log_button


class Win(WinGUI):
    def __init__(self):
        super().__init__()
        self.__event_bind()

    # 后端逻辑
    def on_submit(self, *args):
        self.tk_text_output_message.delete("1.0", "end")
        str_input = self.tk_text_input_message.get("1.0", "end-1c")
        vm_mac = self.tk_text_mac_message.get("1.0", "end-1c")
        # 定义用户名、密码、端口号、数据库名等参数
        # host_ips = [] if str_input == "" else [item.strip().strip("'") for item in str_input.split(",")]
        port = 3306
        username = 'admin'
        password = 'admin'
        database = 'xxx'

        def run():
            # 按钮置灰
            self.tk_button_submit.config(state="disabled")
            self.tk_button_submit.unbind('<Button-1>')
            # 调用主函数
            res = main(str_input, port, username, password, database, vm_mac)
            # 按钮恢复
            self.tk_button_submit.config(state="enabled")
            self.__event_bind()
            # 输出结果
            self.tk_text_output_message.delete("1.0", "end")
            self.tk_text_output_message.insert("end", res)

        task = Thread(target=run)
        task.start()

    def __event_bind(self):
        self.tk_button_submit.bind('<Button-1>', self.on_submit)
        pass


if __name__ == "__main__":
    # 以下两行代码用于在控制界面打包exe时隐藏CMD界面直接用，如果直接pyinstaller -F -w，subprocess模块会无法执行
    # whnd = ctypes.windll.kernel32.GetConsoleWindow()
    # ctypes.windll.user32.ShowWindow(whnd, 0)
    win = Win()
    win.mainloop()
