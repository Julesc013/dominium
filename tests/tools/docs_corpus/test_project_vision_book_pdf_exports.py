import unittest

from tools.docs_corpus.render_project_vision_book_pdfs import (
    mobile_latex,
    printable_latex,
    strip_status_and_promote_chapters,
)


class ProjectVisionBookPdfExportTests(unittest.TestCase):
    def test_strip_status_promotes_chapters(self):
        source = "Status: DERIVED\n\n# Title\n\n## Chapter One\n\nText"
        self.assertEqual(strip_status_and_promote_chapters(source), "# Chapter One\n\nText\n")

    def test_mobile_style_uses_phone_dark_profile(self):
        latex = mobile_latex("# Title\n\n## Chapter\n\nBody", "xelatex")
        self.assertIn("paperwidth=108mm,paperheight=192mm", latex)
        self.assertIn("left=4mm,right=4mm", latex)
        self.assertIn("\\pagecolor{MobileDarkBg}", latex)
        self.assertIn("\\fontsize{10.2pt}{14.6pt}", latex)
        self.assertIn("\\raggedright", latex)
        self.assertIn("\\hyphenpenalty=10000", latex)
        self.assertIn("\\lefthyphenmin=64", latex)
        self.assertIn("\\chapter*{Chapter}", latex)
        self.assertNotIn("\\chapter{Chapter}", latex)

    def test_printable_style_uses_black_on_white_a4(self):
        latex = printable_latex("# Title\n\n## Chapter\n\nBody", "xelatex")
        self.assertIn("a4paper", latex)
        self.assertNotIn("\\pagecolor{MobileDarkBg}", latex)
        self.assertIn("Printable Desktop Edition", latex)


if __name__ == "__main__":
    unittest.main()
