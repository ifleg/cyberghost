import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import signal
import re
import os

class CyberGhostApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CyberGhost VPN GUI")
        self.geometry("900x650")

        self.proc = None  # running openvpn process

        # --- Country selection ---
        tk.Label(self, text="Country:").pack(anchor="w", padx=10, pady=(10, 0))
        self.country_combo = ttk.Combobox(self, state="readonly", width=50)
        self.country_combo.pack(padx=10, fill="x")
        self.country_combo.bind("<<ComboboxSelected>>", self.load_cities)

        # --- City selection ---
        tk.Label(self, text="City:").pack(anchor="w", padx=10, pady=(10, 0))
        self.city_combo = ttk.Combobox(self, state="readonly", width=50)
        self.city_combo.pack(padx=10, fill="x")
        self.city_combo.config(state="disabled")
        self.city_combo.bind("<<ComboboxSelected>>", self.load_servers)

        # --- Server selection ---
        tk.Label(self, text="Server:").pack(anchor="w", padx=10, pady=(10, 0))
        self.server_combo = ttk.Combobox(self, state="readonly", width=50)
        self.server_combo.pack(padx=10, fill="x")
        self.server_combo.config(state="disabled")
        self.server_combo.bind("<<ComboboxSelected>>", self.update_command_preview)

        # --- Buttons ---
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        self.connect_btn = tk.Button(button_frame, text="Connect", command=self.connect_vpn, state="disabled")
        self.connect_btn.pack(side="left", padx=5)
        self.stop_btn = tk.Button(button_frame, text="Stop", command=self.stop_vpn, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # --- Command preview ---
        tk.Label(self, text="Command preview:").pack(anchor="w", padx=10)
        self.command_box = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=4, bg="#f5f5f5")
        self.command_box.pack(padx=10, fill="x")
        self.command_box.config(state="disabled")

        # --- Output box ---
        tk.Label(self, text="Output:").pack(anchor="w", padx=10, pady=(10, 0))
        self.output_box = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=18)
        self.output_box.pack(padx=10, pady=(0,10), fill="both", expand=True)

        # Internal storage
        self.countries = {}
        self.cities = []
        self.servers = []
        self.selected_country_code = None
        self.selected_city = None

        # Load countries on startup
        threading.Thread(target=self.load_countries, daemon=True).start()

    # ----- Utility -----
    def append_output(self, text):
        self.output_box.insert(tk.END, text + "\n")
        self.output_box.see(tk.END)

    def set_command_preview(self, text):
        self.command_box.config(state="normal")
        self.command_box.delete(1.0, tk.END)
        self.command_box.insert(tk.END, text)
        self.command_box.config(state="disabled")

    # ----- Loaders -----
    def load_countries(self):
        self.append_output("Loading country list...\n")
        try:
            result = subprocess.run(["cyberghostvpn", "--country-code"], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            for line in lines:
                match = re.match(r"\|\s*\d+\s*\|\s*(.*?)\s*\|\s*([A-Z]{2})\s*\|", line)
                if match:
                    name, code = match.groups()
                    self.countries[name.strip()] = code.strip()
            if not self.countries:
                raise RuntimeError("No countries found.")
            sorted_countries = sorted(self.countries.keys(), key=str.lower)
            self.country_combo["values"] = sorted_countries
            self.append_output("Countries loaded.\n")
        except Exception as e:
            self.append_output(f"Error loading countries: {e}\n")

    def load_cities(self, event):
        country_name = self.country_combo.get()
        if not country_name:
            return
        self.selected_country_code = self.countries[country_name]
        self.append_output(f"Loading cities for {country_name} ({self.selected_country_code})...\n")

        self.city_combo.set("")
        self.city_combo.config(state="disabled")
        self.server_combo.config(state="disabled")
        self.connect_btn.config(state="disabled")
        self.servers.clear()
        self.set_command_preview("")

        def worker():
            try:
                result = subprocess.run(
                    ["cyberghostvpn", "--country-code", self.selected_country_code, "--city"],
                    capture_output=True, text=True
                )
                lines = result.stdout.splitlines()
                cities = []
                for line in lines:
                    match = re.match(r"\|\s*\d+\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*\d+%", line)
                    if match:
                        city, _ = match.groups()
                        city = city.strip()
                        if city not in cities:
                            cities.append(city)
                if not cities:
                    raise RuntimeError("No cities found.")
                cities.sort(key=str.lower)
                self.cities = cities
                self.city_combo["values"] = cities
                self.city_combo.config(state="readonly")
                self.append_output(f"Cities loaded for {country_name}.\n")
            except Exception as e:
                self.append_output(f"Error loading cities: {e}\n")

        threading.Thread(target=worker, daemon=True).start()

    def load_servers(self, event):
        self.selected_city = self.city_combo.get()
        if not self.selected_city:
            return

        code = self.selected_country_code
        self.append_output(f"Loading servers for {self.selected_city} ({code})...\n")

        self.server_combo.set("")
        self.server_combo.config(state="disabled")
        self.connect_btn.config(state="disabled")
        self.set_command_preview("")

        def worker():
            try:
                result = subprocess.run(
                    ["cyberghostvpn", "--country-code", code, "--city", self.selected_city],
                    capture_output=True, text=True
                )
                lines = result.stdout.splitlines()
                servers = []
                for line in lines:
                    match = re.match(r"\|\s*\d+\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*\d+%", line)
                    if match:
                        _, instance = match.groups()
                        servers.append(instance.strip())
                if not servers:
                    raise RuntimeError("No servers found.")
                servers.sort(key=str.lower)
                self.servers = servers
                self.server_combo["values"] = servers
                self.server_combo.config(state="readonly")
                self.connect_btn.config(state="normal")
                self.append_output(f"Servers loaded for {self.selected_city}.\n")
            except Exception as e:
                self.append_output(f"Error loading servers: {e}\n")

        threading.Thread(target=worker, daemon=True).start()

    # ----- Command builder -----
    def build_openvpn_command(self, instance):
        return [
            "openvpn",
            "--client",
            "--remote", f"{instance}.cg-dialup.net", "443",
            "--dev", "tun",
            "--proto", "tcp",
            "--auth-user-pass", os.path.expanduser("~/.cyberghost/auth"),
            "--resolv-retry", "infinite",
            "--redirect-gateway", "def1",
            "--persist-key",
            "--persist-tun",
            "--nobind",
            "--data-ciphers", "AES-256-GCM:AES-128-GCM:AES-256-CBC",
            "--data-ciphers-fallback", "AES-256-CBC",
            "--auth", "SHA256",
            "--ping", "5",
            "--script-security", "2",
            "--remote-cert-tls", "server",
            "--route-delay", "5",
            "--verb", "4",
            "--ca", os.path.expanduser("~/.cyberghost/ca.crt"),
            "--cert", os.path.expanduser("~/.cyberghost/client.crt"),
            "--key", os.path.expanduser("~/.cyberghost/client.key"),
        ]

    def update_command_preview(self, event=None):
        instance = self.server_combo.get()
        if not instance:
            self.set_command_preview("")
            return
        cmd = self.build_openvpn_command(instance)
        self.set_command_preview(" ".join(cmd))

    # ----- VPN control -----
    def connect_vpn(self):
        instance = self.server_combo.get()
        if not instance:
            messagebox.showerror("Error", "Please select a server.")
            return

        cmd = self.build_openvpn_command(instance)
        self.set_command_preview(" ".join(cmd))
        self.append_output(f"Connecting to {instance}.cg-dialup.net...\n")

        self.connect_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        def run_openvpn():
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in self.proc.stdout:
                self.append_output(line.strip())
            self.append_output("\n[Disconnected]\n")
            self.proc = None
            self.stop_btn.config(state="disabled")
            self.connect_btn.config(state="normal")

        threading.Thread(target=run_openvpn, daemon=True).start()

    def stop_vpn(self):
        if self.proc and self.proc.poll() is None:
            self.append_output("Stopping VPN connection...\n")
            self.proc.send_signal(signal.SIGINT)
            self.proc = None
            self.stop_btn.config(state="disabled")
            self.connect_btn.config(state="normal")
        else:
            self.append_output("No running VPN process.\n")

if __name__ == "__main__":
    app = CyberGhostApp()
    app.mainloop()

