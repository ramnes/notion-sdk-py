# Iterators #

The iterator helpers make paging through API results easier.  Rather than requiring
each caller to look for additional data, the iterators take care of this task.

See [](https://developers.notion.com/reference/pagination) for more information.

## EndpointIterator ##

Iterates over results from a given API endpoint.  It accepts the target endpoint
as well as any additional parameters required by the endpoint.

### EndpointIterator Example ###

```python
iter = EndpointIterator(
    endpoint=client.search,
    query='task',
    sort={
        'direction': 'ascending',
        'timestamp': 'last_edited_time'
    }
)
```
