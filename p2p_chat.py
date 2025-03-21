import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class PeerToPeerChat:
    def __init__(self, root, host, port, peer_host, peer_port):
        self.root = root
        self.root.title("P2P Chat")
        
        self.text_area = scrolledtext.ScrolledText(root, state='disabled', wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.entry = tk.Entry(root)
        self.entry.pack(padx=10, pady=5, fill=tk.X)
        self.entry.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(root, text="Envoyer", command=self.send_message)
        self.send_button.pack(pady=5)
        
        self.host = host
        self.port = port
        self.peer_host = peer_host
        self.peer_port = peer_port
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        
        self.running = True
        threading.Thread(target=self.receive_messages, daemon=True).start()
        
    def send_message(self, event=None):
        message = self.entry.get()
        if message:
            self.sock.sendto(message.encode(), (self.peer_host, self.peer_port))
            self.display_message(f"Moi: {message}")
            self.entry.delete(0, tk.END)
            
    def receive_messages(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                self.display_message(f"Ami: {data.decode()}")
            except:
                break
        
    def display_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + '\n')
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)
        
    def stop(self):
        self.running = False
        self.sock.close()
        self.root.quit()
        
if __name__ == "__main__":
    host = "" # machine address 1
    port = 5000 # machine port 1
    peer_host = "" # machine address 2
    peer_port = 5001 # machine port 2
    
    root = tk.Tk()
    chat = PeerToPeerChat(root, host, port, peer_host, peer_port)
    root.protocol("WM_DELETE_WINDOW", chat.stop)
    root.mainloop()
