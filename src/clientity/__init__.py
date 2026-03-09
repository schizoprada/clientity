"""
clientity
"""
__author__ = "Joel Yisrael"
__version__ = "0.1.7"

VERSION = tuple(map(int, __version__.split('.')))

from .core import (
    Client, client,
    endpoint, resource, namespace,
    query, unwrap, payload
)

rs = resource
ns = namespace
ep = endpoint
get = ep.get
put = ep.put
post = ep.post
head = ep.head
patch = ep.patch
delete = ep.delete
options = ep.options
