"""
解析 Java 项目中的 properties 文件

properties 文件特性：
1. 文件后缀为 ".properties"
2. properties 文件由一系列键值对组成，每个键值对为一行
3. 键和值之间用等号分隔，键通常表示配置项的名称，值通常表示配置项的具体内容
4. 键和值前后的空白字符会被忽略，但值中的空白字符会被保留
6. 如果一个值需要跨越多行，可以在行尾使用反斜杠 "\" 来表示值的延续
7. 可以使用 "#" 或 "!" 作为注释标识符，注释标识符仅在行首时生效，此时这一行会被视为注释，不会被程序解析
8. properties 文件通常使用 IOS-8859-1 字符编码；如果使用其他编码，文件的第一行必须是相关的声明
9. 如果键和值中包含 "="、":"、"\" 等特殊字符时，需要对这些字符进行转义
"""

import re
from typing import Dict, Optional

# 前面不是反斜杠（"\"）的等号（"="）
PATTERN_EQUAL = re.compile("(?<!\\\\)=")


class PropertiesSyntaxError(Exception):
    """Properties 文件语法错误"""


def parse_properties(properties_path: str) -> Dict[str, str]:
    """解析 Java 项目中的 properties 文件"""
    if not properties_path.endswith(".properties"):
        raise PropertiesSyntaxError(f"{properties_path} 不是 properties 文件")

    result = {}

    with open(properties_path, "r", encoding="ISO-8859-1") as file:
        actual_line: Optional[str] = None
        for line in file:
            # 去除行首、行尾的空格符和换行符（因为续行符之后的行开头可能存在空格）
            line = line.strip()

            # 如果前一行末尾使用反斜杠（续行符），则将当前行与上一行累加
            actual_line = line if actual_line is None else actual_line + line

            # 如果一个值需要跨越多行，可以在行尾使用反斜杠 "\" 来表示值的延续（且这个 "\" 不在注释中）
            if not (line.startswith("#") or line.startswith("!")) and line.endswith("/"):
                continue

            # 如果当前行为空则跳过（之所以在这里判断，是因为可能前一行包含续行符且当前行为空）
            if actual_line == "":
                continue

            # 如果当前行为注释则忽略
            if actual_line.startswith("#") or actual_line.startswith("!"):
                actual_line = None
                continue

            # 将配置项切分为键和值
            match = PATTERN_EQUAL.search(actual_line)
            if not match:
                raise PropertiesSyntaxError(f"不满足 properties 格式: {actual_line}")
            key = actual_line[:match.span()[0]]
            value = actual_line[match.span()[1]:]

            # 将配置项写入结果
            if key in result:
                raise PropertiesSyntaxError(f"存在重复的配置项: {key}")
            result[key.strip()] = value.strip()

            # 将正在处理中的行置空
            actual_line = None

    return result


if __name__ == "__main__":
    print(PATTERN_EQUAL.split("key=value"))
    print(PATTERN_EQUAL.split("key=value1\\=value2"))
