from unittest import TestCase
from ansibler.utils.subprocesses import get_subprocess_output


class TestSubprocesses(TestCase):
    def test_get_subprocess_output(self):
        """
        Test subprocess output
        """
        out = get_subprocess_output(["echo", "Hello, world!"])
        self.assertEqual(out, "Hello, world!")
