"""
装饰器工具模块
提供常用的函数装饰器
"""

from functools import wraps
from typing import Callable, Any


def validate_non_empty(return_value: Any = 0):
    """
    验证函数输入列表/字符串不为空的装饰器

    参数:
        return_value: 当输入为空时返回的默认值

    返回:
        装饰器函数

    示例:
        @validate_non_empty(return_value=0)
        def sum_numbers(numbers):
            return sum(numbers)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取第一个参数（通常是输入数据）
            if args:
                input_data = args[0]
                # 检查是否为 None 或空
                if input_data is None or input_data == []:
                    return return_value
            # 调用原函数
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_string_not_empty(return_value: Any = ""):
    """
    验证字符串输入不为空的装饰器

    参数:
        return_value: 当输入为空时返回的默认值

    返回:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(text: str, *args, **kwargs):
            # 检查是否为 None 或空字符串
            if text is None or text == "":
                return return_value
            # 调用原函数
            return func(text, *args, **kwargs)
        return wrapper
    return decorator
