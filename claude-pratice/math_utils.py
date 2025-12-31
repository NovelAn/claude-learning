"""
数学工具函数库
提供常用的数学计算功能
"""

from typing import Optional
from decorators import validate_non_empty


@validate_non_empty(return_value=0)
def sum_numbers(numbers: Optional[list[float]]) -> float:
    """
    计算列表中所有数字的总和

    参数:
        numbers: 数字列表

    返回:
        总和，如果列表为空或 None 则返回 0
    """
    return sum(numbers)


@validate_non_empty(return_value=0)
def average(numbers: Optional[list[float]]) -> float:
    """
    计算列表中数字的平均值

    参数:
        numbers: 数字列表

    返回:
        平均值，如果列表为空或 None 则返回 0
    """
    return sum(numbers) / len(numbers)


@validate_non_empty(return_value=0)
def find_max(numbers: Optional[list[float]]) -> float:
    """
    找出列表中的最大值

    参数:
        numbers: 数字列表

    返回:
        最大值，如果列表为空或 None 则返回 0
    """
    return max(numbers)


@validate_non_empty(return_value=0)
def find_min(numbers: Optional[list[float]]) -> float:
    """
    找出列表中的最小值

    参数:
        numbers: 数字列表

    返回:
        最小值，如果列表为空或 None 则返回 0
    """
    return min(numbers)


@validate_non_empty(return_value=0)
def median(numbers: Optional[list[float]]) -> float:
    """
    计算列表的中位数

    中位数是将数据排序后位于中间位置的值。
    - 如果数据个数是奇数：中位数就是中间的那个值
    - 如果数据个数是偶数：中位数是中间两个值的平均值

    参数:
        numbers: 数字列表

    返回:
        中位数，如果列表为空或 None 则返回 0

    示例:
        >>> median([1, 3, 5])
        3
        >>> median([1, 3, 5, 7])
        4.0
    """
    # 步骤1: 对列表进行排序（创建副本，不修改原列表）
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)

    # 步骤2: 找到中间位置
    mid = n // 2

    # 步骤3: 根据数据个数判断如何计算中位数
    if n % 2 == 1:
        # 奇数个数据：直接返回中间值
        # 例如: [1, 2, 3] → mid=1 → 返回 sorted_numbers[1] = 2
        return sorted_numbers[mid]
    else:
        # 偶数个数据：返回中间两个值的平均值
        # 例如: [1, 2, 3, 4] → mid=2 → 返回 (sorted_numbers[1] + sorted_numbers[2]) / 2
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2


def variance(numbers: Optional[list[float]]) -> float:
    """
    计算列表的方差

    方差衡量数据与其平均值的偏差程度。
    计算公式：方差 = Σ(xi - 平均值)² / n

    参数:
        numbers: 数字列表

    返回:
        方差，如果列表为空、None 或只有一个元素则返回 0

    示例:
        >>> variance([1, 2, 3, 4, 5])
        2.0
    """
    if not numbers or len(numbers) < 2:
        return 0

    # 步骤1: 计算平均值
    avg = average(numbers)

    # 步骤2: 计算每个数据与平均值的偏差平方
    # 偏差平方 = (每个值 - 平均值)²
    squared_deviations = [(x - avg) ** 2 for x in numbers]

    # 步骤3: 计算偏差平方的平均值（即方差）
    return sum(squared_deviations) / len(numbers)


def standard_deviation(numbers: Optional[list[float]]) -> float:
    """
    计算列表的标准差

    标准差是方差的平方根，表示数据的离散程度。
    与方差相比，标准差与原始数据具有相同的单位。

    参数:
        numbers: 数字列表

    返回:
        标准差，如果列表为空、None 或只有一个元素则返回 0

    示例:
        >>> standard_deviation([1, 2, 3, 4, 5])
        约 1.414
    """
    if not numbers or len(numbers) < 2:
        return 0

    # 标准差 = 方差的平方根
    var = variance(numbers)
    return var ** 0.5  # 或者使用: var ** 0.5 或 math.sqrt(var)


# 这个代码块让我们可以测试这些函数
if __name__ == "__main__":
    # 测试数据
    test_data = [10, 20, 30, 40, 50]

    print(f"测试数据: {test_data}")
    print(f"总和: {sum_numbers(test_data)}")
    print(f"平均值: {average(test_data)}")
    print(f"最大值: {find_max(test_data)}")
    print(f"最小值: {find_min(test_data)}")

    print("\n--- 高级统计功能 ---")
    print(f"中位数: {median(test_data)}")
    print(f"方差: {variance(test_data)}")
    print(f"标准差: {standard_deviation(test_data)}")

    # 测试偶数个数据的中位数
    test_data_even = [10, 20, 30, 40]
    print(f"\n测试数据（偶数个）: {test_data_even}")
    print(f"中位数: {median(test_data_even)}")
