"""
04 - SQL Query Builder (accumulated state)
==========================================

A SQL SELECT statement is built up clause by clause:
  SELECT cols FROM table [WHERE ...] [ORDER BY ...] [LIMIT ...]

The Builder gathers the parts; build() assembles them into a Query
whose .to_sql() emits the final string.

This is the pattern behind Django QuerySets, SQLAlchemy select(), etc.
"""

from dataclasses import dataclass


@dataclass
class Query:
    columns: str
    table: str
    where: str | None
    order_by: str | None
    limit: int | None

    def to_sql(self) -> str:
        sql = f"SELECT {self.columns} FROM {self.table}"
        if self.where:
            sql += f" WHERE {self.where}"
        if self.order_by:
            sql += f" ORDER BY {self.order_by}"
        if self.limit is not None:
            sql += f" LIMIT {self.limit}"
        return sql


class QueryBuilder:
    def __init__(self):
        self._cols = "*"
        self._table = None
        self._where = None
        self._order = None
        self._limit = None

    def select(self, *cols):
        self._cols = ", ".join(cols) if cols else "*"
        return self

    def from_(self, table):
        self._table = table
        return self

    def where(self, cond):
        self._where = cond
        return self

    def order_by(self, col):
        self._order = col
        return self

    def limit(self, n):
        self._limit = n
        return self

    def build(self) -> Query:
        if not self._table:
            raise ValueError("from_() required")
        return Query(self._cols, self._table, self._where, self._order, self._limit)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("--- Adults sorted by name, top 10 ---")
    q1 = (QueryBuilder()
            .select("name", "email", "age")
            .from_("users")
            .where("age >= 18")
            .order_by("name")
            .limit(10)
            .build())
    print(q1.to_sql())

    print("\n--- All columns, no where ---")
    q2 = QueryBuilder().from_("products").build()
    print(q2.to_sql())

    print("\n--- Just a count ---")
    q3 = (QueryBuilder()
            .select("COUNT(*) AS n")
            .from_("orders")
            .where("status = 'paid'")
            .build())
    print(q3.to_sql())

    print("\n--- Missing FROM raises early ---")
    try:
        QueryBuilder().select("*").build()
    except ValueError as e:
        print(f"ValueError: {e}")


if __name__ == "__main__":
    demo()
