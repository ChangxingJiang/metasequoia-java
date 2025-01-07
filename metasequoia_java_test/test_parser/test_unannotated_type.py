"""
测试 JavaPaser.unannotated_type 方法
"""

import unittest

from metasequoia_java import init_parser
from metasequoia_java_test import demo


class GrammarParseTypeTest(unittest.TestCase):
    """测试用例"""

    def test_demo(self):
        for expect_kind, code in demo.element_level.UNANNOTATED_TYPE:
            self.assertEqual(expect_kind, init_parser(code).unannotated_type().kind, f"失败 Case: {code}")
