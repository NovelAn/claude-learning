"""
Python 工具函数库
提供常用的数学计算和字符串处理功能
"""

# 从数学工具模块导入所有函数
from .math_utils import (
    sum_numbers,
    average,
    find_max,
    find_min,
    median,
    variance,
    standard_deviation
)

# 从字符串工具模块导入所有函数
from .string_utils import (
    reverse_string,
    capitalize_words,
    count_words,
    remove_extra_spaces
)

__all__ = [
    # 数学工具
    'sum_numbers',
    'average',
    'find_max',
    'find_min',
    'median',
    'variance',
    'standard_deviation',
    # 字符串工具
    'reverse_string',
    'capitalize_words',
    'count_words',
    'remove_extra_spaces',
]

__version__ = '0.2.0'
__author__ = 'Claude Code 学习者'
