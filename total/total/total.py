import tkinter as tk                        #用户使用界面
from tkinter import messagebox              #用户信息窗口
import os
import shutil                               #清空文件夹
import webbrowser                           #浏览器
from datetime import datetime               #日期和时间计算
#from timeit import default_timer as timer   #测试程序运行时间（回来测试）

#用于私网，本程序默认IP地址：7788(IP_address)，当私网连接多台电脑同时使用时，为避免冲突应改变IP_address
import socket
IP_address = 7788

histroy_step = 100                  #每100个接收文件整合成一个历史文件

class verification_window(tk.Frame):

    #调用时初始化
    def __init__(self):
        global root
        root = tk.Tk()                  #一个python的用户窗口

        # 窗口大小设置为600x600
        root.geometry('600x600+500+50')
                
        super().__init__()
        self.username = tk.StringVar()  #用户名变量
        self.password = tk.StringVar()  #用户密码变量
        self.device_name = []           #设备名变量
        self.device_IP = []             #设备身份变量
        self.unfinish = False           #注册或修改未完成时，设置此falg为1
        
        self.Device_label = []          #存放设备编号的显示位置
        self.name_label = []            #汉字“名称：”的显示位置
        self.name_entry = []            #设备名称输入框的显示位置
        self.IP_label = []              #英文“IP”的显示位置
        self.IP_entry = []              #设备IP输入框的显示位置

        self.add_button = 0             #添加设备的按钮
        self.remove_button = 0          #移除设备的按钮
        self.finish_button = 0          #完成按钮
        self.cancel_button = 0          #取消按钮
        self.fix_in_file_botton = 0     #以文件修改按钮

        self.pack()                     #.pack()用于后面调用函数
        self.user_dict = {}             #用户名和密码的存储字典，存放不同用户信息
        self.device_number = 0          #设备数
        self.control_number = 0         #注册控件数
                
        self.mkdir('rec')               #创建文件夹“rec”于当前目录，存放设备发送过来的信息
        self.mkdir('users')             #创建文件夹“users”于当前目录，存放用户信息
        self.set_user_dict()            #载入已经存在的用户信息
        self.main_window()              #打开用户窗口
        root.mainloop()                 #保持窗口

    ##加密算法，用于对用户的密码和设备IP进行加密，使得设备专属于某个用户
    def encode(self,coding_s):                          #coding_s表示用于加密的字符串
        
        s_username = str(self.username.get())
        s_password = str(self.password.get())           #导入设备名和密码

        mod_n = 0
        for c in s_username:
            mod_n = mod_n + ord(c) * ord(c)

        for c in s_password:
            mod_n = mod_n + ord(c) * ord(c)

        if mod_n % 95 == 0:
            if mod_n == 0:
                mod_n = 29    
            else:
                mod_n = int(mod_n / 7)                  #以上处理，添加用户名和密码到密匙中

        shift = mod_n % 95
        count = ord(s_password[-1])                     #初始化
        encoded_s = ""
        tmp_n = 0
        tmp_mod = len(s_password)
        for c in coding_s:
            encoded_s = encoded_s + chr( (ord(c) -32 + shift * count) % 95 + 32)
            count = (count * ord(s_password[tmp_n]) + 1654) % 65535
            tmp_n = (tmp_n + 1) % tmp_mod               #加密算法

        return encoded_s                                #返回加密结果

    ##解密算法
    def decode(self,coding_s):                          #coding_s，需要解密的字符串
        input_username = str(self.username.get())        
        input_password = str(self.password.get())
        
        mod_n = 0
        for c in input_username:
            mod_n = mod_n + ord(c) * ord(c)

        for c in input_password:
            mod_n = mod_n + ord(c) * ord(c)

        if mod_n % 95 == 0:
            if mod_n == 0:
                mod_n = 29
            else:
                mod_n = int(mod_n / 7)

        shift = mod_n % 95
        count = ord(input_password[-1])
        tmp_n = 0
        tmp_mod = len(input_password)
        solved_code = ""
        for c in coding_s:
            solved_code = solved_code + chr( (ord(c) -32 - shift * count) % 95 + 32)
            count = (count * ord(input_password[tmp_n]) + 1654) % 65535
            tmp_n = (tmp_n + 1) % tmp_mod

        return solved_code                              #解密结果返回

    ##载入用户名和密码，根据以往存留的文件
    def set_user_dict(self):
        self.user_dict = {}
        try:
            with open("users//" + "userInformation.txt" , "r" , encoding='utf-8') as f:
                while True:
                    s1 = f.readline()
                    s2 = f.readline()                   #读取文件的行
                    
                    if s1 == '' and s2 == '':           #读到末尾退出
                        break
                    #载入
                    self.user_dict[s1[s1.index(':')+2 : -1]] = str(s2[s2.index(':')+2 : -1])        #载入到字典self.user_dict

        except:
            pass

    ##载入设备信息，根据不同的用户名
    def set_device_information(self):
        self.device_name = []
        self.device_IP = []

        try:
            with open("users//" +  str(self.username.get()) + ".txt" , "r" , encoding='utf-8') as f:
                self.device_number = 0              #记录设备数量
                while True:
                    s = f.readline()
                    
                    if s == '':
                        break
                    #载入
                    s_tobe_decode = s[s.find('; IP: ') + 6:-1]                              #需要解密的部分
                    s = s[:s.find('; IP: ') + 6] + self.decode(coding_s = s_tobe_decode)    #解密结果
                    self.device_name.append(s[s.find('名称: ') + 4 : s.find('; IP: ')])
                    self.device_IP.append(s[s.find('; IP: ') + 6 :])                        #保存解密结果以供显示
                    self.device_number = self.device_number + 1
            
            return True

        except:
            return False

    #窗口布局，用户窗口的显示界面
    def main_window(self):
        username_label=tk.Label(root,text='用户名:',font=('Arial',12)).place(x=2,y=10)
        username_entry=tk.Entry(root,textvariable=self.username).place(x=65,y=10)
        self.username.set('lilili')                 #初始用户名设置为“lilili”

        password_label=tk.Label(root,text='密码:',font=('Arial',12)).place(x=2,y=35)
        password_entry=tk.Entry(root,textvariable=self.password,show='*').place(x=65,y=35)
        self.password.set('123')                    #初始密码“123”，调试方便用

        # 在按下登录按钮时调用验证函数
        conformation_button = tk.Button(root,text='登录',command=self.working,fg='white',bg='black', activeforeground='white', activebackground='navy',width=8,height=1)
        conformation_button.place(x=6,y=64)

        fix_button = tk.Button(root, text='修改', command=self.fix, fg='white', bg='black', activeforeground='white', activebackground='red', width=8, height=1)
        fix_button.place(x=78,y=64)                 #修改设备信息按钮

        register_button = tk.Button(root, text='注册', command=self.register, fg='white', bg='black', activeforeground='white', activebackground='red', width=8, height=1)
        register_button.place(x=150,y=64)           #注册用户按钮

        clear_button = tk.Button(root, text='注销', command=self.clear_user, fg='white', bg='black', activeforeground='white', activebackground='red', width=8, height=1)
        clear_button.place(x=222,y=64)              #注销用户按钮

        check_button = tk.Button(root, text='现有用户', command=self.check_user, fg='white', bg='black', activeforeground='white', activebackground='red', width=8, height=1)
        check_button.place(x=294,y=64)              #查看现有用户按钮

        quit_button = tk.Button(root, text='退出程序', command=root.destroy, fg='white', bg='black', activeforeground='white', activebackground='red', width=16, height=1)
        quit_button.place(x=450,y=10)               #退出程序按钮
        
    #启动浏览器，当登录成功后，浏览器要在中心设备收到第一条信息后才启动
    def working(self):
        if self.unfinish:
            messagebox.showerror(title='错误', message='请先完成修改或注册')       #不正确的登录时机，提示用户
            return

        if self.verification():
            # 打开浏览器具体操作   
            
            # 先创建使用用户文件标签，供html读取使用，决定载入哪一位用户的设备信息
            with open('rec//on_use.json', "w", encoding='utf-8') as f:
                f.write('Load_user({\n')
                f.write('\t username:"' + str(self.username.get()) + '",\n')
                f.write('})')

            # 先进行文件的书写
            # 1.创建套接字
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
            # 2.绑定一个本地信息
            localaddr = ("",IP_address)                               # 必须绑定自己电脑IP和port，IP_address见代码开头设定
            udp_socket.bind(localaddr)        

            # 文件管理，先创建文件，然后检查文件是否为空，再清除文件中的所有内容
            self.mkdir('rec//' + str(self.username.get()))
            if not os.listdir('rec//' + str(self.username.get())):
                pass                                                  # 空文件夹，不用管
            else:
                 shutil.rmtree('rec//' + str(self.username.get()))
                 self.mkdir('rec//' + str(self.username.get()))       # 清空文件夹，此操作删除了用户所有的设备信息
           

            for Dev_number in range( self.device_number):
                self.mkdir("rec//" + str(self.username.get()) + '//' + self.device_name[Dev_number])            # 为不同设备创建文件夹

            # 写入设备名，作为json保存给html读取
            with open('rec//' + str(self.username.get()) + '//' + 'device_name.json', "w", encoding='utf-8') as f:
                f.write('Name({\n')
                f.write('\t device_Num:' + str(self.device_number) + ',\n')
                f.write('\t devices:"')
                for i in range(self.device_number):
                    f.write(self.device_name[i])     
                    if i != self.device_number -1:
                        f.write(';')

                f.write('",\n})')

            # 记录数据状态
            flag = [0] *  self.device_number                 # 收到4条数据：（1）纬度，（2）经度，（3）日期，（4）时间。才算收到一个位置信息，设置状态为1
            device_json = [''] *  self.device_number         # 为每个设备创建json字符
            num = [0] *  self.device_number                  # 用一个变化的数字命名不同的文件
            flag_webbrouser_open = False                     # 设置不要重复打开浏览器
            
            # 记录历史状态
            rec_dat = ''                                     # 保存时间以比对
            device_histroy_Lat = [''] * self.device_number   # 每个设备的历史文件的内容，Lat为维度
            device_histroy_Lng = [''] * self.device_number   # Lng为经度
            device_histroy_Dat = [''] * self.device_number   # Dat为日期
            device_histroy_Time = [''] * self.device_number  # Time为时间
            device_histroy_num = [0] * self.device_number    # 历史文件的坐标个数
            flag_histroy_exist = [False] * self.device_number# 是否存在历史

            # 3.接收数据
            while True:
                #print('准备收数据')
                recv_data = udp_socket.recvfrom(1024)       # 从电脑IP处收到信息
                #print('已收数据')
                #print('data received')
                #print(recv_data)

                #tic = timer()                               # 记录时间
                #recv_data存储元组（接收到的数据，（发送方的ip,port））
                recv_msg = recv_data[0]                     # 信息内容
                #send_addr = recv_data[1]                   # 信息地址
        
                #tmp_s = str(send_addr)                
                rec_IP = recv_msg[0:2].decode('UTF-8')
            
                if rec_IP in  self.device_IP:                   # 区分不同设备
                    #print('设备匹配')
                    device_N =  self.device_IP.index(rec_IP)    # 设备号，从0到N-1
                    recv_s = recv_msg.decode("gbk")             # 接收到的字符串
                    if recv_s[2] == '#' and recv_s[15] == '#':  # 判断是否有效
                        recv_s_type = recv_s[3]                 # 4种类型的数据：（1）Lat，（2）Lng，（3）Dat，（4）Time
                        recv_s_content = recv_s[recv_s.find(':')+1 : -1]       # 数据的内容

                        #写json字符, 判断4条数据的顺序及有效性 
                        if flag[device_N] == 0:
                            if recv_s_type == 'L':
                                #print('收到纬度')
                                if device_N == 0:           #进入中心设备
                                    if num[0] == 0:
                                        device_json[device_N] = device_json[device_N] + 'Ini_c({\n'   # 写json头，必须先初始化中心
                                    else:
                                        device_json[device_N] = device_json[device_N] + 'Up({\n'   # 写json头
                                elif num[0] == 0:           #中心设备未初始化，后面跳过
                                    #print('跳过1')
                                    continue
                                else:                       #进入非中心设备
                                    if num[device_N] == 0:
                                        device_json[device_N] = device_json[device_N] + 'Ini({\n'   # 写json头，初始化非中心设备
                                    else:
                                        device_json[device_N] = device_json[device_N] + 'Up({\n'    # 写json头

                                #写json内容
                                if recv_s_content[-1] == 'N':
                                    device_json[device_N] = device_json[device_N] + '\t ' + 'Lat' + ':' + recv_s_content[1:-1] + ',\n'     #北纬
                                elif recv_s_content[-1] == 'S':
                                    device_json[device_N] = device_json[device_N] + '\t ' + 'Lat' + ':-' + recv_s_content[1:-1] + ',\n'    #南纬
                                else:
                                    device_json[device_N] = ''                             # 错误的情况
                                    continue

                                flag[device_N] = flag[device_N] + 1                        # 数据类型 + 1
                            else:
                                device_json[device_N] = ''
                                continue
                            
                        elif flag[device_N] == 1:
                            #print(recv_s_type)
                            if recv_s_type == 'G':                                
                                #print('收到经度')
                                #写json内容
                                if recv_s_content[-1] == 'E':
                                    device_json[device_N] = device_json[device_N] + '\t ' + 'Lng' + ':' + recv_s_content[:-1] + ',\n'     #东经
                                elif recv_s_content[-1] == 'W':                                   
                                    if recv_s_content[0] == ' ':
                                        device_json[device_N] = device_json[device_N] + '\t ' + 'Lng' + ':-' + recv_s_content[1:-1] + ',\n'    #去掉前面的空格
                                    else:
                                        device_json[device_N] = device_json[device_N] + '\t ' + 'Lng' + ':-' + recv_s_content[:-1] + ',\n'    #西经
                                else:
                                    flag[device_N] = 0
                                    device_json[device_N] = ''                             # 错误的情况
                                    continue

                                flag[device_N] = flag[device_N] + 1
                            else:
                                flag[device_N] = 0      #信息不正确，重来
                                device_json[device_N] = ''
                                continue
                            
                        elif flag[device_N] == 2:
                            if recv_s_type == 'D':
                                #print('收到日期')
                                device_json[device_N] = device_json[device_N] + '\t ' + 'Dat' + ':"' + recv_s_content + '",\n'
                                flag[device_N] = flag[device_N] + 1
                                rec_dat = recv_s_content
                            else:
                                flag[device_N] = 0      #信息不正确，重来
                                device_json[device_N] = ''
                                continue
                            
                        else:
                            if recv_s_type == 'T':
                                #print('收到时间')
                                try:
                                    rec_datetime = datetime.strptime(str(rec_dat + ' ' + recv_s_content[:-1]),"%Y/%m/%d %H:%M:%S")       #转换成datetime格式，计算时间差
                                except:
                                    #print('时间出错')
                                    flag[device_N] = 0      #信息不正确，重来
                                    device_json[device_N] = ''
                                    continue
                                curr_time = datetime.now()                                                #当前时间
                                if (curr_time - rec_datetime).days < 0 or ((curr_time - rec_datetime).days == 0 and (curr_time - rec_datetime).seconds <= 40):   #时间差小于40秒才会自动同步   
                                    #print('此时同步')
                                    #查看是否存在历史，如果存在则写为历史文件
                                    if flag_histroy_exist[device_N]:
                                        #书写历史文件
                                        self.mkdir('rec//' + str(self.username.get()) + '//' + self.device_name[device_N] + '//histroy')        #创建历史文件夹
                                        with open('rec//' + str(self.username.get()) + '//' + self.device_name[device_N] + '//histroy//[' 
                                                  + device_histroy_Dat[device_N][:4] + '.' + device_histroy_Dat[device_N][5:7] + '.' 
                                                  + device_histroy_Dat[device_N][8:10] + '] '+ device_histroy_Time[device_N][:2] + '.'
                                                  + device_histroy_Time[device_N][3:5] + ' - ' + device_histroy_Time[device_N][-9:-7] + '.'
                                                  + device_histroy_Time[device_N][-6:-4] + '.txt','w',encoding='utf-8') as f:                   #文件名，指示历史的起始和结束时间
                                            f.write('[' + str(device_N + 1) + ']' + self.device_name[device_N] + '\n')   #第一行
                                            f.write('record_num:' + str(device_histroy_num[device_N]) + '\n')            #第二行                                            
                                            f.write("Lat:" + device_histroy_Lat[device_N][:-1] + '\n')                   #第三行
                                            f.write("Lng:" + device_histroy_Lng[device_N][:-1] + '\n')                   #第四行
                                            f.write("Time:" + device_histroy_Time[device_N][:-1] + '#')                  #第六行

                                        #清空数据
                                        device_histroy_Lat[device_N] = ''
                                        device_histroy_Lng[device_N] = ''
                                        device_histroy_Dat[device_N] = ''
                                        device_histroy_Time[device_N] = ''
                                        device_histroy_num[device_N] = 0
                                        flag_histroy_exist[device_N] = False

                                    #最后的文件写入，NUM是设备号，从0开始，给html辨别，不然加载设备错误
                                    device_json[device_N] = device_json[device_N] + '\t ' + 'Time' + ':"' + recv_s_content[:-1] + '",\n' + '\t NUM:' + str(device_N) + ',\n'
                                    if num[device_N] == 0:
                                        device_json[device_N] += '\t JMP:1,\n})'        #如果是初始化设备，设置跳转到文件名称
                                    else:
                                        device_json[device_N] += '})'                   #非初始化设备，结束写入json
                                    #此时结束一个json的写入
                                    #写成文件
                                    with open('rec//' + str(self.username.get()) + '//' + self.device_name[device_N] + '//site_' + str(num[device_N]) + '.json', "w", encoding='utf-8') as f:
                                        f.write(device_json[device_N])
                                        num[device_N] = num[device_N] + 1               #文件编号自加一
                                        
                                    #（新增）
                                    #查看是否整合成历史文件
                                    #histroy_step = 100                  #每100个接收文件整合成一个历史文件，此变量已经以到代码的开头
                                    if num[device_N] % histroy_step == 5 and num[device_N] != 5:        #当有多余的5个文件才将历史文件转出来
                                        self.file_emerge(device_N, num[device_N]- histroy_step - 5, histroy_step)

                                    #（新增）

                                else:
                                    #print('此时不能同步')
                                    #写到历史数据中保存
                                    if device_histroy_Dat[device_N] != '' and device_histroy_Dat[device_N] != rec_dat:      #跨日，则保存一份历史文件
                                        #书写历史文件
                                        self.mkdir('rec//' + str(self.username.get()) + '//' + self.device_name[device_N] + '//histroy')        #创建历史文件夹
                                        with open('rec//' + str(self.username.get()) + '//' + self.device_name[device_N] + '//histroy//[' 
                                                  + device_histroy_Dat[device_N][:4] + '.' + device_histroy_Dat[device_N][5:7] + '.' 
                                                  + device_histroy_Dat[device_N][8:10] + '] '+ device_histroy_Time[device_N][:2] + '.'
                                                  + device_histroy_Time[device_N][3:5] + ' - ' + device_histroy_Time[device_N][-9:-7] + '.'
                                                  + device_histroy_Time[device_N][-6:-4] + '.txt','w',encoding='utf-8') as f:
                                            f.write('[' + str(device_N + 1) + ']' + self.device_name[device_N] + '\n')   #第一行
                                            f.write('record_num:' + str(device_histroy_num[device_N]) + '\n')       #第二行                                            
                                            f.write("Lat:" + device_histroy_Lat[device_N][:-1] + '\n')              #第三行
                                            f.write("Lng:" + device_histroy_Lng[device_N][:-1] + '\n')              #第四行
                                            f.write("Time:" + device_histroy_Time[device_N][:-1] + '#')             #第六行

                                        #清空数据
                                        device_histroy_Lat[device_N] = ''
                                        device_histroy_Lng[device_N] = ''
                                        device_histroy_Dat[device_N] = ''
                                        device_histroy_Time[device_N] = ''
                                        device_histroy_num[device_N] = 0
                                        flag_histroy_exist[device_N] = False

                                    #print('device_N:', device_N)
                                    device_histroy_Dat[device_N] = rec_dat
                                    device_histroy_Lat[device_N] += device_json[device_N][device_json[device_N].find(":")+1:device_json[device_N].find(",")] + ';'
                                    device_histroy_Lng[device_N] += device_json[device_N][device_json[device_N].find("Lng:")+4:device_json[device_N].find(",\n\t Dat")] + ';'                                    
                                    device_histroy_Time[device_N] += recv_s_content[:-1] + ';'      #以上两条，将json的Lat，Lng信息提取出来
                                    device_histroy_num[device_N] += 1
                                    flag_histroy_exist[device_N] = True

                                #循环到第1类型数据的接收
                                flag[device_N] = 0
                                device_json[device_N] = ''
                            
                            else:
                                flag[device_N] = 0      #信息不正确，重来
                                device_json[device_N] = ''
                                continue

                # print("信息来自:%s 内容是:%s" %(str(send_addr),recv_msg.decode("gbk")))

                #此处打开浏览器进行地图显示
                if (flag_webbrouser_open == False) and (num[0] == 1) :        #中心设备已经收到数据，可以打开浏览器
                   path=os.path.abspath('.')                                  #获取绝对路径
                   webbrowser.open(path + "\\baidu_hello_world_5.html")       #使用浏览器打开html文件“baidu_hello_world_5.html”
                   flag_webbrouser_open = True
                
                #toc = timer()                       # 计时结束
                #print('precess time:', toc - tic)   # 输出的时间，秒为单位

            # 5.退出套接字
            udp_socket.close()
    
    ##创建文件
    def mkdir(self,path):
        #创建文件夹
        folder = os.path.exists(path)       #看是否存在文件夹

        if not folder:
            os.makedirs(path)               #不存在文件夹，则新建文件夹

    ##历史文件的融合（新增）
    def file_emerge(self, device_N, bias, merge_size):             #输入设备编号device_N，融合文件起始偏移bias，融合文件大小merge_size
        Lat_merge = ''
        Lng_merge = ''
        Dat_merge = ''
        Time_merge = ''                     #融合变量初始化为空字符串

        file_mark = 0                       #已经融合的文件计数
        file_site = 'site_' + str(bias + file_mark) + '.json'      #设置融合文件名

        while os.path.exists('rec//' + str(self.username.get()) + '//' + self.device_name[device_N] + '//' + file_site):                           #循环读取文件
            with open('rec//' + str(self.username.get()) + '//' + self.device_name[device_N] + '//' + file_site , "r" , encoding='utf-8') as f:    #读入文件
                s = f.readline()                                   #忽略第一行
                s = f.readline()                                   #第二行Lat
                Lat_merge += s[s.find(':')+1:s.find(',')] + ';'
                s = f.readline()                                   #第三行Lng    
                Lng_merge += s[s.find(':')+1:s.find(',')] + ';'
                s = f.readline()                                   #第四行Dat
                if Dat_merge == '':
                    Dat_merge = s[s.find(':"')+2:s.find('",')]     #如果Dat_merge空，载入第一个读到的日期，否则不处理Dat数据 
                
                s = f.readline()                                   #第五行Time
                Time_merge += s[s.find(':"')+2:s.find('",')] + ';' 

            if bias + file_mark != 0:       #删除已经融合的文件
                os.remove('rec//' + str(self.username.get()) + '//' + self.device_name[device_N] + '//' + file_site)
            file_mark += 1                  #文件名加一，表示读取下一个文件
            if file_mark % merge_size == 0: #融合文件已经读完
                #print('中断历史文件融合')
                break
        
            file_site = 'site_' + str(bias + file_mark) + '.json'   #重置读取文件

        #更改初始化文件跳转，让浏览器能加载未融合的文件
        with open('rec//' + str(self.username.get()) + '//' + self.device_name[device_N] + '//site_0.json',"r",encoding='utf-8') as f:
            s_ini = f.read()
        s_ini = s_ini[:s_ini.find('JMP:')+4] + str(bias + file_mark) + ',\n})'

        with open('rec//' + str(self.username.get()) + '//' + self.device_name[device_N] + '//site_0.json',"w",encoding='utf-8') as f:
            f.write(s_ini)           #写初始化文件

        self.mkdir('rec//' + str(self.username.get()) + '//' + self.device_name[device_N] + '//histroy')#创建历史文件夹
        with open('rec//' + str(self.username.get()) + '//' + self.device_name[device_N] + '//histroy//[' 
                    + Dat_merge[:4] + '.' + Dat_merge[5:7] + '.' + Dat_merge[8:10] + '] '
                    + Time_merge[:2] + '.' + Time_merge[3:5] + ' - ' + Time_merge[-9:-7] + '.'
                    + Time_merge[-6:-4] + '.txt','w',encoding='utf-8') as f:                            #写文件名，包含日期，历史的起始时间和结束时间
            f.write('[' + str(device_N + 1) + ']' + self.device_name[device_N] + '\n')   #第一行
            f.write('record_num:' + str(file_mark) + '\n')                               #第二行                                            
            f.write("Lat:" + Lat_merge[:-1] + '\n')                                      #第三行
            f.write("Lng:" + Lng_merge[:-1] + '\n')                                      #第四行
            f.write("Time:" + Time_merge[:-1] + '#')                                     #第六行


    ##验证函数
    def verification(self):
        # 检查用户名和密码 是否在user_dict字典中          

        input_username = str(self.username.get())        
        input_password = str(self.password.get())

        if input_username == '':
            messagebox.showerror(title='输入错误', message='用户名不能为空')
            return False
        if input_password == '':
            messagebox.showerror(title='输入错误', message='密码不能为空')
            return False        #错误提示

        if input_username in self.user_dict:
            encoded_password = self.user_dict[str(self.username.get())]
            

            solved_password = self.decode(coding_s = encoded_password)


            if solved_password == input_password:           #解密后的密码是否能够和密码对上，如果对上则输入密码正确

                # 验证成功后打开提示窗口
                if self.set_device_information():           #验证成功，并且设备文件加载成功       
                    return True
                else:
                    messagebox.showinfo(title='设备文件出错', message='设备文件不存在或格式错误') 
                    return False
            else:
                messagebox.showerror(title='密码错误', message='请重新输入密码')  # 错误提醒     
                return False
        
        else:
            messagebox.showerror(title='用户名错误', message='用户名不存在')  # 错误提醒
            return False

    #修改用户信息
    def fix(self):
        if self.unfinish:
            messagebox.showerror(title='错误', message='请先完成修改或注册')   #需要先完成上一次的修改和注册，不然程序错误
            return

        #验证用户名与密码正确
        if self.verification():
            pass
        else:
            return
                   
        #将设备显示在程序界面中
        for i in range(self.device_number):
            vertical_position = 102 + 25 * (i % 19 )

            self.Device_label.append(tk.Label(root,text=('中心' if i==0 else '') + '[' + str(i + 1) + ']',font=('Arial',12)))
            self.Device_label[i].place(x=2,y=vertical_position)

            self.name_label.append(tk.Label(root,text='名称:',font=('Arial',12)))
            self.name_label[i].place(x=58,y=vertical_position)
            tmp_s = self.device_name[i]
            self.device_name[i]=tk.StringVar()     #导入设备
            self.name_entry.append(tk.Entry(root,textvariable=self.device_name[i]))
            self.name_entry[i].place(x=118,y=vertical_position)
            self.device_name[i].set(tmp_s)
        
            self.IP_label.append(tk.Label(root,text='IP:',font=('Arial',12)))
            self.IP_label[i].place(x=288,y=vertical_position)
            tmp_s = self.device_IP[i]
            self.device_IP[i]=tk.StringVar()  #导入设备
            self.IP_entry.append(tk.Entry(root,textvariable=self.device_IP[i]))
            self.IP_entry[i].place(x=328,y=vertical_position)
            self.device_IP[i].set(tmp_s)

        #添加修改的增加设备，删除设备，完成修改，取消修改的控件
        self.control_number = self.device_number
        self.add_button=tk.Button(root,text='添加设备',command=self.add_device) #command后面加回调函数名称
        self.add_button.place(x=500,y=102)

        self.remove_button=tk.Button(root,text='移除设备',command=self.remove_device) #command后面加回调函数名称
        self.remove_button.place(x=500,y=147)

        self.finish_button=tk.Button(root,text='完成修改',command=self.finish_fixing) #command后面加回调函数名称
        self.finish_button.place(x=500,y=192)

        self.cancel_button=tk.Button(root,text='取消修改',command=self.cancel_fixing) #command后面加回调函数名称
        self.cancel_button.place(x=500,y=237)

        #添加用文件修改设备信息的控件
        self.fix_in_file_botton=tk.Button(root,text='以文件修改',command=self.fix_in_file) #command后面加回调函数名称
        self.fix_in_file_botton.place(x=500,y=282)

        self.unfinish = True

    ##完成修改
    def finish_fixing(self):
        
        #用户设备的修改，更改设备文件
        with open("users//" + str(self.username.get()) + ".txt", "w", encoding='utf-8') as f:
            for i in range(self.control_number):
                f.write("[" + str(i + 1) + "] " +"名称: " + str(self.device_name[i].get()) + '; ' + "IP: " )
                s_tobe_encode =str(self.device_IP[i].get())         #在设备文件中加密IP
                s_encoded = self.encode(coding_s = s_tobe_encode)   #加密操作

                f.write(s_encoded + '\n')

        
        #清空修改控件
        self.clear_controller()

        messagebox.showinfo(title='成功', message="已修改用户" + f'{str(self.username.get())}')
        self.unfinish = False           #以上提示成功

    ##取消修改
    def cancel_fixing(self):
        #清空修改控件
        self.clear_controller()

        messagebox.showinfo(title='成功', message="已取消修改")
        self.unfinish = False

    ##以文件修改
    def fix_in_file(self):

        #破解文件以编辑
        
        file = open("users//" + str(self.username.get()) + "(破解).txt",'w')
        file.close()
        with open("users//" +  str(self.username.get()) + ".txt" , "r" , encoding='utf-8') as f1:
            with open("users//" +  str(self.username.get()) + "(破解).txt" , "w" , encoding='utf-8') as f2:
                while True:
                    s = f1.readline()                   
                    
                    if s == '':
                        break
                    #载入
                    s_tobe_decode = s[s.find('; IP: ') + 6:-1]       #去除回车符
                    s = s[:s.find('; IP: ') + 6] + self.decode(coding_s = s_tobe_decode)      #解除加密
                    f2.write(s+'\n')

          

        #打开破解文件编辑
        os.system("notepad "+ "users//" + str(self.username.get()) + "(破解).txt")

        #更新设备加密文件，删除破解文件
        with open("users//" +  str(self.username.get()) + "(破解).txt" , "r" , encoding='utf-8') as f1:
            with open("users//" +  str(self.username.get()) + ".txt" , "w" , encoding='utf-8') as f2:
                while True:
                    s = f1.readline()
                    
                    if s == '':
                        break
                    #载入
                    s_tobe_encode = s[s.find('; IP: ') + 6:-1]        #去除回车符
                    s = s[:s.find('; IP: ') + 6] + self.encode(coding_s = s_tobe_encode)
                    f2.write(s+'\n')

        os.remove("users//" + str(self.username.get()) + "(破解).txt")


        #清空修改控件
        self.clear_controller()

        messagebox.showinfo(title='成功', message="已修改用户" + f'{str(self.username.get())}')
        self.unfinish = False

    ##清除控件，完成修改和注册后，删除修改和注册产生的按钮，文本框和文字标题
    def clear_controller(self):
        self.add_button.destroy()
        self.finish_button.destroy()
        self.remove_button.destroy()
        self.cancel_button.destroy()
        self.fix_in_file_botton.destroy()
        for i in range(self.control_number):
            self.Device_label[i].destroy()
            self.name_label[i].destroy()
            self.name_entry[i].destroy()
            self.IP_label[i].destroy()
            self.IP_entry[i].destroy()

        self.Device_label=[]
        self.name_label=[]
        self.name_entry=[]
        self.IP_label=[]
        self.IP_entry=[]
        self.device_name = []
        self.device_IP = []

    #注册，新用户开辟一个账号
    def register(self):
        if self.unfinish:
            messagebox.showerror(title='错误', message='请先完成修改或注册')
            return

        
        if str(self.username.get()) == '':
            messagebox.showerror(title='输入错误', message='用户名不能为空')
            return False
        if str(self.password.get()) == '':
            messagebox.showerror(title='输入错误', message='密码不能为空')
            return False

        self.device_name=[]
        self.device_IP=[]           #清空载入的设备名和设备IP信息，清除上一个用户的影响
        #检查用户名是否被占用
        if str(self.username.get()) in self.user_dict:
            messagebox.showerror(title='注册错误', message='用户名已被占用')  # 错误提醒
            return                                                            # 跳出函数

        #注册一个用户
        self.user_dict[str(self.username.get())] = str(self.password.get())

        #设置用户信息        
        
        self.Device_label.append(tk.Label(root,text='中心[1]',font=('Arial',12)))
        self.Device_label[0].place(x=2,y=102)

        self.name_label.append(tk.Label(root,text='名称:',font=('Arial',12)))
        self.name_label[0].place(x=58,y=102)
        self.device_name.append(tk.StringVar())
        self.name_entry.append(tk.Entry(root,textvariable=self.device_name[0]))
        self.name_entry[0].place(x=118,y=102)
        
        self.IP_label.append(tk.Label(root,text='IP:',font=('Arial',12)))
        self.IP_label[0].place(x=288,y=102)
        self.device_IP.append(tk.StringVar())
        self.IP_entry.append(tk.Entry(root,textvariable=self.device_IP[0]))
        self.IP_entry[0].place(x=328,y=102)         #注册的用户界面

                
        #button 组件        
        self.control_number = 1
        self.add_button=tk.Button(root,text='添加设备',command=self.add_device) #command后面加回调函数名称
        self.add_button.place(x=500,y=102)

        self.remove_button=tk.Button(root,text='移除设备',command=self.remove_device) #command后面加回调函数名称
        self.remove_button.place(x=500,y=147)

        self.finish_button=tk.Button(root,text='完成注册',command=self.finish) #command后面加回调函数名称
        self.finish_button.place(x=500,y=192)

        self.cancel_button=tk.Button(root,text='取消注册',command=self.cancel) #command后面加回调函数名称
        self.cancel_button.place(x=500,y=237)

        self.fix_in_file_botton=tk.Button(root,text='以文件注册',command=self.register_in_file) #command后面加回调函数名称
        self.fix_in_file_botton.place(x=500,y=282)

        self.unfinish = True
    
    ##添加设备
    def add_device(self):       #设置回调函数，添加设备，添加一条新的设备输入
        vertical_position = 102 + 25 * ((self.control_number - 1) % 19 + 1)

        self.Device_label.append(tk.Label(root,text='[' + str(self.control_number + 1) + ']',font=('Arial',12)))
        self.Device_label[self.control_number].place(x=2,y=vertical_position)

        self.name_label.append(tk.Label(root,text='名称:',font=('Arial',12)))
        self.name_label[self.control_number].place(x=58,y=vertical_position)
        self.device_name.append(tk.StringVar())
        self.name_entry.append(tk.Entry(root,textvariable=self.device_name[self.control_number]))
        self.name_entry[self.control_number].place(x=118,y=vertical_position)
        
        self.IP_label.append(tk.Label(root,text='IP:',font=('Arial',12)))
        self.IP_label[self.control_number].place(x=288,y=vertical_position)
        self.device_IP.append(tk.StringVar())
        self.IP_entry.append(tk.Entry(root,textvariable=self.device_IP[self.control_number]))
        self.IP_entry[self.control_number].place(x=328,y=vertical_position)

        self.control_number = self.control_number + 1

    ##删除设备
    def remove_device(self):
        #移除最后一个设备
        if self.control_number == 1:
            messagebox.showerror(title='移除错误', message='中心设备不能移除')  # 错误提醒
            return;

        self.control_number = self.control_number - 1
        #删除控件
        self.Device_label[self.control_number].destroy()
        self.name_label[self.control_number].destroy()
        self.name_entry[self.control_number].destroy()
        self.IP_label[self.control_number].destroy()
        self.IP_entry[self.control_number].destroy()

        #移除输入的信息
        del self.Device_label[self.control_number]
        del self.name_label[self.control_number]
        del self.name_entry[self.control_number]
        del self.IP_label[self.control_number]
        del self.IP_entry[self.control_number]
        del self.device_name[self.control_number]
        del self.device_IP[self.control_number]
         
    ##完成注册
    def finish(self):           #回调函数，完成设备添加        
        #用户设备的添加（加密！）
        with open("users//" + str(self.username.get()) + ".txt", "w", encoding='utf-8') as f:
            for i in range(self.control_number):
                f.write("[" + str(i + 1) + "] " +"名称: " + str(self.device_name[i].get()) + '; ' + "IP: " )
                s_tobe_encode =str(self.device_IP[i].get())             #对设备的IP进行加密，让其他用户无法查看
                s_encoded = self.encode(coding_s = s_tobe_encode)

                f.write(s_encoded + '\n')

        #用户账号的添加，下次程序启动时，可以记住用户名和密码，不用重新注册
        with open("users//" + "userInformation.txt" , "a+" , encoding='utf-8') as f:
            f.write("username: " + str(self.username.get()) + '\n') 

            new_password = self.encode(coding_s = str(self.password.get()))


            f.write("password: " + new_password + '\n')

        self.set_user_dict()

        #清空注册控件
        self.clear_controller()

        self.set_user_dict()
        messagebox.showinfo(title='成功', message="已注册用户" +  f'{str(self.username.get())}')
        self.unfinish = False

    ##取消注册
    def cancel(self):
                
        #清空注册控件
        self.clear_controller()

        #删除创建的用户
        del self.user_dict[str(self.username.get())]

        messagebox.showinfo(title='成功', message="已取消注册")
        self.unfinish = False

    ##以文件注册
    def register_in_file(self):
        os.system("notepad "+"users//" +  str(self.username.get()) + ".txt")        #直接写加密问价，不同于以文件修改

        #用户账号的添加
        with open("users//" + "userInformation.txt" , "a+" , encoding='utf-8') as f:
            f.write("username: " + str(self.username.get()) + '\n') 

            new_password = self.encode(coding_s = str(self.password.get()))


            f.write("password: " + new_password + '\n')

        self.set_user_dict()        #重新载入用户名

        #清空修改控件
        self.clear_controller()

        messagebox.showinfo(title='成功', message="已注册用户" + f'{str(self.username.get())}')
        self.unfinish = False

    #注销
    def clear_user(self):
        if self.unfinish:
            messagebox.showerror(title='错误', message='请先完成修改或注册')
            return

        #删除用户信息
        if self.verification():
            os.remove("users//" + str(self.username.get()) + ".txt")
            f_s = ""            #文件的所有字符
            with open("users//" + "userInformation.txt" , "r" , encoding='utf-8') as f:                
                while True:                   
                    s1 = f.readline()
                    s2 = f.readline()
                    
                    if s1 == '' and s2 == '':
                        break
                    #寻找目标用户以清除
                    if s1[s1.index(':')+2 : -1] == str(self.username.get()):
                        pass
                    else:
                        f_s = f_s + s1
                        f_s = f_s + s2

            with open("users//" + "userInformation.txt" , "w" , encoding='utf-8') as f:
                f.write(f_s)

            folder = os.path.exists('rec//' + str(self.username.get()))     #清空历史信息
            if not folder:
                pass
            else:
                 shutil.rmtree('rec//' + str(self.username.get()))          #此用户的设备接收信息全部清空

            self.set_user_dict()
            messagebox.showinfo(title='正确', message=f'成功删除用户{str(self.username.get())}')
        else:
            pass

    #查看现有用户
    def check_user(self):       
        all_user = ""
        for the_user in list(self.user_dict.keys()):
            all_user = all_user + "["
            all_user = all_user + the_user
            all_user = all_user + "] "          #载入所有用户，[]套住显示

        messagebox.showinfo(title='现有用户', message=all_user)     #显示窗口
        

if __name__ == '__main__':
    verification_window()       #主函数main，调用这个窗口打开用户界面
