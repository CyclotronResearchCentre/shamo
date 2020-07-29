"""Implement the `ParametricForwardSolution` class.

This module implements the `ParametricForwardSolution` class which is the base
for any parametric forward solution.
"""
import abc
import math
from pathlib import Path
import pickle
import re
import shutil

import numpy as np
from scipy.special import gamma, kv
from scipy.spatial.distance import pdist, squareform
from sklearn.gaussian_process import kernels

from shamo.solutions import CommonForwardSolution
from shamo.utils import none_callable


class MaternProd(kernels.Matern):
    """A real matern kernel."""

    def __call__(self, x, y=None, eval_gradient=False):
        """Return the kernel k(x, y) and optionally its gradient.

        Parameters
        ----------
        x : numpy.ndarray
            The left argument of the returned kernel k(x, y).
        y : numpy.ndarray, optional
            The right argument of the returned kernel k(x, y). If set to ``None``,
            k(x, x) is evaluated instead. (The default is ``None``)
        eval_gradient : bool, optional
            If set to ``True``, the gradient with respect to the kernel hyperparameter
            is determined. (The default is ``False``)

        Returns
        -------
        numpy.ndarray
            The kernel k(x, y).
        numpy.ndarray
            The gradient of the kernel k(x, y) with respect to the hyperparameter of
            the kernel.
        """
        x = np.atleast_2d(x)
        length_scale = kernels._check_length_scale(x, self.length_scale)
        if y is not None and eval_gradient:
            raise ValueError("Gradient can only be evaluated when y is None.")

        K = np.prod(self.r(x, y, length_scale), axis=2)

        if eval_gradient:
            if self.hyperparameter_length_scale.fixed:
                K_gradient = np.empty((x.shape[0], x.shape[0], 0))
                return K, K_gradient

            if self.anisotropic:
                D = (x[:, np.newaxis, :] - x[np.newaxis, :, :]) ** 2 / (
                    length_scale ** 2
                )
            else:
                D = squareform(pdist(x / length_scale, metric="euclidean") ** 2)[
                    :, :, np.newaxis
                ]

            if self.nu == 0.5:
                K_gradient = (
                    K[..., np.newaxis] * D / np.sqrt(D.sum(2))[:, :, np.newaxis]
                )
                K_gradient[~np.isfinite(K_gradient)] = 0
            elif self.nu == 1.5:
                K_gradient = 3 * D * np.exp(-np.sqrt(3 * D.sum(-1)))[..., np.newaxis]
            elif self.nu == 2.5:
                tmp = np.sqrt(5 * D.sum(-1))[..., np.newaxis]
                K_gradient = 5.0 / 3.0 * D * (tmp + 1) * np.exp(-tmp)

            if not self.anisotropic:
                return K, K_gradient[:, :].sum(-1)[:, :, np.newaxis]
            else:
                return K, K_gradient
        else:
            return K

    def r(self, x, y=None, length_scale=None):
        """Compute r(x, y).

        Parameters
        ----------
        x : numpy.ndarray
            The left argument of r(x, y).
        y : numpy.ndarray, optional
            The right argument of r(x, y). If set to ``None``, r(x, x) is evaluated
            instead. (The default is ``None``)
        length_scale : float | numpy.ndarray
            The length scale of the kernel. (The default is ``None``)

        Returns
        -------
        numpy.ndarray
            The covariance r(x, y).
        """
        if length_scale is None:
            length_scale = kernels._check_length_scale(x, self.length_scale)

        if y is None:
            r = np.abs(x[:, np.newaxis, :] - x[np.newaxis, :, :]) / length_scale
        else:
            r = np.abs(
                x[:, np.newaxis, :] / length_scale - y[np.newaxis, :, :] / length_scale
            )

        if self.nu == 0.5:
            return np.exp(-r)
        elif self.nu == 1.5:
            tmp = r * math.sqrt(3)
            return (1.0 + tmp) * np.exp(-tmp)
        elif self.nu == 2.5:
            tmp = r * math.sqrt(5)
            return (1.0 + tmp + tmp ** 2 / 3.0) * np.exp(-tmp)
        else:
            raise ValueError("Covariance can only be computed for ν ∈ {0.5, 1.5, 2.5}.")

    def ri(self, x, y, i=0):
        """Compute r_i(x_i, y_i).

        Parameters
        ----------
        x : numpy.ndarray
            The left argument of r(x, y).
        y : numpy.ndarray, optional
            The right argument of r(x, y). If set to ``None``, r(x, x) is evaluated
            instead. (The default is ``None``)
        i : int, optional
            The dimension for which the covariance must be computed. (The default is
            ``0``)

        Returns
        -------
        numpy.ndarray
            The covariance r_i(x_i, y_i).
        """
        if i >= self.length_scale.size:
            raise ValueError(
                "The current kernel is only defined for {} inputs.".format(
                    self.length_scale.size
                )
            )
        length_scale = self.length_scale[i]

        r = np.abs(x[:, np.newaxis] / length_scale - y[np.newaxis, :] / length_scale)

        if self.nu == 0.5:
            return np.exp(-r)
        elif self.nu == 1.5:
            tmp = r * math.sqrt(3)
            return (1.0 + tmp) * np.exp(-tmp)
        elif self.nu == 2.5:
            tmp = r * math.sqrt(5)
            return (1.0 + tmp + tmp ** 2 / 3.0) * np.exp(-tmp)
        else:
            raise ValueError("Covariance can only be computed for ν ∈ {0.5, 1.5, 2.5}.")


class ParametricForwardSolution(CommonForwardSolution):
    """The base for any parametric forward problem solution.

    Parameters
    ----------
    name : str
        The name of the solution.
    parent_path : str
        The path to the parent directory of the solution.

    Other Parameters
    ----------------
    problem : dict [str, Any]
        The problem that result in this solution.
    model_path : PathLike
        The path to the model file.
    shape : tuple (int, int)
        The shape of the matrix.
    sensors : list [str]
        The names of the sensors.
    n_sensors : int
        The number of sensors.
    n_elements : int
        The number of elements.
    n_values_per_element : int
        The number of values by element.
    elements_path : PathLike
        The path to the elements file.
    solution_paths : list [PathLike]
        The paths to the solutions.
    is_finalized : bool
        ``True`` if the solution is finalized.

    See Also
    --------
    shamo.solutions.forward.common_forward_solution.CommonForwardSolution
    """

    SOLUTION_FACTORY = none_callable

    def __init__(self, name, parent_path, **kwargs):
        super().__init__(name, parent_path, **kwargs)
        # Sub-solutions paths
        self["solution_paths"] = [
            str(Path(path)) for path in kwargs.get("solution_paths", [])
        ]
        # Is finalized
        self["is_finalized"] = kwargs.get("is_finalized", False)
        # Surrogate model path
        surrogate_model_path = kwargs.get("surrogate_model_path", None)
        if surrogate_model_path is not None:
            self["surrogate_model_path"] = str(Path(surrogate_model_path))
        else:
            self["surrogate_model_path"] = None
        self._surrogate_model = None

    @property
    def solution_paths(self):
        """Return the paths to the solutions.

        Returns
        -------
        list [str]
            The paths to the solutions.
        """
        return [str(Path(self.path) / path) for path in self["solution_paths"]]

    @property
    def is_finalized(self):
        """Return wether the solution is finalized or not.

        Returns
        -------
        bool
            ``True`` if the solution is finalized, ``False`` otherwise.
        """
        return self["is_finalized"]

    @property
    def surrogate_model_path(self):
        """Return the path to model file.

        Returns
        -------
        str
            The path to model file.

        Raises
        ------
        FileNotFoundError
            If the solution does not contain a model file.
            If the model file does not exist.
        """
        # Check if the matrix file exists
        if self["surrogate_model_path"] is None:
            raise FileNotFoundError("The model does not contain a model.")
        path = Path(self.path) / self["surrogate_model_path"]
        if not path.exists():
            raise FileNotFoundError(("The specified model file no longer " "exists."))
        return str(path)

    def get_solutions(self):
        """Return the solutions.

        Returns
        -------
        list [shamo.core.solution.Solution]
            The solutions.
        """
        return [self.SOLUTION_FACTORY.load(path) for path in self.solution_paths]

    def get_surrogate_model(self):
        """Load the surrogate model.

        Returns
        -------
        object
            The surrogate model.
        """
        # Make sure to only load it once
        if self._surrogate_model is None:
            self._surrogate_model = pickle.load(open(self.surrogate_model_path, "rb"))
        return self._surrogate_model

    def finalize(self, clean=True):
        """Finalize the generation of the parametric solution.

        Parameters
        ----------
        clean : bool, optional
            If set to ``True``, all the temporary files created during the
            generation are removed. (The default is ``True``)

        Returns
        -------
        shamo.solutions.ParametricForwardSolution
            The current solution.

        Raises
        ------
        RuntimeError
            If the solution is not finalized and no sub-solution was found.
        """
        if self.is_finalized:
            return self
        # Check if can be finalized
        sub_paths = []
        pattern = re.compile(r"sol_\d{8}")
        for entry in Path(self.path).iterdir():
            name = entry.name
            if entry.is_dir() and pattern.match(name):
                sub_paths.append(str(Path(name) / "{}.json".format(name)))
        if len(sub_paths) == 0:
            raise RuntimeError("No sub-solution found.")
        self["solution_paths"] = sorted(sub_paths)
        # Remove all `.py` files
        if clean:
            for entry in Path(self.path).iterdir():
                if entry.suffix == ".py":
                    entry.unlink()
        # Set common data
        solutions = self.get_solutions()
        self["shape"] = solutions[0].shape
        self["sensors"] = solutions[0].sensors
        # Remove duplicated elements files
        elements_path = "{}_elements.npz".format(self.name)
        shutil.copy(solutions[0].elements_path, str(Path(self.path) / elements_path))
        self["elements_path"] = elements_path
        for solution in solutions:
            Path(solution.elements_path).unlink()
            solution["elements_path"] = str(Path("..") / elements_path)
            solution.save()
        # Generate the surrogate model
        self.generate_surrogate_model()
        self["is_finalized"] = True
        self.save()
        return self

    @abc.abstractmethod
    def generate_surrogate_model(self):
        """Generate the surrogate model.

        Returns
        -------
        shamo.solutions.ParametricForwardSolution
            The current solution.
        """

    @abc.abstractmethod
    def generate_matrix(self, **kwargs):
        """Generate a new matrix based on the surrogate model.

        Returns
        -------
        numpy.ndarray
            The generated matrix.

        Notes
        -----
        You can pass any named parameter corresponding to a varying parameter.
        """

    @abc.abstractmethod
    def generate_solution(self, name, parent_path, **kwargs):
        """Generate a solution based on the surrogate model.

        Parameters
        ----------
        name : str
            The name of the solution.
        parent_path : PathLike
            The path to the parent directory of the solution.

        Returns
        -------
        shamo.solutions.ForwardSolution
            The generated solution.

        Notes
        -----
        You can pass any named parameter corresponding to a varying parameter.
        """
