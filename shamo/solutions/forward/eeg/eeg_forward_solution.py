"""Implement `EEGForwardSolution` class.

This module implements the `EEGForwardSolution` class which holds the data
corresponding to the solution of the EEG forward problem.
"""
from shamo.solutions import ForwardSolution


class EEGForwardSolution(ForwardSolution):

    from shamo import EEGForwardProblem

    PROBLEM_FACTORY = EEGForwardProblem
    N_VALUES_PER_ELEMENT = 3
