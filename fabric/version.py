"""
Current Fabric version constant plus version pretty-print method.

This functionality is contained in its own module to prevent circular import
problems with ``__init__.py`` (which is loaded by setup.py during installation,
which in turn needs access to this version information.)
"""

import os
import re


_VERSION_RE = re.compile(
    r'^(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<patch>\d+))?'
    r'(?:(?P<type>a|b|rc)(?P<type_num>\d*)?)?$'
)
_PROJECT_VERSION_RE = re.compile(
    r'^version\s*=\s*["\'](?P<version>[^"\']+)["\']\s*$'
)
_VERSION_TYPE_NAMES = {
    'a': 'alpha',
    'b': 'beta',
    'rc': 'release candidate',
}


def _project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_pyproject_version():
    pyproject = os.path.join(_project_root(), 'pyproject.toml')
    in_project = False

    try:
        with open(pyproject) as fd:
            for raw_line in fd:
                line = raw_line.strip()
                if line == '[project]':
                    in_project = True
                    continue
                if line.startswith('['):
                    in_project = False
                if in_project:
                    match = _PROJECT_VERSION_RE.match(line)
                    if match:
                        return match.group('version')
    except IOError:
        return None

    return None


def _read_installed_version():
    try:
        from importlib import metadata
    except ImportError:
        return None

    try:
        return metadata.version('fab-classic')
    except metadata.PackageNotFoundError:
        return None


def _read_project_version():
    version = _read_pyproject_version() or _read_installed_version()
    if version is None:
        raise RuntimeError('Unable to determine fab-classic version')
    return version


def _parse_version(version):
    match = _VERSION_RE.match(version)
    if match is None:
        raise ValueError('Unsupported version string: %s' % version)

    type_key = match.group('type')
    type_num = match.group('type_num')
    return (
        int(match.group('major')),
        int(match.group('minor')),
        int(match.group('patch') or 0),
        _VERSION_TYPE_NAMES[type_key] if type_key else 'final',
        int(type_num) if type_num else 0,
    )


VERSION = _parse_version(_read_project_version())


def git_sha():
    # removed functionality - only worked if this file is currently in a git repo
    return None


def get_version(form='short'):
    """
    Return a version string for this package, based on `VERSION`.

    Takes a single argument, ``form``, which should be one of the following
    strings:

    * ``branch``: just the major + minor, e.g. "0.9", "1.0".
    * ``short`` (default): compact, e.g. "0.9rc1", "0.9.0". For package
      filenames or SCM tag identifiers.
    * ``normal``: human readable, e.g. "0.9", "0.9.1", "0.9 beta 1". For e.g.
      documentation site headers.
    * ``verbose``: like ``normal`` but fully explicit, e.g. "0.9 final". For
      tag commit messages, or anywhere that it's important to remove ambiguity
      between a branch and the first final release within that branch.
    * ``all``: Returns all of the above, as a dict.
    """
    # Setup
    versions = {}
    branch = "%s.%s" % (VERSION[0], VERSION[1])
    tertiary = VERSION[2]
    type_ = VERSION[3]
    final = (type_ == "final")
    type_num = VERSION[4]
    firsts = "".join([x[0] for x in type_.split()])

    # Branch
    versions['branch'] = branch

    # Short
    v = branch
    if (tertiary or final):
        v += "." + str(tertiary)
    if not final:
        v += firsts
        if type_num:
            v += str(type_num)
    versions['short'] = v

    # Normal
    v = branch
    if tertiary:
        v += "." + str(tertiary)
    if not final:
        if type_num:
            v += " " + type_ + " " + str(type_num)
        else:
            v += " pre-" + type_
    versions['normal'] = v

    # Verbose
    v = branch
    if tertiary:
        v += "." + str(tertiary)
    if not final:
        if type_num:
            v += " " + type_ + " " + str(type_num)
        else:
            v += " pre-" + type_
    else:
        v += " final"
    versions['verbose'] = v

    try:
        return versions[form]
    except KeyError:
        if form == 'all':
            return versions
        raise TypeError('"%s" is not a valid form specifier.' % form)


__version__ = get_version('short')

if __name__ == "__main__":
    print(get_version('all'))
