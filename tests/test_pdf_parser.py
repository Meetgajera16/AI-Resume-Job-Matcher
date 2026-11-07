import unittest

from app.utils.file_utils import safe_filename


class FileSafetyTests(unittest.TestCase):
    def test_path_components_are_removed(self):
        self.assertEqual("resume.pdf", safe_filename("../../resume.pdf"))

    def test_unsafe_characters_are_replaced(self):
        self.assertEqual("my_resume_.pdf", safe_filename("my<resume>.pdf"))


if __name__ == "__main__":
    unittest.main()
