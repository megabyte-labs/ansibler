from unittest import TestCase
import pathlib
import shutil
from ansibler.utils.files import (
    check_folder_exists, copy_file, create_folder_if_not_exists, list_files
)


class TestFileUtils(TestCase):
    def setUp(self) -> None:
        """
        Test case setup
        """
        self.example_path = "./test/test_utils/example/"
        self.should_exist_path = "./test/test_utils/exists/"
        self.files_path = "./test/test_utils/example_files/"
        self.copy_path = "./test/test_utils/copy_files/"

    def test_create_folder_if_not_exists(self):
        """
        Test folder creation
        """
        create_folder_if_not_exists(self.example_path)
        self.assertTrue(pathlib.Path(self.example_path).is_dir())
        shutil.rmtree(self.example_path)

    def test_folder_exists(self):
        """
        Test check folder exists
        """
        create_folder_if_not_exists(self.should_exist_path)
        self.assertTrue(check_folder_exists(self.should_exist_path))
        shutil.rmtree(self.should_exist_path)

    def test_folder_not_exists(self):
        """
        Asserts a folder does not exist
        """
        self.assertFalse(check_folder_exists(self.should_exist_path))

    def test_list_files(self):
        """
        Test list files
        """
        # Create dir
        pathlib.Path(self.files_path).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.files_path + "example.file").touch(exist_ok=True)

        files = list_files(self.files_path)
        self.assertEqual(len(files), 1)

        shutil.rmtree(self.files_path)

    def test_copy_file(self):
        """
        Test copy file
        """
        src = self.copy_path + "example.file"
        dst = self.copy_path + "example.copy"
        # Create dir
        pathlib.Path(self.copy_path).mkdir(parents=True, exist_ok=True)
        pathlib.Path(src).touch(exist_ok=True)

        # Copy
        copy_file(src, dst)

        # Read contents
        src_content, dst_content = None, None
        with open(src) as f:
            src_content = f.read()

        with open(dst) as f:
            dst_content = f.read()

        self.assertEqual(src_content, dst_content)

        shutil.rmtree(self.copy_path)

    def test_copy_file_new_content(self):
        """
        Tests copy file but then changes the dst file contents.
        """
        src = self.copy_path + "example.file"
        dst = self.copy_path + "example.copy"
        # Create dir
        pathlib.Path(self.copy_path).mkdir(parents=True, exist_ok=True)
        pathlib.Path(src).touch(exist_ok=True)

        # Copy
        copy_file(src, dst, new_content="Hello, world!")

        # Read contents
        src_content, dst_content = None, None
        with open(src) as f:
            src_content = f.read()

        with open(dst) as f:
            dst_content = f.read()

        self.assertNotEqual(src_content, dst_content)
        self.assertEqual(dst_content, "Hello, world!")

        shutil.rmtree(self.copy_path)
