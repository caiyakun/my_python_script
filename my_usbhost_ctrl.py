import usb.core
import usb.util
import time
import sys

from scapy.all import *  # to use hexdump() function

# 1. 枚举USB设备，找到指定的VENDOR_ID和PRODUCT_ID
VENDOR_ID = 0x303A
PRODUCT_ID = 0x4001

# 打开 USB 设备
dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
if dev is None:
    raise ValueError("USB CDC device not found.")
else:
    print("USB CDC_Device Founded!")

dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
if dev is None:
    raise ValueError("USB-CDC设备未找到")

# 2. 获取USB设备的枚举信息并打印
print("设备描述符：")
print(dev)
print()

# 获取配置描述符
cfg = dev.get_active_configuration()
# print("配置描述符：")
# print(cfg)
# print()

# 获取接口描述符
intf = usb.util.find_descriptor(cfg, bInterfaceClass=0x0a)  # 根据bInterfaceClass查找接口
# print("接口描述符：")
# print(intf)
# print()

# 获取端点描述符
ep_out = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
ep_in = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
# print("端点描述符：")
# print("OUT: ", ep_out)
# print("IN: ", ep_in)
# print()


# 3. 使用必要的信息进行数据通信
# 这里假设需要的信息是设备地址、接口号、端点号等

# # 获取设备地址
# device_address = dev.address

# # 获取接口号
interface_number = intf.bInterfaceNumber

# Fix the error of "usb.core.USBError: [Errno 16] Resource busy"
if dev.is_kernel_driver_active(interface_number):
    try:
        dev.detach_kernel_driver(interface_number)
    except usb.core.USBError as e:
        sys.exit("Could not detatch kernel driver from interface({0}): {1}".format(interface_number, str(e)))

# try:
#     dev.attach_kernel_driver(interface_number)
# except usb.core.USBError as e:
#     sys.exit("Could not attach kernel driver to interface({0}): {1}".format(interface_number, str(e)))

# 获取端点号
endpoint_in_address = ep_in.bEndpointAddress
endpoint_out_address = ep_out.bEndpointAddress


# clear content of "output.txt" at the start of python_script runs
with open("output.txt", "w") as file:
    file.write('')


max_attempts = 16
attempt = 0
# 4. 循环执行数据发送和接收
# while True:
while attempt < max_attempts:
    attempt += 1

    # 通过bulk write发送数据
    data_to_send = b"start\0"
    dev.write(endpoint_out_address, data_to_send)

    # 5. 通过bulk read接收数据
    received_data = b""
    while True:
        data = dev.read(endpoint_in_address, ep_in.wMaxPacketSize) # 阻塞; 如果usb device没有数据，将会always阻塞在此
        print("收到一笔data size = ",len(data))
        received_data += data
        if len(data) < ep_in.wMaxPacketSize:
            break
        
    # 打印接收到的数据长度和内容
    print("接收到的total数据长度:", len(received_data))
    # print("接收到的数据内容：", received_data)


    # 将接收到的数据以十六进制格式写入文件
    
    # option 1 : direcly hexadecimal view
    # hex_data = hexdump(received_data, dump=True)  # 获取十六进制表示的数据包
    # with open("output.txt", "a") as file:          #"a"是以文本模式追加写入的方式打开文件
    #     file.write(hex_data)
    #     file.write("\n\n") 

    # option 2 : use Vscode HexEditor 扩展,1. install hexeditor; 2.Ctrl+Shift+P, input keywords : HexEditor,and let it open 
    with open("output.txt", "ab") as file:       #"ab"是以二进制模式追加写入的方式打开文件
        file.write(received_data)

    # time.sleep(1)

print("cai test end !!!")



'''
descriptor = device.ctrl_transfer(
    bmRequestType=usb.util.CTRL_IN | usb.util.CTRL_TYPE_STANDARD,
    bRequest=0x06,  # GET_DESCRIPTOR
    wValue=(0x01 << 8),  # Descriptor type (0x01 for device descriptor)
    wIndex=0,
    data_or_wLength=18
)

# 解析设备描述符字段
length = descriptor[0]
descriptor_type = descriptor[1]
usb_version = (descriptor[3] << 8) + descriptor[2]
device_class = descriptor[4]
device_subclass = descriptor[5]
device_protocol = descriptor[6]
max_packet_size = descriptor[7]
vendor_id = (descriptor[9] << 8) + descriptor[8]
product_id = (descriptor[11] << 8) + descriptor[10]
device_version = (descriptor[13] << 8) + descriptor[12]
manufacturer_string_index = descriptor[14]
product_string_index = descriptor[15]
serial_number_string_index = descriptor[16]
num_configurations = descriptor[17]

# 打印设备描述符字段
print(f"Length: {length}")
print(f"Descriptor Type: {descriptor_type}")
print(f"USB Version: {usb_version}")
print(f"Device Class: {device_class}")
print(f"Device Subclass: {device_subclass}")
print(f"Device Protocol: {device_protocol}")
print(f"Max Packet Size: {max_packet_size}")
print(f"Vendor ID: {vendor_id}")
print(f"Product ID: {product_id}")
print(f"Device Version: {device_version}")
print(f"Manufacturer String Index: {manufacturer_string_index}")
print(f"Product String Index: {product_string_index}")
print(f"Serial Number String Index: {serial_number_string_index}")
print(f"Number of Configurations: {num_configurations}")
'''

'''
# retrive USB-CDC Driver
try:
    dev.attach_kernel_driver(interface_number)
except usb.core.USBError as e:
    sys.exit("Could not attach kernel driver to interface({0}): {1}".format(interface_number, str(e)))
'''