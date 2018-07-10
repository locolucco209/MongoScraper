# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2016 Continuum Analytics, Inc.
#
# May be copied and distributed freely only as part of an Anaconda or
# Miniconda installation.
# -----------------------------------------------------------------------------
"""Launch applications utilities."""

# Standard library imports
import os
import subprocess

# Local imports
from navigator_updater.config import HOME_PATH, LINUX, MAC, get_conf_path
from navigator_updater.utils.logs import logger


def is_program_installed(basename):
    """
    Return program absolute path if installed in PATH.

    Otherwise, return None
    """
    for path in os.environ["PATH"].split(os.pathsep):
        abspath = os.path.join(path, basename)
        if os.path.isfile(abspath):
            return abspath


def run_app_on_win(prefix, command, package_name, root_prefix):
    """Run application on unix system an ensure proper env activation."""
    quote = '"' if ' ' in prefix and '"' not in prefix else ''

    # Call is needed to avoid the batch script from closing after running
    # the first (environment activation) line
    prefix = prefix.replace('\\', '/')
    cmd = (
        'call {QUOTE}{CONDA_PREFIX}/Scripts/activate{QUOTE} '
        '{QUOTE}{CONDA_PREFIX}{QUOTE}\n'
        '{QUOTE}{COMMAND}{QUOTE}\n'
    ).format(
        CONDA_PREFIX=prefix,
        COMMAND=command,
        QUOTE=quote,
    )
    cmd = cmd.replace('/', '\\')  # Turn slashes back to windows standard

    suffix = 'bat'
    fpath = create_app_run_script(
        cmd,
        package_name,
        prefix,
        root_prefix,
        suffix,
    )
    CREATE_NO_WINDOW = 0x08000000
    pid = subprocess.Popen(
        fpath,
        creationflags=CREATE_NO_WINDOW,
        shell=True,
        cwd=HOME_PATH,
    ).pid
    return pid


def run_app_on_unix(prefix, command, package_name, root_prefix):
    """Run application on unix system an ensure proper env activation."""
    if command.startswith('open'):
        command = command.replace('open ', '')
        start = 'open '
    else:
        start = ''

    quote = '"' if ' ' in prefix and '"' not in prefix else ''
    prefix = prefix.replace('\\', '/')
    cmd = (
        '#!/usr/bin/env bash\n'
        'source {QUOTE}{CONDA_PREFIX}/bin/activate{QUOTE} '
        '{QUOTE}{CONDA_PREFIX}{QUOTE}\n'
        '{START}{QUOTE}{COMMAND}{QUOTE}\n'
    ).format(
        CONDA_PREFIX=prefix,
        COMMAND=command,
        START=start,
        QUOTE=quote,
    )
    suffix = 'sh'
    fpath = create_app_run_script(
        cmd,
        package_name,
        prefix,
        root_prefix,
        suffix,
    )
    pid = subprocess.Popen(
        fpath,
        shell=False,
        cwd=HOME_PATH,
    ).pid
    return pid


def create_app_run_script(command, package_name, prefix, root_prefix, suffix):
    """Create the script to run the application and activate th eenvironemt."""
    # qtpy is adding this to env on startup and this is messing qtconsole
    # and other apps on other envs with different versions of QT
    if 'QT_API' in os.environ:
        os.environ.pop('QT_API')

    package_name = package_name or 'app'

    if root_prefix == prefix:
        scripts_path = os.path.join(get_conf_path(), 'scripts')
    else:
        scripts_path = os.path.join(
            get_conf_path(), 'scripts', prefix.split('/')[-1]
        )

    if not os.path.isdir(scripts_path):
        os.makedirs(scripts_path)
    fpath = os.path.join(scripts_path, '{0}.{1}'.format(package_name, suffix))

    with open(fpath, 'w') as f:
        f.write(command)
    os.chmod(fpath, 0o777)

    return fpath


def launch(
    prefix,
    command,
    leave_path_alone,
    working_directory=HOME_PATH,
    package_name=None,
    root_prefix=None,
):
    """Handle launching commands from projects."""
    logger.debug(str((prefix, command)))
    command = command.replace('\\', '/')
    prefix = prefix.replace('\\', '/')
    root_prefix = root_prefix.replace('\\', '/')

    pid = -1

    if os.name == 'nt' and not leave_path_alone:
        command = command.replace('/bin', '/Scripts')

    if MAC or LINUX:
        pid = run_app_on_unix(
            prefix=prefix,
            command=command,
            package_name=package_name,
            root_prefix=root_prefix
        )
    else:
        pid = run_app_on_win(
            prefix=prefix,
            command=command,
            package_name=package_name,
            root_prefix=root_prefix
        )
    return pid
