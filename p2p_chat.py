import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk
import ipaddress

class PeerToPeerChat:
    def __init__(self, root, host, port):
        self.root = root
        self.root.title("P2P Chat")
        
        self.text_area = scrolledtext.ScrolledText(root, state='disabled', wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.entry = tk.Entry(root)
        self.entry.pack(padx=10, pady=5, fill=tk.X)
        self.entry.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)
        
        self.scan_button = tk.Button(root, text="Scan clients", command=self.scan_clients)
        self.scan_button.pack(pady=5)
        
        self.client_list = ttk.Combobox(root, state="readonly")
        self.client_list.pack(padx=10, pady=5, fill=tk.X)
        self.client_list.bind("<<ComboboxSelected>>", self.select_client)
        
        self.host = host
        self.port = port
        self.peer_addr = None  # Stores last reception address known
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        
        self.running = True
        threading.Thread(target=self.receive_messages, daemon=True).start()
        
        self.clients = set()
        
    def send_message(self, event=None):
        if not self.peer_addr:
            self.display_message("Error: No reception address known.")
            return
        
        message = self.entry.get()
        if message:
            self.sock.sendto(message.encode(), self.peer_addr)
            self.display_message(f"Moi: {message}")
            self.entry.delete(0, tk.END)
            
    def receive_messages(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                
                if data == b'DISCOVER':
                    self.sock.sendto(b'RESPONSE', addr)  # Send a reply to be discovered
                
                if data == b'RESPONSE' or data == b'DISCOVER':
                    self.clients.add(addr[0])  # Add client to the list
                    self.update_client_list()
                    
                if self.peer_addr is None:
                    self.peer_addr = addr 
                    self.display_message(f"Connection established with {addr[0]}:{addr[1]}")
                
                if data not in [b'DISCOVER', b'RESPONSE']:
                    self.display_message(f"{addr[0]}:{addr[1]} -> {data.decode()}")
            except:
                break
        
    def display_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + '\n')
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)
        
    def scan_clients(self):
        local_ip = self.get_local_ip()
        if local_ip:
            subnet = ipaddress.ip_network(local_ip + "/24", strict=False)
            self.display_message("Network scan in progress...")
            
            for ip in subnet.hosts():
                if str(ip) != local_ip:  
                    self.sock.sendto(b'DISCOVER', (str(ip), self.port))
        else:
            self.display_message("Unable to detect local IP address.")
        
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return None
        
    def update_client_list(self):
        self.client_list["values"] = list(self.clients)
        
    def select_client(self, event):
        selected_ip = self.client_list.get()
        self.peer_addr = (selected_ip, self.port)
        self.display_message(f"Recipient defined: {self.peer_addr[0]}:{self.peer_addr[1]}")
        
    def stop(self):
        self.running = False
        self.sock.close()
        self.root.quit()
        
if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5000  # uses port 5000
    
    root = tk.Tk()
    chat = PeerToPeerChat(root, host, port)
    root.protocol("WM_DELETE_WINDOW", chat.stop)
    root.mainloop()
