import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from PIL import Image, ImageTk
from PyQt5.QtWidgets import QApplication
from tktooltip import ToolTip
from ttkthemes import ThemedTk

from gh_issues import issues_init
from own_user_plots.utils import get_api_data
from print_colors import PrintColors
from results_window import ResultsWindow
from search_history import append_to_history, recover_history, get_best_match
from settings import kHEADERS


class TopicsGithub:
    def __init__(self, root_received, width, height):
        self.second_app = QApplication([])
        self.root = root_received
        self.canvas = tk.Canvas(self.root, width=width, height=height)

        self.canvas.pack()
        self.background = Image.open('assets/fondo_claro.png')
        self.background_image = self.background.resize((width, height), Image.ANTIALIAS)
        self.background_image_tk = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image_tk)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.style = ttk.Style()
        self.style.configure('TLabel', background="#ffffff", foreground="#000000")
        self.style.configure("Placeholder.TEntry", foreground="gray")
        self.topic_input_placeholder = "Enter your topic/repo"
        self.top_label = ttk.Label(self.root, text="Select your topic")
        self.top_label.place(x=290, y=0)

        self.history = recover_history()
        self.best_match = None

        self.topic_input = ttk.Entry(self.root)
        self.topic_input.config(foreground="grey")
        self.topic_input.insert(0, self.topic_input_placeholder)
        self.topic_input.bind("<FocusIn>", self.on_entry_click)
        self.topic_input.bind("<FocusOut>", self.on_focus_out)
        self.topic_input.bind("<KeyRelease>", self.on_entry_key_release)
        self.topic_input.bind("<Tab>", self.on_tab_pressed)
        self.topic_input.bind("<BackSpace>", self.on_backspace_pressed)
        self.topic_input.place(x=276, y=20)
        self.autocomplete_label = tk.Label(self.root, text="", foreground="grey", background="white")
        self.autocomplete_label.place(x=276, y=50)

        self.btop_label = ttk.Label(self.root, text="Choose between topic, issues or repositories",
                                    padding=(0, 10, 0, 10))
        self.btop_label.place(x=225, y=69)
        select_opciones = ["Topics", "Repositories", "Issues"]
        self.combobox = ttk.Combobox(self.root, values=select_opciones, state="readonly", width=14)
        self.combobox.set(select_opciones[0])
        self.combobox.bind("<<ComboboxSelected>>", self.select_combobox)
        self.combobox.place(x=290, y=100)

        self.cboxtop_label = ttk.Label(self.root, text="Filter by language", padding=(0, 10, 0, 10))
        self.select_languages_options = ["C", "C++", "Java", "Python", "HTML", "JavaScript", "PHP", "Go", "Dart",
                                         "Kotlin"]
        self.languages_combobox = ttk.Combobox(self.root, values=self.select_languages_options, state="readonly",
                                               width=14)
        self.languages_combobox.set(self.select_languages_options[0])

        self.cboxtop_label_order = ttk.Label(self.root, text="Sort by", padding=(0, 10, 0, 10))
        self.select_order_options = ["Most stars", "Fewest stars", "Most forks", "Fewer forks", "Recently updated",
                                     "Least recently updated"]
        self.order_combobox = ttk.Combobox(self.root, values=self.select_order_options, state="readonly",
                                           width=14)
        self.order_combobox.set(self.select_order_options[0])

        self.search_logo = Image.open('assets/search.png')
        self.search_logo = self.search_logo.resize((20, 20), Image.LANCZOS)
        self.search_logo = ImageTk.PhotoImage(self.search_logo)
        self.search_button = ttk.Button(self.root, text="Search", command=self.search, image=self.search_logo,
                                        compound=tk.LEFT, padding=(0, 10, 0, 10))
        ToolTip(self.search_button, msg="Perform your action", delay=0.01, follow=True,
                fg="black", bg="white", padx=1, pady=1)

        self.issues_logo = Image.open('assets/issues.png')
        self.issues_logo = self.issues_logo.resize((20, 20), Image.LANCZOS)
        self.issues_logo = ImageTk.PhotoImage(self.issues_logo)
        self.issues_button = ttk.Button(self.root, text="Issue by name", command=self.go_to_issues,
                                        image=self.issues_logo,
                                        compound=tk.LEFT, padding=(0, 10, 0, 10))
        self.search_button.place(x=300, y=160)

        self.issues_button.place(x=295, y=215)
        ToolTip(self.issues_button, msg="Search an issue by name", delay=0.01, follow=True,
                fg="black", bg="white", padx=1, pady=1)

        self.go_back_logo = Image.open('assets/go_back.png')
        self.go_back_logo = self.go_back_logo.resize((20, 20), Image.LANCZOS)
        self.go_back_logo = ImageTk.PhotoImage(self.go_back_logo)
        go_back_btn = ttk.Button(self.root, text="Go back", command=self.go_back_tk,
                                 image=self.go_back_logo, compound=tk.LEFT)
        go_back_btn.place(x=5, y=5)
        ToolTip(self.issues_button, msg="Go back to the stats screen", delay=0.01, follow=True,
                fg="black", bg="white", padx=1, pady=1)

        self.frame_border = ttk.Frame(self.root, borderwidth=2, relief='groove')
        self.frame_border.place(x=250, y=305)
        self.progress_bar_value = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.frame_border, variable=self.progress_bar_value, maximum=100,
                                            length=200, mode='determinate')
        self.progress_bar.pack()

    def on_entry_key_release(self, event):
        actual_text_typed = self.topic_input.get()
        self.best_match = get_best_match(self.history, actual_text_typed)
        if self.best_match is not None:
            self.autocomplete_label["text"] = self.best_match
        else:
            self.autocomplete_label["text"] = ""

    def on_tab_pressed(self, event):
        if self.best_match is not None:
            self.topic_input.delete(0, tk.END)
            self.topic_input.insert(0, self.best_match)

    def on_backspace_pressed(self, event):
        self.autocomplete_label["text"] = ""

    def go_back_tk(self):
        from gh_stats import init as stats_init
        self.on_closing()
        stats_init()

    def go_to_issues(self):
        self.on_closing()
        issues_init()

    def select_combobox(self, _):
        if self.combobox.get() == 'Topics':
            self.top_label.config(text='Select your topic')
            self.topic_input_placeholder = "Enter your topic"
            self.languages_combobox.place_forget()
            self.cboxtop_label.place_forget()
            self.order_combobox.place_forget()
            self.cboxtop_label_order.place_forget()
            self.search_button.place_forget()
            self.search_button.place(x=300, y=170)
            self.issues_button.place_forget()
            self.issues_button.place(x=295, y=225)
        elif self.combobox.get() == 'Repositories':
            self.order_combobox.config(
                values=["Most stars", "Fewest stars", "Most forks", "Fewer forks", "Recently updated",
                        "Least recently updated"])
            self.order_combobox.set("Most stars")

            self.top_label.config(text='Select your repository')
            self.topic_input_placeholder = "Enter your repository"
            self.cboxtop_label.place(x=198, y=150)
            self.languages_combobox.place(x=190, y=190)
            self.cboxtop_label_order.place(x=370, y=150)
            self.order_combobox.place(x=335, y=190)
            self.search_button.place_forget()
            self.search_button.place(x=225, y=250)
            self.issues_button.place_forget()
            self.issues_button.place(x=345, y=250)
        elif self.combobox.get() == 'Issues':
            self.order_combobox.config(
                values=["Best match", "Most commented", "Least commented", "Newest", "Oldest", "Recently updated",
                        "Least recently updated"])
            self.order_combobox.set("Best match")

            self.top_label.config(text='Select your issue name')
            self.topic_input_placeholder = "Enter issue name"
            self.cboxtop_label.place(x=198, y=150)
            self.languages_combobox.place(x=190, y=190)
            self.cboxtop_label_order.place(x=370, y=150)
            self.order_combobox.place(x=335, y=190)
            self.search_button.place_forget()
            self.search_button.place(x=225, y=250)
            self.issues_button.place_forget()
            self.issues_button.place(x=345, y=250)
        else:
            raise Exception('Unexpected combobox value')

        self.topic_input.delete(0, "end")
        self.topic_input.insert(0, self.topic_input_placeholder)

    def on_entry_click(self, _):
        if self.topic_input.get() == self.topic_input_placeholder:
            self.topic_input.delete(0, "end")
            self.topic_input.config(foreground="black")

    def on_focus_out(self, _):
        if self.topic_input.get() == "":
            self.topic_input.insert(0, self.topic_input_placeholder)
            self.topic_input.config(foreground="grey")

    def search(self):
        if self.combobox.get() == 'Topics':
            self.get_topics()
        elif self.combobox.get() == 'Repositories':
            self.get_repositories()
        elif self.combobox.get() == 'Issues':
            self.get_issues()
        else:
            raise Exception('Unexpected combobox value')

    def get_sort_code(self):
        opcion = self.order_combobox.get()

        if self.combobox.get() == 'Repositories':
            if opcion == "Most stars":
                return "s=stars&o=desc"
            elif opcion == "Fewest stars":
                return "s=stars&o=asc"
            elif opcion == "Most forks":
                return "s=forks&o=desc"
            elif opcion == "Fewer forks":
                return "s=forks&o=asc"
            elif opcion == "Recently updated":
                return "s=updated&o=desc"
            elif opcion == "Least recently updated":
                return "s=updated&o=asc"
            else:
                return ""
        elif self.combobox.get() == 'Issues':
            if opcion == "Best match":
                return "s=&o=desc"
            elif opcion == "Most commented":
                return "s=comments&o=desc"
            elif opcion == "Least commented":
                return "s=comments&o=asc"
            elif opcion == "Newest":
                return "s=created&o=desc"
            elif opcion == "Oldest":
                return "s=created&o=asc"
            elif opcion == "Recently updated":
                return "s=updated&o=desc"
            elif opcion == "Least recently updated":
                return "s=updated&o=asc"
            else:
                return ""
        else:
            raise Exception('Unexpected combobox value')

    def get_issues(self):
        issue_name = self.topic_input.get()
        append_to_history(issue_name)

        if len(issue_name) == 0 or "Enter issue name" in issue_name:
            messagebox.showerror('Invalid issue name', 'Please introduce a valid issue name')
            print(f'{PrintColors.FAIL}Error{PrintColors.ENDC}: Issue name is empty')
            return

        self.progress_bar_value.set(0)
        self.progress_bar.update()

        url_processed_open = (
            f"https://api.github.com/search/issues?q={issue_name}+language:{self.languages_combobox.get()}+is:issue&"
            f"{self.get_sort_code()}&is:issue".replace(' ', '%20'))

        url_processed_closed = (
            f"https://api.github.com/search/issues?q={issue_name}+language:{self.languages_combobox.get()}+is:issue+is%3Aclosed&"
            f"{self.get_sort_code()}&is:issue".replace(' ', '%20'))

        page_counter = 1
        repos_data_array = []

        while True:
            url_processed = url_processed_closed if page_counter > 15 else url_processed_open
            actual_url = url_processed + "&page=" + str(page_counter)
            repos_data = get_api_data(actual_url, kHEADERS)
            self.progress_bar_value.set(round((page_counter - 1) * 3.3))
            self.progress_bar.update()
            if repos_data is not None:
                if "message" in repos_data or "documentation_url" in repos_data:
                    break
                if "items" not in repos_data or repos_data['items'] is None or len(repos_data["items"]) == 0:
                    messagebox.showerror('Issue not found', 'Your issue was not found')
                    print(f'{PrintColors.FAIL}Error{PrintColors.ENDC}: Issue not found')
                    break
                repos_data_array.append(repos_data)
                page_counter += 1
            else:
                break

        open_issues_count = 0
        issues_len = 0
        for page in repos_data_array:
            for item in page['items']:
                issues_len = issues_len + 1
                if item["state"] == "open":
                    open_issues_count += 1
        closed_issues_count = issues_len - open_issues_count
        to_show_label = f"<p>Total issues found: {issues_len} | Open issues: {open_issues_count}, closed issues: {closed_issues_count}</p><br><h1>Open issues:</h1><br>"

        for page in repos_data_array:
            for item in page['items']:
                if item['state'] == 'open':
                    to_show_label += f"Title: {item['title']}, url: <a href=\"{item['html_url']}\">Visit</a>\n<br>"

        to_show_label += "<br><h1>Closed issues</h1><br><br>"
        for page in repos_data_array:
            for item in page['items']:
                if item['state'] == 'closed':
                    to_show_label += f"Title: {item['title']}, url: <a href=\"{item['html_url']}\">Visit</a>\n<br>"

        datos_csv = []
        datos_csv.append(['Author', 'URL', 'Title', 'State', 'Locked', 'Created at'])
        for page in repos_data_array:
            for item in page['items']:
                datos_csv.append([
                    item['user']['login'], item.get('url', ''), item.get('title', ''), item.get('state', ''),
                    item.get('locked', ''), item.get('created_at', '')
                ])

        self.progress_bar_value.set(100)
        self.progress_bar.update()
        self.open_new_window_with_result(to_show_label, datos_csv)

    def get_repositories(self):
        repo_name = self.topic_input.get()

        if len(repo_name) == 0 or "Enter your repository" in repo_name:
            messagebox.showerror('Invalid repository name', 'Please introduce a repository name')
            print(f'{PrintColors.FAIL}Error{PrintColors.ENDC}: Repository name is empty')
            return

        append_to_history(repo_name)

        self.progress_bar_value.set(0)
        self.progress_bar.update()

        url_processed = \
            (f"https://api.github.com/search/repositories?"
             f"q={repo_name}+language:{self.languages_combobox.get()}&{self.get_sort_code()}")

        page_counter = 1
        repos_data_array = []
        while True:
            actual_url = url_processed + "&page=" + str(page_counter)
            repos_data = get_api_data(actual_url, kHEADERS)
            self.progress_bar_value.set(round((page_counter - 1) * 4.75))
            self.progress_bar.update()
            if repos_data is not None:
                if "message" in repos_data or "documentation_url" in repos_data:
                    break
                if "items" not in repos_data or repos_data['items'] is None or len(repos_data["items"]) == 0:
                    messagebox.showerror('Repository not found', 'Your repository was not found')
                    print(f'{PrintColors.FAIL}Error{PrintColors.ENDC}: Repository not found')
                    break
                repos_data_array.append(repos_data)
                page_counter += 1
            else:
                break

        repos_count = 0
        for page in repos_data_array:
            for _ in page['items']:
                repos_count = repos_count + 1

        to_show_label = f"<p>Total number of repositories shown: {repos_count}</p><br><h1>Repositories found</h1><br>"
        datos_csv = []
        datos_csv.append(
            ['Author', 'Repo name', 'URL', 'Description', 'Created_at', 'Stars', 'Primary language', 'Watchers count',
             'Forks count', 'Open issues count'])
        for page in repos_data_array:
            for item in page['items']:
                to_show_label += f"Name: {item['name']}, url: <a href=\"{item['html_url']}\">Visit</a>\n<br>"
                datos_csv.append([
                    item['owner']['login'], item.get('name', ''), item.get('html_url', ''), item.get('description', ''),
                    item.get('created_at', ''), item.get('stargazers_count', ''), item.get('language', ''),
                    item.get('watchers_count', '', ), item.get('forks_count', ''), item.get('open_issues_count', '')
                ])

        self.progress_bar_value.set(100)
        self.progress_bar.update()
        self.open_new_window_with_result(to_show_label, datos_csv)

    def get_topics(self):
        topic_name = self.topic_input.get()

        if len(topic_name) == 0 or "Enter your topic" in topic_name or "Enter your topic / repository name" in topic_name:
            messagebox.showerror('Invalid topic name', 'Please introduce a topic name')
            print(f'{PrintColors.FAIL}Error{PrintColors.ENDC}: Topic name is empty')
            return

        append_to_history(topic_name)

        self.progress_bar_value.set(0)
        self.progress_bar.update()

        url_pre_arguments = "https://api.github.com/search/repositories"
        url_post_arguments = f"?q={topic_name}&s=stars&o=desc"
        if topic_name.startswith('http'):
            question_mark_position = topic_name.find('?')
            url_post_arguments = topic_name[question_mark_position:]

        final_url = url_pre_arguments + url_post_arguments
        parsed_url_final = final_url.replace("repositories", "topics")

        page_counter = 1
        repos_data_array = []
        while True:
            actual_url = parsed_url_final + "&page=" + str(page_counter)
            repos_data = get_api_data(actual_url, kHEADERS)
            self.progress_bar_value.set(round((page_counter - 1) * 3.15))
            self.progress_bar.update()
            if repos_data is not None:
                if "message" in repos_data or "documentation_url" in repos_data:
                    break
                if "items" not in repos_data or repos_data['items'] is None or len(repos_data["items"]) == 0:
                    messagebox.showerror('Topic not found', 'Your topic was not found')
                    print(f'{PrintColors.FAIL}Error{PrintColors.ENDC}: Topic not found')
                    break
                repos_data_array.append(repos_data)
                page_counter += 1
            else:
                break

        first_topic_data = repos_data_array[0]["items"][0]
        to_show_label = f"Total topics shown: {len(repos_data_array)}<br><br>" + (
            f"Topic name: {first_topic_data['display_name']}, "
            f"description: {first_topic_data['short_description']}\n\n<br><br><br>\n\n<h1>Topics</h1><br>")

        datos_csv = []
        datos_csv.append(['Nombre', 'URL', 'Short_description', 'Created by', 'Released'])
        for page in repos_data_array:
            for item in page['items']:
                to_show_label += \
                    f"Name: {item['name']}, url: <a href=\"https://github.com/topics/{item['name']}\">Visit</a>\n<br>"
                datos_csv.append([
                    item.get('name', ''), f"https://github.com/topics/{item.get('name')}",
                    item.get('short_description', ''),
                    item.get('created_by', ''), item.get('released', '')
                ])

        self.progress_bar_value.set(100)
        self.progress_bar.update()
        self.open_new_window_with_result(to_show_label, datos_csv)

    def on_closing(self):
        self.root.destroy()
        self.root.quit()

    def open_new_window_with_result(self, to_show_label, datos_csv):
        results_window = ResultsWindow(to_show_label, datos_csv, self.second_app)
        results_window.show_window()
        self.second_app.exec_()
        self.second_app.quit()


def topics_init():
    root = ThemedTk(theme="adapta")
    root.configure(bg="#f0f0f0")
    icon_image = ImageTk.PhotoImage(file='./assets/icon.png')
    root.tk.call('wm', 'iconphoto', root._w, icon_image)
    root.title('Mining Open-Source Social Coding Platforms - Topics')
    width = 720
    height = 360
    root.geometry("%dx%d" % (width, height))
    root.resizable(width=False, height=False)
    TopicsGithub(root, width, height)
    root.mainloop()


if __name__ == "__main__":
    topics_init()
