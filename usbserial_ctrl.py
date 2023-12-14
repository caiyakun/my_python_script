import serial
import time
from termcolor import colored

##########  ----  Configure setting  ---- #########
'''
In the testing environment, it is desired to operate in 100Mbps MII mode when use external PHY. so:
1.When the link partner supports 1000Mbps, it is necessary to disable auto-negotiation; 
otherwise, both PHYs will negotiate at 1000Mbps. (The rxclk will provide 125Mbps to emac instead of 25Mbps).
2.When the link partner supports 100Mbps, auto-negotiation can be enabled, 
and in this case, the auto-negotiation will settle at 100Mbps. 
Otherwise(disabled case), it is required to force the link to operate at 100Mbps.
'''
# auto negotiate flag:[true]-> auto negotiate; [false]->can force select speed
AUTO_NEGOTIATE_EN_FLAG = False   #True

# PHY_ADDRESS can be set "0x03"、"0x00"、"0x01"、"0x02"or"0x04" depends on my PCB
PHY_ADDRESS = 0x03


class Uart2I2c(object):
    def __init__(self, port=None, baud=115200):
        self.port = port
        self.baud = baud
        self.serial = serial.Serial(port, baud, timeout=1)
        self.dev = 0x73
        # self.serial.open()

    def reg_wr(self, addr, val):
        cmd = "-device=0x{:x} -reg=0x{:x} -wdata=0x{:x} -w=1\n".format(self.dev, addr, val)
        print("wr reg 0x{:x} = 0x{:x}: \n".format(addr, val), cmd)
        self.serial.write(cmd.encode())
        self.serial.flush()
        time.sleep(0.1)

    def reg_rd(self, addr):
        cmd = "-device=0x{:x} -reg=0x{:x} -wdata=0x{:x} -w=0\n".format(self.dev, addr, 0x00000000)
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

    def reg_wr_phy(self, phy_device_addr, phy_reg_addr, phy_reg_wdata):
        # 确认base_addr
        base_addresses = {
            0x03: 0x00062000,
            0x00: 0x00064000,
            0x01: 0x00066000,
            0x02: 0x00068000,
            0x04: 0x0006a000
        }
        if phy_device_addr not in base_addresses:
            print("Invalid phy_device_addr")
            return

        base_addr = base_addresses[phy_device_addr]
        base_addr1 = base_addr + 0x40
        base_addr2 = base_addr + 0x44

        # 根据固定数值的bit，将addr_access_reg转化成16进制，8个占位，高四位补0，定义为ctrl_reg_wdata
        addr_access_reg = (phy_device_addr << 11) | (phy_reg_addr << 6) | (0b0011 << 2) | (0b0 << 1) | 0b0
        ctrl_reg_wdata = "{:08x}".format(addr_access_reg)
        ctrl_reg_wdata = int(ctrl_reg_wdata, 16)  # 将ctrl_reg_wdata转换为整数类型

        # 定义cmd1和cmd2
        cmd1 = "-device=0x{:x} -reg=0x{:08x} -wdata=0x{:04x} -w=1\n".format(self.dev, base_addr2, phy_reg_wdata)
        cmd2 = "-device=0x{:x} -reg=0x{:08x} -wdata=0x{:04x} -w=1\n".format(self.dev, base_addr1, ctrl_reg_wdata)

        # 调用serial相关的write函数发送出去，分两次发送，间隔0.1s
        self.serial.write(cmd1.encode())
        time.sleep(0.1)
        self.serial.write(cmd2.encode())
        # print("Sending command 1:")
        # print("phy_device_addr: 0x{:x}, phy_reg_addr: 0x{:x}, phy_reg_wdata: 0x{:04x}".format(phy_device_addr, phy_reg_addr, phy_reg_wdata))
        # print("Command 1: {}".format(cmd1))
        # print("Sending command 2:")
        # print("phy_device_addr: 0x{:x}, phy_reg_addr: 0x{:x}, ctrl_reg_wdata: 0x{:08x}".format(phy_device_addr, phy_reg_addr, ctrl_reg_wdata))
        # print("Command 2: {}".format(cmd2))

    def reg_wr_extend_phy_dp83867(self, phy_device_addr, phy_extend_reg_addr, phy_reg_wdata):
        self.reg_wr_phy(phy_device_addr,0x0D,0x001f) 
        self.reg_wr_phy(phy_device_addr,0x0E,phy_extend_reg_addr) 
        self.reg_wr_phy(phy_device_addr,0x0D,0x401f) 
        self.reg_wr_phy(phy_device_addr,0x0E,phy_reg_wdata) 

    def reg_rd_extend_phy_dp83867(self, phy_device_addr, phy_extend_reg_addr):
        result = None
        self.reg_wr_phy(phy_device_addr,0x0D,0x001f) 
        self.reg_wr_phy(phy_device_addr,0x0E,phy_extend_reg_addr) 
        self.reg_wr_phy(phy_device_addr,0x0D,0x401f) 
        result = phy.reg_rd_phy(phy_device_addr,0x0E)
        return result


    def reg_rd_phy(self, phy_device_addr, phy_reg_addr):
        # 确认base_addr
        base_addresses = {
            0x03: 0x00062000,
            0x00: 0x00064000,
            0x01: 0x00066000,
            0x02: 0x00068000,
            0x04: 0x0006a000
        }
        if phy_device_addr not in base_addresses:
            print("Invalid phy_device_addr")
            return

        base_addr = base_addresses[phy_device_addr]
        base_addr1 = base_addr + 0x40
        base_addr2 = base_addr + 0x44

        # 设定addr_access_reg[1]为1 ,means read operation
        addr_access_reg = (phy_device_addr << 11) | (phy_reg_addr << 6) | (0b0011 << 2) | (0b1 << 1) | 0b0
        ctrl_reg_wdata = "{:08x}".format(addr_access_reg)
        ctrl_reg_wdata = int(ctrl_reg_wdata, 16)  # 将ctrl_reg_wdata转换为整数类型

        # 定义cmd1
        cmd1 = "-device=0x{:02x} -reg=0x{:08x} -wdata=0x{:04x} -w=1\n".format(self.dev, base_addr1, ctrl_reg_wdata)

        # 调用serial.write函数发送cmd1
        # print("Sending command 1:")
        # print("phy_device_addr:0x{:02x}, phy_reg_addr: 0x{:02x}".format(phy_device_addr, phy_reg_addr))
        # print("Command 1: {}".format(cmd1))
        self.serial.write(cmd1.encode())

        # 定义cmd2
        cmd2 = "-device=0x{:02x} -reg=0x{:08x} -wdata=0x{:04x} -w=0\n".format(self.dev, base_addr2, 0x00000000)

        # 调用serial.write函数发送cmd2
        # print("Sending command 2:")
        # print("Command 2: {}".format(cmd2))

        time.sleep(0.1)
        self.serial.write(cmd2.encode())

        # 读取数据，提取rdata的值
        rd_result = None
        while True:
            res = self.serial.readline()
            if res:
                res = res.strip("\r\n".encode()).decode()
                print(res)
                if "rdata" in res:
                    rd_result = res.split("rdata:")[1]
                    rd_result = int(rd_result, 16)
                    break

        # print("phy_device_addr: 0x{:x}, phy_reg_addr: 0x{:x}, rd_result: 0x{:x}".format(phy_device_addr, phy_reg_addr, rd_result))
        print(" ***************************************[{}]:{}=0x{:04x}".format(hex(phy_device_addr), hex(phy_reg_addr), rd_result))
        # print("\n")
        # print("****** read ******[{}]:{}={}".format(hex(phy_device_addr), hex(phy_reg_addr), hex(rd_result)))
        return rd_result


    def close(self):
        self.serial.close()

    def test(self):
        pass


if __name__ == "__main__":
    phy = Uart2I2c(port="/dev/ttyUSB0")

    # 0.配置内部寄存器之前需要打开 MAC 时钟和软复位:
    phy.reg_wr(0x00060000,0x001F0001)
    phy.reg_wr(0x00060004,0x001F001F)
    phy.reg_wr(0x00060008,0x001F001F)
    phy.reg_wr(0x0006000c,0x001F001F)

    # value = phy.reg_rd(0x00060000)  
    # print("value: 0x{:08X}".format(value))

    # Shoule be 0x88a8
    reg = phy.reg_rd(0x00042034)
    print("reg: 0x{:4x}".format(reg))

    time.sleep(0.5)
    # 0x03 is fpga on borad phy:dp83867is and the other(0x00,0x01.0x02,0x04)are external phy:vsc8541
    if PHY_ADDRESS == 0x03:
        print("!!!!!!!!!!!!!!! Note: FPGA on_board phy address = 0x{:02x} !!!!!!!!!!\n".format(PHY_ADDRESS))

        phy.reg_rd_phy(PHY_ADDRESS,0x00) #  
        phy.reg_rd_phy(PHY_ADDRESS,0x01) # 
        phy.reg_rd_phy(PHY_ADDRESS,0x02) # default = 0x2000
        phy.reg_rd_phy(PHY_ADDRESS,0x03) # default = 0xa231

        # global software reset(reset internal circuit including IEEE-defined register and all the extended registers)
        phy.reg_wr_phy(PHY_ADDRESS,0x1f,0x8000) 
        
        # software reset:reset IEEE-defined standard registers
        phy.reg_wr_phy(PHY_ADDRESS,0x00,0x8000)

        print("\n---check - softeware reset pass or not!!")
        timeout = 1  # 超时时间（秒）
        start_time = time.time()
        while True:
            reg0 = phy.reg_rd_phy(PHY_ADDRESS,0x00)
            if (reg0 & 0x8000) == 0:
                print(colored("softreset pass!!: reg0[0x00]= 0x{:04X}\n".format(reg0),"yellow"))
                break
            
            if time.time() - start_time > timeout:
                print(colored("timeout,softreset fail"),"red")
                break
            time.sleep(0.01)  # 等待10毫秒
            
        # -diable auo-negotiate + force set 100M+ Full-duplex -> not success
        # phy.reg_wr_phy(PHY_ADDRESS,0x00,0x2100) 
        # phy.reg_rd_phy(PHY_ADDRESS,0x00)
        
        # -diable auo-negotiate + force set 10M+ Full-duplex -> can success
        # phy.reg_wr_phy(PHY_ADDRESS,0x00,0x0100)
        

        sgmiicontrol_reg = phy.reg_rd_extend_phy_dp83867(PHY_ADDRESS,0x00d3)
        print(colored("sgmiicontrol_reg !!: sgmiicontrol_reg[0xd3]= 0x{:04X}\n".format(sgmiicontrol_reg),"yellow"))
        
        # enable 6-wire mode. enable SGMII clock to MAC
        phy.reg_wr_extend_phy_dp83867(PHY_ADDRESS,0x00d3,0x4000)
        
        sgmiicontrol_reg = phy.reg_rd_extend_phy_dp83867(PHY_ADDRESS,0x00d3)
        print(colored("sgmiicontrol_reg !!: sgmiicontrol_reg[0xd3]= 0x{:04X}\n".format(sgmiicontrol_reg),"yellow"))

        start_time = time.time()
        linkup_timeout = 6
        link_status = False
        while True:
            phy_status = phy.reg_rd_phy(PHY_ADDRESS,0x11) # read PHY status Register
            print("寄存器值[0x11]: 0x{:04X}\n".format(phy_status))
            
            if time.time() - start_time > linkup_timeout:
                print("已达到超时时间，跳出循环")
                break
            
            if (phy_status & 0x0400) == 0x0400:  # 检查第10位是否为1
                print(colored("link up!!!!!!!!!!!,跳出循环", "yellow"))
                link_status = True
                break
            time.sleep(1)  # 等待1秒

        speed_status = (phy_status >> 14) & 0b11  # 提取bit[15:14]的值

        if link_status:
            if speed_status == 0b00:
                print(colored("成交在10Mbps !", "yellow"))
            elif speed_status == 0b01:
                print(colored("成交在100Mbps !!!", "yellow"))
            elif speed_status == 0b10:
                print(colored("成交在1000Mbps !!", "yellow"))
            else:
                print(colored("无效的值", "red")) 
        else:
            print(colored("link is down!!!!", "red")) 


        phy.reg_wr(0x00041028,0x0000033f) # set 1ms in fpga 40M env
        phy.reg_wr(0x00062004,0x02100C1C) # 打开 MAC0 的频率计数器
        phy.reg_wr(0x00062030,0x00000003) # MAC0 TX/RX on
        rxclk_cnt = phy.reg_rd(0x00062064) # MAC0 RX clk meter cnt  //
        txclk_cnt = phy.reg_rd(0x00062068) # MAC0TX clk meter cnt 
        print("rxclk_cnt: 0x{:08X}".format(rxclk_cnt))
        print("txclk_cnt: 0x{:08X}".format(txclk_cnt))

    elif (PHY_ADDRESS == 0x00) or (PHY_ADDRESS == 0x01) or (PHY_ADDRESS == 0x02) or (PHY_ADDRESS == 0x04):
        print("!!!!!!!!!!!!!!! Note: external phy address = 0x{:02x} !!!!!!!!!!\n".format(PHY_ADDRESS))
        print("write 0x0f = 0x0000 -> reset to page0 first!")
        phy.reg_wr_phy(PHY_ADDRESS,0x1f,0x0000)

        print("--------------------- PHYREG_Read function check-------------------\n")
        # check register first
        phy.reg_rd_phy(PHY_ADDRESS,0x00) # default 0x1040
        phy.reg_rd_phy(PHY_ADDRESS,0x01) # default 0x7949
        phy.reg_rd_phy(0x00,0x02) # default 0x0007
        # phy.reg_rd_phy(0x00,0x03) # default 0x0772      may diff by diff phy ic?
        # phy.reg_rd_phy(0x00,0x04) # default 0x01e1
        # phy.reg_rd_phy(0x00,0x05) # default 0x0000
        # phy.reg_rd_phy(0x00,0x06) # default 0x0004
        print("------------------------------------------------------------------\n")


        time.sleep(0.02)
        phy.reg_rd_phy(PHY_ADDRESS,0x17) # default 0x1000      may changed by hw latch?
        phy.reg_wr_phy(PHY_ADDRESS,0x17,0x0000)

        print("write 0x00 = 0x3000")
        phy.reg_wr_phy(PHY_ADDRESS,0x00,0x3000)
        phy.reg_rd_phy(PHY_ADDRESS,0x00)

        # software reset
        print("write 0x00 = 0xb000")
        phy.reg_wr_phy(PHY_ADDRESS,0x00,0xb000)

        print("\n---check - softeware reset pass or not!!")
        timeout = 1  # 超时时间（秒）
        start_time = time.time()
        while True:
            reg0 = phy.reg_rd_phy(PHY_ADDRESS,0x00)
            if (reg0 & 0x8000) == 0:
                print(colored("softreset pass!!: reg0[0x00]= 0x{:04X}\n".format(reg0),"yellow"))
                break
            
            if time.time() - start_time > timeout:
                print(colored("timeout,softreset fail"),"red")
                break
            time.sleep(0.01)  # 等待10毫秒

        if AUTO_NEGOTIATE_EN_FLAG:
            phy.reg_wr_phy(PHY_ADDRESS,0x1f,0x0000)  # return to  Default-page00
            # autonegotiate en + restart autonegotiate 
            phy.reg_wr_phy(PHY_ADDRESS,0x00,0x1240)
            start_time = time.time()
            negotiagte_timeout = 5
            while True:
                reg_value = phy.reg_rd_phy(PHY_ADDRESS, 0x00)  # 读取寄存器的值
                print("寄存器值[0x00]: 0x{:04X}\n".format(reg_value))
                
                if time.time() - start_time > negotiagte_timeout:
                    print(colored("restart autonegotiation timeout!!!......","red"))
                    break
                
                if (reg_value & 0x0200) == 0x00:  # 检查第9位是否为1,reset autonegotiation
                    print(colored("auto negotiation enable, restart auto_negotiate Done!!!!!!!!!!! skip","yellow"))
                    break
                time.sleep(1)  # 等待1秒
        else:  # auto negotiate disabled
            phy.reg_wr_phy(PHY_ADDRESS,0x1f,0x0000)  # return to  Default-page00
            # disable autonegotiate + set force 100Mbps + full-duplex  NOte: atuo_negotiate and force_speeds_select are mutually exclusive.
            print(colored("auto negotiation disable, force to set 100Mbps!!!......","yellow"))
            phy.reg_wr_phy(PHY_ADDRESS,0x00,0x2100)
            

        # release coma pin -> set ouput mode ;value = 0
        phy.reg_rd_phy(PHY_ADDRESS,0x1f) # default 0x0000
        print("write 0x0f = 0x0010")
        phy.reg_wr_phy(PHY_ADDRESS,0x1f,0x0010)
        # phy.reg_rd_phy(0x00,0x1f) # default 0x0000
        phy.reg_rd_phy(PHY_ADDRESS,0x0e) # page0x10 : 0x0e;default 0x2?00 depends on HW

        print("write 0x0e = 0x0200")
        phy.reg_wr_phy(PHY_ADDRESS,0x0e,0x0200)
        phy.reg_rd_phy(PHY_ADDRESS,0x0e) # page0x10 : 0x0e;default 0x2?00 depends on HW


        print("write 0x0f = 0x0000 -> page0")
        phy.reg_wr_phy(PHY_ADDRESS,0x1f,0x0000)
        phy.reg_rd_phy(PHY_ADDRESS,0x01) # default 0x7949

        start_time = time.time()
        linkup_timeout = 5
        link_status = False
        while True:
            reg_value = phy.reg_rd_phy(PHY_ADDRESS, 0x01)  # 读取寄存器的值
            print("寄存器值[0x00]: 0x{:04X}\n".format(reg_value))
            
            if time.time() - start_time > linkup_timeout:
                print("link timeout, skip!!!")
                break
            
            if (reg_value & 0x04) == 0x04:  # 检查第2位是否为1
                print(colored("link up!!!!!!!!!!!,skip", "yellow"))
                link_status = True
                break
            time.sleep(1)  # 等待1秒

        reg_value = phy.reg_rd_phy(PHY_ADDRESS, 0x1c)  # 读取寄存器的值
        speed_status = (reg_value >> 3) & 0b11  # 提取bit[4:3]的值

        if link_status:
            if speed_status == 0b00:
                print(colored("成交在10Mbps !", "yellow"))
            elif speed_status == 0b01:
                print(colored("成交在100Mbps !!!", "yellow"))
            elif speed_status == 0b10:
                print(colored("成交在1000Mbps !!", "yellow"))
            else:
                print(colored("无效的值", "red")) 
        else:
            print(colored("link is down!!!!", "red")) 

    else:
        print(colored("无效的phy address参数","red"))

        phy.reg_wr(0x00064004,0x02100C1C) # 打开 MAC1 的频率计数器
        phy.reg_wr(0x00064030,0x00000003) # MAC1 TX/RX on
        rxclk_cnt = phy.reg_rd(0x00064064) # MAC1 RX clk meter cnt  // ideal is 0x1e847 @ FPGA 40M
        txclk_cnt = phy.reg_rd(0x00064068) # MAC1 TX clk meter cnt 
        print("rxclk_cnt: 0x{:08X}".format(rxclk_cnt))
        print("txclk_cnt: 0x{:08X}".format(txclk_cnt))

        value = phy.reg_rd(0x00064058) # 确认下随路时钟域复位是否释放 bit[9] rx_rst_st;bit[8] tx_rst_st;
                                    # 1b 表示mac_rx 处在复位态, 0b:mac_rx_clk已经存在，且mac_rx_rst释放了
                                    # 0x00064058[9:8]='b00 which means emac1 is ready to work

        print("value: 0x{:08X}".format(value))
