# Contributing to shamo

First, I would like to thank you for your interest in *shamo*. If you want to improve the tool, here are the ways you can help:
- [Requesting new features](#requesting-new-features)
- [Finding and reporting bugs](#finding-and-reporting-bugs)
- [Enhancing documentation and examples](enhancing-documentation-and-examples)
- [Developing shamo](#developing-shamo)
    - [Adding new features](#adding-new-features)
    - [Enhancing existing features](#enhancing-existing-features-and-fixing-bugs)

## Requesting new features

To request a new feature, head over to [this page](https://github.com/CyclotronResearchCentre/shamo/issues/new), pick the feature request template and describe as precisely as possible the feature you want to be added.

## Finding and reporting bugs

To report a bug, head over to [this page](https://github.com/CyclotronResearchCentre/shamo/issues/new), pick the bug report template and describe as precisely as possible the issue you are facing.

## Enhancing documentation and examples

If you want to only edit the documentation, make of fork of the project. Once it is done, clone the repository on your machine and start working on the documentation. If you want to edit the code, take a look at [developing shamo](#developing-shamo).

## Developing shamo

If you want to participate to the development of *shamo*, make of fork of the project. Once it is done, clone the repository on your machine and create a virtual environment in the project directory following these steps:

```shell
python3 -m venv --prompt shamo .venv
.venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -r dev-requirements.txt
python3 -m pip install -e .
```

Make sure you also have [Gmsh](https://gmsh.info/#Download), [GetDP](https://getdp.info/#Download) and [CGAL](https://www.cgal.org/download.html) installed on your computer.

This project uses [black](https://black.readthedocs.io/en/stable/index.html) for its code formatting so make sure to either [integrate it to your code editor](https://black.readthedocs.io/en/stable/editor_integration.html) to apply the format directly in it or to [install a pre-commit hook](https://black.readthedocs.io/en/stable/version_control_integration.html).

Once everything is properly setup, create a new branch called `feature/{feature_name}` and start writing code.

When you are done working, create a [pull request](https://github.com/CyclotronResearchCentre/shamo/pulls). We'll review the modifications you did as soon as possible.

### Adding new features

<!-- TODO: Add documentation about how to add a new problem-solution pair. -->

### Enhancing existing features and fixing bugs

<!-- TODO: Add documentation about how to propose bug fixes and features enhancements. -->
