# Structured Logging

You can easily get structured logging with notion-sdk-py by using
[structlog](https://www.structlog.org/en/stable/index.html):

```python
logger = structlog.wrap_logger(
    logging.getLogger("notion-client"),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
)

notion = Client(auth=token, logger=logger, log_level=logging.DEBUG)
```

Don't forget to add the dependency to your project!
