import sys
import threading


from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

import gradio as gr

def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)

demo = gr.Interface(
    fn=greet,
    inputs=["text", "slider"],
    outputs=["text"],
)


# -------------------------
def run_gradio():
    # Important: use_reloader=False pour ne pas lancer deux serveurs dans le thread
    demo.launch(server_name="127.0.0.1",server_port=5000)


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
    flask_thread = threading.Thread(target=run_gradio, daemon=True)
    flask_thread.start()

    # Lancer l'application Qt
    app_qt = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app_qt.exec_())


if __name__ == "__main__":
    main()

