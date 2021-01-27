from shamo.core.surrogate import SurrMaskedScalarNii


class SurrMaskedScalarNiiJ(SurrMaskedScalarNii):
    @classmethod
    def fit(cls, name, parent_path, sol, **kwargs):
        return super().fit(name, parent_path, sol, suffix="j", **kwargs)


class SurrMaskedScalarNiiMagJ(SurrMaskedScalarNii):
    @classmethod
    def fit(cls, name, parent_path, sol, **kwargs):
        return super().fit(name, parent_path, sol, suffix="mag_j", **kwargs)


class SurrMaskedScalarNiiV(SurrMaskedScalarNii):
    @classmethod
    def fit(cls, name, parent_path, sol, **kwargs):
        return super().fit(name, parent_path, sol, suffix="v", **kwargs)
