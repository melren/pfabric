from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
import errno
import sys
import socket
import time
import threading
import fcntl

def writeToFile(sendIP, rcv_ip, rcv_time, count, outfile):
    rcv_time = "{:.4f}".format(rcv_time);
    result = "RCVD {} {} {} {}\n".format(sendIP, rcv_ip, count, rcv_time)
    with open(outfile, "a") as f:
        while True:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB) #lock the file
                break
            except IOError as e:
                if e.errno != errno.EAGAIN:                    
                    raise
                else:
                    time.sleep(0.1)

        f.write(result)
        fcntl.flock(f, fcntl.LOCK_UN)


def handleClient(conn, addr, rcv_ip, outfile): 
    numBytes = 0
    while 1: 
        data = conn.recv(1024)
        if data:
            numBytes += len(data)
        else:
            break
    conn.close()
    count = numBytes/1024.0
    writeToFile(addr[0], rcv_ip, time.time(), int(count), outfile)

def listen(rcv_ip, rcv_port, cong, exp_time, outfile):
    TIMEOUT = exp_time + 2
    if (cong != "none"):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', rcv_port))
        #s.settimeout(TIMEOUT)
        s.listen(128)
        
        start = time.time()
        threads = p[]
        while (time.time()-start) < TIMEOUT: 
            try: 
                conn, addr = s.accept() 
                t = threading.Thread(target=handleClient, args=(conn, addr, rcv_ip, outfile))
                threads.append(t)
                t.start()

            except socket.error:
                continue  
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', rcv_port))
        while (time.time()-start) < TIMEOUT: 
            data, addr = s.recvfrom(1024)     
    
    for t in threads:
        t.join()
        
    s.close()


def main():

    rcv_addr = sys.argv[1]
    cong = sys.argv[2]
    exp_time = int(sys.argv[3])
    load = float(sys.argv[4])
    output = sys.argv[5]

    rcv_ip = rcv_addr.split(":")[0]
    rcv_port = int(rcv_addr.split(":")[1])

    outfile = "{}/rcvlog_load{}.txt".format(output, int(load*10))

    listen(rcv_ip, rcv_port, cong, exp_time, outfile)

if __name__ == '__main__':
    main()


