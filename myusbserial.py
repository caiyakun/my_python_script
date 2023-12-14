
'''
import serial
class Uart2I2c(object):
    def __init__(self, port=None, baud=115200):
        self.port = port
        self.baud = baud
        self.serial = serial.Serial(port, baud, timeout=1)
        self.dev = 0x73
        # self.serial.open()

    def reg_wr(self, addr, val):
        cmd = "-device=0x{:x} -reg=0x{:x} -wdata=0x{:x} -w=1\r\n".format(self.dev, addr, val)
        print("wr reg 0x{:x} = 0x{:x}: \n".format(addr, val), cmd)
        self.serial.write(cmd.encode())
        self.serial.flush()

    def reg_rd(self, addr):
        cmd = "-device=0x{:x} -reg=0x{:x} -wdata=0x{:x} -w=0\r\n".format(self.dev, addr, 0x00000000)
        print("read reg 0x{:x}: \n".format(addr), cmd)
        self.serial.write(cmd.encode())
        # self.serial.flush()
        # return int( str(self.serial.readline().strip()), 16)
        while True:
            res = self.serial.readline()
            
            if res:
                res = res.strip("\r\n".encode()).decode()
                print(res)
                if "rdata" in res:
                    rd_result = res.split("rdata:")[1]
                    rd_result = int(rd_result, 16)
                    return rd_result
            else:
                print("rd fail, no response...")
                break
                
        print(self.serial.read())

    def close(self):
        self.serial.close()

    def test(self):
        pass


if __name__ == "__main__":
    phy = Uart2I2c(port="/dev/ttyUSB0")

    reg = phy.reg_rd(0x00042034)
    print("reg: 0x{:x}".format(reg))

    # read phy1 reg 0x02
    phy.reg_wr(0x00064040, 0x0000008e)
    reg = phy.reg_rd(0x00064044)
    print("reg: 0x{:x}".format(reg))


    phy.close()

'''
import serial
import threading
import time
import sys


ser = serial.Serial('/dev/ttyUSB0', 115200)

# w: 0 read; 1 :write
def write_data(reg='0x00042034', wdata='0x00000000', w='0'):
    device="0x73"
    data = "-device={} -reg={} -wdata={} -w={}\n".format(device, reg, wdata, w)
    ser.write(data.encode())
    time.sleep(0.3)

def read_data():
    try:
        while True:
            if ser.in_waiting > 0:
                data = ser.readline()
                print(data.decode('utf-8'))
    except KeyboardInterrupt:
        sys.exit(0)


def main():
    read_thread = threading.Thread(target=read_data)
    read_thread.start()


    time.sleep(0.5)  # 确保接收线程已经开始运行

    #check default value = 0x000088a8
    # write_data()

    # 0.配置内部寄存器之前需要打开 MAC 时钟和软复位:
    write_data("0x00060000", "0x001F0001", "1") 
    write_data("0x00060004", "0x001F001F", "1") 
    write_data("0x00060008", "0x001F001F", "1") 
    write_data("0x0006000c", "0x001F001F", "1") 

    # 1. chechk read phy1 reg 0x02 = 0007
    write_data("0x00064040", "0x0000008e", "1") 
    write_data("0x00064044", "0x00000000", "0")  

    # # 2. set 100mbps + full-duplex
    # # read phy1 reg 0x00
    # write_data("0x00064040", "0x0000000e", "1") 
    # write_data("0x00064044", "0x00000000", "0")   
    # # write phy1 reg 0x00
    # write_data("0x00064044", "0x00003000", "1") 
    # write_data("0x00064040", "0x0000000c", "1")  
    # # read phy1 reg 0x00
    # write_data("0x00064040", "0x0000000e", "1") 
    # write_data("0x00064044", "0x00000000", "0")  

    # #3.set coma_mode active(drive high)

    # # swith page to 0x0010
    # write_data("0x00064044", "0x00000010", "1") 
    # write_data("0x00064040", "0x000007cc", "1")  

    # print("after reg31 should be 0x0010")
    # write_data("0x00064040", "0x000007ce", "1") 
    # write_data("0x00064044", "0x00000000", "0")  

    # # 
    # print("coma mode reg0x0E -before")
    # write_data("0x00064040", "0x0000034e", "1") 
    # write_data("0x00064044", "0x00000000", "0")  

    # write_data("0x00064044", "0x00001200", "1") 
    # write_data("0x00064040", "0x0000034c", "1") 

    # print("coma mode reg0x0E -after")
    # write_data("0x00064040", "0x0000034e", "1") 
    # write_data("0x00064044", "0x00000000", "0")   


    # #4.config reg23.12:11 to select mac interface mode; Note1.read reg31 must=0 and then set reg23.12:11
    # # read phy1 reg31-> 0x1e  should be 0
    # write_data("0x00064044", "0x00000000", "1") 
    # write_data("0x00064040", "0x000007cc", "1") 
    # print("reg31 should be 0")
    # write_data("0x00064040", "0x000007ce", "1") 
    # write_data("0x00064044", "0x00000000", "0")  

    # print("read reg23")
    # # read phy1 reg23-> 0x17 = 0x1000 
    # write_data("0x00064040", "0x000005ce", "1") 
    # write_data("0x00064044", "0x00000000", "0")   
    # # write phy1 reg23-> 0x17 = 0x00  GMII/MII interface
    # write_data("0x00064044", "0x00000000", "1") 
    # write_data("0x00064040", "0x000005cc", "1")  
    # print("read reg23")
    # # read phy1 reg23-> 0x17 = 0x0000 
    # write_data("0x00064040", "0x000005ce", "1") 
    # write_data("0x00064044", "0x00000000", "0")  

    read_thread.join()
    ser.close()



if __name__ == "__main__":
    main()





        