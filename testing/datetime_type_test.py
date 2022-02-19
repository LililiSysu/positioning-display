from datetime import datetime               #日期和时间计算

rec_datetime =datetime.strptime(str('2020/12/12' + ' ' + '22:10:40'),"%Y/%m/%d %H:%M:%S")
curr_time = datetime.now()
print(curr_time.hour)

print((curr_time - rec_datetime).days)
