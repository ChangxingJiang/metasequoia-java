"""
测试 JavaPaser.block_statement 方法
"""

import unittest

from metasequoia_java import init_parser
from metasequoia_java_test import demo


class GrammarParseTypeTest(unittest.TestCase):
    """测试用例"""

    def test_demo(self):
        for expect_kind, code in demo.statement_level.BLOCK_STATEMENT:
            self.assertEqual(expect_kind, init_parser(code).block_statement()[0].kind, f"失败 Case: {code}")
