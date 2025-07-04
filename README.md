# VLSM-Wizard
Subnet Calculator
This is a cross-platform, GUI-based subnet calculator built with PyQt5. It supports decimal/binary IP conversion, validation, and fully optimized VLSM (Variable Length Subnet Mask) allocation. Designed to be accurate, interactive, and educational.

---

## Features

- **IP Tools Tab**
  - Decimal ⇄ Binary IP conversion
  - IP address validator

- **VLSM Setup**
  - Enter base network (e.g., `192.168.1.0/24`)
  - Define host count for each subnet
  - Click "Calculate Optimal VLSM" for an accurate, waste-free allocation

- **VLSM Results**
  - Subnet summary table (name, range, mask, etc.)
  - Full IP list for each subnet (usable IPs)
  - Live filter/search box to find any IP or subnet

---

## Project Structure

```

subnet-calculator/
├── subnet\_calculator.py         # Main application
├── launch.bat                   # Windows launcher
├── launch.sh                    # macOS/Linux launcher
└── README.md                    

````

---

## Setup & Launch

### Windows

> double-click `launch.bat` – it will:
> - Create a virtual environment
> - Install dependencies
> - Launch the app

If you want to run manually:

```bat
python -m venv venv
call venv\Scripts\activate
pip install pyqt5 numpy
python subnet_calculator.py
````

---

### macOS/Linux

Make sure Python 3 is installed:

```bash
chmod +x launch.sh
./launch.sh
```

Or run manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install pyqt5 numpy
python subnet_calculator.py
```

---

## Requirements

* Python 3.7+
* Packages:

  * `PyQt5`
  * `numpy`

You do **not** need to install them manually if using the launcher.

