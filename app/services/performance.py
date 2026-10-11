from contextlib import contextmanager
from time import perf_counter
import logging

logger = logging.getLogger(__name__)


@contextmanager
def measure_time(stage: str):
    start = perf_counter()

    try:
        yield
    finally:
        elapsed = perf_counter() - start

        logger.info(
            "Performance | stage=%s | duration=%.3fs",
            stage,
            elapsed,
        )