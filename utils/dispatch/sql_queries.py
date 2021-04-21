from more_itertools import grouper, flatten


def prepare_insert_stmt(on_conflict=False, returning=False, in_batches=False):

    insert_stmt = (
        "INSERT INTO {table} ({fields}) "
        "VALUES ({placeholders})")
    mode = "w"

    if in_batches:
        insert_stmt = insert_stmt.replace("({placeholders})",
                                          "{multivalues}")

    if on_conflict:
        insert_stmt += (" ON CONFLICT ({upsert_key}) DO UPDATE"
                        " SET ({fields}) = ({placeholders})")

    if returning:
        insert_stmt += " RETURNING {returning_key}"
        mode += "r"

    return mode, insert_stmt


def insert_from_dict(engine, conn, data, table, in_batches=False,
                     on_conflict=False, upsert_key=None,
                     returning=False, returning_key=None):

    mode, insert_stmt = prepare_insert_stmt(on_conflict, returning, in_batches)

    return engine.do_query(conn=conn,
                           mode=mode,
                           query=insert_stmt,
                           upsert_key=upsert_key,
                           returning_key=returning_key,
                           table=table,
                           data=data)


def upsert_tuple_containing_jsonb(engine, conn, tuple_, fields, table,
                                  upsert_key, on_conflict=True):

    mode, insert_stmt = prepare_insert_stmt(on_conflict)
    upsert_stmt = insert_stmt.replace("{placeholders}",
                                     ("%s,"*len(tuple_)).rstrip(","))

    # we need to double the elements of data, since we are upserting
    # there is twice the number of placeholders as the elements in tuple_.
    return engine.do_query(conn=conn,
                           mode=mode,
                           query=upsert_stmt,
                           table=table,
                           fields=fields,
                           upsert_key=upsert_key,
                           data=tuple_*2)


def make_delete_stmt(del_keys):

    where_k = del_keys[0]
    del_stmt = f"DELETE FROM {{table}} WHERE {where_k} = %s"

    def add_ands(s, and_ks):
        if not and_ks:
            return s
        else:
            and_k = and_ks[0]
            s += f" AND {and_k} = %s"
        return add_ands(s, and_ks[1:])

    # no and stmt necessary
    if len(del_keys) == 1:
        return del_stmt

    # recursively form and stmts
    if len(del_keys) > 1:
        return add_ands(del_stmt, and_ks=del_keys[1:])


def delete_from_table(engine, conn, table_name, del_keys, data):

    del_keys = list(del_keys) if isinstance(del_keys, str) else del_keys

    return engine.do_query(conn=conn,
                           mode="w",
                           query=make_delete_stmt(del_keys=del_keys),
                           table=table_name,
                           data=data)


def make_batches(data, max_allowed):

    if (not isinstance(data, (tuple, list))
        or not isinstance(data[0], (tuple, list))):

        raise ValueError(f"Collection of collections expected, got"
                         f" {type(data)}")
    if not data:
        raise ValueError("Got any empty collection for batch insert.")

    def get_batch_size():

        # batch data is a rectangle:
        # INSERT INTO TABLE(col1, col2) VALUES
        # ("a", 1),
        # ("a", 2),
        # ("a", 2)...
        # area of the rectangle must be <= max_batch

        def get_area(b, h):
            return b * h

        if not data:
            raise ValueError("Your data collection is empty!")

        base = len(data[0])
        height = len(data)
        area = get_area(base, height)
        max_nearest_multiple_of_base = int(
            (base * int(max_allowed / base)) / base)

        if area <= max_allowed:
            return height  # entire rectangle area can be passed as 1 batch

        elif area > max_allowed and max_nearest_multiple_of_base != 0:
            return max_nearest_multiple_of_base
            # area needs to be sliced in tinier rectangles (each is a batch)

        else:
            return 1  # if not even 1 row of rectangle fits batch, default to 1

    size = get_batch_size()

    return list(grouper(data, size))


def filter_none_from_batch(batch):
    return list(filter(lambda x: x is not None, batch))


def batch_insert(engine, conn, table, data, fields, max_per_batch):

    def prepare_batch_stmt(batch):
        # batch data is a rectangle:
        # INSERT INTO TABLE(col1, col2) VALUES
        # (%s, %s),
        # (%s, %s),
        # (%s, %s)...
        # area of the rectangle must be <= max_batch

        _, batch_draft = prepare_insert_stmt(in_batches=True)

        batch_filtered = filter_none_from_batch(batch)
        rows_num, cols_num = (len(batch_filtered), len(batch_filtered[0]))
        placeholders = ('%s,' * cols_num).rstrip(',')
        multivalues = (f'({placeholders}),' * rows_num).rstrip(',')

        return batch_draft.replace("{multivalues}", multivalues)

    # avoid huge insertions, rather split in multiple executions.
    # first flatten the data, then split into batches.
    batches = make_batches(data=data, max_allowed=max_per_batch)

    for batch in batches:

        batch_stmt = prepare_batch_stmt(batch=batch)
        batch_data = filter_none_from_batch(batch=batch)

        engine.do_query(
            conn=conn, mode="w", query=batch_stmt, table=table,
            data=list(flatten(batch_data)), fields=fields)

    return
