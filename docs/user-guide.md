# User Guide

## Logging

### Structlog

If you use [structlog](https://www.structlog.org/en/stable/index.html) you need to use a wrapper like so:

```python
_log = structlog.wrap_logger(
    logging.getLogger("notion-client"),  # You can change the name to whatever you like.
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
)
notion = Client(auth=token, logger=_log, log_level=logging.DEBUG)
```
