# pylatex_ext
🔌Extension of pylatex

## Download
It has not been uploaded to pypi, download it from github.

## What am I proud of?

```python
class Slash:
    """Shorthand for Command.
    
    Make defining command more eazy.
    """

    escape = False

    def __getattr__(self, command):
        def f(*args, **kwargs):
            args = Arguments(*args)
            args.escape = self.escape
            return Command(command, arguments=args, **kwargs)
        return f

__ = Slash()  # __.frac('x', 'y').dumps() == '\frac{x}{y}'

def diff(y, x='x'):
    r"""Generate Latex code r'\frac{d y}{d x}'.

    Arguments:
        y {str} -- dependent variable

    Keyword Arguments:
        x {str} -- independent variable (default: {'x'})

    Returns:
        Command
    """
    return __.frac(
        (__.mathrm('d').dumps()) + y, (__.mathrm('d').dumps()) + x)

```

## Application
I make a system to produce exam paper (with or without answer) with `pylatex_ext`
