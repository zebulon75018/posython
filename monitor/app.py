import sys
import threading


from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView



from flask import Flask,abort, render_template, jsonify
import psutil
import platform
from datetime import datetime

import random
import string

def random_alphanum(longueur: int = 12) -> str:
    """Génère une chaîne alphanumérique aléatoire (lettres + chiffres)"""
    caracteres = string.ascii_letters + string.digits  # a-z A-Z 0-9
    return ''.join(random.choice(caracteres) for _ in range(longueur))


app = Flask(__name__)

SECRET_KEY = random_alphanum(16)
PORT = 5012


def get_cpu_info():
    """Récupère les informations CPU"""
    return {
        'percent': psutil.cpu_percent(interval=1),
        'count': psutil.cpu_count(),
        'freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
        'per_cpu': psutil.cpu_percent(interval=1, percpu=True)
    }

def get_memory_info():
    """Récupère les informations mémoire"""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        'total': mem.total / (1024**3),  # GB
        'available': mem.available / (1024**3),
        'used': mem.used / (1024**3),
        'percent': mem.percent,
        'swap_total': swap.total / (1024**3),
        'swap_used': swap.used / (1024**3),
        'swap_percent': swap.percent
    }

def get_disk_info():
    """Récupère les informations disque"""
    partitions = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            partitions.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total': usage.total / (1024**3),
                'used': usage.used / (1024**3),
                'free': usage.free / (1024**3),
                'percent': usage.percent
            })
        except PermissionError:
            continue
    return partitions

def get_network_info():
    """Récupère les informations réseau"""
    net_io = psutil.net_io_counters()
    return {
        'bytes_sent': net_io.bytes_sent / (1024**2),  # MB
        'bytes_recv': net_io.bytes_recv / (1024**2),
        'packets_sent': net_io.packets_sent,
        'packets_recv': net_io.packets_recv
    }

def get_load_average():
    """Récupère le load average"""
    try:
        load = psutil.getloadavg()
        return {
            'load1': load[0],
            'load5': load[1],
            'load15': load[2]
        }
    except AttributeError:
        # Windows n'a pas getloadavg
        return {
            'load1': 0,
            'load5': 0,
            'load15': 0
        }

def get_system_info():
    """Récupère les informations système"""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    return {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'hostname': platform.node(),
        'processor': platform.processor(),
        'boot_time': boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        'uptime': str(uptime).split('.')[0]
    }

@app.route('/<key>')
def index(key):
    """Page principale du dashboard"""
    if key!=SECRET_KEY:
        return abort(403)
    return render_template('dashboard.html',key=SECRET_KEY)

@app.route('/api/metrics/')
def get_metrics():
    """API pour récupérer toutes les métriques"""
    return jsonify({
        'cpu': get_cpu_info(),
        'memory': get_memory_info(),
        'disk': get_disk_info(),
        'network': get_network_info(),
        'load': get_load_average(),
        'system': get_system_info(),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route('/api/cpu')
def get_cpu():
    return jsonify(get_cpu_info())

@app.route('/api/memory')
def get_memory():
    return jsonify(get_memory_info())

@app.route('/api/load')
def get_load():
    return jsonify(get_load_average())


def run_flask():
    # Important: use_reloader=False pour ne pas lancer deux serveurs dans le thread
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)

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

    def load(self, port, secretkey):
        # Charger le serveur Flask local
        self.view.load(QUrl(f"http://127.0.0.1:{port}/{secretkey}"))

def main():
    # Lancer le serveur Flask dans un thread séparé
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    #"   posython.run()

    # Lancer l'application Qt
    app_qt = QApplication(sys.argv)
    window = MainWindow()
    window.load(PORT,SECRET_KEY)
    window.show()
    sys.exit(app_qt.exec_())

if __name__ == "__main__":
    main()

