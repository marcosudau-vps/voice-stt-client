"""Retired launcher: no server/profile/process side effects."""
import ast
from pathlib import Path
import unittest
import test_instance_launcher as subject


class RetiredLauncher(unittest.TestCase):
    def test_start_is_unconditionally_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'deaktiviert'):
            subject.start_client(lambda value: self.fail('No startup status expected'))

    def test_no_docker_profile_or_subprocess_imports_remain(self):
        tree = ast.parse(Path(subject.__file__).read_text(encoding='utf-8'))
        imports = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertEqual(imports, ['sys'])
        from_imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        self.assertEqual(from_imports, ['PySide6.QtWidgets'])

    def test_information_window_has_no_enabled_start_button(self):
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication, QPushButton
        app = QApplication.instance() or QApplication([])
        def inspect():
            window = next(w for w in app.topLevelWidgets() if w.windowTitle() == 'V2-Testinstanz – deaktiviert')
            buttons = {b.text(): b for b in window.findChildren(QPushButton)}
            self.assertFalse(buttons['Teststarter deaktiviert'].isEnabled())
            self.assertTrue(buttons['Schließen'].isEnabled())
            app.quit()
        QTimer.singleShot(100, inspect)
        self.assertEqual(subject.main(), 0)


if __name__ == '__main__':
    unittest.main()
