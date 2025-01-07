"""
测试 JavaPaser.parse_type 方法
"""

import unittest

from metasequoia_java import parse_type
from metasequoia_java_test import demo


class GrammarParseTypeTest(unittest.TestCase):
    """测试用例"""

    def test_demo(self):
        for expect_kind, code in demo.element_level.UNANNOTATED_TYPE:
            self.assertEqual(expect_kind, parse_type(code).kind, f"失败 Case: {code}")
