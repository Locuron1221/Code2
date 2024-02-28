import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk
from tktooltip import ToolTip
from ttkthemes import ThemedTk

from gh_issues import issues_init
from gh_stats import init as stats_init
from gh_topics import topics_init


class HomePage:
    def __init__(self, root_received, width, height, username):
        self.root = root_received
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.canvas = tk.Canvas(self.root, width=width, height=height)

        self.canvas.pack()
        self.background = Image.open('assets/fondo_claro.png')
        self.background_image = self.background.resize((width, height), Image.ANTIALIAS)
        self.background_image_tk = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image_tk)

        self.style = ttk.Style()
        self.style.configure('TLabel', background="#fff")
        self.style.configure("Placeholder.TEntry", foreground="grey")
        self.top_label = ttk.Label(self.root, text=f"Welcome {username}")
        self.top_label.place(x=277, y=5)

        self.issues_logo = Image.open('assets/issues.png')
        self.issues_logo = self.issues_logo.resize((20, 20), Image.LANCZOS)
        self.issues_logo = ImageTk.PhotoImage(self.issues_logo)
        self.issues_button = ttk.Button(self.root, text="Go to Github issues", command=self.go_to_issues,
                                        image=self.issues_logo, compound=tk.LEFT, padding=(0, 10, 0, 10))
        self.issues_button.place(x=277, y=35)
        ToolTip(self.issues_button, msg="Go to issues", delay=0.01, follow=True,
                fg="black", bg="white", padx=1, pady=1)

        self.stats_logo = Image.open('assets/stats.png')
        self.stats_logo = self.stats_logo.resize((20, 20), Image.LANCZOS)
        self.stats_logo = ImageTk.PhotoImage(self.stats_logo)
        self.stats_button = ttk.Button(self.root, text="Go to Github stats", command=self.go_to_stats,
                                       image=self.stats_logo, compound=tk.LEFT, padding=(0, 10, 0, 10))
        self.stats_button.place(x=280, y=85)
        ToolTip(self.stats_button, msg="Go to GIthub stats", delay=0.01, follow=True,
                fg="black", bg="white", padx=1, pady=1)

        self.topics_logo = Image.open('assets/topics.png')
        self.topics_logo = self.topics_logo.resize((20, 20), Image.LANCZOS)
        self.topics_logo = ImageTk.PhotoImage(self.topics_logo)
        self.topics_button = ttk.Button(self.root, text="Go to Github topics", command=self.go_to_topics,
                                        image=self.topics_logo, compound=tk.LEFT, padding=(0, 10, 0, 10))
        self.topics_button.place(x=277, y=135)
        ToolTip(self.topics_button, msg="Go to Github topics", delay=0.01, follow=True,
                fg="black", bg="white", padx=1, pady=1)

    def on_closing(self):
        self.root.destroy()
        self.root.quit()

    def go_to_issues(self):
        self.on_closing()
        issues_init()

    def go_to_stats(self):
        self.on_closing()
        stats_init()

    def go_to_topics(self):
        self.on_closing()
        topics_init()


def home_page_init(username):
    root = ThemedTk(theme="adapta")
    root.configure(bg="#f0f0f0")
    icon_image = ImageTk.PhotoImage(file='./assets/icon.png')
    root.tk.call('wm', 'iconphoto', root._w, icon_image)
    root.title('Mining Open-Source Social Coding Platforms - Issues')
    width = 600
    height = 200
    root.geometry("%dx%d" % (width, height))
    root.resizable(width=False, height=False)
    HomePage(root, width, height, username)
    root.mainloop()


if __name__ == "__main__":
    home_page_init("unknown")
