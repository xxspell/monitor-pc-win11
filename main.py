from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtSvg import QSvgWidget
import psutil
import time
import threading
import signal
import sys
import subprocess


class BaseWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)


class CustomWidget(BaseWidget):
    def __init__(self):
        super().__init__()

        self.svg_widget = QSvgWidget(
            "icon.svg", self
        )  # Замените 'icon.svg' на путь к вашему SVG-изображению
        self.svg_widget.setGeometry(
            10, 13, 25, 25
        )  # Установите размер и позицию изображения
        self.svg_widget.setStyleSheet("color: white;")

        # Создаем метку для отображения информации
        self.info_label = QLabel(self)
        self.info_label.setGeometry(35, 10, 264, 28)
        font = QFont("Calibri", 10)
        self.info_label.setStyleSheet("color: white;")
        self.info_label.setFont(font)
        # Обновляем информацию при создании виджета
        self.update_thread = threading.Thread(
            target=self.update_info_thread, daemon=True
        )
        self.update_thread.start()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Отрисовываем фон
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

        # # Рисуем иконку слева от текста
        # icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        # icon_pixmap = QPixmap(icon_path)
        # icon_rect = QRect(10, 10, 16, 16)  # Размер и позиция иконки
        # painter.drawPixmap(icon_rect, icon_pixmap)

    def update_info_thread(self):
        while True:
            while True:
                try:
                    result = subprocess.run(
                        ["wmic", "cpu", "get", "loadpercentage"],
                        capture_output=True,
                        text=True,
                    )
                    output_lines = result.stdout.strip().split("\n")

                    # Пропустить первую строку с заголовком "LoadPercentage"
                    load_percentage_line = (
                        output_lines[-1] if len(output_lines) > 1 else "0"
                    )

                    load_percentage = load_percentage_line.strip()
                    load_percentage = float(load_percentage)
                    break
                except Exception as e:
                    print(f"Произошла ошибка: {e}")

            # cpu_percent = psutil.cpu_percent(interval=1)
            # cpu_percent = get_cpu_usage()
            ram_info = psutil.virtual_memory()
            disk_info_c = psutil.disk_usage("C:")
            disk_info_d = psutil.disk_usage("D:")

            info_text = (
                f"CPU: {load_percentage}% | "
                f"RAM: {self.format_size_ram(ram_info.used)} / {self.format_size_ram(ram_info.total)}\n"
                f"C: {self.format_size(disk_info_c.used)} / {self.format_size(disk_info_c.total)} | "
                f"D: {self.format_size(disk_info_d.used)} / {self.format_size(disk_info_d.total)}"
            )
            # print(info_text)

            # Используем метод self.update() для обновления интерфейса в основном потоке
            self.update_label(info_text)
            time.sleep(2)

    def update_label(self, text):
        # Используем метод self.update() для обновления интерфейса в основном потоке
        self.info_label.setText(text)
        self.update()

    def format_size(self, size):
        gb_size = size / (1024**3)  # Перевести в GB
        return f"{gb_size:.0f} GB"

    def format_size_ram(self, size):
        gb_size = size / (1024**3)  # Перевести в GB
        return f"{gb_size:.2f} GB"


def handle_ctrl_c(signum, frame):
    sys.exit()


if __name__ == "__main__":
    app = QApplication([])

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
        # | Qt.SplashScreen
        | Qt.WindowDoesNotAcceptFocus
        | Qt.Tool
    )

    signal.signal(signal.SIGINT, handle_ctrl_c)

    window.show()

    app.exec()
