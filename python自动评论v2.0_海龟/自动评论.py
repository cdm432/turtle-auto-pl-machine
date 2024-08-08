# 定义标准库
from webbrowser import open as webbrowser_open
from time import time
from requests import get, post
from json import loads, dumps
from random import randrange
import tkinter as tk
from tkinter.simpledialog import askstring
from tkinter import messagebox
from PIL import Image, ImageTk

"""
用前须知：
需要的标准库都已经下载好了，不需要在下载，如真有缺失，请另外下载
"""

# 存储地址（需要换地方可在这更改）
DATA_PATH = "data/本地数据.json"
COMMENTED_USER_PATH = "./data/已评论用户.txt"

# 以面向对象编程的方式编写爬虫项目
class RequestsMain:
    # 初始化程序
    def __init__(self):
        """初始化评论部分"""
        self.last_comment_time = 0  # 初始化上次评论时间
        self.comment_time = 12  # 初始化评论间隔
        self.have_error = False  # 初始化报错状态
        self.need_to_reset = False  # 初始化是否需要否重置数据
        self.last_ui_need_to_forget = False  # 初始化是否需要否隐藏界面
        self.is_open_select_ui = False
        self.my_cookie = None   # 初始化cookie
        self.subject_work_total = None
        self.select_n = 0  # 初始化选择要修改的评论
        self.fans_total = 0
        self.my_name = "未登录"
        self.my_id = "未登录"
        self.ui = "root"  # 初始化显示ui

        self.image_avatar = Image.open("./data/未登录.gif")
        self.set_all_data()  # 设置评论数据
        self.get_fans_total()  # 获取粉丝数

        """初始化GUI界面部分"""
        self.state = "停止"  # 初始化默认程序运行状态
        self.window = tk.Tk()  # 创建窗口对象

        self.window.geometry("900x600+100+100")  # 设置窗口宽高
        self.window.title("自动评论v2.2")  # 设置显示标头

        self.create_widget()  # 生成窗口上的各个组件

    # 生成窗口上的各个组件方法
    def create_widget(self):
        """root页面"""
        # 生成主菜单
        self.main_menu = tk.Menu(self.window)

        # 生成子菜单
        self.ui_menu = tk.Menu(self.main_menu)
        self.select_menu = tk.Menu(self.main_menu)

        self.main_menu.add_cascade(label="其他页面", menu=self.ui_menu)
        self.main_menu.add_cascade(label="账号", menu=self.select_menu)

        self.ui_menu.add_command(label="执行程序", command=self.set_ui_to_root)
        self.ui_menu.add_command(label="评论内容", command=self.set_ui_to_comment)
        self.select_menu.add_command(label="登录", command=self.security_ui)

        # 生成运行消息栏
        self.data_show_text = tk.Text(self.window, bg="lightgray", fg="black", borderwidth=2, relief="solid",
                                      font=("黑体", 12), state=tk.DISABLED)

        # 生成控制程序运行状态的按钮
        self.start_botton = tk.Button(self.window, text="开始运行", height=2, font=("黑体", 16),
                                      command=self.set_state_start)
        self.time_out_botton = tk.Button(self.window, text="暂停运行", height=2, font=("黑体", 16),
                                         command=self.set_state_time_out)
        self.stop_botton = tk.Button(self.window, text="停止运行", height=2, font=("黑体", 16),
                                     command=self.set_state_stop)

        self.root_label_1 = tk.Label(self.window, text="评论粉丝用户ID", font=("黑体", 12))
        self.root_id_entry = tk.Entry(self.window)  # 设置root_id
        self.root_id_entry.insert(0, str(self.root_id))

        # 生成各种提示文字
        self.root_frame = tk.Frame(self.window, bg="goldenrod")
        self.data_label = tk.Label(self.window, font=("微软雅黑", 12), justify="left")
        self.root_label_2 = tk.Label(self.window, text="设置评论间隔：", font=("黑体", 12))
        self.my_data_label = tk.Label(self.window, font=("华文琥珀", 22), bg="goldenrod", fg="white")

        self.image_avatar = ImageTk.PhotoImage(self.image_avatar)
        self.image_button = tk.Button(self.window, command=self.security_ui, cursor="hand2", bg="goldenrod")

        # 生成调整爬虫发评论的速度的滑块
        self.comment_time_scale = tk.Scale(self.window, from_=12, to=24, tickinterval=6, orient=tk.HORIZONTAL,
                                           command=self.set_comment_time, cursor="sb_h_double_arrow")
        """comment页面"""
        self.comment_frame = tk.Frame(self.window, bg="goldenrod")

        self.comment_title_label = tk.Label(self.window, text="所有评论内容:", font=("黑体", 20))
        self.comment_label = tk.Label(self.window, text="评论文字:", font=("黑体", 15))
        self.emoji_label = tk.Label(self.window, text="评论表情:", font=("黑体", 15))

        self.comment_text = tk.Text(self.window, bg="lightgray", fg="black", font=("黑体", 12))
        self.emoji_text = tk.Text(self.window, bg="lightgray", fg="black", font=("黑体", 12))

        self.add_comment_button = tk.Button(self.window, text="添加评论", height=2, font=("黑体", 10),
                                            command=self.add_comment, cursor="hand2")
        self.del_comment_button = tk.Button(self.window, text="删除评论", height=2, font=("黑体", 10),
                                            command=self.del_comment, cursor="hand2")
        self.set_comment_button = tk.Button(self.window, text="修改评论", height=2, font=("黑体", 10),
                                            command=self.set_comment, cursor="hand2")

        self.window.bind("<Button-1>", self.select)

        self.update_comment_ui_text()

        # 添加主菜单
        self.window["menu"] = self.main_menu

        self.widget_update()  # 放入组件

    # 刷新组件
    def widget_update(self):
        # 显示程序界面ui
        if self.ui == "root":
            # 判断不同状态，控制程序运行状态的按钮此时的状态
            if self.state == "正在":
                self.need_to_reset = True
                self.start_botton["text"] = "开始运行"
                self.start_botton["state"] = tk.DISABLED
                self.time_out_botton["state"] = tk.NORMAL
                self.stop_botton["state"] = tk.NORMAL

                self.start_botton["cursor"] = "arrow"
                self.time_out_botton["cursor"] = "hand2"
                self.stop_botton["cursor"] = "hand2"
            elif self.state == "暂停":
                self.need_to_reset = True
                self.start_botton["text"] = "继续运行"
                self.start_botton["state"] = tk.NORMAL
                self.time_out_botton["state"] = tk.DISABLED
                self.stop_botton["state"] = tk.NORMAL

                self.start_botton["cursor"] = "hand2"
                self.time_out_botton["cursor"] = "arrow"
                self.stop_botton["cursor"] = "hand2"
            elif self.state == "停止":
                self.start_botton["text"] = "开始运行"
                self.start_botton["state"] = tk.NORMAL
                self.time_out_botton["state"] = tk.DISABLED
                self.stop_botton["state"] = tk.DISABLED

                self.start_botton["cursor"] = "hand2"
                self.time_out_botton["cursor"] = "arrow"
                self.stop_botton["cursor"] = "arrow"

            # 刷新程序运行状态及参数的显示文字的内容

            self.data_label["text"] = \
                 ("程序运行状态：%s运行\n已评论用户数：%d个\n目标评论用户数：%d个\n程序运行进度： " % (self.state, self.fans_n, self.fans_total)) + \
                     ((str(int(self.fans_n / self.fans_total * 1000) / 10) + "%") if self.fans_total != 0 else "###")

            self.my_data_label["text"] = "%s(%s)" % (self.my_name, self.my_id)

            self.image_button["image"] = self.image_avatar
            if self.my_cookie is None:
                self.image_button["command"] = self.security_ui
            else:
                self.image_button["command"] = self.open_mine

            # 放入
            self.start_botton.place(relx=0.75, x=20, y=75, relwidth=0.22)
            self.time_out_botton.place(relx=0.75, x=20, y=140, relwidth=0.22)
            self.stop_botton.place(relx=0.75, x=20, y=205, relwidth=0.22)
            self.data_label.place(relx=0.75, x=20, y=280)
            self.data_show_text.place(x=10, y=75, relwidth=0.75, relheight=0.86)
            self.root_label_1.place(relx=0.75, x=20, rely=0.72)
            self.root_id_entry.place(relx=0.75, x=25, rely=0.72, y=30, relwidth=0.21)
            self.root_label_2.place(relx=0.75, x=20, rely=0.72, y=60)
            self.comment_time_scale.place(relx=0.75, x=20, rely=0.72, y=80, relwidth=0.22)
            self.my_data_label.place(x=80, y=20)
            self.image_button.place(x=10, y=10)
            self.root_frame.place(x=0, y=0, relwidth=1, height=70)

        elif self.last_ui_need_to_forget:

            self.data_show_text.place_forget()
            self.start_botton.place_forget()
            self.time_out_botton.place_forget()
            self.stop_botton.place_forget()
            self.data_label.place_forget()
            self.root_label_1.place_forget()
            self.root_label_2.place_forget()
            self.comment_time_scale.place_forget()
            self.my_data_label.place_forget()
            self.image_button.place_forget()
            self.root_id_entry.place_forget()
            self.root_frame.place_forget()

            self.last_ui_need_to_forget = False

        # 显示评论界面ui
        if self.ui == "comment":
            self.comment_title_label.pack()

            self.comment_text.place(y=80, relx=0.05, relwidth=0.65, relheight=0.75)
            self.emoji_text.place(y=80, relx=0.7, relwidth=0.25, relheight=0.75)

            self.comment_label.place(y=45, relx=0.05)
            self.emoji_label.place(y=45, relx=0.7)

            self.add_comment_button.place(rely=0.75, y=90, relx=0.05, relwidth=0.25)
            self.del_comment_button.place(rely=0.75, y=90, relx=0.35, relwidth=0.25)
            self.set_comment_button.place(rely=0.75, y=90, relx=0.65, relwidth=0.25)

            self.comment_frame.place(x=0, y=0, relwidth=0.04, relheight=1)

            if self.select_n >= len(self.data["comments"]):
                self.select_n = len(self.data["comments"]) - 1
                self.update_comment_ui_text()

        elif self.last_ui_need_to_forget:
            self.comment_title_label.pack_forget()
            self.comment_text.place_forget()
            self.emoji_text.place_forget()
            self.comment_label.place_forget()
            self.emoji_label.place_forget()
            self.add_comment_button.place_forget()
            self.del_comment_button.place_forget()
            self.set_comment_button.place_forget()
            self.comment_frame.place_forget()

            self.last_ui_need_to_forget = False

        root_id = self.root_id_entry.get()
        if root_id != "" and root_id is not None:
            root_id = int(root_id)
        else:
            self.fans_total = 0
            self.fans_n = 0
        if root_id != self.root_id:
            self.root_id = root_id
            self.need_to_reset = True
            self.state = "停止"

    # 用户手动登录界面
    def security_ui(self):
        if not self.is_open_select_ui:
            self.state = "暂停"

            self.out_security()

            self.my_num = None
            self.my_password = None
            self.my_name = "未登录"
            self.my_id = "未登录"

            image = Image.open("./data/未登录.gif")
            self.image_avatar = ImageTk.PhotoImage(image)

            self.security_window = tk.Toplevel()
            self.security_window.geometry("400x480")  # 设置窗口宽高
            self.security_window.title("登录")  # 设置显示标头

            tk.Frame(self.security_window, bg="white").place(x=0, y=0, relwidth=1, relheight=1)

            self.security_image = tk.PhotoImage(file="data/登录.gif")
            tk.Label(self.security_window, image=self.security_image).pack()

            tk.Label(self.security_window, text="登录编程猫账号", font=("微软雅黑", 15), bg="white", fg="dimgrey", height=2).pack()
            tk.Frame(self.security_window, bg="dimgrey", height=2).place(relx=0.35, y=215, relwidth=0.3)

            self.my_num_entry = tk.Entry(self.security_window, width=40, font=("黑体", 14), bg="whitesmoke", fg="dimgrey",
                                         borderwidth=1, relief="solid", )
            self.my_num_entry.place(y=250, relx=0.05, height=40, relwidth=0.9)
            self.my_password_entry = tk.Entry(self.security_window, width=40, font=("黑体", 14), bg="whitesmoke",
                                              fg="dimgrey", borderwidth=1, relief="solid")
            self.my_password_entry.place(y=310, relx=0.05, height=40, relwidth=0.9)

            tk.Button(self.security_window, text="点击登录", command=self.user_security, width=10, font=("黑体", 18),
                      background="goldenrod", fg="white", cursor="hand2").place(y=370, relx=0.05, height=40, relwidth=0.9)

            self.error_label = tk.Label(self.security_window, text="账号或密码错误，请重新输入", font=("黑体", 10), background="white", fg="red")

            self.my_num_entry.insert(0, "请输入账号...")
            self.my_password_entry.insert(0, "请输入密码...")

            self.my_num_entry.bind("<FocusIn>", self.my_num_default_entry)
            self.my_num_entry.bind("<FocusOut>", self.my_num_replace_entry)
            self.my_password_entry.bind("<FocusIn>", self.my_password_default_entry)
            self.my_password_entry.bind("<FocusOut>", self.my_password_replace_entry)

            self.security_window.bind("<KeyRelease-Return>", self.user_security)

            self.security_window.protocol("WM_DELETE_WINDOW", self.out_security_window)

            self.is_open_select_ui = True

    def my_num_default_entry(self, event):
        if self.my_num_entry.get() == "请输入账号...":
            self.my_num_entry.delete("0", tk.END)
            self.my_num_entry["fg"] = "black"
        self.error_label.place_forget()

    def my_num_replace_entry(self, event):
        if self.my_num_entry.get() == "":
            self.my_num_entry.insert(0, "请输入账号...")
            self.my_num_entry["fg"] = "dimgrey"
        self.error_label.place_forget()

    def my_password_default_entry(self, event):
        if self.my_password_entry.get() == "请输入密码...":
            self.my_password_entry["show"] = "*"
            self.my_password_entry.delete("0", tk.END)
            self.my_password_entry["fg"] = "black"
        self.error_label.place_forget()

    def my_password_replace_entry(self, event):
        if self.my_password_entry.get() == "":
            self.my_password_entry["show"] = ""
            self.my_password_entry.insert(0, "请输入密码...")
            self.my_password_entry["fg"] = "dimgrey"
        self.error_label.place_forget()

    # 设置评论需求的基本参数
    def set_all_data(self):
        # 获取本地数据
        with open(DATA_PATH, encoding="utf-8") as f:
            self.data = loads(f.read())

        self.my_num = self.data["data"]["user_num"]
        self.my_password = self.data["data"]["user_password"]
        self.root_id = self.data["data"]["last_comment_user"]["user_id"]
        self.fans_n = self.data["data"]["last_comment_user"]["fans_n"]

        # 设置不变参数
        self.fans_list_url = "https://api.codemao.cn/creation-tools/v1/user/fans"
        self.user_data_url = "https://api.codemao.cn/creation-tools/v1/user/center/honor"
        self.hot_work_url = "https://api.codemao.cn/creation-tools/v2/user/center/work-list"
        self.half_cookie = "_ga_Q22QJM382R=GS1.2.1718409823.1.0.1718409830.0.0.0; visitor_id=101719647845233#F0E61E40890F832CEF22A1702AFAE819C8ACF4D7B7F503666E84B54A22DDDA27; _ga=GA1.2.1596171762.1718409823; _ga_QY67JTHD3D=GS1.1.1720164315.1.1.1720164373.0.0.0; __ca_uid_key__=e55b8720-383d-406f-8c1c-39f093911da4; _ga_JEHRTN2DXN=GS1.2.1720746473.1.0.1720746473.0.0.0; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221201009%22%2C%22first_id%22%3A%2218d7bc8c5b7a6b-0d02cf301c17e1-4c657b58-1296000-18d7bc8c5b8b5e%22%2C%22props%22%3A%7B%22%24latest_utm_medium%22%3A%22%E9%A6%96%E9%A1%B5%E7%B2%BE%E9%80%89%22%2C%22%24latest_utm_campaign%22%3A%22%E7%A4%BE%E5%8C%BA%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThkN2JjOGM1YjdhNmItMGQwMmNmMzAxYzE3ZTEtNGM2NTdiNTgtMTI5NjAwMC0xOGQ3YmM4YzViOGI1ZSIsIiRpZGVudGl0eV9sb2dpbl9pZCI6Ijk2NjQwMjUzMyJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221201009%22%7D%2C%22%24device_id%22%3A%2218d7bc8c5b7a6b-0d02cf301c17e1-4c657b58-1296000-18d7bc8c5b8b5e%22%7D; aliyungf_tc=0e762ec124311d3c7f0185b1f1121fefb5cfe3315dba18e2dc06e7ce9ceee8a7; acw_tc=ac11000117217374430997070e16755f28f86481a4628bcfd083c38dd4513c; authorization="
        self.security_url = "https://api.codemao.cn/tiger/v3/web/accounts/login"
        self.out_security_url = "https://api.codemao.cn/tiger/v3/web/accounts/logout"

        if not (self.my_num is None or self.my_password is None):
            if self.security() == 0:
                messagebox.showerror("错误", "账号或密码错误")
        else:
            self.security()

    # 用户手动登录
    def user_security(self, event=None):
        self.my_num = self.my_num_entry.get()
        self.my_password = self.my_password_entry.get()
        if self.security() == 1:
            self.image_avatar = ImageTk.PhotoImage(self.image_avatar)
            self.security_window.destroy()
            self.is_open_select_ui = False
        else:
            self.error_label.place(y=230, relx=0.05)

    # 退出登录
    def out_security(self):
        if self.my_cookie is not None:
            post(self.out_security_url, headers=self.get_headers())
            self.my_cookie = None

    # 打开用户界面
    def open_mine(self):
        webbrowser_open("https://shequ.codemao.cn/user/%s" % self.my_id)

    # 选择评论项
    def select(self, event):
        if "text" in str(event.widget):
            select_n = event.y // 16
            if len(self.data["comments"]) > select_n >= 0:
                self.select_n = select_n
                self.update_comment_ui_text()

    # 修改评论内容
    def set_comment(self):
        if self.select_n < len(self.data["comments"]):
            set_comment_data = {"content": "", "emoji": ""}
            set_comment_data["content"] = askstring("设置", "设置评论文字",
                                                    initialvalue=self.data["comments"][self.select_n]["content"])
            set_comment_data["emoji"] = askstring("设置", "设置评论表情",
                                                  initialvalue=self.data["comments"][self.select_n]["emoji"])

            self.data["comments"][self.select_n] = set_comment_data
            self.update_comment_ui_text()
        else:
            messagebox.showerror("错误", "此项不存在任何内容")

    # 删除评论内容
    def del_comment(self):
        if self.select_n < len(self.data["comments"]) and len(self.data["comments"]) > 0:
            self.data["comments"].pop(self.select_n)

            self.update_comment_ui_text()
        else:
            messagebox.showerror("错误", "此项不存在任何内容")

    # 添加评论信息显示内容
    def add_comment(self):
        add_comment_data = {"content": "", "emoji": ""}
        add_comment_data["content"] = askstring("设置", "设置评论文字", initialvalue="写下一个醒目的评论吧")
        add_comment_data["emoji"] = askstring("设置", "设置评论表情", initialvalue="发送一个合适的表情包吧")

        if add_comment_data["content"] is None or len(add_comment_data["content"]) > 80:
            messagebox.showinfo("提示", "请输入80个字符以内的评论(中文字符站2个字符)")
        elif add_comment_data["emoji"] is None or len(add_comment_data["emoji"]) > 12:
            messagebox.showinfo("提示", "请输入20个字符以内的表情(中文字符站2个字符)")
        else:
            self.data["comments"].append(add_comment_data)

            self.select_n = len(self.data["comments"]) - 1
            self.update_comment_ui_text()
            self.comment_text.see(tk.END)
            self.emoji_text.see(tk.END)

    # 刷新评论信息数据
    def update_comment_ui_text(self):
        self.comment_text["state"] = tk.NORMAL
        self.emoji_text["state"] = tk.NORMAL

        self.comment_text.tag_delete("select")
        self.emoji_text.tag_delete("select")

        self.comment_text.delete(1.0, tk.END)
        self.emoji_text.delete(1.0, tk.END)

        for i in range(len(self.data["comments"])):
            self.comment_text.insert(tk.END, "%d.%s\n" % (i + 1, self.data["comments"][i]["content"]))
            self.emoji_text.insert(tk.END, "%s\n" % self.data["comments"][i]["emoji"])

        self.comment_text.tag_add("select", float(f"%d.0" % (self.select_n + 1)),
                                  float("%d.114" % (self.select_n + 1)))
        self.emoji_text.tag_add("select", float("%d.0" % (self.select_n + 1)),
                                float("%d.114" % (self.select_n + 1)))

        self.comment_text.tag_config("select", background="lightblue")
        self.emoji_text.tag_config("select", background="lightblue")

        self.comment_text["state"] = tk.DISABLED
        self.emoji_text["state"] = tk.DISABLED

    # 设置ui为程序
    def set_ui_to_root(self):
        self.last_ui_need_to_forget = True
        self.ui = "root"

    # 设置ui为评论
    def set_ui_to_comment(self):
        self.last_ui_need_to_forget = True
        self.ui = "comment"

    # 设置评论间隔
    def set_comment_time(self, value):
        self.comment_time = int(value)

    # 程序运行状态为正在运行
    def set_state_start(self):
        if self.my_cookie is None:
            messagebox.showinfo("提示", "您还未登录")
            self.security_ui()
        elif self.fans_total == 0:
            messagebox.showinfo("提示", "您还未确定评论谁的粉丝（推荐1201009）")
            self.root_id = 1201009
            self.root_id_entry.delete(0, tk.END)
            self.root_id_entry.insert(0, str(self.root_id))
        elif len(self.data["comments"]) == 0:
            messagebox.showinfo("提示", "您还未设置评论内容，去设置吧")
            self.last_ui_need_to_forget = True
            self.ui = "comment"
        else:
            self.state = "正在"

    # 程序运行状态为暂停运行
    def set_state_time_out(self):
        self.state = "暂停"

    # 程序运行状态为停止运行
    def set_state_stop(self):
        self.state = "停止"

    # 获取登录需求的data
    def get_security_data(self):
        data = {
            'identity': self.my_num,
            'password': self.my_password,
            'pid': "65edCTyg"
        }
        return dumps(data)

    # 登录账号
    def security(self):
        r = post(self.security_url, data=self.get_security_data(), headers=self.get_security_headers())
        if r.status_code == 200:
            data = r.json()
            token = data["auth"]["token"]
            self.my_cookie = self.half_cookie + token

            self.my_name = data["user_info"]["nickname"]
            self.my_id = str(data["user_info"]["id"])

            avatar_url = data["user_info"]["avatar_url"]
            r = get(avatar_url)
            with open("./data/头像.gif", "wb") as f:
                f.write(r.content)

            image = Image.open("./data/头像.gif")
            self.image_avatar = image.resize((50, 50))

            return 1
        else:
            return 0

    # 获取获得玩家数据需求的params
    def get_user_data_params(self, user_id):
        params = {"user_id": user_id}
        return params

    # 获取获得粉丝列表需求的params
    def get_fans_list_params(self, offset):
        params = {
            'user_id': self.root_id,
            'offset': offset,
            'limit': 15
        }
        return params

    # 获取获得玩家火热作品需求的params
    def get_hot_work_params(self, user_id):
        params = {
            "type": "hot",
            "user_id": user_id,
            "offset": 0,
            "limit": 15
        }
        return params

    # 生成评论的data，并转化为json格式
    def set_comment_data(self, content, emoji_content):
        comment_data = {
            'content': content,
            'emoji_content': emoji_content
        }
        return dumps(comment_data)

    # 获取评论作品的url
    def set_comment_url(self, work_id):
        comment_url = f"https://api.codemao.cn/creation-tools/v1/works/%d/comment" % work_id
        return comment_url

    # 获取粉丝总数
    def get_fans_total(self):
        if isinstance(self.root_id, int):
            r = get(self.user_data_url, params=self.get_user_data_params(self.root_id), headers=self.get_headers())
            data = r.json()
            try:
                if data["error_message"] == "用户不存在":
                    self.fans_total = 0
                    self.fans_n = 0
            except:
                self.fans_total = data["fans_total"]

    # 点赞作品
    def like_work(self, work_id):
        like_url = f"https://api.codemao.cn/nemo/v2/works/%d/like" % work_id
        post(like_url, headers=self.get_headers())

    def get_security_headers(self):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        }
        return headers

    def get_headers(self):
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
            "cookie": self.my_cookie
        }
        return headers

    def out_security_window(self):
        self.is_open_select_ui = False
        self.my_num = None
        self.my_password = None
        self.security_window.destroy()

    # 重要的函数：评论
    def comment(self):
        time_now = time()
        if time_now - self.last_comment_time >= self.comment_time or self.last_comment_time == 0:  # 判断间隔到了没
            if self.fans_n < self.fans_total:  # 判断目标是否达成
                offset = self.fans_n // 15 * 15  # 获取当前编号粉丝所在的页数
                r = get(self.fans_list_url, params=self.get_fans_list_params(offset), headers=self.get_headers())  # 获取当前页的数据
                data = r.json()  # 将数据转化为python的格式
                fans = data["items"][self.fans_n % 15]  # 得到当前粉丝的大致数据

                # 比较此用户是否已被评论
                can_comment = True
                with open(COMMENTED_USER_PATH, encoding="utf-8") as f:
                    line_data = f.readline()
                    while line_data != "":
                        if str(fans["id"]) in line_data:
                            can_comment = False
                            break
                        line_data = f.readline()

                if can_comment:
                    user_id = fans["id"]  # 获取用户id
                    self.data_show_text["state"] = tk.NORMAL  # 启用消息显示栏，让程序写入消息

                    """查找粉丝最火作品"""
                    r = get(self.hot_work_url, params=self.get_hot_work_params(user_id),
                            headers=self.get_headers())  # 获取粉丝最火作品数据
                    data = r.json()  # 将数据转化为python的格式
                    hot_works = data["items"]  # 获取作品列表

                    if len(hot_works) > 0:  # 判断有没有作品
                        work_id = hot_works[0]["id"]  # 获取最火那一个作品
                        work_name = hot_works[0]["work_name"]
                        liked_times = hot_works[0]["liked_times"]
                        collect_times = hot_works[0]["collect_times"]
                        view_times = hot_works[0]["view_times"]

                        """评论"""
                        r = get(self.user_data_url, params=self.get_user_data_params(user_id),
                                headers=self.get_headers())
                        data = r.json()
                        user_name = data["nickname"]

                        comment_number = randrange(0, len(self.data["comments"]))  # 随机一个评论

                        old_content = self.data["comments"][comment_number]["content"]
                        emoji = self.data["comments"][comment_number]["emoji"]

                        content = ""
                        replace = ""
                        replace_now = False
                        for i in range(len(old_content)):
                            if replace_now:
                                if old_content[i] == "]":
                                    replace_now = False
                                    if replace == "用户名":
                                        content += user_name
                                    elif replace == "作品名":
                                        content += work_name
                                    elif replace == "我的用户名":
                                        content += self.my_name
                                    elif replace == "点赞量":
                                        content += liked_times
                                    elif replace == "收藏量":
                                        content += collect_times
                                    elif replace == "浏览量":
                                        content += view_times
                                    else:
                                        content += "[%s]" % replace
                                    replace = ""
                                else:
                                    replace += old_content[i]
                            else:
                                if old_content[i] == "[":
                                    replace_now = True
                                else:
                                    content += old_content[i]


                        # 发送评论
                        r = post(self.set_comment_url(work_id),
                                 data=self.set_comment_data(content, emoji),
                                 headers=self.get_headers())

                        # 检测是否出现问题
                        if r.status_code == 200 or r.status_code == 201:
                            if self.have_error:  # 恢复正常
                                self.data_show_text.insert(tk.END, "已恢复正常\n")
                            else:  # 正常状态
                                self.data_show_text.insert(tk.END, "已成功评论用户%d的作品%d\n" % (user_id, work_id))

                            self.have_error = False
                            self.like_work(work_id)  # 点赞
                            self.last_comment_time = time_now  # 更新上次显示时间
                        else:
                            # 如果出问题情况
                            if not self.have_error:
                                # 报错处理
                                #messagebox.showerror("错误", "评论失败，错误代码为%d，作品id为%d\n" % (r.status_code, work_id))
                                self.data_show_text.insert(tk.END,"评论失败，错误代码为%d，作品id为%d\n" % (r.status_code, work_id))
                            self.have_error = True
                        if not self.have_error:  # 错误等待
                            # 添加用户进已评论用户
                            with open(COMMENTED_USER_PATH, "a", encoding="utf-8") as f:
                                f.write("%d\n" % fans["id"])
                    else:
                        self.have_error = False
                        self.data_show_text.insert(tk.END, "用户%d无作品\n" % user_id)

                    # 显示运行内容
                    self.data_show_text.see(tk.END)
                    self.data_show_text["state"] = tk.DISABLED

                if not self.have_error:  # 错误等待
                    # 跳转下一粉丝
                    self.fans_n += 1
            else:
                self.state = "停止"
                self.data_show_text.insert(tk.END, "运行结束")
                messagebox.showinfo("程序结束", "程序运行结束")

    # 程序运行
    def run(self):
        self.is_running = True
        while self.is_running:
            if self.state == "正在":
                self.comment()
            elif self.state == "停止":
                # 停止后初始化
                if self.need_to_reset:
                    self.need_to_reset = False
                    self.have_error = False
                    self.data_show_text.delete(1.0, tk.END)
                    self.last_comment_time = 0
                    self.commented_user_total = 0
                    self.get_fans_total()

            if self.is_open_select_ui:
                self.security_window.update()

            self.widget_update()
            self.window.update()

            try:
                self.is_running = self.window.winfo_exists()
            except :
                self.is_running = False


        # 保存数据
        self.data["data"]["user_num"] = self.my_num
        self.data["data"]["user_password"] = self.my_password
        self.data["data"]["last_comment_user"]["user_id"] = self.root_id
        self.data["data"]["last_comment_user"]["fans_n"] = self.fans_n

        with open(DATA_PATH, "w", encoding="utf-8") as f:
            f.write(dumps(self.data))

        with open("./data/头像.gif", "w", encoding="utf-8") as f:
            f.write("")

        self.out_security()

# ******************************************************************************************

if __name__ == "__main__":
    main = RequestsMain()
    main.run()
