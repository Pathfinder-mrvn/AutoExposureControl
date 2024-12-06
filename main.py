import tkinter as tk
from tkinter import messagebox
from threading import Thread
from queue import Queue
import time
import math
import serial

def calculate_result(x):
    # 检查 x 是否在 230 到 2000 之间
    if x < 230 or x > 2000:
        raise ValueError("x must be in the range [230, 2000].")

    # 计算 457.8 / (2 * x)
    value = 457.8 / (2 * x)

    # 检查 value 是否在 [-1, 1] 的范围内
    if value < -1 or value > 1:
        raise ValueError("Input value is out of the domain for arcsin.")

    # 计算 arcsin 的值
    arcsin_value = math.asin(value)  # 计算反正弦值，返回弧度

    # 将弧度转换为度
    arcsin_value_degrees = math.degrees(arcsin_value)

    # 计算最终结果并取整
    result = int(800 * arcsin_value_degrees)
    return result


def send_to_serial(data):
    with serial.Serial('COM7', 9600, timeout=1) as ser:
        ser.write(data.encode('utf-8'))

def set_function(a, b, output_widget):

    message = f"确保此时处于遮光状态\n"
    output_widget.insert(tk.END, message)  # 将信息插入到文本框
    output_widget.see(tk.END)  # 滚动到文本框的末尾

    x2set = calculate_result(a)

    send_to_serial(f"+X,{x2set}\r")
    # print("+X,%d\r" % x2set)

    message = f"开始静置，时间为180s\n"
    output_widget.insert(tk.END, message)  # 将信息插入到文本框
    output_widget.see(tk.END)  # 滚动到文本框的末尾

    time.sleep(180)
    send_to_serial("+Y,66666\r")
    # print("+Y,66666\r")

    message = f"开始曝光，曝光周期为：{a}nm, 曝光时间为{b}s\n"
    output_widget.insert(tk.END, message)  # 将信息插入到文本框
    output_widget.see(tk.END)  # 滚动到文本框的末尾

    time.sleep(b)

    send_to_serial("-Y,66666\r")

    time.sleep(5)
    send_to_serial(f"-X,{x2set}\r")
    # print("-X,%d\r" % x2set)

    message = f"周期{a}nm曝光完成\n"
    output_widget.insert(tk.END, message)  # 将信息插入到文本框
    output_widget.see(tk.END)  # 滚动到文本框的末尾


def check_serial_connection():
    try:
        with serial.Serial('COM7', 9600, timeout=1) as ser:
            return True
    except (serial.SerialException, OSError):
        return False

class DynamicSetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Set Function Workflow")

        # Add a label for instructions
        instructions_label = tk.Label(self.root, text="确保程序开始时反光镜处于校准完成位置，挡光板处于遮光位置", fg="blue")
        instructions_label.pack(pady=10)
        
        self.scrollable_frame = tk.Frame(self.root)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.scrollable_frame)
        self.scrollbar = tk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.container = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.container, anchor="nw")

        self.input_frames = []  # 存储输入框的引用
        self.add_input_field()  # 添加第一个输入框

        # 创建一个新的框架用于放置加号和减号按钮
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        self.add_button = tk.Button(button_frame, text="+", command=self.add_input_field)
        self.add_button.pack(side=tk.LEFT, padx=(0, 20))  # 给 "+" 按钮右侧添加间距

        self.remove_button = tk.Button(button_frame, text="-", command=self.remove_input_field)
        self.remove_button.pack(side=tk.LEFT)

        self.start_button = tk.Button(self.root, text="Start Workflow", command=self.start_workflow)
        self.start_button.pack(pady=5)

        # 创建一个文本框用于显示输出信息
        self.output_text = tk.Text(self.root, height=10, width=50)
        self.output_text.pack(pady=10)

        self.queue = Queue()  # 创建一个队列用于存储任务
        self.thread = Thread(target=self.process_queue)  # 创建处理队列的线程
        self.thread.daemon = True  # 设置为守护线程，主线程结束时会自动结束
        self.thread.start()  # 启动线程

    def add_input_field(self):
        frame = tk.Frame(self.container)
        frame.pack(pady=5)

        a_entry = tk.Entry(frame)
        a_entry.insert(0, "输入曝光周期(nm)")
        a_entry.pack(side=tk.LEFT)

        b_entry = tk.Entry(frame)
        b_entry.insert(0, "输入曝光时间(s)")
        b_entry.pack(side=tk.LEFT)

        self.input_frames.append(frame)  # 保存输入框的引用

    def remove_input_field(self):
        if self.input_frames:  # 确保有输入框可以删除
            frame = self.input_frames.pop()  # 删除最后一个输入框
            frame.destroy()  # 销毁该框架

    def start_workflow(self):
        if not check_serial_connection():
            messagebox.showerror("Connection Error", "Unable to connect to COM7. Please check the connection.")
            return
        for widget in self.container.winfo_children():
            if isinstance(widget, tk.Frame):
                entries = widget.winfo_children()
                if len(entries) == 2:  # 每个 Frame 包含 2 个输入框
                    a = entries[0].get()
                    b = entries[1].get()

                    try:
                        a = int(a)
                        b = int(b)

                        # 将任务放入队列
                        self.queue.put((a, b))
                    except ValueError:
                        messagebox.showerror("Input Error", "Please enter valid integers.")

    def process_queue(self):
        while True:
            a, b = self.queue.get()  # 从队列中获取任务
            set_function(a, b, self.output_text)  # 执行 set_function
            self.queue.task_done()  # 标记任务完成


if __name__ == "__main__":
    root = tk.Tk()
    app = DynamicSetApp(root)
    root.mainloop()