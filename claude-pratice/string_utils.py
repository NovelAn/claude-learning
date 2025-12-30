"""
字符串工具函数库
提供常用的字符串处理功能
"""


def reverse_string(text: str) -> str:
    """
    反转字符串

    参数:
        text: 要反转的字符串

    返回:
        反转后的字符串
    """
    return text[::-1]  # Python 切片语法，反转字符串


def capitalize_words(text: str) -> str:
    """
    将每个单词的首字母大写

    参数:
        text: 输入字符串

    返回:
        首字母大写的字符串
    """
    return text.title()


def count_words(text: str) -> int:
    """
    统计字符串中的单词数量

    参数:
        text: 输入字符串

    返回:
        单词数量
    """
    words = text.split()  # 按空格分割字符串
    return len(words)


def remove_extra_spaces(text: str) -> str:
    """
    移除字符串中多余的空格

    参数:
        text: 输入字符串

    返回:
        移除多余空格后的字符串
    """
    return ' '.join(text.split())


# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_text = "hello world"

    print(f"原字符串: {test_text}")
    print(f"反转后: {reverse_string(test_text)}")
    print(f"首字母大写: {capitalize_words(test_text)}")
    print(f"单词数量: {count_words(test_text)}")

    # 测试移除多余空格
    test_spaces = "  hello    world   python  "
    print(f"\n原字符串（多余空格）: '{test_spaces}'")
    print(f"处理后: '{remove_extra_spaces(test_spaces)}'")
