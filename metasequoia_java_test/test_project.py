"""
遍历一个项目的全量测试
"""

import os

from metasequoia_java.lexical import LexicalFSM

PROJECT_PATH = r"D:\tyc-git\darwin"


def main():
    cnt = 0
    for dir_path, sub_dir_list, file_list in os.walk(PROJECT_PATH):
        for file_name in file_list:
            if file_name.endswith(".java"):
                file_path = os.path.join(dir_path, file_name)
                with open(file_path, "r", encoding="UTF-8") as file:
                    cnt += 1
                    print(f"[{cnt:03}] 开始尝试解析 Java 文件: {file_path}")
                    source_code = file.read()

                    # 尝试解析 Java 源码
                    try:
                        lexical_fsm = LexicalFSM(source_code)
                        token_list = []
                        while token := lexical_fsm.lex():
                            if token.is_end:
                                break
                            token_list.append(token)
                        print("解析成功!")
                    except Exception as e:
                        print(f"失败的源代码: {source_code}")
                        raise e


if __name__ == "__main__":
    main()
