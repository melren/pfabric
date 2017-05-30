from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
import sys
import socket
import time
import threading

def handleClient(conn, addr): 
    while 1: 
        data = conn.recv(1024)
        if not data:
            break
    conn.close()

def listen(rcv_port, cong, exp_time):
    TIMEOUT = exp_time + 2
    if (cong != "none"):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', rcv_port))
        #s.settimeout(TIMEOUT)
        s.listen(128)
        
        start = time.time()
        while True: #(time.time()-start) < TIMEOUT: 
            try: 
                conn, addr = s.accept() 
                t = threading.Thread(target=handleClient, args=(conn, addr))
                t.start()
            except socket.error:
                continue  
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', rcv_port))
        while (time.time()-start) < TIMEOUT: 
            data, addr = s.recvfrom(1024)     
    
    s.close()


def main():
    rcv_port = int(sys.argv[1])
    cong = sys.argv[2]
    exp_time = int(sys.argv[3])

    listen(rcv_port, cong, exp_time)

if __name__ == '__main__':
    main()


