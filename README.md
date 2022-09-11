
This is a python script I'm working on that I'm hoping to release publicly once any kinks have been figured out.

In the meantime you are free to use it, and I appreciate any feedback.

# What is the purpose of this?

PyMysql is the standard library for writing MySQL queries from Python. However, I've always found the process for this really unfriendly for Python - essentially you end up writing full MySQL queries in a Python script.

This script builds upon the PyMysql library and creates a series of very intuitive features that allow writing to / reading / editing MySQL tables much easier.

It should be noted, this isn't designed for creating databases or tables. The idea is to make the regular usage cleaner and easier, rather than the initial setup or major operations.

# Guide to Use

## Initial setup

As the script builds on PyMysql you will need PyMysql installed before use.

`From sqlConnector import *`

This will import an object called SQLConnector into your python file.

To setup simple create a variable name of your choice and pass a dictionary with your MySQL login info (host, port, user, password, db).

```
loginInfo = {'host':'XXX',
              'port':'xxx',
              'user':'xxx',
              'password':'xxx',
              'db':'xxx'}

mysql = SQLConnector(loginInfo)
```

_Note: For security reasons you generally shouldn't be writing your login info directly into your Python file and you are probably better importing this from a separate file._

### Test Connection

To test you've connected successfully you can use the testConnection function. This just returns the verion MySQL you are running, but only if the connection is successful.

```
mysql.testConnection()
>> (('8.0.26',),)
```

### Connecting

You can explicitly connect and close to the database as needed, although as we'll see in a second, this isn't necessary.

```
mysql.connect()
>> Connection Made
```

*Note: Sending incorrect login information will lead to an error*

###Commit and Close

You can close the mysql connection with the commit and close function. This automatically commits any existing changes sent to the mysql database and then closes the connection

```
sql.commitAndClose()
>> SQL Connection Closed
```

You can set SQLConnector to automatically commit and close after every query via the default settings if desired.

### Default Settings

There are two attributes to the sql connector that have default settings. All of these are True/False booleans. These can be changed manually. *Note: You can set these settings to things other than True or False, but doing so will cause fatal errors in almost any other action.*

When you first create the sql connector object, both of these items are set to False by default.

Whatever the default values are, these can be overridden in each call.

For instance, the mysql.read function accepts the optional arguments *returnAsDict* and *closeWhenDone*. These default to the default values for the attributes, but can be overridden in each call. 

The two settings that can be toggled on or off (true or false) are.

**returnAsDict**

One of the key design features of SQLConnector was to be able to read from mysql and return the results as a list of python dictionaries, making mysql queries more Python friendly. By default mysql queries are returned as a tuple of tuples.

`mysql.returnAsDict = True`

*Note: To return a query as a list of dictionaries, you will have to have downloaded the columns for that table. See more on that below.*

**closeConnectionAfterEachQuery**

By default SQLConnector assumes you want to keep your connection to mysql open and are sending multiple queries. However, if you want to close the connection after every query you can set this as true.

`mysql.closeConnectionAfterEachQuery = True`

**convertDownloadedJsons**

If the SQL column type is json, SQLConnector can automatically convert the json type to a python or list, allowing easier conversion between python and JSON.

`mysql.convertDownloadedJsons = True`

*Note: When adding/updating data, if the downloaded column type (see below) is set to json, SQLConnector will automatically convert the given value to JSON irelevant of the above set default*

## Using Columns

### Downloading Columns

**Structure** SQLConnector.setColumnDefault(tables)

**Returns** string

**Variables**
*tables* = Either a list of tables from your database or a string with the name of one table that you want to save the columns from

If successful the query returns a string confirming success.

```
mysql.downloadColumns(['TableA','TableB'])
>> Sucessfully downloaded columns for TableA, TableB. Info on these table columns can be seen in the SQLConnector.tables attribute of your SQLConnector object.
```

This saves a dictionary of the columns as objects within your SQLConnector object. 

_Note: This doesn't refresh. It saves them locally. If you updated your column settings you would need to redownload again_

The main purpose for this command is it allows you to return read queries from mysql as dictionaries where the column names will be used as keys.

If you want to examine the information on the columns you downloaded you can do so via the attributes.

```
mysql.tables['TestA']['ColumnX'].type
>> varchar(10)
```

The following attributes for each column are stored: type, null, key, default, extra. These attributes are the same name and value as mysql stores them as. To understand what each one means, visit the mysql documentation.

### Column Defaults

**Structure** SQLConnector.setColumnDefault(table,columnDictionary)

**Returns** string

**Variables**
*table* = name of table you want to set the defaults for
*columnDictionary* = dictionary of key/value pairs where the keys are column names and values are the new default.

The setColumnDefault function overwrites the set default for the column. When you add a row to a table, if the columns have been downloaded, SQLConnector will check if you have provided a value for each column. If there is a column with no value provided, and a default has been set then SQLConnector will automatically send the default value.

Defaults that were already on the mysql side will be downloaded with the download columns function.

*Note: This only sets the defaults for Python. It does not change the default settings in mysql. This means you can have different defaults set on the mysql side and on the Python side. Additionally, SQLConnector will not ensure you're given default value is valid for that column. For instance, it will gladly let you set the default value for a column of type integer to a string. This will lead to errors.*

The function returns a string that informs you of the success of each column given.

```
sql.setColumnDefault('TestTable',{'User':'NA','Age':0,'Country':'US'})
>> Default value for User set to NA
>> WARNING: Age already had a default value of -99. This has now been overwritten with 0
>> Could not set default value for Country - perhaps column is not in TestTable?'
```

## Reading and Writing to DB

The other functions mostly deal with core read/write functions.

One nice thing is that you don't need to explicitly connect with any of these functions. If you try to read/write to MySQL the script will check if you are already connected, if not, then it will automatically connect for you. Therefore you don't need the explicit connect function given earlier.

### Read

**Structure** SQLConnector.read(tables)

**Returns** string

**Variables**
*tables* = Either a list of tables from your database or a string with the name of one table that you want to save the columns from

### Insert

**Structure** SQLConnector.insert(table,data,closeWhenDone = Default)

**Returns** string

**Variables**
*table* = The table you want to update.  
*data* = Dictionary of key/value pairs where keys are the names of the table columns and the values the information you want to insert.  
*closeWhenDone* = Boolean optional. See section on defaults above.  

Inserts a row into your mysql table. Returns a string confirming the row has been inserted.

```
sql.insert('TestTable',{'User':'Steve','Approved':False,'Sports_Liked':['Rugby,Table Tennis']})
>> 1 record(s) inserted.
```

*Note: Currently you can only insert one row at a time. Hoping to improve this in future to allow multiple inserts with singular command*

## Automatic Type Conversion

SQLConnector has inbuilt functions that help translate things into mysql friendly terms.

If a column type is json, SQL connector will automatically convert any given value to json. 




