import sys
import threading

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from jinja2 import Environment, BaseLoader

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


# -------------------------
#  Backend : FastAPI
# -------------------------

app = FastAPI()

# Todo-list en mémoire
class TodoItem:
    def __init__(self, text, done=False):
        self.text = text
        self.done = done

TODOS = []

HTML_TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>TodoList FastAPI + QtWebEngine</title>
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
    <h1>TodoList – FastAPI &amp; QtWebEngine</h1>

    <form method="post" action="/add">
        <input type="text" name="task" placeholder="Nouvelle tâche..." required>
        <button type="submit">Ajouter</button>
    </form>

    {% if todos %}
        <ul>
        {% for todo in todos %}
            {% set i = loop.index0 %}
            <li>
                <form style="display:inline;" method="post" action="/toggle/{{ i }}">
                    <button type="submit">
                        {% if todo.done %}☑{% else %}☐{% endif %}
                    </button>
                </form>
                <span class="{{ 'done' if todo.done else '' }}">{{ todo.text }}</span>
                <form style="display:inline;" method="post" action="/delete/{{ i }}">
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

# Jinja2 "à la main" avec un template en string
jinja_env = Environment(loader=BaseLoader())
template = jinja_env.from_string(HTML_TEMPLATE)


@app.get("/", response_class=HTMLResponse)
async def index():
    # Rendu du template avec la liste des todos
    return template.render(todos=TODOS)


@app.post("/add")
async def add_todo(task: str = Form(...)):
    task = task.strip()
    if task:
        TODOS.append(TodoItem(task))
    # Redirection vers la page principale (303 = "See Other" après un POST)
    return RedirectResponse(url="/", status_code=303)


@app.post("/toggle/{index}")
async def toggle_done(index: int):
    if 0 <= index < len(TODOS):
        TODOS[index].done = not TODOS[index].done
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{index}")
async def delete_todo(index: int):
    if 0 <= index < len(TODOS):
        TODOS.pop(index)
    return RedirectResponse(url="/", status_code=303)


def run_fastapi():
    import uvicorn
    # Lancement du serveur FastAPI dans ce thread
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


# -------------------------
#  Frontend : Qt + QWebEngine
# -------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TodoList – FastAPI + QtWebEngine")
        self.resize(900, 700)

        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)

        # Charger le serveur FastAPI local
        self.view.load(QUrl("http://127.0.0.1:8000/"))


def main():
    # Lancer FastAPI dans un thread séparé
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()

    # Lancer l'application Qt
    app_qt = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app_qt.exec_())


if __name__ == "__main__":
    main()

