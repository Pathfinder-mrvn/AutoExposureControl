import math


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


# 示例：调用函数并打印结果
x_value = 300  # 你可以根据需要修改 x 的值
try:
    result = calculate_result(x_value)
    print("Result:", result)
except ValueError as e:
    print("Error:", e)