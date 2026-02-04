'''
BLS series ID builder and parser.

BLS series IDs are fixed-width strings whose character positions encode
the survey program, seasonal adjustment, area, industry, item, and other
components.  The exact layout differs by program and is defined in the
:mod:`eco_stats.api.bls.programs` registry.

This module provides two pure functions:

* :func:`parse_series_id` — decompose an existing ID into named fields.
* :func:`build_series_id` — construct an ID from named components.
'''

from typing import Dict

from eco_stats.api.bls.programs import get_program


def parse_series_id(series_id: str) -> Dict[str, str]:
    '''
    Decompose a BLS series ID into its component fields.

    The first two characters identify the program, which determines
    how the remaining positions are interpreted.

    Args:
        series_id: A full BLS series ID string
            (e.g., ``"CUUR0000SA0"`` or ``"CES0000000001"``).

    Returns:
        Dictionary mapping field names to their extracted values.
        Always includes a ``"program"`` key with the two-letter prefix.

    Raises:
        KeyError: If the program prefix is not in the registry.
        ValueError: If the series ID is shorter than the program format
            requires.

    Example::

        >>> parse_series_id("CUUR0000SA0")
        {'program': 'CU', 'prefix': 'CU', 'seasonal': 'U',
         'periodicity': 'R', 'area': '0000', 'item': 'SA0'}

        >>> parse_series_id("CES0000000001")
        {'program': 'CE', 'prefix': 'CE', 'seasonal': 'S',
         'supersector': '00', 'industry': '000000', 'data_type': '01'}
    '''
    if len(series_id) < 2:
        raise ValueError(f'Series ID must be at least 2 characters, got {series_id!r}')

    prefix = series_id[:2].upper()
    program = get_program(prefix)

    if len(series_id) < program.series_id_length:
        raise ValueError(
            f'Series ID {series_id!r} is too short for program {prefix}. '
            f'Expected at least {program.series_id_length} characters, '
            f'got {len(series_id)}.'
        )

    result: Dict[str, str] = {'program': prefix}
    for field in program.fields:
        result[field.name] = field.extract(series_id)

    return result


def build_series_id(program: str, **components: str) -> str:
    '''
    Construct a BLS series ID from named components.

    Components that are not provided will be filled with ``"0"`` padding
    to the correct width (suitable for "all" / default values in most
    BLS programs).

    The ``"prefix"`` component is set automatically from the *program*
    argument and should not be passed.

    Args:
        program: Two-letter program prefix (e.g., ``"CU"``).
        **components: Field values keyed by name.  Unknown names are
            silently ignored.

    Returns:
        The assembled series ID string.

    Raises:
        KeyError: If the program prefix is not in the registry.

    Example::

        >>> build_series_id("CU", seasonal="U", periodicity="R",
        ...                 area="0000", item="SA0")
        'CUUR0000SA0'

        >>> build_series_id("CE", seasonal="S", supersector="00",
        ...                 industry="000000", data_type="01")
        'CES0000000001'
    '''
    prog = get_program(program)

    # Start with a mutable list of characters, zero-filled.
    length = prog.series_id_length
    chars = ['0'] * length

    # Always set the prefix.
    components['prefix'] = prog.prefix

    for field in prog.fields:
        value = components.get(field.name, None)
        if value is not None:
            # Right-pad or left-pad depending on convention:
            # BLS uses left-aligned text and zero-padded numerics, but
            # we keep it simple — just place the value left-aligned
            # and truncate / pad to fit.
            padded = value.ljust(field.length, '0')[: field.length]
            for i, ch in enumerate(padded):
                chars[field.start - 1 + i] = ch

    return ''.join(chars)
