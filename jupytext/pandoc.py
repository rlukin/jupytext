"""Jupyter notebook to Markdown and back, using Pandoc"""

import os
import subprocess
import tempfile
import nbformat
from pkg_resources import parse_version


class PandocError(OSError):
    """An error related to Pandoc"""
    pass


def pandoc(args, filein=None, fileout=None):
    """Execute pandoc with the given arguments"""
    cmd = [u'pandoc']

    if filein:
        cmd.append(filein)

    if fileout:
        cmd.append('-o')
        cmd.append(fileout)

    cmd.extend(args.split())

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode:
        raise PandocError('pandoc exited with return code {}\n{}'.format(proc.returncode, str(err)))
    return out.decode('utf-8')


def is_pandoc_available():
    """Is Pandoc>=2.7.1 available?"""
    try:
        pandoc_version()
        return True
    except (IOError, OSError, PandocError):
        return False


def pandoc_version():
    """Pandoc's version number"""
    version = pandoc(u'--version').splitlines()[0].split()[1]
    if parse_version(version) < parse_version('2.7.1'):
        raise PandocError('Please install pandoc>=2.7.1 (found version {})'.format(version))

    return version


def md_to_notebook(text):
    """Convert a Markdown text to a Jupyter notebook, using Pandoc"""
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_file.write(text.encode('utf-8'))
    tmp_file.close()

    pandoc(u'--from markdown --to ipynb -s --atx-headers --wrap=preserve', tmp_file.name, tmp_file.name)

    with open(tmp_file.name, encoding='utf-8') as opened_file:
        notebook = nbformat.read(opened_file, as_version=4)
    os.unlink(tmp_file.name)

    return notebook


def notebook_to_md(notebook):
    """Convert a notebook to its Markdown representation, using Pandoc"""
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_file.write(nbformat.writes(notebook).encode('utf-8'))
    tmp_file.close()

    pandoc(u'--from ipynb --to markdown -s --atx-headers --wrap=preserve', tmp_file.name, tmp_file.name)

    with open(tmp_file.name, encoding='utf-8') as opened_file:
        text = opened_file.read()

    os.unlink(tmp_file.name)
    return '\n'.join(text.splitlines())
