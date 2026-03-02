import threading
import time

# def func():
#     print("run\n")
#     time.sleep(1)
#     print("x done 1\n")
#     time.sleep(1)
#     print("x done 2\n")

# x=threading.Thread(target=func)
# x.start()
# print(threading.active_count())
# print('\n')
# time.sleep(2)# very intersting, actually I can change to 1,2,0.5 to try
# print("main thread done")



# time0=time.time()
# def count(n):
#     for i in range(1,n+1):
#         print(f"{i}\n")
#         time.sleep(0.01)

# def count2(n):
#     for i in range(1,n+1):
#         print(f"{i}\n")
#         time.sleep(0.1)
# x=threading.Thread(target=count,args=(10,))
# x.start()
# print(time.time()-time0)
# y=threading.Thread(target=count2,args=(10,))
# y.start()
# print(time.time()-time0)
# print("all done")
# print(time.time()-time0)

# ls=[]
# def count(n):
#     for i in range(1,n+1):
#         ls.append(i)
#         time.sleep(0.01)

# def count2(n):
#     for i in range(1,n+1):
#         ls.append(i)
#         time.sleep(0.01)
# x=threading.Thread(target=count,args=(10,))
# x.start()

# y=threading.Thread(target=count2,args=(10,))
# y.start()
# time0=time.time()
# print(ls)
# print('\n')
# print(time.time()-time0) 
# time1=time.time()
# time.sleep(0.1)
# print(ls)
# print(time.time()-time1)

ls=[]
def count(n):
    for i in range(1,n+1):
        ls.append(i)
        time.sleep(0.01)

def count2(n):
    for i in range(1,n+1):
        ls.append(i)
        time.sleep(0.01)
x=threading.Thread(target=count,args=(10,))
x.start()
x.join()
y=threading.Thread(target=count2,args=(10,))
y.start()


print(ls)
print('\n')

y.join()
time.sleep(0.000001)
print(ls)