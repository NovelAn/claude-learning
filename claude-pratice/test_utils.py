"""
单元测试文件
测试数学工具和字符串工具的所有功能
"""

import unittest
from math_utils import sum_numbers, average, find_max, find_min, median, variance, standard_deviation
from string_utils import reverse_string, capitalize_words, count_words, remove_extra_spaces


class TestMathUtils(unittest.TestCase):
    """测试数学工具函数"""

    def test_sum_numbers(self):
        """测试 sum_numbers 函数"""
        self.assertEqual(sum_numbers([1, 2, 3, 4, 5]), 15)
        self.assertEqual(sum_numbers([10, 20, 30]), 60)
        self.assertEqual(sum_numbers([-1, -2, -3]), -6)
        self.assertEqual(sum_numbers([]), 0)  # 空列表返回 0
        self.assertEqual(sum_numbers([0]), 0)

    def test_average(self):
        """测试 average 函数"""
        self.assertEqual(average([1, 2, 3, 4, 5]), 3.0)
        self.assertEqual(average([10, 20, 30]), 20.0)
        self.assertEqual(average([-5, 5]), 0.0)
        self.assertEqual(average([]), 0)  # 空列表返回 0

    def test_find_max(self):
        """测试 find_max 函数"""
        self.assertEqual(find_max([1, 5, 3, 9, 2]), 9)
        self.assertEqual(find_max([-10, -5, -3]), -3)
        self.assertEqual(find_max([100]), 100)
        self.assertEqual(find_max([]), 0)  # 空列表返回 0

    def test_find_min(self):
        """测试 find_min 函数"""
        self.assertEqual(find_min([1, 5, 3, 9, 2]), 1)
        self.assertEqual(find_min([-10, -5, -3]), -10)
        self.assertEqual(find_min([100]), 100)
        self.assertEqual(find_min([]), 0)  # 空列表返回 0

    def test_median(self):
        """测试 median 函数"""
        # 奇数个数据
        self.assertEqual(median([1, 3, 5]), 3)
        self.assertEqual(median([10, 20, 30, 40, 50]), 30)
        # 偶数个数据
        self.assertEqual(median([1, 3, 5, 7]), 4.0)
        self.assertEqual(median([10, 20, 30, 40]), 25.0)
        # 单个数据
        self.assertEqual(median([42]), 42)
        # 空列表
        self.assertEqual(median([]), 0)

    def test_variance(self):
        """测试 variance 函数"""
        # 方差计算：每个数据与平均值的偏差平方的平均
        self.assertAlmostEqual(variance([1, 2, 3, 4, 5]), 2.0)  # 已知结果
        self.assertAlmostEqual(variance([10, 20, 30, 40, 50]), 200.0)
        # 空或单个数据返回 0
        self.assertEqual(variance([]), 0)
        self.assertEqual(variance([42]), 0)

    def test_standard_deviation(self):
        """测试 standard_deviation 函数"""
        # 标准差 = 方差的平方根
        self.assertAlmostEqual(standard_deviation([1, 2, 3, 4, 5]), 2.0 ** 0.5)  # √2
        self.assertAlmostEqual(standard_deviation([10, 20, 30, 40, 50]), 200.0 ** 0.5)  # √200
        # 空或单个数据返回 0
        self.assertEqual(standard_deviation([]), 0)
        self.assertEqual(standard_deviation([42]), 0)


class TestStringUtils(unittest.TestCase):
    """测试字符串工具函数"""

    def test_reverse_string(self):
        """测试 reverse_string 函数"""
        self.assertEqual(reverse_string("hello"), "olleh")
        self.assertEqual(reverse_string("world"), "dlrow")
        self.assertEqual(reverse_string(""), "")
        self.assertEqual(reverse_string("a"), "a")
        self.assertEqual(reverse_string("123"), "321")

    def test_capitalize_words(self):
        """测试 capitalize_words 函数"""
        self.assertEqual(capitalize_words("hello world"), "Hello World")
        self.assertEqual(capitalize_words("python is great"), "Python Is Great")
        self.assertEqual(capitalize_words(""), "")
        self.assertEqual(capitalize_words("a"), "A")

    def test_count_words(self):
        """测试 count_words 函数"""
        self.assertEqual(count_words("hello world"), 2)
        self.assertEqual(count_words("this is a test"), 4)
        self.assertEqual(count_words(""), 0)
        self.assertEqual(count_words("single"), 1)
        self.assertEqual(count_words("  multiple   spaces  "), 2)  # 忽略多余空格

    def test_remove_extra_spaces(self):
        """测试 remove_extra_spaces 函数"""
        self.assertEqual(remove_extra_spaces("hello    world"), "hello world")
        self.assertEqual(remove_extra_spaces("  a  b  c  "), "a b c")
        self.assertEqual(remove_extra_spaces(""), "")
        self.assertEqual(remove_extra_spaces("   "), "")
        self.assertEqual(remove_extra_spaces("noextra"), "noextra")


def run_tests():
    """运行所有测试并打印结果"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestMathUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestStringUtils))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印总结
    print("\n" + "="*60)
    print("测试总结:")
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*60)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
