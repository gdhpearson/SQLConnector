
This is a python script I'm working on that I'm hoping to release publicly once any kinds have been figured out.

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

## Functions

### Test Connection

To test you've connected successfully you can use the testConnection function. This just returns the verion MySQL you are running, but only if the connection is successful.

```
mysql.testConnection()
>>(('8.0.26',),)
```

### Connecting

You can explicitly connect and close to the database as needed, although as we'll see in a second, this isn't necessary.

`mysql.connect()`

### Using Columns

You can download the columns from your dictionary using the download columns command. The command takes a list of tables from your database that you want to save the columns from.

`mysql.downloadColumns(['TableA'],['TableB'])`

This saves a dictionary of the columns as objects within your SQLConnector object. 

_Note: This doesn't refresh. It saves them locally. If you updated your column settings you would need to redownload again_

The use of this is that it stores the default values, if your variable is requires, etc. as type variables. This becomes very useful as the script has inbuilt functions for dealing with variables.

```
mysql.tables['TableA']['ColumnX'].type
>> 'varchar(10)'
```

For instance, you can't send a dictionary of a list to MySQL as those are python types. Similarly MySQL can store JSON which isn't a python type. However, JSON can be easily converted to a Python Dict. Once the columns are downloaded, if you try to send a dictionary to the MySQL it will automatically convert it to a dictionary, and if you try to read a JSON file it will automatically convert it to a Python dictionary once the columns have been downloaded.

You can also set a column as required within Python. Sometimes you may want to ensure, even though the MySQL table will accept a blank variables, that you want to ensure you never leave that value empty anyway.

Pass the function a table name as a string, and a list of columns in a string. It will then set those columns as required.

_Note: This is only for your Python file. Other MySQL queries will still be able to ignore those columns. It just means you can't ignore them in your script. The script will actually warn you of this on return._

```
print(mysql.setAsRequired('TableA',['ColumnX','ColumnY']))
>> WARNING: Columns (['ColumnX', 'ColumnY']) set to required in table Table. However only sets required on Python end - not in MySql. Will only work on commands using this instance.
```

You can also use a similar command to set new defaults for columns. Here, instead of a list of columns, you pass a dictionary with the new default values.

_Note: Again, these only work for this python script now elsewhere_

```
print(mysql.setDefaults('TableA',{'ColumnX':'X',
                                'ColumnY':'Y'}))
>> WARNING: Defaults for TableA set. However only sets default on Python end - not in MySql. Will set values to given default if using Sql.add function, but not if using other MySQL syntax
```

### Reading and Writing to DB

The other functions mostly deal with core read/write functions.

One nice thing is that you don't need to explicitly connect with any of these functions. If you try to read/write to MySQL the script will check if you are already connected, if not, then it will automatically connect for you. Therefore you don't need the explicit connect function given earlier.

**Read**

The read function takes three required variables and one optional variable.

* The column containing the information as a string you want to retrieve. See note below about the all option.
* The table you want to pull the data from as a string
* A key/value pair containing the condition where the key is the column in the mysql table and the value is the value to check for. 
* (Optional - keyFirst): Requires column is set to all (see below). keyFirst can be set to 'yes' or 1. Default is 0. If set to 'yes' or 1 it will include the key column in the MySQL table as the first item in the returned dictionary. Otherwise, keys are ignored.
* (optional - returnAsDict): Requires column is set to all (see below). Also requires the table columns have been downloaded. returnAsDict can be set to 1 or yes. Default is 0. If set to 'yes' or 1 it will return each row as a dictionary whereby keys will be column names and values the returned value.

**Add**

The add function takes two values. The name of the table as a string, plus a dictionary of key value pairs where the keys are the names of the columns, and the values the insert values.

```
mysql.add('TableA',{'ColumnX:'Foo',
                    'ColumnY:'Bar'})
>> 1 record inserted
```

**Edit**

The edit function takes three values. The table as a string. A key value pair for the condition where the key is the column name and the value is the condition to check for, and another dictionary with key, value pairs for the data to change.

So to change any ColumnY value to 12 where ColumnX equals 'Foo'...

```
mysql.edit('TableA',{'ColumnX':'Foo},{'ColumnY':12})
```

**Edit or Add**

The edit or add function is a special function that combines the edit and add function. It is specially designed for changing single rows of a table where you unsure of the value exists. For instance, if you want to update a row to have a timestamp corresponding to now, but you aren't sure if that value exists.

The script will check if the condition is met. If the condition is met, it updates the row with the given value. If the condition is not met, then it will add a new row with the given values.

The function takes four arguments. 
* The table as a string
* The condition as a key value pair where the key is the column name and the value is the condition to check for
* The new values as a key, value pairs for the data to change
* The new data to add as a dictionary if the condition is not met.

For example, you have a table called users. The user does something and you want to update the time of their latest action, and if not then add them to the table.

```
mysql.editOrAdd('Users',{'Name':'George'},{'updateTime:time.time()},{'Name':'George','Age':34,'Country':'US','updateTime:time.time()})
>> Could not edit but successfully added: 1 record inserted
```

**Delete**

The delete function takes two arguments. The name of the table plus a dictionary key/value pair where the key is the column in the mysql table and the value is the value to check for. 

So to delete all values where ColumnX = 'Spam'...

```
mysql.delete('TableA',{'ColumnX','Spam'})
>> 4 rows were deleted
```





