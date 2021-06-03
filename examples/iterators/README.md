# Iterators #

The iterator helpers make paging through API results easier.  Rather than requiring
each caller to look for additional data, the iterators take care of this task.

See [](https://developers.notion.com/reference/pagination) for more information.

## EndpointIterator ##

This is the generalized form of the endpoint iterators.  It accepts the target
endpoint as well as any additional parameters required by the endpoint.

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

## SearchIterator ##

Provides iteration over search results.  The parameters used by this iterator
are standard search parameters.

See [](https://developers.notion.com/reference/post-search) for more
information.

### SearchIterator Example ###

```python
iter = SearchIterator(
    client=client,
    query=findme,
    sort={
        'direction': 'ascending',
        'timestamp': 'last_edited_time'
    }
)
```

## QueryIterator ##

Provides iteration over database query results.  The parameters used by this
iterator are standard database query parameters.

See [](https://developers.notion.com/reference/post-database-query) for more
information.

### QueryIterator Example ###

```python
iter = QueryIterator(
    client=client,
    database_id=dbid,
    sorts=[
        {
            'direction': 'ascending',
            'timestamp': 'last_edited_time'
        }
    ]
)
```

## DatabaseIterator ##

Iterates over all available databases to the integration.

See [](https://developers.notion.com/reference/post-database-query) for more
information.

### DatabaseIterator Example ###

```python
iter = DatabaseIterator(client)
```

## UserIterator ##

Iterates over all users in the current workspace.

See [](https://developers.notion.com/reference/get-users) for more information.

### UserIterator Example ###

```python
iter = UserIterator(client)
```

## ChildrenIterator ##

Iterates over all child blocks of a given page.

See [](https://developers.notion.com/reference/get-block-children) for more
information.

### ChildrenIterator Example ###

```python
iter = ChildrenIterator(client, page_id)
```
