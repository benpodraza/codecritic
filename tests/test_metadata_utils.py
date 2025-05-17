import unittest
from app.utils.metadata.footer_annotation_helper import (
    strip_metadata_footer,
    append_metadata_footer,
    reapply_footer,
)

class MetadataUtilsTest(unittest.TestCase):
    def test_strip_and_append(self):
        code = "print('x')\n# === AI-FIRST METADATA ===\n# a: 1"
        stripped, footer = strip_metadata_footer(code)
        self.assertNotIn('AI-FIRST', stripped)
        reapplied = append_metadata_footer(stripped, {'b': '2'})
        self.assertIn('# b: 2', reapplied)
        reapplied2 = reapply_footer(stripped, footer, {'c': '3'})
        self.assertIn('# a: 1', reapplied2)
        self.assertIn('# c: 3', reapplied2)

if __name__ == '__main__':
    unittest.main()
