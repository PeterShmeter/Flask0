import functools
import inspect
import sqlite3
import collections
from tprint import *

class SQLstorage:
    conn = None
    cursor = None

    @staticmethod
    def _as_table(f):
        @functools.wraps(f)
        def wrap(self, *args):
            query = f(self, *args)
            col_names = [d[0].lower() for d in query.description]
            r = [dict(zip(col_names, r)) for r in query.fetchall()]
            del query
            return r

        return wrap

    @staticmethod
    def _as_row(f):
        @functools.wraps(f)
        def wrap(self, *args):
            query = f(self, *args)
            r = query.fetchone()
            col_names = [d[0].lower() for d in query.description]
            del query
            if r is None: return None
            else: return dict(zip(col_names, r))

        return wrap

    @staticmethod
    def _as_value(f):
        ins_res = inspect.getfullargspec(f)
        if ins_res.args == ['self'] and not ins_res.varargs:
            @functools.wraps(f)
            def wrap(self):
                query = f(self)
                r = query.fetchone()
                del query
                if r is None:
                    return None
                else:
                    return r[0]
        else:
            @functools.wraps(f)
            def wrap(self, *args):
                query = f(self, *args)
                r = query.fetchone()
                del query
                if r is None:
                    return None
                else:
                    return r[0]

        return wrap

    @staticmethod
    def _as_true_false(f):
        @functools.wraps(f)
        def wrap(self, *args):
            query = f(self, *args)
            r = query.fetchone()
            del query
            return r is not None

        return wrap

    def execute(self, *args):
        return self.conn.cursor().execute(*args)

    @_as_value
    def last_insert_rowid(self):
        return self.execute('select last_insert_rowid()')

    @_as_table
    def select(self, __sql, *args):
        return self.conn.cursor().execute(__sql, *args)

    def insert(self, table, raw_row):
        # t = TPrint(True)
        t = TPrint(False)
        row = collections.OrderedDict(raw_row)
        sql = f'insert into {table}({",".join(row.keys())}) values({",".join(["?" for _ in row.keys()])})'
        t.print(sql)
        self.conn.cursor().execute(sql, tuple(row.values()))
        return self.last_insert_rowid()

    def update(self, table, condition, values):
        # t = TPrint(True)
        t = TPrint(False)
        o_condition = collections.OrderedDict(condition)
        o_values = collections.OrderedDict(values)
        sql = (
            f'update {table} set {",".join([x + " = ?" for x in o_values.keys()])}'
            f' where {" and ".join([x + " = ?" for x in o_condition.keys()])}'
        )
        t.print(sql)
        t.print(tuple(list(o_values.values()) + list(o_condition.values())))
        return self.conn.cursor().execute(sql, tuple(list(o_values.values()) + list(o_condition.values()))).rowcount

    def delete(self, table, raw_row):
        # t = TPrint(True)
        t = TPrint(False)
        row = collections.OrderedDict(raw_row)
        sql = f'delete from {table} where {" and ".join([x + " = ?" for x in row.keys()])}'
        t.print(sql)
        return self.conn.cursor().execute(sql, tuple(row.values())).rowcount

    def check_tf(self, query_text: str, params=tuple()) -> bool:
        query = self.conn.cursor().execute(query_text, params)
        r = query.fetchone()
        del query
        return r is not None

    @_as_value
    def check(self, query_text, params=tuple()):
        # t = TPrint(True)
        t = TPrint(False)
        if query_text.split()[0].lower() == 'select':
            return self.execute(query_text, params)
        else:
            o_params = collections.OrderedDict(params)
            __sql = (
                f'select {",".join(o_params.keys())} from {query_text} where '
                + ' and '.join([key + ' = ?' for key in o_params.keys()])
            )
            t.print(__sql)
            return self.execute(__sql, tuple(o_params.values()))


class chat_storage(SQLstorage):
    db_name: str

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, check_same_thread=False)

    def commit(self):
        self.conn.commit()

    @SQLstorage._as_row
    def get_message_attachment(self, id):
        return self.execute('select attachment_name, attachment from messages where id = :id', {'id':id})
