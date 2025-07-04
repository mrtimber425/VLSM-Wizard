import sys
import ipaddress
import random
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QTabWidget, QMessageBox, QHBoxLayout,
    QScrollArea, QFrame, QTextEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class SubnetCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professional Subnet Calculator")
        self.setMinimumSize(1200, 700)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { height: 30px; width: 150px; font-weight: bold; }")
        self.tabs.addTab(self.create_ip_tools_tab(), "IP Tools")
        self.tabs.addTab(self.create_vlsm_tab(), "VLSM Setup")
        self.tabs.addTab(self.create_result_tab(), "VLSM Results")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_ip_tools_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        header = QLabel("IP Conversion and Validation")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)

        self.dec_input = QLineEdit()
        self.bin_input = QLineEdit()

        layout.addWidget(QLabel("Decimal IP:"))
        layout.addWidget(self.dec_input)
        layout.addWidget(QLabel("Binary IP:"))
        layout.addWidget(self.bin_input)

        dec_to_bin_btn = QPushButton("Decimal to Binary")
        bin_to_dec_btn = QPushButton("Binary to Decimal")

        dec_to_bin_btn.clicked.connect(self.dec_to_bin)
        bin_to_dec_btn.clicked.connect(self.bin_to_dec)

        layout.addWidget(dec_to_bin_btn)
        layout.addWidget(bin_to_dec_btn)

        self.validator_input = QLineEdit()
        self.validator_result = QLineEdit()
        self.validator_result.setReadOnly(True)

        validate_btn = QPushButton("Validate IP")
        validate_btn.clicked.connect(self.validate_ip)

        layout.addWidget(QLabel("IP Address to Validate:"))
        layout.addWidget(self.validator_input)
        layout.addWidget(validate_btn)
        layout.addWidget(QLabel("Validation Result:"))
        layout.addWidget(self.validator_result)

        tab.setLayout(layout)
        return tab

    def create_vlsm_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.network_input = QLineEdit()
        layout.addWidget(QLabel("Base Network (e.g. 192.168.1.0/24):"))
        layout.addWidget(self.network_input)

        self.subnet_host_inputs = []
        self.subnet_count_input = QLineEdit()
        layout.addWidget(QLabel("Number of Subnets:"))
        layout.addWidget(self.subnet_count_input)

        gen_fields_btn = QPushButton("Generate Subnet Fields")
        gen_fields_btn.clicked.connect(self.generate_subnet_fields)
        layout.addWidget(gen_fields_btn)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_container = QWidget()
        self.subnet_host_layout = QVBoxLayout(scroll_container)
        scroll_area.setWidget(scroll_container)
        layout.addWidget(scroll_area)

        calc_btn = QPushButton("Calculate VLSM")
        calc_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        calc_btn.clicked.connect(self.calculate_vlsm_accurate)
        layout.addWidget(calc_btn)

        tab.setLayout(layout)
        return tab

    def create_result_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.result_table = QTableWidget()
        layout.addWidget(self.result_table)

        layout.addWidget(QLabel("Available IPs in Each Subnet:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search IP or Subnet name...")
        self.filter_input.textChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_input)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        layout.addWidget(self.detail_text)

        tab.setLayout(layout)
        return tab

    def apply_filter(self):
        query = self.filter_input.text().strip().lower()
        filtered = "\n".join([line for line in self.full_ip_details.splitlines() if query in line.lower()])
        self.detail_text.setPlainText(filtered)

    def generate_subnet_fields(self):
        count = self.subnet_count_input.text().strip()
        if not count.isdigit():
            QMessageBox.warning(self, "Error", "Invalid subnet count")
            return

        self.subnet_host_inputs.clear()
        while self.subnet_host_layout.count():
            child = self.subnet_host_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for i in range(int(count)):
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Host count for Subnet {i+1}")
            self.subnet_host_layout.addWidget(input_field)
            self.subnet_host_inputs.append(input_field)

    def calculate_min_prefix(self, host_count):
        for prefix in range(32, 0, -1):
            if (2 ** (32 - prefix)) >= (host_count + 2):
                return prefix
        raise ValueError("Cannot assign subnet for host count")

    def calculate_vlsm_accurate(self):
        try:
            base = self.network_input.text().strip()
            subnet_reqs = []
            for idx, input_field in enumerate(self.subnet_host_inputs):
                val = input_field.text().strip()
                if not val.isdigit():
                    raise ValueError(f"Subnet {idx+1} has invalid host count")
                subnet_reqs.append((f"Subnet {idx+1}", int(val)))

            net = ipaddress.IPv4Network(base, strict=False)
            current = net.network_address

            # Sort by host count descending for optimal assignment
            subnet_reqs.sort(key=lambda x: x[1], reverse=True)

            self.result_table.setColumnCount(6)
            self.result_table.setHorizontalHeaderLabels([
                "Subnet", "Network Address", "Subnet Mask", "First Host", "Last Host", "Broadcast"])

            results = []
            details = ""
            for name, hosts in subnet_reqs:
                prefix = self.calculate_min_prefix(hosts)
                subnet = ipaddress.IPv4Network((current, prefix), strict=False)
                first = subnet.network_address + 1
                last = subnet.broadcast_address - 1
                results.append([
                    name,
                    f"{subnet.network_address}/{prefix}",
                    str(subnet.netmask),
                    str(first),
                    str(last),
                    str(subnet.broadcast_address)
                ])
                ip_list = list(subnet.hosts())
                details += f"{name} ({subnet.network_address}/{prefix}):\n"
                for ip in ip_list:
                    details += f"  {ip}\n"
                details += "\n"
                current = subnet.broadcast_address + 1

            self.result_table.setRowCount(len(results))
            for row_idx, row in enumerate(results):
                for col_idx, val in enumerate(row):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(val))

            self.full_ip_details = details
            self.detail_text.setPlainText(details)
            self.tabs.setCurrentIndex(2)

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def dec_to_bin(self):
        try:
            ip = self.dec_input.text().strip()
            binary = '.'.join([format(int(x), '08b') for x in ip.split('.')])
            self.bin_input.setText(binary)
        except:
            QMessageBox.warning(self, "Error", "Invalid Decimal IP")

    def bin_to_dec(self):
        try:
            binary = self.bin_input.text().strip()
            decimal = '.'.join([str(int(b, 2)) for b in binary.split('.')])
            self.dec_input.setText(decimal)
        except:
            QMessageBox.warning(self, "Error", "Invalid Binary IP")

    def validate_ip(self):
        ip = self.validator_input.text().strip()
        try:
            ipaddress.ip_address(ip)
            self.validator_result.setText("Valid")
        except:
            self.validator_result.setText("Invalid")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = SubnetCalculator()
    win.show()
    sys.exit(app.exec_())
