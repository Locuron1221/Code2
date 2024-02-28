import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from PIL import Image, ImageTk
from tktooltip import ToolTip
from ttkthemes import ThemedTk

from gh_topics import topics_init
from own_user_plots.plots import plot_pie, plot_stem_array_count, plot_bar, plot_stairs, get_arrays_singular_top_10, \
    get_arrays_singular
from own_user_plots.repo_data_class import RepoDataClass
from own_user_plots.utils import *
from print_colors import PrintColors
from search_history import recover_history, get_best_match
from settings import kHEADERS


class MineGithub:
    def __init__(self, root_received, width, height):
        self.root = root_received
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.canvas = tk.Canvas(self.root, width=width, height=height)
        self.canvas.pack()
        self.background = Image.open('assets/fondo_claro.png')
        self.background_image = self.background.resize((width, height), Image.ANTIALIAS)
        self.background_image_tk = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image_tk)

        self.root_child = tk.Toplevel(self.root)
        self.root_child.title('Results')
        self.root_child.geometry('1275x750')
        self.root_child.configure(bg='#f0f0f0')
        self.root_child.resizable(width=False, height=False)
        self.root_child.withdraw()

        top_label = ttk.Label(self.root, text="Enter your GitHub username")
        top_label.place(x=250, y=0)

        self.style = ttk.Style()
        self.style.configure('TLabel', background="#fff", foreground="#000")

        self.history = recover_history()
        self.best_match = None
        self.username_input = ttk.Entry(self.root)
        self.username_input.place(x=255, y=23)
        self.username_input.bind("<KeyRelease>", self.on_entry_key_release)
        self.username_input.bind("<Tab>", self.on_tab_pressed)
        self.username_input.bind("<BackSpace>", self.on_backspace_pressed)

        self.autocomplete_label = tk.Label(self.root, text="", foreground="grey", background="white")
        self.autocomplete_label.place(x=255, y=53)

        self.process_logo = Image.open('assets/process.png')
        self.process_logo = self.process_logo.resize((20, 20), Image.LANCZOS)
        self.process_logo = ImageTk.PhotoImage(self.process_logo)
        save_input = ttk.Button(self.root, text="Process", command=self.get_and_show_plots, image=self.process_logo,
                                compound=tk.LEFT)
        save_input.place(x=275, y=75)
        ToolTip(save_input, msg="Process and generate stats for the specified user ", delay=0.01, follow=True,
                fg="black", bg="white", padx=1, pady=1)

        self.go_back_logo = Image.open('assets/topics.png')
        self.go_back_logo = self.go_back_logo.resize((20, 20), Image.LANCZOS)
        self.go_back_logo = ImageTk.PhotoImage(self.go_back_logo)
        go_to_topics_btn = ttk.Button(self.root, text="Go to topics", command=self.go_to_topics_tk,
                                      image=self.go_back_logo, compound=tk.LEFT)
        go_to_topics_btn.place(x=275, y=115)
        ToolTip(go_to_topics_btn, msg="Go back to search topics", delay=0.01, follow=True,
                fg="black", bg="white", padx=1, pady=1)

        self.frame_border = ttk.Frame(self.root, borderwidth=2, relief='groove')
        self.frame_border.place(x=240, y=160)

        self.progress_bar_value = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.frame_border, variable=self.progress_bar_value, maximum=100,
                                            length=200, mode='determinate')
        self.progress_bar.pack()

        self.myscrollbar = ttk.Scrollbar(self.root_child, orient="vertical")
        self.myscrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(self.root_child, yscrollcommand=self.myscrollbar.set, bg="#f0f0f0",
                                background="#f0f0f0")

        self.myscrollbar.config(command=self.canvas.yview)

        self.graph_frame_container = ttk.Frame(self.canvas)
        self.canvas.create_window((100, 0), window=self.graph_frame_container, anchor="nw")

        self.graphs = []
        self.graphs_labels = []

        graphs_titles = ['Stargazers', 'Forks', 'Licenses', 'Open Issues', 'Programming languages',
                         'Days since creation', 'Topics', 'Top issue asignees', 'Top issue labels',
                         'Top issue creators']

        self.create_grid(graphs_titles)

        self.graph_frame_container.bind("<Configure>", self.on_canvas_configure)

    def on_canvas_configure(self, _):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_entry_key_release(self, _):
        actual_text_typed = self.username_input.get()
        self.best_match = get_best_match(self.history, actual_text_typed)
        if self.best_match is not None:
            self.autocomplete_label["text"] = self.best_match
        else:
            self.autocomplete_label["text"] = ""

    def on_tab_pressed(self, event):
        if self.best_match is not None:
            self.username_input.delete(0, tk.END)
            self.username_input.insert(0, self.best_match)

    def on_backspace_pressed(self, event):
        self.autocomplete_label["text"] = ""

    def create_grid(self, graphs_titles):
        for row in range(5):
            row_frame = ttk.Frame(self.graph_frame_container)
            row_frame.pack(side="top")

            for col in range(2):
                frame = ttk.Frame(row_frame)
                frame.pack(side="left", padx=10, pady=10)

                label = ttk.Label(frame, text=graphs_titles[(row * 2 + col + 1) - 1], anchor="center")
                self.graphs_labels.append(label)

                self.graphs.append(frame)

    def go_to_topics_tk(self):
        self.on_closing()
        topics_init()

    def get_and_show_plots(self):
        user_login = self.username_input.get()

        if len(user_login) == 0:
            messagebox.showerror('User invalid', 'You have to introduce a valid GitHub username')
            print(f'{PrintColors.FAIL}Error{PrintColors.ENDC}: You have to introduce a valid GitHub username')
            return

        append_to_history(user_login)

        user_url = f"https://api.github.com/users/{user_login}"
        repos_url = f"https://api.github.com/users/{user_login}/repos"
        user_data = get_api_data(user_url, kHEADERS)
        if user_data is None:
            messagebox.showerror('User not found', 'Your GitHub username was not found')
            print(f'{PrintColors.FAIL}Error{PrintColors.ENDC}: User not found')
            return

        user_time_since_creation = get_time_passed_since_now(user_data["created_at"])
        user_followers = user_data["followers"]
        user_following = user_data["following"]
        user_public_repos = user_data["public_repos"]
        user_name = user_data["name"]
        user_bio = user_data["bio"]
        #
        repos_data = get_api_data(repos_url, kHEADERS)
        repo_data_class_list = []

        # with open('repo_data_class_list.pkl', 'rb') as archivo:
        #    repo_data_class_list = dill.load(archivo)

        len_repos_data = len(repos_data)
        old_percent = 0

        for (index, repo) in enumerate(repos_data):
            if index == 3:
                break
            percent_value = round(((index / len_repos_data) * 100), 2)
            self.progress_bar_value.set(percent_value)
            self.progress_bar.update()
            print(f"Analyzing: {repo['name']} {index + 1}/{len_repos_data} {percent_value}%")
            closed_issues_url = f"https://api.github.com/repos/{user_login}/{repo['name']}/issues?state=closed"
            open_issues_url = f"https://api.github.com/repos/{user_login}/{repo['name']}/issues?state=open"
            closed_issues_data = get_api_data(closed_issues_url, kHEADERS)
            mid_step_percent_value = round(((percent_value - old_percent) * 0.66 + percent_value), 2)
            self.progress_bar_value.set(mid_step_percent_value)
            self.progress_bar.update()
            old_percent = mid_step_percent_value
            print(f"Analyzing: {repo['name']} {index + 1}/{len_repos_data} {self.progress_bar_value.get()}%")

            open_issues_data = get_api_data(open_issues_url, kHEADERS)

            issues_data = closed_issues_data + open_issues_data
            new_repo = RepoDataClass(repo, issues_data, len(open_issues_data), len(closed_issues_data))
            repo_data_class_list.append(new_repo)

        print(f'Analyzing: "DONE" {len_repos_data}/{len_repos_data}')
        self.progress_bar_value.set(100)

        #     ################################################################3
        #
        # with open('repo_data_class_list.pkl', 'wb') as archivo:
        #     dill.dump(repo_data_class_list, archivo)
        #
        stargazers_count = []
        forks_count = []
        licenses_names = []
        open_issues_count = []
        languages_names = []
        time_passed = []
        topics_found = []
        assignee_found = []
        issue_labels = []
        creator_found = []
        issue_html_text_as_one = ''

        for (index, repo) in enumerate(repo_data_class_list):
            stargazers_count.append(repo.stargazers_count)
            forks_count.append(repo.forks_count)
            licenses_names.append(repo.license_name)
            open_issues_count.append(repo.open_issues_count)
            languages_names.append(repo.language)
            time_passed.append(repo.time_since_creation.days)
            topics_found.extend(repo.topics)
            assignee_found.extend(get_assignees(repo.issues))
            issue_labels.extend(get_issue_labels_individually(repo.issues))
            creator_found.extend(get_creators_individually(repo.issues))
            # for issue in repo.issues:
            #    if issue is not None and issue.body is not None and len(issue.body) > 0:
            #        issue_html_text_as_one += issue.body

        # print(process_and_get_key_words_data(issue_html_text_as_one))

        languages_names_singular, languages_repetition = get_arrays_singular(languages_names)
        licenses_names_singular, licenses_repetition = get_arrays_singular(licenses_names)
        topics_names_singular, topics_repetition = get_arrays_singular_top_10(topics_found)
        issue_assignee_names_singular, issue_assignee_repetition = get_arrays_singular_top_10(assignee_found)
        issue_labels_names_singular, issue_labels_repetition = get_arrays_singular_top_10(issue_labels)
        creator_labels_names_singular, creator_labels_repetition = get_arrays_singular_top_10(creator_found)

        for label in self.graphs_labels:
            label.pack()

        plot_stem_array_count(stargazers_count, 'Stargazers', self.graphs[0])
        plot_stem_array_count(forks_count, 'Forks', self.graphs[1])
        plot_pie(licenses_names_singular, licenses_repetition, canvas=self.graphs[2])
        plot_stem_array_count(open_issues_count, 'Open issues', self.graphs[3])
        plot_bar(languages_names_singular, languages_repetition, self.graphs[4])
        plot_stairs(time_passed, self.graphs[5])
        plot_pie(topics_names_singular, topics_repetition, canvas=self.graphs[6])
        plot_pie(issue_assignee_names_singular, issue_assignee_repetition, title='Top issue assignees',
                 canvas=self.graphs[7])
        plot_pie(issue_labels_names_singular, issue_labels_repetition, title='Top issue labels', canvas=self.graphs[8])
        plot_pie(creator_labels_names_singular, creator_labels_repetition, title='Top issue creators',
                 canvas=self.graphs[9])

        self.root_child.deiconify()
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.yview_moveto(0)

    def on_closing(self):
        self.root.destroy()
        self.root.quit()


def init():
    root = ThemedTk(theme="adapta")
    icon_image = ImageTk.PhotoImage(file='./assets/icon.png')
    root.tk.call('wm', 'iconphoto', root._w, icon_image)
    root.title('Mining Open-Source Social Coding Platforms - User stats')
    root.configure(bg="#f0f0f0")
    width = 600
    height = 175
    root.geometry("%dx%d" % (width, height))
    root.resizable(width=False, height=False)
    MineGithub(root, width, height)
    root.mainloop()


if __name__ == "__main__":
    init()
