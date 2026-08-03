"""
tests/test_auto_aggregator_ast_structure.py
=============================================
AST-based structural integrity test for auto_aggregator.py:
 1. Ensures top-level functions (query_tavily, build_gemini_url, query_gemini_batch, extract_domain, main) are defined EXACTLY once.
 2. Ensures no nested FunctionDef exists inside main() or query_gemini_batch().
 3. Ensures exactly one `if __name__ == "__main__": main()` entrypoint block.
"""

import sys
import os
import ast
import unittest

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_FILE = os.path.join(SCRIPTS_DIR, "auto_aggregator.py")


class TestAutoAggregatorASTStructure(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.exists(TARGET_FILE), f"Target file missing: {TARGET_FILE}")
        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            self.source_code = f.read()
        self.tree = ast.parse(self.source_code, filename=TARGET_FILE)

    def test_top_level_functions_uniqueness(self):
        """Verify each critical function is defined EXACTLY once at top level."""
        target_funcs = [
            "query_tavily",
            "build_gemini_url",
            "query_gemini_batch",
            "extract_domain",
            "main"
        ]

        top_level_func_counts = {fn: 0 for fn in target_funcs}

        for node in ast.iter_child_nodes(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name in top_level_func_counts:
                top_level_func_counts[node.name] += 1

        for fn_name, count in top_level_func_counts.items():
            self.assertEqual(
                count, 1,
                f"Function '{fn_name}' must be defined EXACTLY once at top level, but found {count} definitions."
            )

    def test_no_nested_function_definitions_in_main_or_gemini(self):
        """Verify main() and query_gemini_batch() do not contain nested function definitions."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name in ("main", "query_gemini_batch"):
                nested_funcs = [
                    child.name for child in ast.walk(node)
                    if isinstance(child, ast.FunctionDef) and child != node
                ]
                self.assertEqual(
                    len(nested_funcs), 0,
                    f"Function '{node.name}' contains unexpected nested function definitions: {nested_funcs}"
                )

    def test_single_main_entrypoint_block(self):
        """Verify there is exactly one `if __name__ == '__main__': main()` block."""
        entrypoint_count = 0
        for node in ast.walk(self.tree):
            if isinstance(node, ast.If):
                # Check for __name__ == '__main__'
                if isinstance(node.test, ast.Compare):
                    left = node.test.left
                    if isinstance(left, ast.Name) and left.id == "__name__":
                        entrypoint_count += 1

        self.assertEqual(
            entrypoint_count, 1,
            f"Expected exactly 1 `if __name__ == '__main__'` entrypoint block, but found {entrypoint_count}."
        )


if __name__ == "__main__":
    unittest.main()
