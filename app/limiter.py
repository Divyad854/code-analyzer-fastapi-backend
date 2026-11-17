from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
# Creates a rate limiter that identifies clients by their IP address.