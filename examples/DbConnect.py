'''
Created on Apr 21, 2015

@author: kkong
'''

from mysql import connector
import mysql.connector
from mysql.connector import errorcode
from contextlib import closing
import operator

class DbConnect(object):

    def __init__(self, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
#         print "TitanDB Connect"
#         if self.connect():
#             #Connection successful
#             print "Connection Successful"
#         

    def connect(self):
        connectSuccess = True
        self.__cnx__ = None
        
        try:
            self.__cnx__ = mysql.connector.connect(user='user', password='Simple123',
                                    host='F0G2H12', database='tms', port='3306',
                                    charset='utf8',
                                    use_unicode=False,
                                    autocommit=True
                                    )
            
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                connectSuccess = False
                print("Invalid username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                connectSuccess = False
            else:
                print(err)
                connectSuccess = False
                
        return connectSuccess
    
            
    def getDbConnection(self):
        return self.__cnx__
    
    def isDbConnected(self):
	if self.getDbConnection.cursor() is None:
		return False
	else:
		return True
 
    
    
    
    def callStproc(self, storedproc, args):
        with closing(self.getDbConnection().cursor()) as cursor:
                
            if type(args) is not tuple:
                args = (args,)
                
            columnNames = None
            results = None
            columnDic = None
            
            cursor.callproc(storedproc, args)
            self.getDbConnection().commit()
            
            if cursor.stored_results() is not None:
                for result in cursor.stored_results():
                    columnNames = result.description
                    results = result.fetchall()
                
                        
            #place column names into dict
            if columnNames is not None:
                for (i, d) in enumerate(columnNames):
                    columnDic[d[0]] = i
            
                #Sort column names by value
                sorted_Columns = sorted(columnDic.items(),key=operator.itemgetter(1))
        return results, columnDic
   	
    def createDeviceID(self, details):
	(results,columnDic) = self.callStproc('createTMSDevice',details)	
 
    def setSerialResetFlag(self, details): #EXAMPLE
        (results,columnDic) = self.callStproc('setSerialResetFlag', details)
    
    def addTempByDevice(self, details):
        (results,columnDic) = self.callStproc('addTempByDevice', details)
    
    def closeDb(self):
        self.getDbConnection().close()
    
