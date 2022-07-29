
import pymysql, logging, json

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')

class SQL:
    def __init__(self,connectionInfo):
        self.host = connectionInfo['host']
        self.port = connectionInfo['port']
        self.user = connectionInfo['user']
        self.password = connectionInfo['password']
        self.db = connectionInfo['db']
        self.connection = None
        self.cursor = None
        self.tables = {}


    class Column:
        def __init__ (self,type,null,key,default,extra,required):
            self.type=type
            self.null=null
            self.key=key
            self.default=default
            self.extra=extra
            self.required=required

    def jsonToDict(self,var):
        return json.loads(var)
    
    def dictToJson(self,var):
        return json.dumps(var)
    
    def connect(self):
        self.connection = pymysql.connect(host=self.host,
                                port=self.port,
                                user=self.user,
                                password=self.password,
                                db=self.db)
    
    def commitAndClose(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        self.cursor = None
        self.connection = None


    def testConnection(self):
        self.connect()
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT VERSION()")
        output = self.cursor.fetchall()
        self.cursor.close()
        self.connection.close()
        self.connection = None
        self.cursor = None
        return(output)

    def connectIfNeeded(self):
        if self.connection == None:
            self.connect()
        self.cursor = self.connection.cursor()

    def downloadColumns(self,tables):
        self.connectIfNeeded()
        for i in range(len(tables)):
            if tables[i] not in self.tables:
                self.tables[tables[i]] = {}
            self.cursor.execute(f"SHOW COLUMNS FROM {tables[i]};")
            columns = self.cursor.fetchall()
            for j in range(len(columns)):
                self.tables[tables[i]][columns[j][0]] = self.Column(columns[j][1],columns[j][2],columns[j][3],columns[j][4],columns[j][5],0)

    def setAsRequired(self,table,columns):
        if table not in self.tables:
            return "SQL ERROR: Tried to set columns as required, but columns have to be downloaded first"
        for col in columns:
            if col not in self.table[table]:
                return f"SQL ERROR: Tried to set required for {col} that doesn't exist in the table (if column has been added since columns were downloaded, they will have to be redownloaded)"
        for col in columns:
            self.table[table][col].required = 1

    def setDefaults(self,table,columns):
        if table not in self.tables:
            return "SQL ERROR: Tried to set column defaults, but columns have to be downloaded first"
        for col in columns:
            if col not in self.table[table]:
                return f"SQL ERROR: Tried to set default value for {col} that doesn't exist in the table (if column has been added since columns were downloaded, they will have to be redownloaded)"
        for col in columns:
            self.table[table][col].default = columns[col]
        return f"WARNING: Defaults for {table} set. However only sets default on Python end - not in MySql. Will set values to given default if using Sql.add function, but not if using other MySQL syntax"

    def add(self,table,data):
        self.connectIfNeeded()
        if table in self.table:
            newEntry = {}
            for v in self.tables[table]:
                if v in data:
                    if self.tables[table][v].default != None:
                        data[v] = self.tables[table][v].default
                    if self.tables[table][v].type == 'json':
                        data[v] = self.dictToJson(data[v])
                    newEntry[v] = data[v]
                elif self.tables[table][v].required == 1:
                    return(f"SQL ERROR :Missing default for database entry: {str(data)}")
        else:
            newEntry = data
        text = f"""INSERT INTO {table} {str(tuple(newEntry.keys())).replace("'","")} VALUES {str(tuple(["x" for i in range(len(newEntry.values()))])).replace("'x'","%s")}"""
        logging.debug(f"""Query of... 
{text}
with values of {tuple(newEntry.values())}""")
        self.cursor.execute(text,tuple(newEntry.values()))
        return f"{self.cursor.rowcount} record inserted."
        

    def edit(self,table,condition,toChange):
        self.connectIfNeeded()
        text = f"UPDATE {table} SET "
        for v in toChange:
            text += f"{v}=%s"
            if v != list(toChange.keys())[-1]:
                text += ", "
            else:
                text+= " "
        text += f"WHERE {list(condition.keys())[0]}=%s"
        values = tuple(toChange.values())+tuple(condition.values())
        logging.debug(f"""Query of... 
{text}
with values of {tuple(values)}""")
        self.cursor.execute(text,values)
        output = f"{self.cursor.rowcount} rows affected"
        return output


    def read(self,toSelect,table,condition,keyFirst,returnAsDict):
        self.connectIfNeeded()
        if toSelect.lower().strip() == "all":
            toSelect = "*"
        #check to see syntax options are valud
        if toSelect != "*" and (returnAsDict == 1 or returnAsDict == 'dict'): 
            return "SQL ERROR: Requested to return as dict. This is only available if all variables are returned."
        text = f"""SELECT {toSelect} FROM {table} WHERE {list(condition.keys())[0]} = '{list(condition.values())[0]}'"""
        logging.debug(text)
        self.cursor.execute(text)
        output = self.cursor.fetchall()
        logging.debug(output)
        if output == ():
            return "Empty"
        #if return as dict, then convert values
        if returnAsDict == 1 or returnAsDict == 'dict':
            if table not in self.tables:
                return f"SQL ERROR: Wanted read to return as dict but there are no record of columns for {table}"
            values = output
            output = {}
            if keyFirst == 1 or (keyFirst==str and keyFirst.lower().startswith('y')):
                keyStart = 1
            else:
                keyStart = 0
            if len(values) == 1:
                logging.debug(values)
                for v in range(keyStart,len(list(self.tables[table].keys()))):
                    output[list(self.tables[table].keys())[v]] = values[v]
            else:
                for i in range(len(values)):
                    if keyStart == 1:
                        key = values[0]
                    else:
                        key = i
                    output[key] = {}
                    for v in range(keyStart,keyStart,len(list(self.tables[table].keys()))):
                        output[key][list(self.tables[table].keys())[v]] = values[v]
        return output

    def editOrAdd(self,table,condition,toChange,toAdd):
        readAttempt = self.read('*',table,condition,0)
        logging.debug(f"Edit/Add read output: {readAttempt}")
        if readAttempt != "Empty": #if not empty then can edit
            output = self.edit(table,condition,toChange)
            if type(output) != str or not output.startswith("SQL ERROR"):
                return(f"Successefully edited: {output}")
            else:
                return output
        else:
            if list(condition.keys())[0] in toAdd: #check that condition key isn't in toadd
                return("SQL ERROR: Condition key also in To Add value")
            condition.update(toAdd)
            output = self.add(table,condition)
            if not output.startswith("SQL ERROR"):
                return(f"Could not edit, but successefully added: {output}")
            else:
                return output

    def delete(self,table,condition):
        self.connectIfNeeded()
        if type(list(condition.values())[0]) == str:
            condition[list(condition.keys())[0]] = f"'{condition[list(condition.keys())[0]]}'"
        text = f"DELETE FROM {table} WHERE {list(condition.keys())[0]} = {list(condition.values())[0]}"
        logging.debug(text)
        self.cursor.execute(text)
        if self.cursor.rowcount == 0:
            return "SQL ERROR: Tried to delete, but no conditions were met"
        else:
            return f"{self.cursor.rowcount} rows were deleted"



"""sqlLogin = {'host':'mysql-81614-0.cloudclusters.net',
            'port':16872,
            'user':'WPHelper',
            'password':'WPH3lp3r',
            'db':'WPHub'}
sql = SQL(sqlLogin)
print(sql.testConnection())"""


    