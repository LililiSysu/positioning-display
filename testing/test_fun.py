import os
import shutil  
from timeit import default_timer as timer

def mkdir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)
        print('new folder created')

    else:
        print('folder exists')


        

tic = timer()
print('here')
toc = timer()

print(toc - tic) # 输出的时间，秒为单位

folder = os.path.exists('test_fold')
if not folder:
    print('file not found')
else:
    if not os.listdir('test_fold'):
        print('empty')
        shutil.rmtree('test_fold')
    else:
        print('not empty')
        shutil.rmtree('test_fold')
