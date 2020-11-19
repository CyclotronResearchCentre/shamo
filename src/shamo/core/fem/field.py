"""Implement the `Field` class."""
import logging

logger = logging.getLogger(__name__)


class Field(dict):
    """A FEM field.

    Parameters
    ----------
    field_type : str
        The type of the field.
    view : int
        The view corresponding to the field.
    formula : str, optional
        The formula linking the field to a physical property.

    Notes
    -----
    The argument `formula` must be a valid formatter expression with named placeholders.
    To reference a tissue property, use the dict accessor.
    Available properties are:
        - 'sigma[tissue]'
    """

    SCALAR = "scalar"
    VECTOR = "vector"
    TENSOR = "tensor"

    def __init__(self, field_type, view, formula="1"):
        field_type = str(field_type)
        if field_type not in {self.SCALAR, self.VECTOR, self.TENSOR}:
            raise ValueError(
                "Argument 'field_type' must be one of 'scalar', 'vector' or 'tensor'."
            )
        super().__init__(
            {"field_type": field_type, "view": int(view), "formula": formula}
        )

    @property
    def field_type(self):
        """Return the type of the fied.

        Returns
        -------
        str
            The type of the field.
        """
        return self["field_type"]

    @property
    def view(self):
        """Return the view corresponding to the field.

        Returns
        -------
        int
            The view corresponding to the field.
        """
        return self["view"]

    @property
    def formula(self):
        """Return the formula linking the field to a physical property.

        Returns
        -------
        str
            The formula linking the field to a physical property.
        """
        return self["formula"]

    def gen_formula(self, **kwargs):
        """Generate the formula to use the field in a property.

        Returns
        -------
        str
            The generated formula.
        """
        formula = self.formula.format(**kwargs)
        field_type = f"{self.field_type.capitalize()}Field"
        return f"{formula} * {field_type}[XYZ[]]{{ {self.view} }}"
