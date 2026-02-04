'''
Backward-compatible import shim.

The BLS client has been refactored into the ``eco_stats.api.bls``
package.  This module re-exports :class:`BLSClient` so that existing
code using ``from eco_stats.api.bls_client import BLSClient`` continues
to work.
'''

from eco_stats.api.bls.client import BLSClient

__all__ = ['BLSClient']
