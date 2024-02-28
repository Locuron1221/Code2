import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from PIL import Image, ImageTk
from PyQt5.QtWidgets import QApplication
from tktooltip import ToolTip
from ttkthemes import ThemedTk

from own_user_plots.utils import get_api_data
from print_colors import PrintColors
from results_window import ResultsWindow
from search_history import recover_history, get_best_match, append_to_history
from settings import kHEADERS


class GithubIssues:
    def __init__(self, root_received, width, height):
        self.second_app = QApplication([])
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
        self.topic_input_placeholder = "Enter your \"username/repository\""
        self.top_label = ttk.Label(self.root, text='Enter your "username/repository"')
        self.top_label.place(x=270, y=5)

        self.history = recover_history()
        self.best_match = None

        self.issues_input = ttk.Entry(self.root)
        self.issues_input.config(foreground="white", width=30)
        self.issues_input.insert(0, self.topic_input_placeholder)
        self.issues_input.bind("<FocusIn>", self.on_entry_click)
        self.issues_input.bind("<FocusOut>", self.on_focus_out)
        self.issues_input.bind("<KeyRelease>", self.on_entry_key_release)
        self.issues_input.bind("<Tab>", self.on_tab_pressed)
        self.issues_input.bind("<BackSpace>", self.on_backspace_pressed)

        self.issues_input.place(x=255, y=35)

        self.autocomplete_label = tk.Label(self.root, text="", foreground="grey", background="white")
        self.autocomplete_label.place(x=255, y=65)

        self.search_logo = Image.open('assets/search.png')
        self.search_logo = self.search_logo.resize((20, 20), Image.LANCZOS)
        self.search_logo = ImageTk.PhotoImage(self.search_logo)
        self.search_button = ttk.Button(self.root, text="Search", command=self.search, image=self.search_logo,
                                        compound=tk.LEFT, padding=(0, 10, 0, 10))
        self.search_button.place(x=320, y=85)
        ToolTip(self.search_button, msg="Search for issues", delay=0.01, follow=True,
                fg="black", bg="white", padx=1, pady=1)

        self.go_back_logo = Image.open('assets/go_back.png')
        self.go_back_logo = self.go_back_logo.resize((20, 20), Image.LANCZOS)
        self.go_back_logo = ImageTk.PhotoImage(self.go_back_logo)
        go_back_btn = ttk.Button(self.root, text="Go back", command=self.go_back_tk,
                                 image=self.go_back_logo, compound=tk.LEFT)
        go_back_btn.place(x=5, y=5)
        ToolTip(go_back_btn, msg="Go back to the topics screen", delay=0.01, follow=True,
                fg="black", bg="white", padx=1, pady=1)

    def on_entry_key_release(self, _):
        actual_text_typed = self.issues_input.get()
        self.best_match = get_best_match(self.history, actual_text_typed)
        if self.best_match is not None:
            self.autocomplete_label["text"] = self.best_match
        else:
            self.autocomplete_label["text"] = ""

    def on_tab_pressed(self, _):
        if self.best_match is not None:
            self.issues_input.delete(0, tk.END)
            self.issues_input.insert(0, self.best_match)

    def on_backspace_pressed(self, _):
        self.autocomplete_label["text"] = ""

    def go_back_tk(self):
        from gh_topics import topics_init as topics_init_start
        self.on_closing()
        topics_init_start()

    def on_entry_click(self, _):
        if self.issues_input.get() == self.topic_input_placeholder:
            self.issues_input.delete(0, "end")
            self.issues_input.config(foreground="black")

    def on_focus_out(self, _):
        if self.issues_input.get() == "":
            self.issues_input.insert(0, self.topic_input_placeholder)
            self.issues_input.config(foreground="grey")

    def search(self):
        issues_data = []
        pages_iterator = 1
        append_to_history(self.issues_input.get())

        while True:
            issues_api_url = (f"https://api.github.com/repos/{self.issues_input.get()}/issues?state=all&per_page=100"
                              f"&page={pages_iterator}")
            issues_data_obtained = get_api_data(issues_api_url, kHEADERS)
            if issues_data_obtained is None or len(issues_data_obtained) == 0:
                break
            issues_data = issues_data + issues_data_obtained
            pages_iterator += 1

        if len(issues_data) == 0:
            messagebox.showerror('Not found',
                                 'Your repository was not found or it does not have any issue. The appropiate syntax '
                                 'is: username/repositoryname')
            print(f'{PrintColors.FAIL}Error{PrintColors.ENDC}: Your repository was not found')
            return

        open_issues_count = 0
        for issue in issues_data:
            if issue["state"] == "open":
                open_issues_count += 1
        closed_issues_count = len(issues_data) - open_issues_count
        to_show_label = f"<p>Total issues found: {len(issues_data)} | Open issues: {open_issues_count}, closed issues: {closed_issues_count}</p><br><h1>Open issues:</h1><br>"

        open_issues_html = ""
        closed_issues_html = ""
        datos_csv = [['Nombre', 'URL', 'Open', 'Author', 'Assignee', 'Comments']]

        for issue in issues_data:
            datos_csv.append([issue["title"],
                              issue["url"],
                              "Yes" if issue["state"] == "open" else "No",
                              issue["user"]["login"],
                              issue["assignee"]["login"] if issue["assignee"] is not None else '',
                              issue["comments"]])
            if issue["state"] == "open":
                open_issues_html += f'<strong>Title</strong>: {issue["title"]}. | <strong>URL</strong> <a href="{issue["html_url"]}">Visit</a>\n<br>'
            else:
                closed_issues_html += f'<strong>Title</strong>: {issue["title"]}. | <strong>URL</strong> <a href="{issue["html_url"]}">Visit</a>\n<br>'

        to_show_label += open_issues_html

        to_show_label += "<br><h1>Closed issues:</h1><br>"
        to_show_label += closed_issues_html

        self.open_new_window_with_result(to_show_label, datos_csv)

    def open_new_window_with_result(self, to_show_label, datos_csv):
        results_window = ResultsWindow(to_show_label, datos_csv, self.second_app)
        results_window.show_window()
        self.second_app.exec_()
        self.second_app.quit()

    def on_closing(self):
        self.root.destroy()
        self.root.quit()


def issues_init():
    root = ThemedTk(theme="adapta")
    root.configure(bg="#f0f0f0")
    icon_image = ImageTk.PhotoImage(file='./assets/icon.png')
    root.tk.call('wm', 'iconphoto', root._w, icon_image)
    root.title('Mining Open-Source Social Coding Platforms - Issues')
    width = 600
    height = 140
    root.geometry("%dx%d" % (width, height))
    root.resizable(width=False, height=False)
    GithubIssues(root, width, height)
    root.mainloop()


if __name__ == "__main__":
    issues_init()
