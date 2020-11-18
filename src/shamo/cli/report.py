import os
import subprocess as sub
import yaml

import click
import gmsh


def _get_os_info():
    info = os.uname()
    return {
        "os": info.sysname,
        "release": info.release,
        "version": info.version,
        "architecture": info.machine,
    }


def _get_gmsh_info():
    gmsh.initialize()
    info = gmsh.option.getString("General.BuildInfo")
    gmsh.finalize()
    lines = info.split("; ")
    pairs = [l.split(": ") for l in lines]
    info = {p[0].replace(" ", "-").lower(): p[1] for p in pairs}
    unwanted = ["license", "build-host", "web-site", "issue-tracker"]
    for u in unwanted:
        info.pop(u, None)
    info["build-options"] = info["build-options"].split(" ")
    return info


def _get_getdp_info():
    info = sub.run(["getdp", "-info"], capture_output=True).stderr.decode("utf-8")
    lines = info.strip().split("\n")
    pairs = [l.split(": ") for l in lines]
    info = {p[0].strip().replace(" ", "-").lower(): p[1] for p in pairs}
    unwanted = ["license", "build-host", "web-site", "issue-tracker"]
    for u in unwanted:
        info.pop(u, None)
    build = ["build-options", "gmsh-lib-options"]
    for b in build:
        info[b] = info[b].split(" ")
    return info


def _get_pip_info():
    info = sub.run(["pip", "list"], capture_output=True).stdout.decode("utf-8")
    lines = info.strip().split("\n")[2:]
    pairs = [l.split() for l in lines]
    return {p[0]: p[1] for p in pairs}


@click.command()
def main():
    _get_os_info()
    report = {
        "os": _get_os_info(),
        "gmsh": _get_gmsh_info(),
        "getdp": _get_getdp_info(),
        "packages": _get_pip_info(),
    }
    click.echo(yaml.dump(report))
