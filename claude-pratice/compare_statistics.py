"""
统计函数实现对比：手动实现 vs statistics 模块

这个文件展示了我们手动实现的统计函数与 Python 标准库 statistics 模块的对比。

学习目标：
1. 理解手动实现的算法原理
2. 了解标准库的实现方式
3. 对比两者的优缺点
"""

import statistics
from math_utils import median, variance, standard_deviation


def compare_median():
    """对比中位数计算"""
    print("=" * 60)
    print("中位数 (Median) 对比")
    print("=" * 60)

    test_data = [10, 20, 30, 40, 50]
    test_data_even = [10, 20, 30, 40]

    print(f"测试数据（奇数个）: {test_data}")
    print(f"我们的实现: {median(test_data)}")
    print(f"statistics 模块: {statistics.median(test_data)}")
    print()

    print(f"测试数据（偶数个）: {test_data_even}")
    print(f"我们的实现: {median(test_data_even)}")
    print(f"statistics 模块: {statistics.median(test_data_even)}")

    print("\n差异分析:")
    print("- 我们的实现: 简单的排序 + 取中间值算法")
    print("- statistics 模块: 使用优化的快速选择算法，性能更好")
    print("- 对于大数据集，statistics 模块更快")


def compare_variance():
    """对比方差计算"""
    print("\n" + "=" * 60)
    print("方差 (Variance) 对比")
    print("=" * 60)

    test_data = [1, 2, 3, 4, 5]

    print(f"测试数据: {test_data}")
    print(f"我们的实现: {variance(test_data)}")
    print(f"statistics.pvariance (总体方差): {statistics.pvariance(test_data)}")

    print("\n差异分析:")
    print("- 我们的实现: 计算总体方差 (除以 n)")
    print("- statistics 模块提供:")
    print("  * pvariance(): 总体方差 (population variance, 除以 n)")
    print("  * variance(): 样本方差 (sample variance, 除以 n-1)")
    print("- 样本方差用于估算总体方差，更准确")


def compare_standard_deviation():
    """对比标准差计算"""
    print("\n" + "=" * 60)
    print("标准差 (Standard Deviation) 对比")
    print("=" * 60)

    test_data = [10, 20, 30, 40, 50]

    print(f"测试数据: {test_data}")
    print(f"我们的实现: {standard_deviation(test_data):.6f}")
    print(f"statistics.pstdev (总体标准差): {statistics.pstdev(test_data):.6f}")

    print("\n差异分析:")
    print("- 我们的实现: 总体标准差 (方差开平方根)")
    print("- statistics 模块提供:")
    print("  * pstdev(): 总体标准差 (population standard deviation)")
    print("  * stdev(): 样本标准差 (sample standard deviation)")


def performance_comparison():
    """性能对比"""
    import time

    print("\n" + "=" * 60)
    print("性能对比 (大数据集)")
    print("=" * 60)

    # 创建一个大数据集
    large_data = list(range(1, 10001))  # 1 到 10000

    # 测试我们的实现
    start = time.time()
    for _ in range(100):
        median(large_data)
    our_time = time.time() - start

    # 测试 statistics 模块
    start = time.time()
    for _ in range(100):
        statistics.median(large_data)
    stats_time = time.time() - start

    print(f"数据集大小: {len(large_data)}")
    print(f"测试次数: 100")
    print(f"\n我们的实现: {our_time:.4f} 秒")
    print(f"statistics 模块: {stats_time:.4f} 秒")
    print(f"性能差异: {our_time/stats_time:.2f}x")

    print("\n结论:")
    print("- statistics 模块使用优化算法，性能更好")
    print("- 但我们的实现更容易理解算法原理")


def summary():
    """总结"""
    print("\n" + "=" * 60)
    print("总结与建议")
    print("=" * 60)

    print("""
[优点] 手动实现的优势:
   1. 深入理解算法原理
   2. 学习编程技巧（排序、列表推导式等）
   3. 完全掌控代码逻辑

[优点] statistics 模块的优势:
   1. 性能优化（使用快速选择算法）
   2. 更多功能（样本方差、样本标准差等）
   3. 经过充分测试，可靠性高
   4. 处理边界情况更完善

[建议] 使用场景:
   - 学习/练习: 手动实现
   - 生产环境: 使用 statistics 模块
   - 面试/考试: 需要手动实现

[进阶] 学习建议:
   研究 statistics 模块的源码，了解:
   1. 快速选择算法 (Quickselect)
   2. 数值稳定性处理
   3. 边界条件处理
   """)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("统计函数实现对比：手动实现 vs Python 标准库")
    print("=" * 60)

    # 运行所有对比
    compare_median()
    compare_variance()
    compare_standard_deviation()
    performance_comparison()
    summary()

    print("\n" + "=" * 60)
    print("对比完成！")
    print("=" * 60)
