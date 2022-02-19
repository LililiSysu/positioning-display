import socket
import os

device_number = 2
device_name = ['my car', 'my tool']
device_IP = ['8080','6480']

def mkdir(path):                #创建文件夹
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)

def working():
        global device_number
        global device_name
        global device_IP

        # 1.创建套接字
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
        # 2.绑定一个本地信息
        localaddr = ("",7788)                               # 必须绑定自己电脑IP和port
        udp_socket.bind(localaddr)        

        num = [0] *  device_number         # 用一个变化的数字命名不同的文件
        f_num = [0] *  device_number       # 清除上次的文件
        for Dev_number in range( device_number):
            mkdir("rec//" + device_name[Dev_number])            # 为不同设备创建文件夹
            while(1):
                if os.path.exists("rec//" + device_name[Dev_number] + '//site_' + str(f_num[Dev_number]) + ".json"):
                    os.remove("rec//" + device_name[Dev_number] + '//site_' + str(f_num[Dev_number]) + ".json")
                    f_num[Dev_number] = f_num[Dev_number] + 1
                else:
                    break

        # 写入设备名，作为json保存给html读取
        with open("rec//device_name.json", "w", encoding='utf-8') as f:
            f.write('Name({\n')
            f.write('\t device_num:' + str(device_number) + '\n')
            for i in range(device_number):
                f.write('\t dev' + str(i) + ':' + device_name[i] + '\n')
            f.write('})')

        # 记录数据状态
        flag = [0] *  device_number                 # 收到4条数据：（1）纬度，（2）经度，（3）日期，（4）时间。才算收到一个位置信息，设置状态为1
        device_json = [''] *  device_number         # 为每个设备创建json字符

        # 3.接收数据
        while True:
            recv_data = udp_socket.recvfrom(1024)
            # recv_data存储元组（接收到的数据，（发送方的ip,port））
            recv_msg = recv_data[0]                         # 信息内容
            send_addr = recv_data[1]                        # 信息地址
        
            tmp_s = str(send_addr)
            rec_IP = tmp_s[tmp_s.find(', ')+2:-1]           # 设备地址
            
            if rec_IP in  device_IP:                    # 区分不同设备！！！可能需要改
                device_N =  device_IP.index(rec_IP)     # 设备号，从0到N-1
                recv_s = recv_msg.decode("gbk")             # 接收到的字符串
                if recv_s[0] == '#' and recv_s[15] == '#':  # 判断是否有效
                    recv_s_type = recv_s[1:recv_s.find(':')]               # 4种类型的数据：（1）Lat，（2）Lng，（3）Dat，（4）Time
                    recv_s_content = recv_s[recv_s.find(':')+1 : -1]       # 数据的内容

                    #写json字符, 判断4条数据的顺序及有效性 
                    if flag[device_N] == 0:
                        if recv_s_type == 'Lat':
                            device_json[device_N] = device_json[device_N] + 'Up({\n'   # 写json头
                            device_json[device_N] = device_json[device_N] + '\t ' + recv_s_type + ':' + recv_s_content + ',\n'
                            flag[device_N] = flag[device_N] + 1                        # 数据类型 + 1
                        else:
                            device_json[device_N] = ''
                            
                    elif flag[device_N] == 1:
                        if recv_s_type == 'Lng':
                            device_json[device_N] = device_json[device_N] + '\t ' + recv_s_type + ':' + recv_s_content + ',\n'
                            flag[device_N] = flag[device_N] + 1
                        else:
                            flag[device_N] = 0      #信息不正确，重来
                            device_json[device_N] = ''
                            
                    elif flag[device_N] == 2:
                        if recv_s_type == 'Dat':
                            device_json[device_N] = device_json[device_N] + '\t ' + recv_s_type + ':' + recv_s_content + ',\n'
                            flag[device_N] = flag[device_N] + 1
                        else:
                            flag[device_N] = 0      #信息不正确，重来
                            device_json[device_N] = ''
                            
                    else:
                        if recv_s_type == 'Time':
                            device_json[device_N] = device_json[device_N] + '\t ' + recv_s_type + ':' + recv_s_content + ',\n'
                            #此时结束一个json的写入
                            device_json[device_N] = device_json[device_N] + '})'

                            #写成文件
                            with open("rec//" + device_name[device_N] + '//site_' + str(num[device_N]) + ".json", "w", encoding='utf-8') as f:
                                f.write(device_json[device_N])
                                num[device_N] = num[device_N] + 1
                        
                            #循环到第1类型数据的接收
                            flag[device_N] = 0
                            device_json[device_N] = ''
                            
                        else:
                            flag[device_N] = 0      #信息不正确，重来
                            device_json[device_N] = ''



            # print("信息来自:%s 内容是:%s" %(str(send_addr),recv_msg.decode("gbk")))

        # 5.退出套接字
        udp_socket.close()

working()
