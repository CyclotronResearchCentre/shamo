# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 21-10-13

### Added

- Added rectangular electrodes for tDCS.

### Fixed

- Fixed field interpolation. Before, the only case in which field interpolation worked was when the field was aligned with the structural image used to generate the mesh. Now, it works no matter the orientation of the field.
- Fixed template embedding in the package. It looks like, before, template files were not included in the package/not accessible.
- Fixed moving file between different drives. Shamo now uses `shutil` to perform this action.
- Fixed `None` mask in grid conversion.

### Changed

- All `.nii` files are now `.nii.gz` files.
- HD-tDCS solutions now contain the raw GetDP results so that it is possible to regenerate the `.pos` files. This allows the user to only keep the files of interest while still having the ability to get the others back if needed.

## [1.1.1] - 21-06-01

### Fixed

- Fixed structure parsing in `mesh_from_surfaces` to allow single child tissues.

## [1.1.0] - 21-04-22

### Added

- Added logging support for subprocesses and C libraries via `subprocess_to_logger` and `stream_to_logger` context managers.
- Added documentation on how to use the logging library with `shamo`.
- Added the `mesh_from_fem` method to provide a way to generate a mesh from a previously built one by merging tissues together.
- Added the `mesh_from_surfaces` method to provide a way to generate a mesh from a set of surface meshes.
- Added `SurrMaskedScalar` and `SurrMaskedScalarNii` to enable more sensitivity analysis.
- Added `SurrMaskedScalarNiiJ`, `SurrMaskedScalarNiiMagJ` and `SurrMaskedScalarNiiV` for tDCS.

### Changed

- Moved GetDP logging to the new logging `subprocess_to_logger` context manager.

## [1.0.0] - 20-12-16

### Added

- Added `ObjABC`, `ObjFile` and `ObjDir` classes to provide a base for any savable/loadable object.
- Added `Group`, `Tissue`, `Field`, `Sensor`, `PointSensor` and `FEM` classes to provide a way to generate realistic finite element model based on labelled volumes.
- Added `ProbABC`, `CompABC`, `CompFilePath`, `CompGridSampler`, `CompSensors`, `CompTissueProp`, `CompTissues` and `ProbGetDP` classes to define any problem.
- Added `SolGetDP` class to store information about the solution of a `ProbGetDP` problem.
- Added `DistABC`, `DistConstant`, `DistNormal`, `DistTruncNormal` and `DistUniform` to model random parameters for parametric problems.
- Added `ProbParamABC`, `CompParamTissueProp`, `CompParamValue`, and `ProbParamGetDP` classes to define any parametric problem.
- Added `SolParamABC` and `SolParamGetDP` classes to store information about the solution of a `ProbParamABC` problem.
- Added `ProbEEGLeadfield` and `SolEEGLeadfield` classes to solve the EEG forward problem.
- Added `ProbParamEEGLeadfield`, `SolParamEEGLeadfield` and `SurrEEGLeadfield` classes to solve the parametric EEG forward problem. Also added `SurrEEGLeadfieldToRef` class to evalaute the sensitivity of the EEG leadfield matrix.
- Added `ProbHDTDCSSim` and `SolHDTDCSSim` classes to simulate a HD-tDCS.
- Added `ProbParamHDTDCSSim` and `SolParamHDTDCSSim` classes to simulate a parametric HD-tDCS.
- Added `SurrogateABC` class to define any surrogate model based on a `SolParamABC`.
- Added `SurrScalar` class to define any surrogate model returning a scalar to perform sensitivity analysis.
- Added `shamo-report` command to facilitate bug report.
- Added automated full reference with sphinx autosummary.
