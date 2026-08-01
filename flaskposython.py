import sys
import threading

from flask import Flask, request, redirect, url_for, render_template_string, render_template

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView


# -------------------------
#  Serveur Flask (backend)
# -------------------------

app = Flask(__name__)

# Todo-list en mémoire (pour l'exemple)
TODOS = []


HTML_TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>TodoList Flask + Qt</title>
    <style>
        body {
            font-family: sans-serif;
            margin: 2rem;
        }
        h1 {
            margin-bottom: 1rem;
        }
        form {
            margin-bottom: 1rem;
        }
        input[type="text"] {
            padding: 0.4rem;
            width: 250px;
        }
        button {
            padding: 0.4rem 0.8rem;
            cursor: pointer;
        }
        ul {
            list-style: none;
            padding-left: 0;
        }
        li {
            margin-bottom: 0.3rem;
        }
        .done {
            text-decoration: line-through;
            color: #777;
        }
    </style>
</head>
<body>
    <h1>TodoList – Flask &amp; QtWebEngine</h1>

    <form method="post" action="{{ url_for('add_todo') }}">
        <input type="text" name="task" placeholder="Nouvelle tâche..." required>
        <button type="submit">Ajouter</button>
    </form>

    {% if todos %}
        <ul>
{% for todo in todos %}
    {% set i = loop.index0 %}
    <li>
        <form style="display:inline;" method="post" action="{{ url_for('toggle_done', index=i) }}">
            <button type="submit">
                {% if todo.done %}☑{% else %}☐{% endif %}
            </button>
        </form>

        <span class="{{ 'done' if todo.done else '' }}">{{ todo.text }}</span>

        <form style="display:inline;" method="post" action="{{ url_for('delete_todo', index=i) }}">
            <button type="submit">🗑</button>
        </form>
    </li>
{% endfor %}
</ul>
    {% else %}
        <p>Aucune tâche pour le moment.</p>
    {% endif %}
</body>
</html>
"""


class TodoItem:
    def __init__(self, text, done=False):
        self.text = text
        self.done = done


@app.route("/", methods=["GET"])
def index():
    #return render_template_string(HTML_TEMPLATE, todos=TODOS)
    return render_template("todo.html", todos=TODOS)


@app.route("/add", methods=["POST"])
def add_todo():
    task = request.form.get("task", "").strip()
    if task:
        TODOS.append(TodoItem(task))
    return redirect(url_for("index"))


@app.route("/toggle/<int:index>", methods=["POST"])
def toggle_done(index):
    if 0 <= index < len(TODOS):
        TODOS[index].done = not TODOS[index].done
    return redirect(url_for("index"))


@app.route("/delete/<int:index>", methods=["POST"])
def delete_todo(index):
    if 0 <= index < len(TODOS):
        TODOS.pop(index)
    return redirect(url_for("index"))


def run_flask():
    # Important: use_reloader=False pour ne pas lancer deux serveurs dans le thread
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


# -------------------------
#  Application Qt (frontend)
# -------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TodoList – Flask + QtWebEngine")
        self.resize(900, 700)

        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)

        # Charger le serveur Flask local
        self.view.load(QUrl("http://127.0.0.1:5000/"))


def main():
    # Lancer le serveur Flask dans un thread séparé
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Lancer l'application Qt
    app_qt = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app_qt.exec_())


if __name__ == "__main__":
    main()

