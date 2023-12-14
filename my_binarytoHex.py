def binary_to_hex(binary):
    # 将二进制字符串转为整数，再转为十六进制字符串，最后将前两个字符（'0x'）去掉
    hex_value = hex(int(binary, 2))[2:]
    # 使用 zfill 函数在十六进制数前面补零，直到长度为4
    return hex_value.upper().zfill(4)

# 创建一个字典来存储每个位的值
bits = {}
### EMAC_MDIO_ADDRESS_REG/      base_addr + 0x40
#PHY Deviced address:[15:11] = 0x00 (L2 Switch have 5 phy)
BIT_15 = 0
BIT_14 = 0
BIT_13 = 0
BIT_12 = 0
BIT_11 = 0

#PHY reg address:[10:6]
BIT_10 = 0
BIT_9 = 0
BIT_8= 0
BIT_7 = 0
BIT_6 = 0

#分频选择MDIO/MDC 时钟 ,配置 0011b  ；//sys_clk 40MHz
BIT_5 = 0
BIT_4 = 0
BIT_3 = 1
BIT_2 = 1

# write:1  ;  read:0
BIT_1 = 1

# 1b表示SMA正在操作MDIO，0b表示SMA操作MDIO完成
BIT_0 = 0


# 设定每个位的值
for i in range(16):
    bits[i] = str(globals()["BIT_" + str(i)]) # 等效 bits[0] = str(BIT_0)  bits[1] = str(BIT_1)  bits[2] = str(BIT_2) ...

# 创建一个字符串，其中包含所有的二进制位，注意我们需要反转位的顺序
binary_data = "".join(bits[i] for i in reversed(range(16)))

# 转换二进制字符串为十六进制数
hex_value = binary_to_hex(binary_data)
print("转换结果为0x" + hex_value)


#-device=0x73 -reg=0x00064040 -wdata=0x0000008e -w=1
#-device=0x73 -reg=0x00064044 -wdata=0x00000000 -w=0