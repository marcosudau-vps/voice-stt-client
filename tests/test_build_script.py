from __future__ import annotations

import unittest
from unittest.mock import patch

from scripts import build


class BuildScriptTests(unittest.TestCase):
    def test_spec_installs_platform_hook_before_application_imports(self) -> None:
        spec_text = build.SPEC_FILE.read_text(encoding="utf-8")
        self.assertIn(
            'runtime_hooks=[str(ROOT / "scripts" / "pyinstaller_runtime_platform.py")]',
            spec_text,
        )

    def test_pyinstaller_bootstrap_fixes_platform_before_import(self) -> None:
        events: list[tuple[str, object]] = []

        class FakePlatform:
            system = staticmethod(lambda: "blocked")
            machine = staticmethod(lambda: "blocked")
            win32_ver = staticmethod(lambda *args, **kwargs: ("blocked", "", "", ""))
            _get_machine_win32 = staticmethod(lambda: "blocked")

            class _Processor:
                get = staticmethod(lambda: "blocked")

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            del globals, locals, level
            if name == "platform":
                return FakePlatform
            if name == "PyInstaller.__main__":
                events.append(
                    (
                        "platform",
                        (
                            FakePlatform.system(),
                            FakePlatform.machine(),
                            FakePlatform.win32_ver("ignored"),
                            FakePlatform._get_machine_win32(),
                            FakePlatform._Processor.get(),
                        ),
                    )
                )
                return type("FakePyInstaller", (), {"run": lambda: events.append(("run", True))})
            return __import__(name, fromlist=fromlist)

        namespace = {"__builtins__": {"__import__": fake_import}}
        exec(build.PYINSTALLER_BOOTSTRAP, namespace)

        self.assertEqual(
            events,
            [
                (
                    "platform",
                    (
                        "Windows",
                        "AMD64",
                        ("11", "", "", "Multiprocessor Free"),
                        "AMD64",
                        "AMD64",
                    ),
                ),
                ("run", True),
            ],
        )

    def test_build_invokes_bootstrap_instead_of_module_entrypoint(self) -> None:
        with (
            patch.object(build, "read_version", return_value="1.2.3"),
            patch.object(build, "render_windows_version_info", return_value="info"),
            patch.object(build, "run") as run_command,
            patch.object(build, "EXE_PATH") as exe_path,
        ):
            exe_path.is_file.return_value = True
            exe_path.stat.return_value.st_size = 1
            exe_path.read_bytes.return_value = b"x"
            exe_path.relative_to.return_value = exe_path
            build.build(smoke_test=False)

        command = run_command.call_args.args[0]
        environment = run_command.call_args.kwargs["env"]
        self.assertEqual(command[1:3], ["-c", build.PYINSTALLER_BOOTSTRAP])
        self.assertNotIn("-m", command)
        self.assertEqual(
            environment["PYTHONPATH"].split(build.os.pathsep)[0],
            str(build.REPO_ROOT / "scripts" / "pyinstaller_site"),
        )


if __name__ == "__main__":
    unittest.main()
