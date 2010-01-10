import sqlite3
import os

class Table(type):
    """A metaclass used to represent the tables of a database.
    
    Intstances of a table class are stored in the rows attribute, 
    indexed by their primary key. For instance, Slide.rows['foobar'] 
    accesses the instance 'foobar' from the Slide class, 
    which uses the Table metaclass. 
    
    Intstances can also be accessed like a dictionary (e.g. Slide['foobar']), 
    or like attributes (e.g. Slide.foobar) - this comes in handy when
    scripting slides for a large scale video game.
    """
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
    """A generic row of a database. 
    
    This class is used in place of custom classes that 
    would just be used to store data without performing behavior.
    A good example of this in practice are stages."""
    @staticmethod
    def _load(cells):
        return Row(cells)
    def __init__(self, cells):
        self.cells=cells
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
    """Represents an SQLite database used to store data for Pyzzle games.
     
    This class performs higher level functionality than classes within 
    the sqlite3 module. It also acts as an Adapter Class that may allow
    other file formats to be implemented in the future."""
    def __init__(self, file=':memory:'):
        self._connection=sqlite3.connect(file)
        self._connection.row_factory = sqlite3.Row
        self._cursor = self._connection.cursor()
    def load(self, TableClass, tablename=None, idcolumn='id'):
        """Loads all instances a Table class from rows in pyzzle.datafile.
        @param TableClass: A class that uses the Table metaclass.
        @param tablename: The name of the table in the database. 
            If not specified, the name of TableClass is used instead.
        @param idcolumn: The name of the primary key column for the table.
        """
        tablename = tablename if tablename else TableClass.__name__
        query='select * from '+tablename
        results=self._cursor.execute(query)
        rows={}
        for cells in results:
            rows[cells[idcolumn]]=TableClass._load(cells)
        return rows
    def save(self, TableClass, tablename=None, idcolumn='id'):
        """Saves all members of a Table class to pyzzle.datafile."""
        tablename = tablename if tablename else TableClass.__name__
        self._cursor.execute('delete from '+tablename)
        
        for row in TableClass:
            cells=row._save()
            query=' '.join(['insert into',tablename,'(',
                            ', '.join(cells.keys()),
                            ') values (',
                            ', '.join(('?')*len(cells)),')'])
            self._cursor.execute(query, cells.values())
        self._connection.commit()
    def close(self):
        self._cursor.close()
        self._connection.close()