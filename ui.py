import tkinter as tk
from tkinter import ttk
import socket
import psutil

me=0 #my socket
status_label=0

def check_connectivity():
    """Check if the system is connected to the internet."""
    try:
        # Try to connect to a public DNS server (Google)
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def check_network_type():
    """Check if connected via Wi-Fi or Ethernet."""
    interfaces = psutil.net_if_addrs()
    
    for interface in interfaces:
        if "Wi-Fi" in interface or "wlan" in interface.lower():
            return "Wi-Fi"
        elif "Ethernet" in interface or "eth" in interface.lower():
            return "Ethernet"
    
    return "Unknown"

def update_status():
    """Update the network status label."""
    is_connected = check_connectivity()
    
    if is_connected:
        network_type = check_network_type()
        status_label.config(text=f"✅ Connected via {network_type}", fg="green")
    else:
        status_label.config(text="❌ No Internet Connection", fg="red")
def open_to_app():
    global me
    me=socket.create_server(("0.0.0.0",20),reuse_port=True)

# Create the main window
def main():
	root = tk.Tk()
	root.title("Network Connectivity Checker")
	root.geometry("350x200")

	# Label to display network status
	status_label = tk.Label(root, text="Checking network...", font=("Arial", 12))
	status_label.pack(pady=20)

	# Button to refresh network status
	refresh_button = ttk.Button(root, text="Check Connection", command=update_status)
	refresh_button.pack(pady=10)

	# Initial network status check
	update_status()

	# Run the application
	root.mainloop()
