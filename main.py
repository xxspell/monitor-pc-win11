import asyncio
import psutil
import logging
from concurrent.futures import ThreadPoolExecutor
from asyncqt import QEventLoop, asyncSlot
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QRect, QTimer, QEvent
from PyQt5.QtSvg import QSvgWidget
import signal
import sys
import requests

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")


class BaseWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)


class CustomWidget(BaseWidget):
    def __init__(self):
        super().__init__()

        self.svg_widget = QSvgWidget("icon.svg", self)
        self.svg_widget.setGeometry(10, 13, 25, 25)
        self.svg_widget.setStyleSheet("color: white;")
        self.svg_widget.installEventFilter(self)

        self.info_label = QLabel(self)
        self.info_label.setGeometry(35, 10, 264, 28)
        font = QFont("Calibri", 10)
        self.info_label.setStyleSheet("color: white;")
        self.info_label.setFont(font)

        self.show_system_info = True
        self.loading = False
        self.alternate_flag = True

        self.ip_info = "Loading..."
        self.crypto_info = {"BTC": "...", "ETH": "...", "SOL": "...", "TON": "..."}

        logging.debug("Initializing event loop")
        loop = asyncio.get_event_loop()
        logging.debug("Creating initial task for update_initial_info")
        loop.create_task(self.update_initial_info())

        logging.debug("Setting up timers")
        self.system_timer = QTimer(self)
        self.system_timer.timeout.connect(self.update_system_info)
        self.system_timer.start(1000)  # обновление каждую секунду

        self.additional_timer = QTimer(self)
        self.additional_timer.timeout.connect(
            lambda: asyncio.ensure_future(self.update_additional_info())
        )
        self.additional_timer.start(600000)  # обновление каждые 10 минут

        self.executor = ThreadPoolExecutor(max_workers=5)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.setPen(QColor(255, 255, 255, 0))
        painter.setBrush(QColor(28, 28, 28))
        x = 4
        y = 4
        width = 263
        height = 42
        radius = 10
        painter.drawRoundedRect(QRect(x, y, width, height), radius, radius)

    def eventFilter(self, source, event):
        if source == self.svg_widget and event.type() == QEvent.MouseButtonPress:
            logging.debug("Icon clicked")
            self.on_icon_click()
        return super().eventFilter(source, event)

    async def update_initial_info(self):
        logging.debug("Starting initial update of additional info")
        await self.update_additional_info()
        self.show_system_info = True
        logging.debug(
            "Initial update of additional info complete, updating system info"
        )
        self.update_system_info()

    @asyncSlot()
    async def update_system_info(self):
        if self.show_system_info:
            logging.debug("Updating system info")
            cpu_percent = psutil.cpu_percent(interval=1)
            ram_info = psutil.virtual_memory()
            disk_info_c = psutil.disk_usage("C:")
            disk_info_d = psutil.disk_usage("D:")

            info_text = (
                f"CPU: {self.format_percentage(cpu_percent)} | "
                f"RAM: {self.format_size_ram(ram_info.used)} / {self.format_size_ram(ram_info.total)}\n"
                f"C: {self.format_size(disk_info_c.used)} / {self.format_size(disk_info_c.total)} | "
                f"D: {self.format_size(disk_info_d.used)} / {self.format_size(disk_info_d.total)}"
            )
            self.update_label(info_text)

    async def update_additional_info(self):
        logging.debug("Updating additional info (IP and crypto prices)")
        loop = asyncio.get_event_loop()
        ip_info = await loop.run_in_executor(self.executor, self.fetch_ip_info)
        crypto_info = await loop.run_in_executor(self.executor, self.fetch_crypto_info)
        self.ip_info = ip_info
        self.crypto_info = crypto_info
        if not self.show_system_info:
            logging.debug("System info not shown, displaying additional info")
            self.show_additional_info()

    def update_label(self, text):
        logging.debug(f"Updating label with text: {text}")
        self.info_label.setText(text)
        self.update()

    def format_percentage(self, value):
        return f"{value:.0f}%"

    def format_size(self, size):
        gb_size = size / (1024**3)
        return f"{gb_size:.0f} GB"

    def format_size_ram(self, size):
        gb_size = size / (1024**3)
        return f"{gb_size:.2f} GB"

    def on_icon_click(self):
        self.show_system_info = not self.show_system_info
        logging.info(
            f"Icon click detected. Switching to {'system info' if self.show_system_info else 'additional info'} view."
        )
        if self.show_system_info:
            logging.debug("Starting system info timer")
            self.system_timer.start(1000)  # обновление каждую секунду
            self.additional_timer.start(600000)  # обновление каждые 10 минут
        else:
            logging.debug(
                "Stopping system info timer and starting additional info timer"
            )
            self.system_timer.stop()
            self.additional_timer.start(60000)  # обновление каждую минуту
            self.show_additional_info()
            asyncio.ensure_future(self.update_additional_info())

    def show_additional_info(self):
        logging.debug("Displaying additional info")
        ip_info = self.ip_info
        crypto_info = self.crypto_info
        if self.alternate_flag:
            info_text = (
                f"IP: {ip_info} | BTC: ${crypto_info.get('BTC', 'N/A')}\n"
                f"ETH: ${crypto_info.get('ETH', 'N/A')} | SOL: ${crypto_info.get('SOL', 'N/A')}"
            )
        else:
            info_text = (
                f"IP: {ip_info} | BTC: ${crypto_info.get('BTC', 'N/A')}\n"
                f"ETH: ${crypto_info.get('ETH', 'N/A')} | TON: ${crypto_info.get('TON', 'N/A')}"
            )
        self.alternate_flag = not self.alternate_flag
        self.update_label(info_text)

    def fetch_ip_info(self):
        try:
            logging.debug("Fetching IP info")
            response = requests.get(
                "https://proxy-checker-new.dolphin-anty-mirror.org/ip-info"
            )
            response.raise_for_status()
            ip_data = response.json()
            logging.info("Fetched IP info successfully.")
            return ip_data.get("ip", "Unknown")
        except Exception as e:
            logging.error(f"Error fetching IP info: {e}")
            return "Error"

    def fetch_crypto_info(self):
        try:
            logging.debug("Fetching crypto prices")
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,the-open-network&vs_currencies=usd"
            )
            response.raise_for_status()
            prices = response.json()
            logging.info("Fetched crypto prices successfully.")
            return {
                "BTC": prices.get("bitcoin", {}).get("usd", "N/A"),
                "ETH": prices.get("ethereum", {}).get("usd", "N/A"),
                "SOL": prices.get("solana", {}).get("usd", "N/A"),
                "TON": prices.get("the-open-network", {}).get("usd", "N/A"),
            }
        except Exception as e:
            logging.error(f"Error fetching crypto prices: {e}")
            return {}


def handle_ctrl_c(signum, frame):
    logging.info("Program interrupted. Exiting...")
    sys.exit()


if __name__ == "__main__":
    app = QApplication([])

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    desktop = QApplication.desktop()
    desktop_rect = desktop.availableGeometry()
    desktop_width = desktop_rect.width()
    desktop_height = desktop_rect.height()

    window = CustomWidget()

    window.setAttribute(Qt.WA_TranslucentBackground)
    window.setGeometry(0, 0, 496, 48)
    window.move(QApplication.desktop().availableGeometry().bottomLeft())
    window.setWindowFlags(
        Qt.FramelessWindowHint
        | Qt.WindowStaysOnTopHint
        | Qt.X11BypassWindowManagerHint
        | Qt.WindowDoesNotAcceptFocus
        | Qt.Tool
    )

    signal.signal(signal.SIGINT, handle_ctrl_c)

    window.show()

    logging.info("Application started.")
    with loop:
        loop.run_forever()
