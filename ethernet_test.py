# [option_1] send only
'''
import time
from scapy.all import *

# 构建Ethernet II数据包
pkt = Ether()
# 设置目的MAC地址
# pkt.dst = "08:3a:8d:80:5d:d3" #esp32
pkt.dst = "c4:dd:57:5f:2b:d3" # test e.g. P4/S6

#广播包
#pkt.dst = "ff:ff:ff:ff:ff:ff"
# 设置源MAC地址 
#以太网卡
pkt.src = "a4:bb:6d:b0:b8:14"
#pkt.src = "11:22:33:44:55:66" //self defined
#无线网卡
#pkt.src = "68:77:24:77:63:c9"
# # 自定义Type 
pkt.type = 0x1234 #0x2222
# 构建负载内容 (Test firmware中检查收到的data是否符合发送的)
#ETH_HEADER_LEN = 14
payload = b""
for i in range(1024 - 14): # 1024 -14
    payload += struct.pack("B", i & 0xff) # B represent unsigned char
    # payload += struct.pack("B", 0x5a) # B represent unsigned char
# 将负载内容添加到数据包中
pkt = pkt / payload
# 发送数据包
while True:
    sendp(pkt, iface="enp1s0")    #sendp(pkt, iface="以太网")  
    time.sleep(1)

'''


# [option_2] send + receive
'''
import time
from scapy.all import *

# 定义接收数据包的处理函数
def handle_packet(pkt):
    if pkt.haslayer(Ether):
        if pkt[Ether].dst == "a4:bb:6d:b0:b8:14" or pkt[Ether].dst == "ff:ff:ff:ff:ff:ff":
            print("Received packet:")
            pkt.show()
            # 保存数据包到文本文件
            with open("/home/caiyakun3070/01-FW/00-my_code/00-python/testuse/packets.txt", "a") as file:
                file.write(str(pkt))
                file.write("\n\n")

# 创建接收线程
sniff_thread = threading.Thread(target=sniff, kwargs={"prn": handle_packet, "iface": "enp1s0", "filter": "ether dst a4:bb:6d:b0:b8:14 or ether dst ff:ff:ff:ff:ff:ff"})

# 启动接收线程
sniff_thread.start()

# 构建Ethernet II数据包
pkt = Ether()
pkt.dst = "c4:dd:57:5f:2b:d3" # 目的MAC地址
pkt.src = "a4:bb:6d:b0:b8:14" # 源MAC地址
pkt.type = 0x1234 # 自定义Type

# 构建负载内容
payload = b""
for i in range(1024 - 14):
    payload += struct.pack("B", i & 0xff)

# 将负载内容添加到数据包中
pkt = pkt / payload

# 发送数据包
while True:
    sendp(pkt, iface="enp1s0")
    time.sleep(1)
'''

# [option_3] receive only
import time
from scapy.all import *

# 定义接收数据包的处理函数
def handle_packet(pkt):
    if pkt.haslayer(Ether):
        # if pkt[Ether].dst == "a4:bb:6d:b0:b8:14" or pkt[Ether].dst == "ff:ff:ff:ff:ff:ff":
        if pkt[Ether].dst == "a4:bb:6d:b0:b8:14":    
            print("Received packet:")
            hex_data = hexdump(pkt, dump=True)  # 获取十六进制表示的数据包
            # 保存数据包到文本文件
            # with open("/home/caiyakun3070/01-FW/00-my_code/00-python/testuse/eth_packets.txt", "a") as file:   #need check the path
            with open("eth_packets.txt", "a") as file: #packets.txt 文件将will被创建在current目录下
                file.write(hex_data)
                file.write("\n\n")
                print("write done!")    

# 创建接收线程
sniff_thread = threading.Thread(target=sniff, kwargs={"prn": handle_packet, "iface": "enp1s0", "filter": "ether dst a4:bb:6d:b0:b8:14 or ether dst ff:ff:ff:ff:ff:ff"})

# 启动接收线程
sniff_thread.start()

# 让程序持续运行，以便接收数据包
while True:
    time.sleep(1)