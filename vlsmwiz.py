import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ipaddress
import matplotlib.pyplot as plt
import csv
import pandas as pd
import os

CLI_DATASET_PATH = "commands_dataset.csv"  # Adjust if needed

class SubnetCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Subnet Calculator")
        self.root.geometry("1280x800")

        self.style = ttk.Style()
        self.style.configure("TNotebook.Tab", padding=[10, 5], font=("Segoe UI", 11, "bold"))
        self.style.configure("TButton", padding=6)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.full_ip_details = ""
        self.chart_data = []

        self.tab_control = ttk.Notebook(self.root)
        self.create_ip_tools_tab()
        self.create_vlsm_tab()
        self.create_result_tab()
        self.create_cli_tab()
        self.tab_control.pack(expand=1, fill="both")

    def create_ip_tools_tab(self):
        tab = ttk.Frame(self.tab_control)
        self.tab_control.add(tab, text="🧮 IP Tools")

        frame = ttk.Frame(tab, padding=20)
        frame.pack()

        ttk.Label(frame, text="Decimal IP:").pack()
        self.dec_entry = tk.Entry(frame, font=("Consolas", 12))
        self.dec_entry.pack()

        ttk.Label(frame, text="Binary IP:").pack()
        self.bin_entry = tk.Entry(frame, font=("Consolas", 12))
        self.bin_entry.pack()

        btns = ttk.Frame(frame)
        btns.pack(pady=10)
        ttk.Button(btns, text="Decimal → Binary", command=self.dec_to_bin).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Binary → Decimal", command=self.bin_to_dec).grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Validate IP:").pack(pady=(10, 0))
        self.validate_entry = tk.Entry(frame, font=("Consolas", 12))
        self.validate_entry.pack()
        self.validation_result = tk.StringVar()
        ttk.Label(frame, textvariable=self.validation_result, foreground="blue").pack()
        ttk.Button(frame, text="Check IP Validity", command=self.validate_ip).pack(pady=5)
    def create_vlsm_tab(self):
        tab = ttk.Frame(self.tab_control)
        self.tab_control.add(tab, text="📐 VLSM Setup")

        frame = ttk.Frame(tab, padding=20)
        frame.pack()

        ttk.Label(frame, text="Base Network (e.g. 192.168.1.0/24):").pack()
        self.base_network_entry = tk.Entry(frame)
        self.base_network_entry.pack()

        ttk.Label(frame, text="Number of Subnets:").pack()
        self.subnet_count_entry = tk.Entry(frame)
        self.subnet_count_entry.pack()

        ttk.Button(frame, text="Generate Subnet Fields", command=self.generate_subnet_fields).pack(pady=10)
        self.subnet_frame = ttk.Frame(frame)
        self.subnet_frame.pack()

        ttk.Button(frame, text="🔍 Calculate Optimal VLSM", command=self.calculate_vlsm).pack(pady=10)

    def generate_subnet_fields(self):
        for widget in self.subnet_frame.winfo_children():
            widget.destroy()
        self.subnet_inputs = []

        try:
            count = int(self.subnet_count_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid number of subnets.")
            return

        for i in range(count):
            ttk.Label(self.subnet_frame, text=f"Hosts for Subnet {i+1}:").grid(row=i, column=0, sticky="e")
            entry = tk.Entry(self.subnet_frame)
            entry.grid(row=i, column=1)
            self.subnet_inputs.append(entry)

    def calculate_min_prefix(self, host_count):
        for prefix in range(32, 0, -1):
            if (2 ** (32 - prefix)) >= (host_count + 2):
                return prefix
        raise ValueError("Cannot assign subnet for host count")
    def create_vlsm_tab(self):
        tab = ttk.Frame(self.tab_control)
        self.tab_control.add(tab, text="📐 VLSM Setup")

        frame = ttk.Frame(tab, padding=20)
        frame.pack()

        ttk.Label(frame, text="Base Network (e.g. 192.168.1.0/24):").pack()
        self.base_network_entry = tk.Entry(frame)
        self.base_network_entry.pack()

        ttk.Label(frame, text="Number of Subnets:").pack()
        self.subnet_count_entry = tk.Entry(frame)
        self.subnet_count_entry.pack()

        ttk.Button(frame, text="Generate Subnet Fields", command=self.generate_subnet_fields).pack(pady=10)
        self.subnet_frame = ttk.Frame(frame)
        self.subnet_frame.pack()

        ttk.Button(frame, text="🔍 Calculate Optimal VLSM", command=self.calculate_vlsm).pack(pady=10)

    def generate_subnet_fields(self):
        for widget in self.subnet_frame.winfo_children():
            widget.destroy()
        self.subnet_inputs = []

        try:
            count = int(self.subnet_count_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid number of subnets.")
            return

        for i in range(count):
            ttk.Label(self.subnet_frame, text=f"Hosts for Subnet {i+1}:").grid(row=i, column=0, sticky="e")
            entry = tk.Entry(self.subnet_frame)
            entry.grid(row=i, column=1)
            self.subnet_inputs.append(entry)

    def calculate_min_prefix(self, host_count):
        for prefix in range(32, 0, -1):
            if (2 ** (32 - prefix)) >= (host_count + 2):
                return prefix
        raise ValueError("Cannot assign subnet for host count")
    def create_result_tab(self):
        tab = ttk.Frame(self.tab_control)
        self.tab_control.add(tab, text="📊 Results")

        frame = ttk.Frame(tab, padding=10)
        frame.pack(fill="both", expand=True)

        self.vlsm_table = ttk.Treeview(frame, columns=("Subnet", "Network", "Mask", "First", "Last", "Broadcast"), show="headings")
        for col in self.vlsm_table["columns"]:
            self.vlsm_table.heading(col, text=col)
        self.vlsm_table.pack(fill="x")

        btns = ttk.Frame(frame)
        btns.pack(pady=5)
        ttk.Button(btns, text="💾 Export CSV", command=self.export_to_csv).pack(side="left", padx=5)
        ttk.Button(btns, text="📈 Show Chart", command=self.show_chart).pack(side="left", padx=5)

        self.detail_text = tk.Text(frame, height=15)
        self.detail_text.pack(fill="both", expand=True)

    def calculate_vlsm(self):
        try:
            net = ipaddress.IPv4Network(self.base_network_entry.get(), strict=False)
            current = net.network_address
            subnet_reqs = [(f"Subnet {i+1}", int(e.get())) for i, e in enumerate(self.subnet_inputs)]

            subnet_reqs.sort(key=lambda x: x[1], reverse=True)
            self.chart_data = []
            self.full_ip_details = ""
            self.vlsm_table.delete(*self.vlsm_table.get_children())
            existing_subnets = []

            for name, hosts in subnet_reqs:
                prefix = self.calculate_min_prefix(hosts)
                subnet = ipaddress.IPv4Network((current, prefix), strict=False)
                for existing in existing_subnets:
                    if subnet.overlaps(existing):
                        raise ValueError("Overlapping subnet detected")
                existing_subnets.append(subnet)
                first = subnet.network_address + 1
                last = subnet.broadcast_address - 1
                self.vlsm_table.insert("", "end", values=(
                    name, f"{subnet.network_address}/{prefix}", str(subnet.netmask),
                    str(first), str(last), str(subnet.broadcast_address)))
                self.chart_data.append((name, subnet.num_addresses))
                self.full_ip_details += f"{name} ({subnet}):\n" + '\n'.join([f"  {ip}" for ip in subnet.hosts()]) + "\n\n"
                current = subnet.broadcast_address + 1

            self.detail_text.delete("1.0", tk.END)
            self.detail_text.insert(tk.END, self.full_ip_details)
            self.tab_control.select(2)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_to_csv(self):
        file = filedialog.asksaveasfilename(defaultextension=".csv")
        if not file:
            return
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Subnet", "Network", "Mask", "First", "Last", "Broadcast"])
            for row in self.vlsm_table.get_children():
                writer.writerow(self.vlsm_table.item(row)["values"])
        messagebox.showinfo("Exported", f"CSV saved to {file}")

    def show_chart(self):
        if not self.chart_data:
            messagebox.showwarning("Warning", "No data to chart.")
            return
        labels, sizes = zip(*self.chart_data)
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title("IP Allocation by Subnet")
        plt.axis("equal")
        plt.show()

    def create_cli_tab(self):
        tab = ttk.Frame(self.tab_control)
        self.tab_control.add(tab, text="📚 CLI Cheatsheet")

        frame = ttk.Frame(tab, padding=10)
        frame.pack(fill="both", expand=True)

        # Load CLI dataset
        if os.path.exists(CLI_DATASET_PATH):
            self.cli_df = pd.read_csv(CLI_DATASET_PATH)
        else:
            messagebox.showerror("Error", f"{CLI_DATASET_PATH} not found.")
            self.cli_df = pd.DataFrame(columns=["OS", "Command", "Function"])

        # OS dropdown filter
        os_frame = ttk.Frame(frame)
        os_frame.pack(fill="x", pady=5)
        ttk.Label(os_frame, text="Filter by OS:").pack(side="left")
        self.selected_os = tk.StringVar(value="All")
        os_options = ["All"] + sorted(self.cli_df["OS"].dropna().unique().tolist())
        os_menu = ttk.OptionMenu(os_frame, self.selected_os, "All", *os_options,
                                 command=lambda _: self.update_cli_results())
        os_menu.pack(side="left", padx=5)

        # Search bar
        ttk.Label(frame, text="Search by keyword:").pack(anchor="w")
        self.cli_search = tk.Entry(frame)
        self.cli_search.pack(fill="x", pady=(0, 5))
        self.cli_search.bind("<KeyRelease>", lambda e: self.update_cli_results())

        # Scrollable output area
        output_frame = ttk.Frame(frame)
        output_frame.pack(fill="both", expand=True)
        self.cli_output = tk.Text(output_frame, wrap="word")
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.cli_output.yview)
        self.cli_output.configure(yscrollcommand=scrollbar.set)
        self.cli_output.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.update_cli_results()

    def update_cli_results(self):
        query = self.cli_search.get().lower()
        selected_os = self.selected_os.get()

        df = self.cli_df.copy()
        if selected_os != "All":
            df = df[df["OS"].str.lower() == selected_os.lower()]

        if query:
            df = df[df.apply(lambda row: query in str(row["Command"]).lower() or query in str(row["Function"]).lower(),
                             axis=1)]

        self.cli_output.delete("1.0", tk.END)

        if df.empty:
            self.cli_output.insert(tk.END, "No matching commands found.\n")
            return

        grouped = df.groupby("OS")
        for os_type, group in grouped:
            self.cli_output.insert(tk.END, f"\n=== {os_type.upper()} Commands ===\n")
            for _, row in group.iterrows():
                self.cli_output.insert(tk.END, f"\n• {row['Command']}\n  ➜ {row['Function']}\n")

    def dec_to_bin(self):
        try:
            ip = self.dec_entry.get().strip()
            binary = '.'.join([format(int(x), '08b') for x in ip.split('.')])
            self.bin_entry.delete(0, tk.END)
            self.bin_entry.insert(0, binary)
        except:
            messagebox.showerror("Error", "Invalid Decimal IP")

    def bin_to_dec(self):
        try:
            binary = self.bin_entry.get().strip()
            decimal = '.'.join([str(int(b, 2)) for b in binary.split('.')])
            self.dec_entry.delete(0, tk.END)
            self.dec_entry.insert(0, decimal)
        except:
            messagebox.showerror("Error", "Invalid Binary IP")

    def validate_ip(self):
        ip = self.validate_entry.get().strip()
        try:
            ipaddress.ip_address(ip)
            self.validation_result.set("✅ Valid IP")
        except:
            self.validation_result.set("❌ Invalid IP")

if __name__ == "__main__":
    root = tk.Tk()
    app = SubnetCalculatorApp(root)
    root.mainloop()
