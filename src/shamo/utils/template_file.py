"""Implement `TemplateFile` class.

This module implements the `TemplateFile` class which is used to edit a
template by replacing tags with their value.
"""
import re


class TemplateFile:
    """Allow edition of template files.

    Parameters
    ----------
    source_path : str
        The path to the source template file.

    destination_path : str
        The path to the destination file.

    Attributes
    ----------
    text : str
    """

    def __init__(self, source_path, destination_path):
        self._source_path = source_path
        self._destination_path = destination_path
        with open(source_path, "r") as source_file:
            self.text = source_file.read()

    def __enter__(self):
        """Enter the context."""
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Exit the context."""
        with open(self._destination_path, "w") as destination_file:
            destination_file.write(self.text)

    def replace_with_text(self, key, value, text):
        """Replace a tag by a text.

        Parameters
        ----------
        key : str
            The key of the tag.
        value : str
            The value of the tag.
        text : str
            The text to replace the tag with.

        Returns
        -------
        TemplateFile
            The current template file.

        Notes
        -----
        The tags are formatted as <key:value> in a template file.
        """
        pattern = r"\<{}:{}\>".format(key, value)
        self.text = re.sub(pattern, text, self.text)
        return self

    def replace_with_list(self, key, value, data, separator=","):
        """Replace a tag by a text.

        Parameters
        ----------
        key : str
            The key of the tag.
        value : str
            The value of the tag.
        data : list[str | int | float]
            The list of values to replace the tag with.
        separator : str, optional
            The separator to place between each items.
            (The default is ``','``).

        Returns
        -------
        TemplateFile
            The current template file.

        See Also
        --------
        TemplateFile.replace_with_text

        Notes
        -----
        The tags are formatted as <key:value> in a template file.
        """
        text = separator.join(data)
        self.replace_with_text(key, value, text)
        return self

    def replace_with_dict(
        self,
        key,
        value,
        data,
        prefix="",
        key_value_separator="",
        suffix="",
        separator="",
    ):
        """Replace a tag by a text.

        Parameters
        ----------
        key : str
            The key of the tag.
        value : str
            The value of the tag.
        data : dict[str: str | int | float]
            The dictionary containing the data to replace the tag with.
        prefix : str, optional
            A prefix to add before each items. (The default is ``''``).
        key_value_separator : str, optional
            A separator to add between the keys and the values. (The default
            is ``''``).
        suffix : str, optional
            A suffix to add after each items. (The default is ``''``).
        separator : str, optional
            The separator to place between each items.
            (The default is ``','``).

        Returns
        -------
        TemplateFile
            The current template file.

        See Also
        --------
        TemplateFile.replace_with_text

        Notes
        -----
        The tags are formatted as <key:value> in a template file.
        """
        items = [
            "{}{}{}{}{}".format(
                prefix, data_key, key_value_separator, data_value, suffix
            )
            for data_key, data_value in data.items()
        ]
        self.replace_with_list(key, value, items, separator)
        return self
