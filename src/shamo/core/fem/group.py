"""Implement the `Group` class."""
from collections.abc import Iterable
import logging

logger = logging.getLogger(__name__)


class Group(dict):
    """A FEM physical group.

    Parameters
    ----------
    dim : int
        The dimension of the group. Can be one of `DIM_POINT`, `DIM_LINE`, `DIM_SURF` or
        `DIM_VOL`.
    entities : int or Iterable [int]
        The tags of the entities composing the physical group.
    group : int
        The physical group tag.

    Raises
    ------
    ValueError
        If argument `dim` is not convertible to `int`.
        If an element of argument `entities` is not convertible to `int`.
        If argument `group` is not convertible to `int`.
    """

    DIM_POINT = 0
    DIM_LINE = 1
    DIM_SURF = 2
    DIM_VOL = 3

    def __init__(self, dim, entities, group):
        if not isinstance(entities, Iterable):
            entities = [entities]
        super().__init__(
            {"dim": int(dim), "entities": entities, "group": int(group),}
        )

    @property
    def dim(self):
        """Return the dimension of the physical group.

        Returns
        -------
        int
            The dimension of the physical group.
        """
        return self["dim"]

    @property
    def entities(self):
        """Return the tags of the entities composing the physical group.

        Returns
        -------
        set [int]
            The tags of the entities composing the physical group.
        """
        return self["entities"]

    @property
    def n_entities(self):
        """Return the number of entities composing the physical group.

        Returns
        -------
        int
            The number of entities composing the physical group.
        """
        return len(self.entities)

    @property
    def group(self):
        """Return the tag of the physical group.

        Returns
        -------
        int
            The tag of the physical group.
        """
        return self["group"]
