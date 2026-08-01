import sys
import threading

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

from dash import Dash, html, dcc, Input, Output, State, ctx, ALL, no_update


# -------------------------
#  Frontend+Backend : Dash
# -------------------------

dash_app = Dash(__name__)
server = dash_app.server  # utile si tu veux brancher autre chose plus tard

dash_app.layout = html.Div(
    style={"fontFamily": "sans-serif", "margin": "2rem"},
    children=[
        html.H1("TodoList – Dash & QtWebEngine", style={"marginBottom": "1rem"}),

        html.Div(
            style={"marginBottom": "1rem"},
            children=[
                dcc.Input(
                    id="task-input",
                    type="text",
                    placeholder="Nouvelle tâche...",
                    style={"padding": "0.4rem", "width": "250px"},
                ),
                html.Button(
                    "Ajouter",
                    id="add-btn",
                    n_clicks=0,
                    style={"padding": "0.4rem 0.8rem", "cursor": "pointer", "marginLeft": "0.5rem"},
                ),
            ],
        ),

        # Stockage en mémoire (dans le navigateur) : remplace la liste globale FastAPI
        dcc.Store(id="todos-store", data=[]),

        html.Div(id="todos-view"),
    ],
)


def render_todos(todos):
    if not todos:
        return html.P("Aucune tâche pour le moment.")

    items = []
    for i, t in enumerate(todos):
        done = bool(t.get("done"))
        text = t.get("text", "")

        items.append(
            html.Li(
                style={"marginBottom": "0.3rem"},
                children=[
                    html.Button(
                        "☑" if done else "☐",
                        id={"type": "toggle-btn", "index": i},
                        n_clicks=0,
                        style={"padding": "0.15rem 0.5rem", "cursor": "pointer"},
                        title="Terminer / Ré-ouvrir",
                    ),
                    html.Span(
                        text,
                        style={
                            "marginLeft": "0.6rem",
                            "textDecoration": "line-through" if done else "none",
                            "color": "#777" if done else "inherit",
                        },
                    ),
                    html.Button(
                        "🗑",
                        id={"type": "delete-btn", "index": i},
                        n_clicks=0,
                        style={"padding": "0.15rem 0.5rem", "cursor": "pointer", "marginLeft": "0.6rem"},
                        title="Supprimer",
                    ),
                ],
            )
        )

    return html.Ul(items, style={"listStyle": "none", "paddingLeft": 0})


@dash_app.callback(
    Output("todos-store", "data"),
    Output("task-input", "value"),
    Input("add-btn", "n_clicks"),
    Input({"type": "toggle-btn", "index": ALL}, "n_clicks"),
    Input({"type": "delete-btn", "index": ALL}, "n_clicks"),
    State("task-input", "value"),
    State("todos-store", "data"),
    prevent_initial_call=True,
)
def mutate_todos(add_clicks, toggle_clicks, delete_clicks, task_value, todos):
    # todos est une liste de dicts: [{"text": "...", "done": bool}, ...]
    todos = list(todos or [])

    trig = ctx.triggered_id

    # Ajout
    if trig == "add-btn":
        task = (task_value or "").strip()
        if task:
            todos.append({"text": task, "done": False})
            return todos, ""  # clear input
        return no_update, no_update

    # Toggle
    if isinstance(trig, dict) and trig.get("type") == "toggle-btn":
        i = trig.get("index")
        if isinstance(i, int) and 0 <= i < len(todos):
            todos[i]["done"] = not bool(todos[i].get("done"))
            return todos, no_update
        return no_update, no_update

    # Delete
    if isinstance(trig, dict) and trig.get("type") == "delete-btn":
        i = trig.get("index")
        if isinstance(i, int) and 0 <= i < len(todos):
            todos.pop(i)
            return todos, no_update
        return no_update, no_update

    return no_update, no_update


@dash_app.callback(
    Output("todos-view", "children"),
    Input("todos-store", "data"),
)
def update_view(todos):
    return render_todos(todos or [])


def run_dash():
    # Note: debug=False sinon ça spawn un reloader (2 process) -> callbacks bizarres
    dash_app.run(host="127.0.0.1", port=8000, debug=False)


# -------------------------
#  Frontend : Qt + QWebEngine
# -------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TodoList – Dash + QtWebEngine")
        self.resize(900, 700)

        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)

        self.view.load(QUrl("http://127.0.0.1:8000/"))


def main():
    # Lancer Dash dans un thread séparé
    web_thread = threading.Thread(target=run_dash, daemon=True)
    web_thread.start()

    # Lancer l'application Qt
    app_qt = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app_qt.exec_())


if __name__ == "__main__":
    main()

