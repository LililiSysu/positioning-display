import socket
import time
from datetime import datetime               #日期和时间计算

IP_head = "172.26.37.128"

def main():
    # 创建一个套接字
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        send_data = "A1#L: 34.12300N#"
        udp_socket.sendto(send_data.encode("gbk"),(IP_head, 7788))
        time.sleep(0.01)
        send_data = "A1#G:123.12345E#"
        udp_socket.sendto(send_data.encode("gbk"),(IP_head, 7788)) 
        time.sleep(0.01)
        send_data = "A1#D:2020/12/06#"
        udp_socket.sendto(send_data.encode("gbk"),(IP_head, 7788)) 
        time.sleep(0.01)
        
        send_data = "A1#Ti:" + time.strftime("%H:%M:%S", time.localtime()) + " #"
        udp_socket.sendto(send_data.encode("gbk"),(IP_head, 7788)) 
        time.sleep(1)

        send_data = "A2#L: 34.13300N#"
        udp_socket.sendto(send_data.encode("gbk"),(IP_head, 7788))
        time.sleep(0.01)
        send_data = "A2#G:123.11345E#"
        udp_socket.sendto(send_data.encode("gbk"),(IP_head, 7788)) 
        time.sleep(0.01)
        send_data = "A2#D:2020/12/06#"
        udp_socket.sendto(send_data.encode("gbk"),(IP_head, 7788)) 
        time.sleep(0.01)
        
        send_data = "A2#Ti:" + time.strftime("%H:%M:%S", time.localtime()) + " #"
        udp_socket.sendto(send_data.encode("gbk"),(IP_head, 7788)) 
        time.sleep(1)
        

    # 关闭套接字
    udp_socket.close()
if __name__ == '__main__':
    main()
