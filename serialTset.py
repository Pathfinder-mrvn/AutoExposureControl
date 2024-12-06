import serial
import time

# 配置串口参数
port = 'COM7'  # 替换为实际的串口号，例如 '/dev/ttyUSB0' 在 Linux 上
baudrate = 19200  # 波特率，替换为控制器的实际波特率
timeout = 1  # 读取超时设置

ser = None  # 初始化串口对象

try:
    # 创建串口对象
    ser = serial.Serial(port, baudrate, timeout=timeout)

    # 等待串口初始化
    time.sleep(2)  # 有时需要等待串口稳定

    # 发送命令 HX 和回车符
    command = 'HX\r'  # "\r" 是回车符
    ser.write(command.encode('utf-8'))  # 发送命令

    print(f"Sent command: {command.strip()}")

    # 读取响应（如果需要）
    response = ser.readline()  # 读取一行响应
    print(f"Received response: {response.decode('utf-8').strip()}")

except serial.SerialException as e:
    print(f"Serial error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if ser and ser.is_open:  # 确保 ser 被定义并且打开
        ser.close()  # 关闭串口