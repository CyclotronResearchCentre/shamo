from pathlib import Path
from tempfile import TemporaryDirectory

from shamo.core import TemplateFile


def test_init():
    content = "test"
    with TemporaryDirectory() as temporary_path:
        source_path = str(Path(temporary_path) / "source.txt")
        with open(source_path, "w") as source_file:
            source_file.write(content)
        destination_path = str(Path(temporary_path) / "destination.txt")
        tempalte_file = TemplateFile(source_path, destination_path)
        assert(tempalte_file.text == content)


def test_context():
    content = "test"
    with TemporaryDirectory() as temporary_path:
        source_path = str(Path(temporary_path) / "source.txt")
        with open(source_path, "w") as source_file:
            source_file.write(content)
        destination_path = str(Path(temporary_path) / "destination.txt")
        with TemplateFile(source_path, destination_path) as template_file:
            pass
        with open(destination_path, "r") as destination_file:
            test_content = destination_file.read()
        assert(test_content == content)


def test_replace_with_text():
    content = "<key:value>"
    replace = "test"
    with TemporaryDirectory() as temporary_path:
        source_path = str(Path(temporary_path) / "source.txt")
        with open(source_path, "w") as source_file:
            source_file.write(content)
        destination_path = str(Path(temporary_path) / "destination.txt")
        with TemplateFile(source_path, destination_path) as template_file:
            template_file.replace_with_text("key", "value", replace)
        with open(destination_path, "r") as destination_file:
            test_content = destination_file.read()
        assert(test_content == replace)


def test_replace_with_list():
    content = "<key:value>"
    replace = ["test_1", "test_2"]
    with TemporaryDirectory() as temporary_path:
        source_path = str(Path(temporary_path) / "source.txt")
        with open(source_path, "w") as source_file:
            source_file.write(content)
        destination_path = str(Path(temporary_path) / "destination.txt")
        with TemplateFile(source_path, destination_path) as template_file:
            template_file.replace_with_list("key", "value", replace)
        with open(destination_path, "r") as destination_file:
            test_content = destination_file.read()
        assert(test_content == ",".join(replace))


def test_replace_with_dict():
    content = "<key:value>"
    replace = {"1": 1, "2": 2}
    with TemporaryDirectory() as temporary_path:
        source_path = str(Path(temporary_path) / "source.txt")
        with open(source_path, "w") as source_file:
            source_file.write(content)
        destination_path = str(Path(temporary_path) / "destination.txt")
        with TemplateFile(source_path, destination_path) as template_file:
            template_file.replace_with_dict("key", "value", replace,
                                            prefix="test_",
                                            key_value_separator="=",
                                            suffix=";", separator="\n")
        with open(destination_path, "r") as destination_file:
            test_content = destination_file.read()
        assert(test_content == "test_1=1;\ntest_2=2;")
