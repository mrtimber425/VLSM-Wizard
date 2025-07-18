import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ipaddress
import matplotlib.pyplot as plt
import networkx as nx
import csv
import pandas as pd
import os
import json
import subprocess
import threading
import socket
import struct
import random
from datetime import datetime
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import time

# AI Integration imports (install: pip install transformers torch)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("AI features disabled. Install transformers: pip install transformers torch")


class AdvancedNetworkCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Network Calculator v2.0")
        self.root.geometry("1400x900")

        # AI Model Management
        self.ai_model = None
        self.ai_tokenizer = None
        self.current_model_path = None

        # Data storage
        self.projects = {}
        self.network_data = {}
        self.scan_results = {}

        self.setup_styles()
        self.create_menu()
        self.create_main_interface()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.dark_mode = False

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Export Documentation", command=self.export_documentation)

        # AI Menu
        ai_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="AI", menu=ai_menu)
        ai_menu.add_command(label="Load Model", command=self.load_ai_model)
        ai_menu.add_command(label="Model Info", command=self.show_model_info)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)

    def create_main_interface(self):
        self.notebook = ttk.Notebook(self.root)

        # Create all tabs
        self.create_enhanced_vlsm_tab()
        self.create_ipv6_tab()
        self.create_network_tools_tab()
        self.create_scanning_tab()
        self.create_practice_tab()
        self.create_vlan_tab()
        self.create_topology_tab()
        self.create_ai_troubleshoot_tab()
        self.create_cli_advanced_tab()

        self.notebook.pack(expand=1, fill="both", padx=5, pady=5)

    def create_enhanced_vlsm_tab(self):
        """Enhanced VLSM with utilization analysis and overlap detection"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="VLSM")  # Changed tab name to "VLSM"

        main_frame = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Input Panel
        input_frame = ttk.Frame(main_frame)
        main_frame.add(input_frame, weight=1)

        ttk.Label(input_frame, text="Base Network:").pack(anchor="w")
        self.vlsm_network_entry = ttk.Entry(input_frame)
        self.vlsm_network_entry.pack(fill="x", pady=(0, 10))

        # New: Number of Subnets Input
        ttk.Label(input_frame, text="Number of Subnets Needed:").pack(anchor="w")
        self.num_subnets_entry = ttk.Entry(input_frame, width=10)
        self.num_subnets_entry.pack(fill="x", pady=(0, 5))
        ttk.Button(input_frame, text="Generate Subnet Fields",
                   command=self.generate_subnet_fields).pack(anchor="w", pady=(0, 10))

        # Frame to hold dynamically generated subnet requirement entries
        self.subnet_requirements_frame = ttk.Frame(input_frame)
        self.subnet_requirements_frame.pack(fill="x", pady=(0, 10))

        self.subnet_entries = [] # This will be populated dynamically

        # Buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Calculate VLSM",
                   command=self.calculate_enhanced_vlsm).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Check Overlaps",
                   command=self.check_overlaps).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Optimize",
                   command=self.optimize_subnets).pack(side="left", padx=5)

        # Results Panel
        result_frame = ttk.Frame(main_frame)
        main_frame.add(result_frame, weight=2)

        # Results tree
        self.vlsm_tree = ttk.Treeview(result_frame, columns=(
            "Network", "Mask", "Hosts", "Used", "Efficiency", "First", "Last", "Broadcast"
        ), show="headings")

        for col in self.vlsm_tree["columns"]:
            self.vlsm_tree.heading(col, text=col)
            self.vlsm_tree.column(col, width=90)

        # Scrollbars
        v_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.vlsm_tree.yview)
        h_scroll = ttk.Scrollbar(result_frame, orient="horizontal", command=self.vlsm_tree.xview)
        self.vlsm_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.vlsm_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        # Utilization chart
        self.create_utilization_chart(result_frame)

    def generate_subnet_fields(self):
        """Dynamically generates subnet requirement input fields based on user input."""
        # Clear existing fields
        for widget in self.subnet_requirements_frame.winfo_children():
            widget.destroy()
        self.subnet_entries = []

        try:
            num_subnets = int(self.num_subnets_entry.get())
            if num_subnets <= 0:
                messagebox.showwarning("Invalid Input", "Please enter a positive number of subnets.")
                return
            if num_subnets > 50: # Set a reasonable limit to prevent UI issues
                messagebox.showwarning("Too Many Subnets", "Please enter a number up to 50 for performance reasons.")
                num_subnets = 50

            ttk.Label(self.subnet_requirements_frame, text="Subnet Requirements:").grid(row=0, column=0, columnspan=3, sticky="w", pady=(5,0))
            ttk.Label(self.subnet_requirements_frame, text="Name").grid(row=1, column=0, padx=5)
            ttk.Label(self.subnet_requirements_frame, text="Hosts").grid(row=1, column=1, padx=5)
            ttk.Label(self.subnet_requirements_frame, text="Priority").grid(row=1, column=2, padx=5)

            for i in range(num_subnets):
                name_entry = ttk.Entry(self.subnet_requirements_frame, width=15)
                name_entry.grid(row=i + 2, column=0, padx=2, pady=1)

                hosts_entry = ttk.Entry(self.subnet_requirements_frame, width=10)
                hosts_entry.grid(row=i + 2, column=1, padx=2, pady=1)

                priority_var = tk.StringVar(value="Normal")
                priority_combo = ttk.Combobox(self.subnet_requirements_frame, textvariable=priority_var,
                                              values=["High", "Normal", "Low"], width=8)
                priority_combo.grid(row=i + 2, column=2, padx=2, pady=1)

                self.subnet_entries.append((name_entry, hosts_entry, priority_var))

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for subnets.")


    def create_ipv6_tab(self):
        """IPv6 subnetting support"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🌐 IPv6 Tools")

        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill="both", expand=True)

        # IPv6 Network Input
        ttk.Label(frame, text="IPv6 Network (e.g., 2001:db8::/32):").pack(anchor="w")
        self.ipv6_network_entry = ttk.Entry(frame, width=50)
        self.ipv6_network_entry.pack(fill="x", pady=(0, 10))

        # Subnetting options
        options_frame = ttk.LabelFrame(frame, text="Subnetting Options")
        options_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(options_frame, text="New Prefix Length:").pack(anchor="w")
        self.ipv6_prefix_entry = ttk.Entry(options_frame, width=10)
        self.ipv6_prefix_entry.pack(anchor="w", pady=(0, 5))

        ttk.Label(options_frame, text="Number of Subnets:").pack(anchor="w")
        self.ipv6_subnet_count = ttk.Entry(options_frame, width=10)
        self.ipv6_subnet_count.pack(anchor="w", pady=(0, 5))

        ttk.Button(options_frame, text="Calculate IPv6 Subnets",
                   command=self.calculate_ipv6_subnets).pack(anchor="w", pady=5)

        # Results
        self.ipv6_tree = ttk.Treeview(frame, columns=(
            "Subnet", "Network", "Prefix", "Hosts"
        ), show="headings")

        for col in self.ipv6_tree["columns"]:
            self.ipv6_tree.heading(col, text=col)

        self.ipv6_tree.pack(fill="both", expand=True, pady=10)

    def create_network_tools_tab(self):
        """Network utilities and converters"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔧 Network Tools")

        notebook = ttk.Notebook(tab)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # CIDR Converter
        cidr_frame = ttk.Frame(notebook)
        notebook.add(cidr_frame, text="CIDR Converter")

        converter_frame = ttk.LabelFrame(cidr_frame, text="Subnet Mask Converter")
        converter_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(converter_frame, text="CIDR Notation (/24):").grid(row=0, column=0, sticky="w")
        self.cidr_entry = ttk.Entry(converter_frame)
        self.cidr_entry.grid(row=0, column=1, padx=5)

        ttk.Label(converter_frame, text="Subnet Mask:").grid(row=1, column=0, sticky="w")
        self.mask_entry = ttk.Entry(converter_frame)
        self.mask_entry.grid(row=1, column=1, padx=5)

        ttk.Button(converter_frame, text="CIDR → Mask",
                   command=self.cidr_to_mask).grid(row=0, column=2, padx=5)
        ttk.Button(converter_frame, text="Mask → CIDR",
                   command=self.mask_to_cidr).grid(row=1, column=2, padx=5)

        # Supernetting Calculator
        super_frame = ttk.LabelFrame(cidr_frame, text="Supernetting/Route Summarization")
        super_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(super_frame, text="Enter networks (one per line):").pack(anchor="w")
        self.supernet_text = tk.Text(super_frame, height=6)
        self.supernet_text.pack(fill="x", pady=5)

        ttk.Button(super_frame, text="Calculate Summary Route",
                   command=self.calculate_supernet).pack(anchor="w")

        self.supernet_result = tk.StringVar()
        ttk.Label(super_frame, textvariable=self.supernet_result,
                  foreground="blue").pack(anchor="w", pady=5)

        # Bandwidth Calculator
        bw_frame = ttk.Frame(notebook)
        notebook.add(bw_frame, text="Bandwidth Calculator")

        bw_calc_frame = ttk.LabelFrame(bw_frame, text="Bandwidth Converter")
        bw_calc_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(bw_calc_frame, text="Value:").grid(row=0, column=0)
        self.bw_value_entry = ttk.Entry(bw_calc_frame)
        self.bw_value_entry.grid(row=0, column=1, padx=5)

        ttk.Label(bw_calc_frame, text="From:").grid(row=0, column=2)
        self.bw_from = ttk.Combobox(bw_calc_frame, values=[
            "bps", "Kbps", "Mbps", "Gbps", "Tbps"
        ])
        self.bw_from.grid(row=0, column=3, padx=5)

        ttk.Label(bw_calc_frame, text="To:").grid(row=0, column=4)
        self.bw_to = ttk.Combobox(bw_calc_frame, values=[
            "bps", "Kbps", "Mbps", "Gbps", "Tbps"
        ])
        self.bw_to.grid(row=0, column=5, padx=5)

        ttk.Button(bw_calc_frame, text="Convert",
                   command=self.convert_bandwidth).grid(row=0, column=6, padx=5)

        self.bw_result = tk.StringVar()
        ttk.Label(bw_calc_frame, textvariable=self.bw_result,
                  foreground="blue").grid(row=1, column=0, columnspan=7, pady=5)

    def create_scanning_tab(self):
        """Network scanning tools"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔍 Network Scanner")

        main_frame = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Controls
        control_frame = ttk.Frame(main_frame)
        main_frame.add(control_frame, weight=1)

        # Ping Sweep
        ping_frame = ttk.LabelFrame(control_frame, text="Ping Sweep")
        ping_frame.pack(fill="x", pady=5)

        ttk.Label(ping_frame, text="Network Range:").pack(anchor="w")
        self.ping_range_entry = ttk.Entry(ping_frame)
        self.ping_range_entry.pack(fill="x", pady=2)
        self.ping_range_entry.insert(0, "192.168.1.0/24")

        ttk.Button(ping_frame, text="Start Ping Sweep",
                   command=self.start_ping_sweep).pack(anchor="w", pady=5)

        # Port Scanner
        port_frame = ttk.LabelFrame(control_frame, text="Port Scanner")
        port_frame.pack(fill="x", pady=5)

        ttk.Label(port_frame, text="Target IP:").pack(anchor="w")
        self.port_target_entry = ttk.Entry(port_frame)
        self.port_target_entry.pack(fill="x", pady=2)

        ttk.Label(port_frame, text="Port Range (e.g., 1-1000):").pack(anchor="w")
        self.port_range_entry = ttk.Entry(port_frame)
        self.port_range_entry.pack(fill="x", pady=2)
        self.port_range_entry.insert(0, "1-1000")

        ttk.Button(port_frame, text="Start Port Scan",
                   command=self.start_port_scan).pack(anchor="w", pady=5)

        # Results
        result_frame = ttk.Frame(main_frame)
        main_frame.add(result_frame, weight=2)

        self.scan_tree = ttk.Treeview(result_frame, columns=(
            "IP", "Status", "Ports", "Response Time"
        ), show="headings")

        for col in self.scan_tree["columns"]:
            self.scan_tree.heading(col, text=col)

        scroll_y = ttk.Scrollbar(result_frame, orient="vertical", command=self.scan_tree.yview)
        self.scan_tree.configure(yscrollcommand=scroll_y.set)

        self.scan_tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Progress bar
        self.scan_progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.scan_progress.pack(fill="x", pady=5)

    def create_practice_tab(self):
        """Subnetting practice mode"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📚 Practice Mode")

        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill="both", expand=True)

        # Difficulty selection
        diff_frame = ttk.LabelFrame(frame, text="Practice Settings")
        diff_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(diff_frame, text="Difficulty:").pack(anchor="w")
        self.practice_difficulty = tk.StringVar(value="Beginner")
        diff_combo = ttk.Combobox(diff_frame, textvariable=self.practice_difficulty,
                                  values=["Beginner", "Intermediate", "Advanced", "Expert"])
        diff_combo.pack(anchor="w", pady=2)

        ttk.Label(diff_frame, text="Question Type:").pack(anchor="w")
        self.practice_type = tk.StringVar(value="Subnetting")
        type_combo = ttk.Combobox(diff_frame, textvariable=self.practice_type,
                                  values=["Subnetting", "VLSM", "Supernetting", "Mixed"])
        type_combo.pack(anchor="w", pady=2)

        ttk.Button(diff_frame, text="Generate Question",
                   command=self.generate_practice_question).pack(anchor="w", pady=5)

        # Question display
        question_frame = ttk.LabelFrame(frame, text="Question")
        question_frame.pack(fill="x", pady=(0, 10))

        self.practice_question = tk.Text(question_frame, height=4, wrap="word")
        self.practice_question.pack(fill="x", pady=5)

        # Answer input
        answer_frame = ttk.LabelFrame(frame, text="Your Answer")
        answer_frame.pack(fill="x", pady=(0, 10))

        self.practice_answer = tk.Text(answer_frame, height=3)
        self.practice_answer.pack(fill="x", pady=5)

        ttk.Button(answer_frame, text="Check Answer",
                   command=self.check_practice_answer).pack(anchor="w", pady=5)

        # Results
        result_frame = ttk.LabelFrame(frame, text="Result")
        result_frame.pack(fill="both", expand=True)

        self.practice_result = tk.Text(result_frame, height=6, wrap="word")
        self.practice_result.pack(fill="both", expand=True, pady=5)

        # Statistics
        self.practice_stats = {"correct": 0, "total": 0}
        self.stats_label = tk.StringVar(value="Score: 0/0 (0%)")
        ttk.Label(frame, textvariable=self.stats_label).pack(anchor="w", pady=5)

    def create_vlan_tab(self):
        """VLAN planning tool"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🏷️ VLAN Planner")

        main_frame = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Input panel
        input_frame = ttk.Frame(main_frame)
        main_frame.add(input_frame, weight=1)

        # VLAN entry
        entry_frame = ttk.LabelFrame(input_frame, text="Add VLAN")
        entry_frame.pack(fill="x", pady=5)

        ttk.Label(entry_frame, text="VLAN ID:").grid(row=0, column=0, sticky="w")
        self.vlan_id_entry = ttk.Entry(entry_frame, width=10)
        self.vlan_id_entry.grid(row=0, column=1, padx=5)

        ttk.Label(entry_frame, text="Name:").grid(row=1, column=0, sticky="w")
        self.vlan_name_entry = ttk.Entry(entry_frame, width=20)
        self.vlan_name_entry.grid(row=1, column=1, padx=5)

        ttk.Label(entry_frame, text="Subnet:").grid(row=2, column=0, sticky="w")
        self.vlan_subnet_entry = ttk.Entry(entry_frame, width=20)
        self.vlan_subnet_entry.grid(row=2, column=1, padx=5)

        ttk.Label(entry_frame, text="Description:").grid(row=3, column=0, sticky="w")
        self.vlan_desc_entry = ttk.Entry(entry_frame, width=30)
        self.vlan_desc_entry.grid(row=3, column=1, padx=5)

        ttk.Button(entry_frame, text="Add VLAN",
                   command=self.add_vlan).grid(row=4, column=0, columnspan=2, pady=5)

        # VLAN management
        mgmt_frame = ttk.LabelFrame(input_frame, text="VLAN Management")
        mgmt_frame.pack(fill="x", pady=5)

        ttk.Button(mgmt_frame, text="Generate Config",
                   command=self.generate_vlan_config).pack(anchor="w", pady=2)
        ttk.Button(mgmt_frame, text="Check Conflicts",
                   command=self.check_vlan_conflicts).pack(anchor="w", pady=2)
        ttk.Button(mgmt_frame, text="Export VLAN Plan",
                   command=self.export_vlan_plan).pack(anchor="w", pady=2)

        # Results panel
        result_frame = ttk.Frame(main_frame)
        main_frame.add(result_frame, weight=2)

        self.vlan_tree = ttk.Treeview(result_frame, columns=(
            "VLAN ID", "Name", "Subnet", "Description", "Status"
        ), show="headings")

        for col in self.vlan_tree["columns"]:
            self.vlan_tree.heading(col, text=col)

        scroll_v = ttk.Scrollbar(result_frame, orient="vertical", command=self.vlan_tree.yview)
        self.vlan_tree.configure(yscrollcommand=scroll_v.set)

        self.vlan_tree.pack(side="left", fill="both", expand=True)
        scroll_v.pack(side="right", fill="y")

        # Initialize VLAN data
        self.vlan_data = []

    def create_topology_tab(self):
        """Network topology visualizer"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🗺️ Topology")

        # Create matplotlib figure
        self.topology_fig = Figure(figsize=(12, 8))
        self.topology_ax = self.topology_fig.add_subplot(111)

        # Canvas
        canvas = FigureCanvasTkAgg(self.topology_fig, tab)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Controls
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill="x", pady=5)

        ttk.Button(control_frame, text="Auto-Generate Topology",
                   command=self.auto_generate_topology).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Load from CSV",
                   command=self.load_topology_csv).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Save Topology",
                   command=self.save_topology).pack(side="left", padx=5)

        # Initialize network graph
        self.network_graph = nx.Graph()

    def create_ai_troubleshoot_tab(self):
        """AI-powered troubleshooting"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🤖 AI Assistant")

        main_frame = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Input panel
        input_frame = ttk.Frame(main_frame)
        main_frame.add(input_frame, weight=1)

        # Model status
        model_frame = ttk.LabelFrame(input_frame, text="AI Model Status")
        model_frame.pack(fill="x", pady=5)

        self.model_status = tk.StringVar(value="No model loaded")
        ttk.Label(model_frame, textvariable=self.model_status).pack(anchor="w")

        ttk.Button(model_frame, text="Load Model",
                   command=self.load_ai_model).pack(anchor="w", pady=2)

        # Troubleshooting input
        trouble_frame = ttk.LabelFrame(input_frame, text="Describe Your Issue")
        trouble_frame.pack(fill="x", pady=5)

        self.trouble_input = tk.Text(trouble_frame, height=6, wrap="word")
        self.trouble_input.pack(fill="x", pady=5)

        ttk.Button(trouble_frame, text="Get AI Solution",
                   command=self.get_ai_troubleshoot).pack(anchor="w", pady=5)

        # ACL Generator
        acl_frame = ttk.LabelFrame(input_frame, text="ACL Generator")
        acl_frame.pack(fill="x", pady=5)

        ttk.Label(acl_frame, text="Requirements:").pack(anchor="w")
        self.acl_requirements = tk.Text(acl_frame, height=4, wrap="word")
        self.acl_requirements.pack(fill="x", pady=2)

        ttk.Button(acl_frame, text="Generate ACL",
                   command=self.generate_acl).pack(anchor="w", pady=5)

        # Results panel
        result_frame = ttk.Frame(main_frame)
        main_frame.add(result_frame, weight=2)

        self.ai_output = tk.Text(result_frame, wrap="word")
        scroll_ai = ttk.Scrollbar(result_frame, orient="vertical", command=self.ai_output.yview)
        self.ai_output.configure(yscrollcommand=scroll_ai.set)

        self.ai_output.pack(side="left", fill="both", expand=True)
        scroll_ai.pack(side="right", fill="y")

    def create_cli_advanced_tab(self):
        """Advanced CLI reference with multi-vendor support"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📖 CLI Reference")

        frame = ttk.Frame(tab, padding=10)
        frame.pack(fill="both", expand=True)

        # Vendor selection
        vendor_frame = ttk.Frame(frame)
        vendor_frame.pack(fill="x", pady=5)

        ttk.Label(vendor_frame, text="Vendor:").pack(side="left")
        self.cli_vendor = tk.StringVar(value="Cisco")
        vendor_combo = ttk.Combobox(vendor_frame, textvariable=self.cli_vendor,
                                    values=["Cisco", "Juniper", "Huawei", "HPE", "Mikrotik", "Ubiquiti"])
        vendor_combo.pack(side="left", padx=5)
        vendor_combo.bind("<<ComboboxSelected>>", self.update_cli_reference)

        # Category selection
        ttk.Label(vendor_frame, text="Category:").pack(side="left", padx=(20, 0))
        self.cli_category = tk.StringVar(value="Basic")
        category_combo = ttk.Combobox(vendor_frame, textvariable=self.cli_category,
                                      values=["Basic", "Routing", "Switching", "Security", "Troubleshooting"])
        category_combo.pack(side="left", padx=5)
        category_combo.bind("<<ComboboxSelected>>", self.update_cli_reference)

        # Search
        ttk.Label(vendor_frame, text="Search:").pack(side="left", padx=(20, 0))
        self.cli_search_var = tk.StringVar()
        search_entry = ttk.Entry(vendor_frame, textvariable=self.cli_search_var)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", self.filter_cli_commands)

        # Command display
        self.cli_display = tk.Text(frame, wrap="word", font=("Consolas", 10))
        cli_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.cli_display.yview)
        self.cli_display.configure(yscrollcommand=cli_scroll.set)

        self.cli_display.pack(side="left", fill="both", expand=True, pady=10)
        cli_scroll.pack(side="right", fill="y", pady=10)

        # Load CLI data
        self.load_cli_database()
        self.update_cli_reference()

    def create_utilization_chart(self, parent):
        """Create utilization analysis chart"""
        chart_frame = ttk.LabelFrame(parent, text="Utilization Analysis")
        chart_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

        self.util_fig = Figure(figsize=(8, 4))
        self.util_ax = self.util_fig.add_subplot(111)

        chart_canvas = FigureCanvasTkAgg(self.util_fig, chart_frame)
        chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    # Implementation methods for all features
    def calculate_enhanced_vlsm(self):
        """Enhanced VLSM calculation with efficiency analysis"""
        try:
            base_network = ipaddress.IPv4Network(self.vlsm_network_entry.get(), strict=False)

            # Collect subnet requirements
            requirements = []
            for name_entry, hosts_entry, priority_var in self.subnet_entries:
                if name_entry.get() and hosts_entry.get():
                    requirements.append({
                        'name': name_entry.get(),
                        'hosts': int(hosts_entry.get()),
                        'priority': priority_var.get()
                    })

            if not requirements:
                messagebox.showwarning("Warning", "No subnet requirements specified")
                return

            # Sort by priority and size
            priority_order = {"High": 0, "Normal": 1, "Low": 2}
            requirements.sort(key=lambda x: (priority_order[x['priority']], -x['hosts']))

            # Clear previous results
            self.vlsm_tree.delete(*self.vlsm_tree.get_children())

            current_address = base_network.network_address
            subnets = []

            for req in requirements:
                # Calculate minimum prefix for required hosts
                host_bits = (req['hosts'] + 2).bit_length()
                prefix = 32 - host_bits

                if prefix < base_network.prefixlen:
                    raise ValueError(f"Subnet {req['name']} requires too many hosts")

                # Create subnet
                subnet = ipaddress.IPv4Network((current_address, prefix), strict=False)

                # Check if subnet fits in base network
                if not base_network.supernet_of(subnet):
                    raise ValueError(f"Cannot fit subnet {req['name']} in base network")

                # Calculate efficiency
                available_hosts = subnet.num_addresses - 2
                efficiency = (req['hosts'] / available_hosts) * 100

                # Add to tree
                self.vlsm_tree.insert("", "end", values=(
                    req['name'],
                    f"{subnet.network_address}/{prefix}",
                    str(subnet.netmask),
                    str(available_hosts),
                    str(req['hosts']),
                    f"{efficiency:.1f}%",
                    str(subnet.network_address + 1),
                    str(subnet.broadcast_address - 1),
                    str(subnet.broadcast_address)
                ))

                subnets.append((req['name'], subnet, efficiency, req['hosts']))
                current_address = subnet.broadcast_address + 1

            # Update utilization chart
            self.update_utilization_chart(subnets)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def optimize_subnets(self):
        """Optimize subnet allocation for better efficiency and addressing"""
        try:
            # Check if we have any subnets to optimize
            if not self.vlsm_tree.get_children():
                messagebox.showwarning("Warning", "No subnets to optimize. Please calculate VLSM first.")
                return

            # Get current subnet data from the tree
            current_subnets = []
            for item in self.vlsm_tree.get_children():
                values = self.vlsm_tree.item(item)['values']
                current_subnets.append({
                    'name': values[0],
                    'network': values[1],
                    'hosts_available': int(values[3]),
                    'hosts_used': int(values[4]),
                    'efficiency': float(values[5].replace('%', ''))
                })

            # Sort subnets by efficiency (lowest first) to identify optimization opportunities
            current_subnets.sort(key=lambda x: x['efficiency'])

            optimization_suggestions = []

            # Analyze efficiency and suggest improvements
            for subnet in current_subnets:
                if subnet['efficiency'] < 50:
                    # Calculate optimal subnet size
                    optimal_hosts = subnet['hosts_used']
                    optimal_prefix = 32 - (optimal_hosts + 2).bit_length()

                    optimization_suggestions.append(
                        f"• {subnet['name']}: Current efficiency {subnet['efficiency']:.1f}% - "
                        f"Consider using /{optimal_prefix} for {optimal_hosts} hosts"
                    )
                elif subnet['efficiency'] > 90:
                    optimization_suggestions.append(
                        f"• {subnet['name']}: Excellent efficiency {subnet['efficiency']:.1f}% - Well optimized"
                    )

            # Check for potential consolidation opportunities
            small_subnets = [s for s in current_subnets if s['hosts_used'] < 10]
            if len(small_subnets) > 1:
                optimization_suggestions.append(
                    f"• Consider consolidating {len(small_subnets)} small subnets for better address utilization"
                )

            # Display optimization results
            if optimization_suggestions:
                result_text = "Subnet Optimization Analysis:\n\n" + "\n".join(optimization_suggestions)

                # Calculate overall efficiency
                total_used = sum(s['hosts_used'] for s in current_subnets)
                total_available = sum(s['hosts_available'] for s in current_subnets)
                overall_efficiency = (total_used / total_available) * 100 if total_available > 0 else 0

                result_text += f"\n\nOverall Network Efficiency: {overall_efficiency:.1f}%"

                if overall_efficiency < 60:
                    result_text += "\n\nRecommendation: Consider redesigning subnet allocation for better efficiency."
                elif overall_efficiency > 80:
                    result_text += "\n\nRecommendation: Good subnet utilization. Minor optimizations possible."

                messagebox.showinfo("Optimization Results", result_text)
            else:
                messagebox.showinfo("Optimization Results", "No optimization suggestions available.")

            # Automatically re-sort subnets by size (largest first) for optimal allocation
            base_network_str = self.vlsm_network_entry.get()
            if base_network_str:
                # Re-trigger calculation with optimized sorting
                self.calculate_enhanced_vlsm()
                messagebox.showinfo("Optimization Complete", "Subnets have been re-ordered for optimal allocation.")

        except Exception as e:
            messagebox.showerror("Error", f"Optimization failed: {str(e)}")

    def update_utilization_chart(self, subnets):
        """Update the utilization efficiency chart"""
        self.util_ax.clear()

        names = [s[0] for s in subnets]
        efficiencies = [s[2] for s in subnets]

        bars = self.util_ax.bar(names, efficiencies)

        # Color code based on efficiency
        for bar, eff in zip(bars, efficiencies):
            if eff >= 80:
                bar.set_color('green')
            elif eff >= 60:
                bar.set_color('yellow')
            else:
                bar.set_color('red')

        self.util_ax.set_ylabel('Efficiency %')
        self.util_ax.set_title('Subnet Utilization Efficiency')
        self.util_ax.set_ylim(0, 100)

        # Rotate labels if needed
        if len(names) > 5:
            self.util_ax.tick_params(axis='x', rotation=45)

        self.util_fig.tight_layout()
        self.util_fig.canvas.draw()

    def check_overlaps(self):
        """Check for subnet overlaps"""
        networks = []
        for item in self.vlsm_tree.get_children():
            values = self.vlsm_tree.item(item)['values']
            network_str = values[1]  # Network column
            try:
                network = ipaddress.IPv4Network(network_str)
                networks.append((values[0], network))  # (name, network)
            except:
                continue

        overlaps = []
        for i, (name1, net1) in enumerate(networks):
            for j, (name2, net2) in enumerate(networks[i + 1:], i + 1):
                if net1.overlaps(net2):
                    overlaps.append(f"{name1} overlaps with {name2}")

        if overlaps:
            messagebox.showwarning("Overlaps Detected", "\n".join(overlaps))
        else:
            messagebox.showinfo("No Overlaps", "No subnet overlaps detected")

    def calculate_ipv6_subnets(self):
        """Calculate IPv6 subnets"""
        try:
            base_network = ipaddress.IPv6Network(self.ipv6_network_entry.get())
            new_prefix = int(self.ipv6_prefix_entry.get())

            if new_prefix <= base_network.prefixlen:
                raise ValueError("New prefix must be larger than base network prefix")

            # Clear previous results
            self.ipv6_tree.delete(*self.ipv6_tree.get_children())

            # Generate subnets
            subnets = list(base_network.subnets(new_prefix=new_prefix))

            for i, subnet in enumerate(subnets):
                hosts = 2 ** (128 - subnet.prefixlen)
                self.ipv6_tree.insert("", "end", values=(
                    f"Subnet {i + 1}",
                    str(subnet.network_address),
                    f"/{subnet.prefixlen}",
                    f"{hosts:,}"
                ))

                # Limit display for performance
                if i >= 100:
                    self.ipv6_tree.insert("", "end", values=(
                        "...", "More subnets available", "", ""
                    ))
                    break

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cidr_to_mask(self):
        """Convert CIDR to subnet mask"""
        try:
            cidr = int(self.cidr_entry.get().replace('/', ''))
            mask = ipaddress.IPv4Network(f"0.0.0.0/{cidr}").netmask
            self.mask_entry.delete(0, tk.END)
            self.mask_entry.insert(0, str(mask))
        except Exception as e:
            messagebox.showerror("Error", "Invalid CIDR notation")

    def mask_to_cidr(self):
        """Convert subnet mask to CIDR"""
        try:
            mask = self.mask_entry.get()
            # Convert mask to CIDR
            binary = ''.join([bin(int(x))[2:].zfill(8) for x in mask.split('.')])
            cidr = binary.count('1')
            self.cidr_entry.delete(0, tk.END)
            self.cidr_entry.insert(0, f"/{cidr}")
        except Exception as e:
            messagebox.showerror("Error", "Invalid subnet mask")

    def calculate_supernet(self):
        """Calculate supernet/route summarization"""
        try:
            networks_text = self.supernet_text.get("1.0", tk.END).strip()
            if not networks_text:
                return

            networks = []
            for line in networks_text.split('\n'):
                line = line.strip()
                if line:
                    networks.append(ipaddress.IPv4Network(line))

            if len(networks) < 2:
                self.supernet_result.set("Need at least 2 networks")
                return

            # Find the supernet
            supernet = ipaddress.collapse_addresses(networks)
            supernet_list = list(supernet)

            if len(supernet_list) == 1:
                result = f"Summary route: {supernet_list[0]}"
            else:
                result = f"Multiple summary routes needed: {', '.join(str(s) for s in supernet_list)}"

            self.supernet_result.set(result)

        except Exception as e:
            self.supernet_result.set(f"Error: {str(e)}")

    def convert_bandwidth(self):
        """Convert between bandwidth units"""
        try:
            value = float(self.bw_value_entry.get())
            from_unit = self.bw_from.get()
            to_unit = self.bw_to.get()

            # Convert to bps first
            multipliers = {
                "bps": 1,
                "Kbps": 1000,
                "Mbps": 1000000,
                "Gbps": 1000000000,
                "Tbps": 1000000000000
            }

            bps_value = value * multipliers[from_unit]
            result = bps_value / multipliers[to_unit]

            self.bw_result.set(f"{value} {from_unit} = {result:,.2f} {to_unit}")

        except Exception as e:
            self.bw_result.set("Error in conversion")

    def start_ping_sweep(self):
        """Start ping sweep in background thread"""

        def ping_sweep():
            try:
                network = ipaddress.IPv4Network(self.ping_range_entry.get())
                self.scan_tree.delete(*self.scan_tree.get_children())
                self.scan_progress.start()

                for ip in network.hosts():
                    # Simple ping using subprocess
                    try:
                        start_time = time.time()
                        result = subprocess.run(['ping', '-c', '1', '-W', '1000', str(ip)],
                                                capture_output=True, timeout=2)
                        response_time = (time.time() - start_time) * 1000

                        if result.returncode == 0:
                            status = "Up"
                            self.scan_tree.insert("", "end", values=(
                                str(ip), status, "N/A", f"{response_time:.1f}ms"
                            ))
                    except:
                        pass

                self.scan_progress.stop()

            except Exception as e:
                self.scan_progress.stop()
                messagebox.showerror("Error", str(e))

        threading.Thread(target=ping_sweep, daemon=True).start()

    def start_port_scan(self):
        """Start port scan in background thread"""

        def port_scan():
            try:
                target = self.port_target_entry.get()
                port_range = self.port_range_entry.get()

                if '-' in port_range:
                    start_port, end_port = map(int, port_range.split('-'))
                else:
                    start_port = end_port = int(port_range)

                self.scan_progress.start()
                open_ports = []

                for port in range(start_port, min(end_port + 1, start_port + 100)):  # Limit scan
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    result = sock.connect_ex((target, port))
                    if result == 0:
                        open_ports.append(str(port))
                    sock.close()

                # Update tree with results
                ports_str = ", ".join(open_ports) if open_ports else "None open"
                self.scan_tree.insert("", "end", values=(
                    target, "Scanned", ports_str, "N/A"
                ))

                self.scan_progress.stop()

            except Exception as e:
                self.scan_progress.stop()
                messagebox.showerror("Error", str(e))

        threading.Thread(target=port_scan, daemon=True).start()

    def generate_practice_question(self):
        """Generate practice questions based on difficulty"""
        difficulty = self.practice_difficulty.get()
        question_type = self.practice_type.get()

        self.practice_question.delete("1.0", tk.END)
        self.practice_result.delete("1.0", tk.END)

        if question_type == "Subnetting":
            if difficulty == "Beginner":
                # Simple Class C subnetting
                network = f"192.168.{random.randint(1, 254)}.0"
                subnets_needed = random.choice([2, 4, 8])
                question = f"Given the network {network}/24, subnet it to create {subnets_needed} equal subnets.\n\n"
                question += "Provide:\n1. New subnet mask\n2. First 3 subnet networks\n3. Host range for first subnet"

            elif difficulty == "Intermediate":
                # Variable subnetting
                base_nets = ["172.16.0.0/16", "10.0.0.0/8", "192.168.0.0/16"]
                network = random.choice(base_nets)
                hosts = [random.randint(50, 500) for _ in range(3)]
                question = f"Given {network}, create subnets for:\n"
                for i, h in enumerate(hosts, 1):
                    question += f"Subnet {i}: {h} hosts\n"
                question += "\nProvide the network address and mask for each subnet."

        # Store correct answer for checking
        self.current_answer = self.calculate_practice_answer(question_type, difficulty)
        self.practice_question.insert("1.0", question)

    def calculate_practice_answer(self, question_type, difficulty):
        """Calculate the correct answer for practice question"""
        # This would contain the logic to calculate correct answers
        # For now, return a placeholder
        return "Answer calculation logic would go here"

    def check_practice_answer(self):
        """Check the practice answer"""
        user_answer = self.practice_answer.get("1.0", tk.END).strip()

        # Simple checking logic (would be enhanced in production)
        if user_answer:
            self.practice_stats["total"] += 1
            # For demo, randomly mark as correct 70% of time
            if random.random() < 0.7:
                self.practice_stats["correct"] += 1
                result = "✅ Correct! Good job."
            else:
                result = "❌ Incorrect. Here's the correct answer:\n" + str(self.current_answer)
        else:
            result = "Please provide an answer."

        self.practice_result.delete("1.0", tk.END)
        self.practice_result.insert("1.0", result)

        # Update statistics
        total = self.practice_stats["total"]
        correct = self.practice_stats["correct"]
        percentage = (correct / total * 100) if total > 0 else 0
        self.stats_label.set(f"Score: {correct}/{total} ({percentage:.1f}%)")

    def add_vlan(self):
        """Add VLAN to the plan"""
        vlan_id = self.vlan_id_entry.get()
        name = self.vlan_name_entry.get()
        subnet = self.vlan_subnet_entry.get()
        description = self.vlan_desc_entry.get()

        if not all([vlan_id, name, subnet]):
            messagebox.showwarning("Warning", "Please fill all required fields")
            return

        # Check for duplicate VLAN ID
        for vlan in self.vlan_data:
            if vlan['id'] == vlan_id:
                messagebox.showerror("Error", "VLAN ID already exists")
                return

        # Validate subnet
        try:
            ipaddress.IPv4Network(subnet)
        except:
            messagebox.showerror("Error", "Invalid subnet format")
            return

        # Add VLAN
        vlan_info = {
            'id': vlan_id,
            'name': name,
            'subnet': subnet,
            'description': description,
            'status': 'Planned'
        }

        self.vlan_data.append(vlan_info)

        # Update tree
        self.vlan_tree.insert("", "end", values=(
            vlan_id, name, subnet, description, "Planned"
        ))

        # Clear entries
        for entry in [self.vlan_id_entry, self.vlan_name_entry,
                      self.vlan_subnet_entry, self.vlan_desc_entry]:
            entry.delete(0, tk.END)

    def generate_vlan_config(self):
        """Generate VLAN configuration commands"""
        if not self.vlan_data:
            messagebox.showwarning("Warning", "No VLANs to generate config for")
            return

        config_lines = ["! VLAN Configuration"]
        config_lines.append("! Generated by Advanced Network Calculator")
        config_lines.append("")

        for vlan in self.vlan_data:
            config_lines.append(f"vlan {vlan['id']}")
            config_lines.append(f" name {vlan['name']}")
            config_lines.append("!")

            # Add interface VLAN configuration
            config_lines.append(f"interface vlan{vlan['id']}")
            try:
                network = ipaddress.IPv4Network(vlan['subnet'])
                gateway_ip = str(network.network_address + 1)
                config_lines.append(f" ip address {gateway_ip} {network.netmask}")
            except:
                config_lines.append(f" ! Invalid subnet: {vlan['subnet']}")
            config_lines.append(" no shutdown")
            config_lines.append("!")

        config_text = "\n".join(config_lines)

        # Show in a new window
        config_window = tk.Toplevel(self.root)
        config_window.title("VLAN Configuration")
        config_window.geometry("600x400")

        text_widget = tk.Text(config_window, wrap="none", font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(config_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.insert("1.0", config_text)
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def check_vlan_conflicts(self):
        """Check for VLAN conflicts"""
        conflicts = []

        # Check subnet overlaps
        for i, vlan1 in enumerate(self.vlan_data):
            for j, vlan2 in enumerate(self.vlan_data[i + 1:], i + 1):
                try:
                    net1 = ipaddress.IPv4Network(vlan1['subnet'])
                    net2 = ipaddress.IPv4Network(vlan2['subnet'])
                    if net1.overlaps(net2):
                        conflicts.append(f"VLAN {vlan1['id']} and {vlan2['id']} have overlapping subnets")
                except:
                    pass

        if conflicts:
            messagebox.showwarning("Conflicts Found", "\n".join(conflicts))
        else:
            messagebox.showinfo("No Conflicts", "No VLAN conflicts detected")

    def export_vlan_plan(self):
        """Export VLAN plan to CSV"""
        if not self.vlan_data:
            messagebox.showwarning("Warning", "No VLAN data to export")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if filename:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['VLAN ID', 'Name', 'Subnet', 'Description', 'Status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for vlan in self.vlan_data:
                    writer.writerow({
                        'VLAN ID': vlan['id'],
                        'Name': vlan['name'],
                        'Subnet': vlan['subnet'],
                        'Description': vlan['description'],
                        'Status': vlan['status']
                    })

            messagebox.showinfo("Export Complete", f"VLAN plan exported to {filename}")

    def auto_generate_topology(self):
        """Auto-generate network topology from VLSM data"""
        self.topology_ax.clear()

        # Create a simple topology based on current subnets
        self.network_graph.clear()

        # Add core router
        self.network_graph.add_node("Core Router", type="router")

        # Add subnets from VLSM calculation
        for item in self.vlsm_tree.get_children():
            values = self.vlsm_tree.item(item)['values']
            subnet_name = values[0]
            self.network_graph.add_node(subnet_name, type="subnet")
            self.network_graph.add_edge("Core Router", subnet_name)

        # Generate layout
        pos = nx.spring_layout(self.network_graph)

        # Draw nodes
        router_nodes = [n for n, d in self.network_graph.nodes(data=True) if d.get('type') == 'router']
        subnet_nodes = [n for n, d in self.network_graph.nodes(data=True) if d.get('type') == 'subnet']

        nx.draw_networkx_nodes(self.network_graph, pos, nodelist=router_nodes,
                               node_color='red', node_size=1000, ax=self.topology_ax)
        nx.draw_networkx_nodes(self.network_graph, pos, nodelist=subnet_nodes,
                               node_color='lightblue', node_size=500, ax=self.topology_ax)

        # Draw edges and labels
        nx.draw_networkx_edges(self.network_graph, pos, ax=self.topology_ax)
        nx.draw_networkx_labels(self.network_graph, pos, font_size=8, ax=self.topology_ax)

        self.topology_ax.set_title("Network Topology")
        self.topology_ax.axis('off')
        self.topology_fig.tight_layout()
        self.topology_fig.canvas.draw()

    def load_topology_csv(self):
        """Load topology from CSV file"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )

        if filename:
            try:
                df = pd.read_csv(filename)
                self.network_graph.clear()

                # Assuming CSV has columns: Source, Target, Type
                for _, row in df.iterrows():
                    source = row.get('Source', '')
                    target = row.get('Target', '')
                    node_type = row.get('Type', 'device')

                    if source and target:
                        self.network_graph.add_node(source, type=node_type)
                        self.network_graph.add_node(target, type=node_type)
                        self.network_graph.add_edge(source, target)

                # Redraw topology
                self.auto_generate_topology()
                messagebox.showinfo("Success", "Topology loaded from CSV")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load topology: {str(e)}")

    def save_topology(self):
        """Save current topology to file"""
        if not self.network_graph.nodes():
            messagebox.showwarning("Warning", "No topology to save")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf")]
        )

        if filename:
            try:
                self.topology_fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Topology saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save topology: {str(e)}")

    def load_ai_model(self):
        """Load AI model for troubleshooting"""
        if not AI_AVAILABLE:
            messagebox.showerror("Error", "AI libraries not installed. Install: pip install transformers torch")
            return

        # File dialog for model selection
        model_path = filedialog.askdirectory(title="Select Model Directory")
        if not model_path:
            # Use default model
            model_name = "microsoft/DialoGPT-small"  # Lightweight model for demo
            try:
                self.ai_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.ai_model = AutoModelForCausalLM.from_pretrained(model_name)
                self.current_model_path = model_name
                self.model_status.set(f"Model loaded: {model_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load model: {str(e)}")
        else:
            # Load custom model
            try:
                self.ai_tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.ai_model = AutoModelForCausalLM.from_pretrained(model_path)
                self.current_model_path = model_path
                self.model_status.set(f"Custom model loaded: {os.path.basename(model_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load custom model: {str(e)}")

    def get_ai_troubleshoot(self):
        """Get AI-powered troubleshooting suggestions"""
        if not self.ai_model:
            messagebox.showwarning("Warning", "Please load an AI model first")
            return

        problem = self.trouble_input.get("1.0", tk.END).strip()
        if not problem:
            return

        try:
            # Prepare network context
            context = "Network troubleshooting context:\n"

            # Add VLSM data if available
            for item in self.vlsm_tree.get_children():
                values = self.vlsm_tree.item(item)['values']
                context += f"Subnet: {values[0]} - {values[1]}\n"

            # Add scan results if available
            for item in self.scan_tree.get_children():
                values = self.scan_tree.item(item)['values']
                context += f"Host: {values[0]} - Status: {values[1]}\n"

            full_prompt = f"{context}\nProblem: {problem}\nSuggested solution:"

            # Generate response (simplified for demo)
            # In production, this would use more sophisticated prompting
            inputs = self.ai_tokenizer.encode(full_prompt, return_tensors='pt')
            outputs = self.ai_model.generate(inputs, max_length=200, do_sample=True)
            response = self.ai_tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract only the generated part
            solution = response[len(full_prompt):].strip()

            # Add some predefined networking solutions for better results
            if not solution or len(solution) < 10:
                solution = self.get_predefined_solution(problem)

            self.ai_output.delete("1.0", tk.END)
            self.ai_output.insert("1.0", f"Problem: {problem}\n\nAI Suggestion:\n{solution}")

        except Exception as e:
            messagebox.showerror("Error", f"AI processing failed: {str(e)}")

    def get_predefined_solution(self, problem):
        """Fallback predefined solutions"""
        problem_lower = problem.lower()

        if "ping" in problem_lower and "fail" in problem_lower:
            return """1. Check physical connectivity
2. Verify IP configuration
3. Check routing tables
4. Verify firewall rules
5. Test with traceroute"""

        elif "slow" in problem_lower or "performance" in problem_lower:
            return """1. Check bandwidth utilization
2. Analyze latency with ping
3. Review QoS settings
4. Check for network congestion
5. Verify duplex settings"""

        elif "dhcp" in problem_lower:
            return """1. Check DHCP server status
2. Verify DHCP scope
3. Check relay agent configuration
4. Review lease duration
5. Validate IP helper addresses"""

        else:
            return """General troubleshooting steps:
1. Identify the scope of the problem
2. Check physical layer connectivity
3. Verify configuration settings
4. Review logs for errors
5. Test with network tools"""

    def generate_acl(self):
        """Generate Access Control List from requirements"""
        requirements = self.acl_requirements.get("1.0", tk.END).strip()
        if not requirements:
            return

        # Simple ACL generation based on keywords
        acl_lines = ["! Generated ACL"]
        acl_number = 100
        line_number = 10

        lines = requirements.split('\n')
        for line in lines:
            line = line.strip().lower()
            if not line:
                continue

            if "deny" in line and "tcp" in line:
                if "port" in line:
                    # Extract port if mentioned
                    words = line.split()
                    for i, word in enumerate(words):
                        if word == "port" and i + 1 < len(words):
                            port = words[i + 1]
                            acl_lines.append(f"access-list {acl_number} deny tcp any any eq {port}")
                            break
                else:
                    acl_lines.append(f"access-list {acl_number} deny tcp any any")

            elif "allow" in line or "permit" in line:
                if "web" in line or "http" in line:
                    acl_lines.append(f"access-list {acl_number} permit tcp any any eq 80")
                    acl_lines.append(f"access-list {acl_number} permit tcp any any eq 443")
                elif "any" in line:
                    acl_lines.append(f"access-list {acl_number} permit ip any any")

        # Add implicit deny
        acl_lines.append(f"access-list {acl_number} deny ip any any")

        # Display result
        self.ai_output.delete("1.0", tk.END)
        self.ai_output.insert("1.0", "\n".join(acl_lines))

    def load_cli_database(self):
        """Load CLI command database"""
        self.cli_data = {
            "Cisco": {
                "Basic": [
                    ("enable", "Enter privileged mode"),
                    ("configure terminal", "Enter global configuration mode"),
                    ("interface gigabitethernet 0/1", "Enter interface configuration"),
                    ("ip address 192.168.1.1 255.255.255.0", "Set IP address"),
                    ("no shutdown", "Enable interface"),
                    ("exit", "Exit current mode"),
                    ("copy running-config startup-config", "Save configuration"),
                    ("show running-config", "Display current configuration"),
                    ("show ip interface brief", "Show interface status"),
                    ("ping 192.168.1.1", "Test connectivity")
                ],
                "Routing": [
                    ("router ospf 1", "Enable OSPF process"),
                    ("network 192.168.1.0 0.0.0.255 area 0", "Advertise network in OSPF"),
                    ("ip route 0.0.0.0 0.0.0.0 192.168.1.1", "Set default route"),
                    ("show ip route", "Display routing table"),
                    ("show ip ospf neighbor", "Show OSPF neighbors"),
                    ("router bgp 65001", "Configure BGP"),
                    ("neighbor 192.168.1.2 remote-as 65002", "Configure BGP neighbor")
                ],
                "Switching": [
                    ("vlan 10", "Create VLAN 10"),
                    ("name Sales", "Name the VLAN"),
                    ("interface vlan 10", "Enter VLAN interface"),
                    ("switchport mode access", "Set port as access"),
                    ("switchport access vlan 10", "Assign port to VLAN"),
                    ("switchport mode trunk", "Set port as trunk"),
                    ("show vlan brief", "Display VLAN information"),
                    ("spanning-tree mode rapid-pvst", "Set spanning tree mode")
                ]
            },
            "Juniper": {
                "Basic": [
                    ("configure", "Enter configuration mode"),
                    ("set interfaces ge-0/0/0 unit 0 family inet address 192.168.1.1/24", "Set IP address"),
                    ("commit", "Commit configuration"),
                    ("show configuration", "Display configuration"),
                    ("show interfaces terse", "Show interface summary"),
                    ("ping 192.168.1.1", "Test connectivity")
                ],
                "Routing": [
                    ("set protocols ospf area 0.0.0.0 interface ge-0/0/0", "Configure OSPF"),
                    ("set routing-options static route 0.0.0.0/0 next-hop 192.168.1.1", "Set default route"),
                    ("show route", "Display routing table"),
                    ("show ospf neighbor", "Show OSPF neighbors")
                ]
            }
        }

    def update_cli_reference(self, event=None):
        """Update CLI reference display"""
        vendor = self.cli_vendor.get()
        category = self.cli_category.get()

        self.cli_display.delete("1.0", tk.END)

        if vendor in self.cli_data and category in self.cli_data[vendor]:
            commands = self.cli_data[vendor][category]

            self.cli_display.insert(tk.END, f"=== {vendor} {category} Commands ===\n\n")

            for command, description in commands:
                self.cli_display.insert(tk.END, f"Command: {command}\n")
                self.cli_display.insert(tk.END, f"Description: {description}\n\n")

    def filter_cli_commands(self, event=None):
        """Filter CLI commands based on search"""
        search_term = self.cli_search_var.get().lower()
        vendor = self.cli_vendor.get()
        category = self.cli_category.get()

        self.cli_display.delete("1.0", tk.END)

        if vendor in self.cli_data and category in self.cli_data[vendor]:
            commands = self.cli_data[vendor][category]

            self.cli_display.insert(tk.END, f"=== {vendor} {category} Commands (Filtered) ===\n\n")

            for command, description in commands:
                if search_term in command.lower() or search_term in description.lower():
                    self.cli_display.insert(tk.END, f"Command: {command}\n")
                    self.cli_display.insert(tk.END, f"Description: {description}\n\n")

    # Additional utility methods
    def new_project(self):
        """Create new project"""
        self.projects = {}
        # Clear all data
        for tree in [self.vlsm_tree, self.ipv6_tree, self.scan_tree, self.vlan_tree]:
            tree.delete(*tree.get_children())
        messagebox.showinfo("New Project", "New project created")

    def save_project(self):
        """Save current project"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            project_data = {
                "vlsm_data": [],
                "vlan_data": self.vlan_data,
                "network_config": {}
            }

            # Save VLSM data
            for item in self.vlsm_tree.get_children():
                project_data["vlsm_data"].append(self.vlsm_tree.item(item)['values'])

            with open(filename, 'w') as f:
                json.dump(project_data, f, indent=2)

            messagebox.showinfo("Saved", f"Project saved to {filename}")

    def open_project(self):
        """Open existing project"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    project_data = json.load(f)

                # Load VLSM data
                self.vlsm_tree.delete(*self.vlsm_tree.get_children())
                for row in project_data.get("vlsm_data", []):
                    self.vlsm_tree.insert("", "end", values=row)

                # Load VLAN data
                self.vlan_data = project_data.get("vlan_data", [])
                self.vlan_tree.delete(*self.vlan_tree.get_children())
                for vlan in self.vlan_data:
                    self.vlan_tree.insert("", "end", values=(
                        vlan['id'], vlan['name'], vlan['subnet'],
                        vlan['description'], vlan['status']
                    ))

                messagebox.showinfo("Opened", f"Project loaded from {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to open project: {str(e)}")

    def toggle_dark_mode(self):
        """Toggle between light and dark themes"""
        if self.dark_mode:
            self.style.theme_use('clam')
            self.dark_mode = False
        else:
            # Configure dark theme
            self.style.configure('TFrame', background='#2d2d2d')
            self.style.configure('TLabel', background='#2d2d2d', foreground='white')
            self.style.configure('TButton', background='#404040', foreground='white')
            self.dark_mode = True

    def export_documentation(self):
        """Export network documentation"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")]
        )
        if filename:
            with open(filename, 'w') as f:
                f.write("Network Documentation\n")
                f.write("=" * 50 + "\n\n")

                # VLSM Documentation
                f.write("VLSM Configuration:\n")
                f.write("-" * 20 + "\n")
                for item in self.vlsm_tree.get_children():
                    values = self.vlsm_tree.item(item)['values']
                    f.write(f"Subnet: {values[0]}\n")
                    f.write(f"Network: {values[1]}\n")
                    f.write(f"Mask: {values[2]}\n\n")

                # VLAN Documentation
                f.write("\nVLAN Configuration:\n")
                f.write("-" * 20 + "\n")
                for vlan in self.vlan_data:
                    f.write(f"VLAN {vlan['id']}: {vlan['name']}\n")
                    f.write(f"Subnet: {vlan['subnet']}\n")
                    f.write(f"Description: {vlan['description']}\n\n")

            messagebox.showinfo("Exported", f"Documentation exported to {filename}")

    def show_model_info(self):
        """Show current AI model information"""
        if self.ai_model:
            info = f"Current model: {self.current_model_path}\n"
            info += f"Model type: {type(self.ai_model).__name__}\n"
            if self.ai_tokenizer:
                info += f"Vocabulary size: {self.ai_tokenizer.vocab_size}\n"
        else:
            info = "No model loaded"

        messagebox.showinfo("Model Information", info)


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedNetworkCalculator(root)
    root.mainloop()