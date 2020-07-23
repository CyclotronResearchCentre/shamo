"""Implement `Anisotropy` class.

This module implements the `Anisotropy` class which holds the data
corresponding to a different anisotropic properties.
"""
import re


class Anisotropy(dict):
    """Store anisotropy information.

    Parameters
    ----------
    anisotropy_type : str
        The type of anisotropic data.
    view : int
        The tag of the view the anisotropy is in.
    formula : str, optional
        The formula multiplying anisotropic data. (The default is ``1``).
    """

    SCALAR = "scalar"
    VECTOR = "vector"
    TENSOR = "tensor"

    def __init__(self, anisotropy_type, view, formula="1"):
        super().__init__()
        self["anisotropy_type"] = anisotropy_type
        self["view"] = int(view)
        self["formula"] = formula

    @property
    def anisotropy_type(self):
        """Return the type of anisotropic data.

        Returns
        -------
        str
            The type of anisotropic data.
        """
        return self["anisotropy_type"]

    @property
    def view(self):
        """Return the view the anisotropy is in.

        Returns
        -------
        int
            The name the view the anisotropy is in.
        """
        return self["view"]

    @property
    def formula(self):
        """Return the formula multiplying the anisotropic data.

        Returns
        -------
        str
            The formula multiplying the anisotropic data.
        """
        return self["formula"]

    def evaluate_formula(self, **kwargs):
        """Compute the coefficient multiplying the values of anisotropic data.

        Returns
        -------
        float
            The computed coefficient.

        Notes
        -----
        The parameters are both the sigmas of the model and a given set of
        additional parameters.
        The evaluation string of the tensor should contain named tags
        corresponding to the given parameters (e.g. '<example> * 2').
        """
        formula = self.formula
        pattern = re.compile(r"<[\w\d]*>")
        for match in re.finditer(pattern, self.formula):
            text = match.group(0)
            key = match.group(0)[1:-1]
            value = kwargs.get(key, None)
            if value is None:
                raise KeyError("No parameter '{}' given to the " "formula.".format(key))
            formula = re.sub(re.compile(text), str(value), formula)
        return eval(formula)

    def generate_formula_text(self, **kwargs):
        """Generate a string to define formula value.

        Returns
        -------
        str
            The string defining formula value.

        See Also
        --------
        shamo.model.anisotropy.Anisotropy.evaluate_formula
            For more information on how to define the formula.
        """
        coefficient = self.evaluate_formula(**kwargs)
        field = "{}Field".format(self.anisotropy_type.capitalize())
        sigma_text = "{} * {}[XYZ[]]{{{}}}".format(coefficient, field, self.view)
        return sigma_text
