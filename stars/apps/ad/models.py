
from abstract_models import AbstractRollingAd
from oscar.core.loading import is_model_registered

__all__ = []

__APP_LABEL__ = 'ad'
if not is_model_registered(__APP_LABEL__, 'RollingAd'):
    class RollingAd(AbstractRollingAd):
        pass
    __all__.append('RollingAd')
