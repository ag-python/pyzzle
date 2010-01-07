import sqlite3
import os
from linq import *

class Table(type):
    """A class corresponding to a table in """
    def __init__(cls, name, bases=(), attrs={}):
        super(Table, cls).__init__(name, bases, attrs)
        cls.rows={}
    def __getattr__(cls, attr):
        return cls.rows[attr]
    def __getitem__(cls, key):
        return cls.rows[key]
    def __setitem__(cls, key, value):
        cls.rows[key]=value
    def __contains__(cls,item):
        if type(item)==cls: return item in cls.rows.values()
        else:               return item in cls.rows.keys()
    def __iter__(cls):
        return cls.rows.itervalues()
class Row:
    def __init__(self, tuple_, columns):
        self.cells={}
        for i in range(len(tuple_)):
            column=columns[i][0]
            cell=tuple_[i]
            self.cells[column]=cell
    def __getattr__(self, attr):
        return self.cells[attr]
    def __getitem__(self, key):
        return self.cells[key]
    def __setitem__(self, key, value):
        self.cells[key]=value
    def __contains__(self,item):
        return item in self.cells
    def __nonzero__(self):
        return True
class DB:
    def __init__(self, file):
        self._connection=sqlite3.connect(file)
        self._cursor = self._connection.cursor()
    def query(self, query, *param):
        try:
            result=self._cursor.execute(query, *param)
            self._connection.commit()
            return result
        except:
            print "Could not excecute: "
            print query
            raise
    def select(self, tables, value=lambda x:x, key=None, duplicate=False,
               where=None, orderby=None, descend=False, 
               groupby=None, having=None):
        """Performs a select query on the database.
        All parameters are strings, except value and key, which are functions
        Returns a dictionary if key is specified. Returns a list, otherwise"""  
        query='select * from '+tables
        if where:   query+=' where ['+where
        if orderby: query+=' order by '+orderby
        if descend: query+=' desc'
        if groupby: query+=' group by '+groupby
        if having:  query+=' having '+having
        
        """creates a dictionary using an existing "key" column in table"""
        rows=map(lambda tuple_: Row(tuple_, self._cursor.description), self.query(query))
        return select(rows,
                      value     =value,
                      key       =key,
                      duplicate =duplicate)
    def insert(self, table, cells):
        columns ='insert into '+table+' ('
        values  =' ) values ( '
        for column in cells.keys()[:-1]:
            columns+=column+', '
            values+='?, '
        last=cells.keys()[-1]
        columns+=last
        values+='? )'
        self.query(columns+values, cells.values())
    def delete(self, table, id, idcolumn='id'):
        self.query('delete from '+table+' where '+idcolumn+" = '"+id+"'")
    def update(self, table, cells):
        update  ='update '+table+' set '
        for column in cells.keys()[:-1]:
            update+=column+' = '
            update+='?, '
        last=cells.keys()[-1]
        columns+=last+' = '
        update+=' ? '
        self.query(columns+values, cells.values())
    def close(self):
        self._cursor.close()
        self._connection.close()