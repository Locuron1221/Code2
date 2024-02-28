import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def get_arrays_singular(array_strs):
    strs_names_singular = []
    values_repetition = []
    for str_json_raw in array_strs:
        if str_json_raw in strs_names_singular:  # si ya existe
            index_found = 0
            for (index, str_lcs) in enumerate(strs_names_singular):
                if str_lcs == str_json_raw:
                    index_found = index
                    break
            values_repetition[index_found] += 1
        else:
            strs_names_singular.append(str_json_raw)
            values_repetition.append(1)
    return [strs_names_singular, values_repetition]


def get_arrays_singular_top_10(array_strs):
    strs_names_singular = []
    for str_json_raw in array_strs:
        if is_in_singular_subarray(str_json_raw, strs_names_singular):  # si ya existe
            index_found = 0
            for (index, str_lcs) in enumerate(strs_names_singular):
                if str_lcs[0] == str_json_raw:
                    index_found = index
                    break
            strs_names_singular[index_found][1] = strs_names_singular[index_found][1] + 1
        else:
            strs_names_singular.append([str_json_raw, 1])

    strs_names_singular_sorted = sorted(strs_names_singular, key=lambda x: x[1], reverse=True)
    strs_names_singular_sorted_top_10 = strs_names_singular_sorted[:10]

    strs_names_singular = []
    values_repetition = []

    for (index, value) in enumerate(strs_names_singular_sorted_top_10):
        strs_names_singular.append(value[0])
        values_repetition.append(value[1])

    return [strs_names_singular, values_repetition]


def is_in_singular_subarray(received_str,strs_names_singular):
    for (index, value) in enumerate(strs_names_singular):
        if (value[0]) == received_str:
            return True
    return False

def plot_stem_array_count(number_array, type, canvas):
    number_array_parsed = [x for x in number_array if x != 0]
    stargazers_array_log = np.log10(number_array_parsed)
    x = 0.5 + np.arange(len(number_array_parsed))
    fig, ax = plt.subplots(figsize=(6,6))
    lines = ax.stem(x, stargazers_array_log, basefmt=" ", linefmt="-", markerfmt="ro")

    ax.set(xlim=(0, len(number_array_parsed)), xticks=np.arange(0, len(number_array_parsed)),
           xticklabels=[f"{i + 1}" for i in range(len(number_array_parsed))])

    for i in range(len(number_array_parsed)):
        ax.annotate(f"{number_array_parsed[i]}", (x[i], stargazers_array_log[i]), textcoords="offset points",
                    xytext=(9.5, 0),
                    ha='center', fontsize=8, color="red")

    plt.xlabel('Repos')
    plt.ylabel(type + ' (log scale)')

    canvas_widget = FigureCanvasTkAgg(fig, master=canvas)
    canvas_widget_w = canvas_widget.get_tk_widget()
    canvas_widget_w.pack()


def plot_pie(textos, valores, canvas, title='Licenses'):
    plt.style.use('_mpl-gallery-nogrid')
    colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(valores)))
    # plot
    fig, ax = plt.subplots(figsize=(6,6))
    wedges, texts, autotexts = ax.pie(valores, labels=textos, colors=colors, autopct='%1.1f%%', radius=3,
                                      center=(4, 4),
                                      wedgeprops={"linewidth": 1, "edgecolor": "white"}, startangle=90, frame=True)

    ax.legend(wedges, textos, title=title, loc='lower left')
    #
    # ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
    #        ylim=(0, 8), yticks=np.arange(1, 8))

    canvas_widget = FigureCanvasTkAgg(fig, master=canvas)
    canvas_widget_w = canvas_widget.get_tk_widget()
    canvas_widget_w.pack()


def plot_bar(textos, valores, canvas):
    plt.style.use('_mpl-gallery-nogrid')
    x = np.arange(len(textos))
    colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(textos)))

    fig, ax = plt.subplots(figsize=(6,6))
    bars = ax.bar(x, valores, color=colors)

    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.annotate(f'{valores[i]}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # Desplazamiento vertical de la etiqueta
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Etiquetas en el eje x
    ax.set_xticks(x)
    ax.set_xticklabels(textos)

    plt.xticks(rotation=45)  # Rotar etiquetas en el eje x para mejor visualización
    plt.tight_layout()

    canvas_widget = FigureCanvasTkAgg(fig, master=canvas)
    canvas_widget_w = canvas_widget.get_tk_widget()
    canvas_widget_w.pack()



def plot_stairs(values, canvas):
    plt.style.use('_mpl-gallery')
    x = np.arange(len(values))
    fig, ax = plt.subplots(figsize=(6,6))
    ax.step(x, [v + 5 for v in values], linewidth=2.5, where='mid')
    for i, val in enumerate(values):
        ax.annotate(val, (x[i], val + 5), textcoords="offset points", xytext=(0, 10), ha='center')
    #ax.legend(title='Days since creation')
    ax.set(xlim=(0, len(values) - 1), ylim=(-5, max(values) + 100))
    canvas_widget = FigureCanvasTkAgg(fig, master=canvas)
    canvas_widget_w = canvas_widget.get_tk_widget()
    canvas_widget_w.pack()
