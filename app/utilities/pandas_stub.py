class DataFrame:
    def __init__(self, rows=None):
        self.rows = list(rows or [])

    @property
    def empty(self):
        return len(self.rows) == 0

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, key):
        return [row[key] for row in self.rows]

    def groupby(self, key):
        return _GroupBy(self.rows, key)

    def reset_index(self, name=None):
        if name:
            return DataFrame(
                [
                    {name if k == "size" else k: v for k, v in row.items()}
                    for row in self.rows
                ]
            )
        return DataFrame(self.rows)


class _GroupBy:
    def __init__(self, rows, key):
        self.rows = rows
        self.key = key

    def size(self):
        counts = {}
        for row in self.rows:
            counts[row[self.key]] = counts.get(row[self.key], 0) + 1
        return DataFrame([{self.key: k, "size": v} for k, v in counts.items()])


def read_sql_query(query, conn):
    cur = conn.cursor()
    rows = cur.execute(query).fetchall()
    columns = [desc[0] for desc in cur.description]
    return DataFrame([dict(zip(columns, row)) for row in rows])


def unique(seq):
    seen = []
    for item in seq:
        if item not in seen:
            seen.append(item)
    return seen


def concat(arrays):
    result = []
    for arr in arrays:
        result.extend(list(arr))
    return result
