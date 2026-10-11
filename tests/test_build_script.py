from __future__ import annotations

import unittest
from unittest.mock import patch

from scripts import build


class BuildScriptTests(unittest.TestCase):
    def test_release_build_requires_qualified_python_patch(self) -> None:
        build.verify_build_python((3, 12, 10))

        with self.assertRaisesRegex(build.BuildError, "require Python 3.12.10"):
            build.verify_build_python((3, 12, 14))

    def test_spec_installs_platform_hook_before_application_imports(self) -> None:
        spec_text = build.SPEC_FILE.read_text(encoding="utf-8")
        self.assertIn(
            'runtime_hooks=[str(ROOT / "scripts" / "pyinstaller_runtime_platform.py")]',
            spec_text,
        )

    def test_spec_prevents_python_runtime_from_shadowing_qt_runtime(self) -> None:
        spec_text = build.SPEC_FILE.read_text(encoding="utf-8")
        self.assertIn('name == "ucrtbase.dll"', spec_text)
        self.assertIn('name.startswith("api-ms-win-")', spec_text)
        self.assertIn('name in {"icuuc.dll", "icuin.dll"}', spec_text)
        self.assertIn('name.startswith("icudt")', spec_text)
        self.assertIn('root_runtime_names = {"vcruntime140.dll", "vcruntime140_1.dll"}', spec_text)
        self.assertIn('str(PYSIDE_DIR / runtime_name)', spec_text)

    def test_build_path_excludes_unrelated_process_directories(self) -> None:
        path_parts = build.sanitized_build_path().split(build.os.pathsep)
        self.assertIn(str(build.Path(build.sys.executable).resolve().parent), path_parts)
        self.assertIn(str(build.Path(build.sys.base_prefix).resolve()), path_parts)
        self.assertTrue(any(part.lower().endswith("windows\\system32") for part in path_parts))
        self.assertFalse(any("poppler" in part.lower() for part in path_parts))

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

    def test_frozen_smoke_checks_version_and_gui_runtime(self) -> None:
        completed = type("Completed", (), {"returncode": 0})()
        with (
            patch.object(build, "read_version", return_value="1.2.3"),
            patch.object(build, "render_windows_version_info", return_value="info"),
            patch.object(build, "run"),
            patch.object(build, "verify_frozen_feedback_assets"),
            patch.object(build.subprocess, "run", return_value=completed) as run_process,
            patch.object(build, "EXE_PATH") as exe_path,
        ):
            exe_path.is_file.return_value = True
            exe_path.stat.return_value.st_size = 1
            exe_path.read_bytes.return_value = b"x"
            exe_path.relative_to.return_value = exe_path
            build.build(smoke_test=True)

        smoke_commands = [call.args[0] for call in run_process.call_args_list]
        self.assertEqual(
            smoke_commands,
            [
                [str(exe_path), "--version"],
                [str(exe_path), "--verify-gui-runtime"],
            ],
        )

    def test_feedback_archive_check_rejects_missing_sound(self) -> None:
        with patch("PyInstaller.archive.readers.CArchiveReader") as reader:
            reader.return_value.toc = {"voice_stt_client\\config.yaml": (0,)}
            with self.assertRaises(build.BuildError):
                build.verify_frozen_feedback_assets(build.EXE_PATH)


if __name__ == "__main__":
    unittest.main()
