# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2020-08-05

### Added

- TruncatedNormalDistribution to model distributions from paper.

## [0.2.0] - 2020-07-29

### Added

- MaternProd kernel to provide proper implementation of the kernel fr further computations.

### Changed

- Use Halton sequence rather than quadrature rule to define evaluation points.
- The kernel used in parametric problems is now a compound of a constant kernel and a MaternProd kernel.

## [0.1.1] - 2020-07-27

### Added

- Automated docker images build.
- Automated PyPI package build.
- Docstrings for non documented functions.

### Changed

- Use [black](https://github.com/psf/black) as a codestyle formatter.
- Use the [src layout](https://blog.ionelmc.ro/2014/05/25/python-packaging/).
- Tox test environments.

## [0.1.0] - 2020-05-13

### Added

- Finite element model generation from labeled (segmented) images.
- EEG forward problem resolution.
- EEG parametric forward resolution and surrogate model generation.
- EEG simulation.
- Sphinx documentation.
- Examples for finite element model generation, EEG forward problem resolution, EEG parametric forward problem resolution and EEG simulation.
