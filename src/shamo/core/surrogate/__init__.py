"""API for `shamo.core.surrogate`."""
from .abc import SurrABC
from .scalar import SurrScalar
from .masked_scalar import SurrMaskedScalar, SurrMaskedScalarNii


__all__ = ["SurrABC", "SurrScalar", "SurrMaskedScalar", "SurrMaskedScalarNii"]
