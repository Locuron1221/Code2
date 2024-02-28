import tkinter as tk
from tkinter import *

import dill

from plots import *
from utils import *

kTOKEN = "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"
kHEADERS = {
    "Authorization": f"Bearer {kTOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}


class MineGithub:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        top_label = tk.Label(self.root, text="Enter your GitHub username")
        top_label.pack()

        self.username_input = tk.Entry(self.root)
        self.username_input.pack()

        save_input = tk.Button(self.root, text="Process", command=self.get_and_show_plots)
        save_input.pack()

        self.myscrollbar = Scrollbar(self.root, orient="vertical")
        self.myscrollbar.pack(side="right", fill="y")

        self.canvas = Canvas(self.root, yscrollcommand=self.myscrollbar.set)
        self.canvas.pack(side="top", fill="both", expand=True)

        self.myscrollbar.config(command=self.canvas.yview)

        self.graph_frame_container = tk.Frame(self.canvas)
        self.canvas.create_window((100, 0), window=self.graph_frame_container, anchor="nw")

        self.graphs = []
        self.graphs_labels = []

        graphs_titles = ['Stargazers', 'Forks', 'Licenses', 'Open Issues', 'Programming languages',
                         'Days since creation', 'Topics', 'Top issue asignees', 'Top issue labels',
                         'Top issue creators', 'Top issue key words', '']

        self.create_grid(graphs_titles)

        self.canvas.yview_moveto(0)

        self.graph_frame_container.bind("<Configure>", self.on_canvas_configure)

    def on_canvas_configure(self, _):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_grid(self, graphs_titles):
        for row in range(6):
            row_frame = tk.Frame(self.graph_frame_container)
            row_frame.pack(side="top")

            for col in range(2):
                frame = tk.Frame(row_frame)
                frame.pack(side="left", padx=10, pady=10)

                label = tk.Label(frame, text=graphs_titles[(row * 2 + col + 1) - 1], anchor="center")
                self.graphs_labels.append(label)

                self.graphs.append(frame)

    def get_and_show_plots(self):
        user_login = self.username_input.get()

        user_url = f"https://api.github.com/users/{user_login}"
        repos_url = f"https://api.github.com/users/{user_login}/repos"

        # user_data = get_api_data(user_url, kHEADERS)
        # user_time_since_creation = get_time_passed_since_now(user_data["created_at"])
        # user_followers = user_data["followers"]
        # user_following = user_data["following"]
        # user_public_repos = user_data["public_repos"]
        # user_name = user_data["name"]
        # user_bio = user_data["bio"]
        #
        # repos_data = get_api_data(repos_url, kHEADERS)
        # repo_data_class_list = []

        with open('../repo_data_class_list.pkl', 'rb') as archivo:
            repo_data_class_list = dill.load(archivo)

        # for (index, repo) in enumerate(repos_data):
        #     closed_issues_url = f"https://api.github.com/repos/{user_login}/{repo['name']}/issues?state=closed"
        #     open_issues_url = f"https://api.github.com/repos/{user_login}/{repo['name']}/issues?state=open"
        #     closed_issues_data = get_api_data(closed_issues_url, kHEADERS)
        #     open_issues_data = get_api_data(open_issues_url, kHEADERS)
        #
        #     issues_data = closed_issues_data + open_issues_data
        #     new_repo = RepoDataClass(repo, issues_data, len(open_issues_data), len(closed_issues_data))
        #     repo_data_class_list.append(new_repo)
        #
        #
        #     ################################################################3
        #
        #
        # with open('repo_data_class_list.pkl', 'wb') as archivo:
        #     dill.dump(repo_data_class_list, archivo)

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
            #     print(issue.html_url)
            #     issue_html_text_as_one += get_html_data(issue.html_url, kHEADERS)

        print(issue_html_text_as_one)

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

    def on_closing(self):
        self.root.destroy()
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    root.title('Mining Open-Source Social Coding Platforms')
    width = 1450
    height = 750
    root.geometry("%dx%d" % (width, height))
    app = MineGithub(root)
    root.mainloop()
