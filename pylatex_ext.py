# -*- coding: utf-8 -*-

'''
extension of pylatex
'''

import pathlib
import codecs

import numpy as np

from pylatex import *
from pylatex.base_classes import *
from pylatex.utils import *

class MyEnvironment(Environment):
    def dumps(self):
        # override method dumps

        content = self.dumps_content()
        if not content.strip() and self.omit_if_empty:
            return ''

        string = ''

        # Something other than None needs to be used as extra arguments, that
        # way the options end up behind the latex_name argument.
        if self.arguments is None:
            extra_arguments = Arguments()
        else:
            extra_arguments = self.arguments

        begin = Command('begin', self.start_arguments, self.options,
                        extra_arguments=extra_arguments)
        begin.arguments._positional_args.insert(0, self.latex_name)
        string += begin.dumps() + '%\n'

        string += content + '%\n'

        string += Command('end', self.latex_name).dumps()

        return string


class Align(MyEnvironment):
    """A class to wrap LaTeX's align environment."""
    escape = False
    content_separator = "\\\\\n"
    _star_latex_name = True

    def add_row(self, row):
        self.append(dumps_list([elm for elm in row], token=' & ', escape=False))


class Cases(MyEnvironment):
    """A class to wrap LaTeX's align environment."""
    escape = False
    content_separator = "\\\\\n"



def sub(x, y):
    return NoEscape('%s_%s'%(x, y))

def sup(x, y):
    return NoEscape('%s^%s'%(x, y))


class XeDocument(Document):
    _latex_name = 'document'
    def dumps(self):
        # add firstline before the document
        firstline = '%!TEX program = xelatex'
        return firstline + '\n\n' + super(XeDocument, self).dumps()

    def usepackage(self, packages):
        if isinstance(packages, str):
            self.packages.append(Package(packages))
        elif isinstance(packages, (tuple, list, set)):
            for package in packages:
               self.usepackage(package)

    def write(self, filename):
        if isinstance(filename, str):
            filename = pathlib.Path(filename)
        with codecs.open(filename.with_suffix('.tex'), 'w', encoding='utf-8') as fo:
            fo.write(self.dumps())

    def topdf(self, filename, clean=True):

        import subprocess
        if isinstance(filename, str):
            filename = pathlib.Path(filename)
        tex = filename.with_suffix('.tex')
        if not tex.exists():
            self.write(filename)
        command = ['latexmk', '-xelatex', '-f', str(tex)]
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            # For all other errors print the output and raise the error
            print(e.output.decode())
            raise
        else:
            print(output.decode())

        if clean:
            try:
                # Try latexmk cleaning first
                subprocess.check_output(['latexmk', '-c', filename], stderr=subprocess.STDOUT)
            except (OSError, IOError, subprocess.CalledProcessError) as e:
                # Otherwise just remove some file extensions.
                extensions = ['aux', 'log', 'out', 'fls', 'fdb_latexmk']
                for ext in extensions:
                    if pathlib.Path(basename + '.' + ext).exists():
                        os.remove(basename + '.' + ext)



def large(s, *, escape=True):
    r"""Make a string appear large in LaTeX formatting.
    large() wraps a given string in the LaTeX command \Large{}.
    Args
    ----
    s : str
        The string to be formatted.
    escape: bool
        If true the large text will be escaped
    Returns
    -------
    NoEscape
        The formatted string.
    Examples
    --------
    >>> large("hello")
    '\\Large{hello}'
    >>> print(large("hello"))
    \Large{hello}
    """

    if escape:
        s = escape_latex(s)

    return NoEscape(r'\Large{' + s + '}')


def dollar(x, *args, **kwargs):
    '''inline math form: $math expression$
    example: dollar('c_B') # $c_B$
    '''
    return Math(data=x, inline=True, escape=False, *args, **kwargs)


def vector(x, mtype='p', *args, **kwargs):
    # x is a matrix(1*n-shape) or vector(n-dim) or a list of numbers
    if isinstance(x, np.ndarray) and x.ndim == 1:
        x = x.reshape(1, x.shape[0])
    elif isinstance(x, (tuple, list)):
        x = np.array([x])
    return Matrix(x, mtype=mtype, *args, **kwargs)

class Determinant(Matrix):
    '''Determinant < Matrix
    data: square matrix
    '''
    def __init__(self, data, *args, **kwargs):
        if isinstance(data, (tuple, list)):
            data = np.array(data)
        assert data.ndim == 2 and data.shape[1] == data.shape[0]
        super(Determinant, self).__init__(data, mtype='v', *args, **kwargs)

    @property
    def T(self):
        self.data = np.transpose(self.data)
        return self

class Vector(Matrix):
    '''Vector < Matrix
    data: array(1D) | tuple | list (of numbers)
    '''
    def __init__(self, data, mtype='p', *args, **kwargs):
        if isinstance(data, np.ndarray):
            data = data
        elif isinstance(data, (tuple, list)):
            data = np.array(data)
        if data.ndim == 1:
            data = data.reshape(1, data.shape[0])
        super(Vector, self).__init__(data, mtype=mtype, *args, **kwargs)

    @property
    def T(self):
        self.data = np.transpose(self.data)
        return self


def colvector(x, mtype='p', *args, **kwargs):
    # x is a matrix(1*n-shape) or vector(n-dim) or a list of numbers
    # x -> a colume vector in latex code
    if isinstance(x, np.ndarray):
        assert data.ndim == 1, 'make sure data.ndim == 1'
        x = x.reshape(x.shape[0], 1)
    elif isinstance(x, (tuple, list)):
        x = np.array([[xi] for xi in x])
    return Matrix(x, mtype=mtype, *args, **kwargs)


def newcommand(name, definition, n=-1, default=None, prefix=''):
    '''generate the latex code of newcommand
    
    Example:
    >>> newcommand('mycmd','#1+#2', -1, 'lala').dumps()
    \newcommand{\mycmd}[2][lala]{#1+#2}
    
    Arguments:
        name {str} -- name of new command
        definition {str} -- the body of command
    
    Keyword Arguments:
        n {number} -- the number of arguments (default: {-1})
        default {str} -- the default value of the first argument (default: {None})
        prefix {str} -- '', re' or 'provide' (default: {''})
    
    Returns:
        UnsafeCommand
    '''
    if prefix:
        newcmd = prefix + 'newcommand'
    if n < 0:
        import re
        rx = re.compile('(?<=#)\d')
        n = max(map(int, rx.findall(definition)))
    if default is None:
        if n == 0:
            return UnsafeCommand(newcmd, arguments='\\%s'%name, extra_arguments=definition)
        return UnsafeCommand(newcmd, arguments='\\%s'%name, options=n, extra_arguments=definition)
    else:
        return UnsafeCommand(newcmd, arguments='\\%s'%name, options=SpecialOptions(n, default), extra_arguments=definition)