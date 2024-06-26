# Monitor-PC-Win11

## Overview
Monitor-PC-Win11 is a lightweight application for real-time system resource monitoring for Windows 11. The program displays important parameters such as CPU load, memory usage, and disk space. Additional information such as IP address and cryptocurrency prices can also be displayed. The application is developed in Python using PyQt5 for the interface and asyncio for asynchronous operation.

## Features
- **System Resource Monitoring:** Displays CPU load, memory usage, and disk space in real-time.
- **Additional Information:** Option to display public IP address and cryptocurrency prices (BTC, ETH, SOL, TON).
- **Lightweight and Unobtrusive:** The application occupies minimal space on the desktop and has a transparent background.
- **Asynchronous Updates:** Uses asyncio for non-blocking updates of system parameters and additional information.
- **Customizable Interface:** Switch between system and additional information by clicking the icon.

## Screenshots
![Application Interface](https://github.com/xxspell/monitor-pc-win11/assets/74972395/fcfedec7-780d-48fc-9359-9e7b6b40ea4b)
![Application Interface](https://github.com/xxspell/monitor-pc-win11/assets/74972395/03ffb25e-f675-42f4-b7dd-97c75c24e5d8)
![Application Interface](https://github.com/xxspell/monitor-pc-win11/assets/74972395/78832b7d-8f1b-4cd8-9543-e7674d4145c4)

## Installation
### Requirements
- Python 3.10 or higher
- Poetry (for dependency management)

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/xxspell/monitor-pc-win11.git
   cd monitor-pc-win11
   ```

2. Set up a virtual environment and install dependencies:
   ```sh
   poetry install
   ```

3. Run the application:
   ```sh
   poetry run python main.py
   ```

## Usage
- The application will start and display system parameters in a small window on the desktop.
- Click the icon to switch between system and additional information (IP address and cryptocurrency prices).

## Configuration
### Logging
- Logs are written to the `app.log` file with detailed debug information.
- You can change the logging settings in the `main.py` file if needed.

### Icon and Styles
- The program uses `icon.svg` to display the icon in the interface. You can replace this file with your preferred icon.
- Styles for labels and other interface elements are configured using the PyQt5 `stylesheet` function. Modify the style strings in `main.py` to customize the appearance.

---

This README will help you quickly get started with the project and configure it to your needs.
