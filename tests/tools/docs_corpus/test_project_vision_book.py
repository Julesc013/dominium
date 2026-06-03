import unittest

from tools.docs_corpus.build_project_vision_book import (
    BANNED_BOOK_PATTERNS,
    count_words,
    extract_first_int,
    main_book_text,
)


class ProjectVisionBookTests(unittest.TestCase):
    def test_extract_first_int(self):
        self.assertEqual(
            extract_first_int([r"Semantic blocks extracted:\s*([0-9,]+)"], "Semantic blocks extracted: 2,500"),
            2500,
        )

    def test_main_book_avoids_machine_report_patterns(self):
        book = main_book_text()
        for pattern in BANNED_BOOK_PATTERNS:
            self.assertNotIn(pattern, book)

    def test_main_book_has_substance(self):
        book = main_book_text()
        self.assertGreater(count_words(book), 4000)
        self.assertIn("# The Dominium Project Vision Book", book)
        self.assertIn("## 20. Closing Vision", book)


if __name__ == "__main__":
    unittest.main()
