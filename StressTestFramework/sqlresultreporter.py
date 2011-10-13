import MySQLdb

###########################################################################
# A class to report the results of stress tests to the Mantid Test database
# (requires MySqldb module)
###########################################################################
class SQLResultReporter(ResultReporter):
    '''
    Send the test results to the Mantid test results database
    '''

    def __init__(self):
        self._testfields = ['test_date', 'test_name', 'host_name', 'environment', 'status']
        pass

    def getConnection(self, host = 'ndw714', user='root', passwd='mantid',
                 db='mantidstresstests'):
        return MySQLdb.connect(host = host, user = user, passwd = passwd,
                               db = db)
    
    def dispatchResults(self, result):
        '''
        Construct the SQL commands and send them to the databse
        '''
        dbcxn = self.getConnection()
        cur = dbcxn.cursor()
        last_id = dbcxn.insert_id()

        testruns = []
        itrtimings = []
        for res in result.resultLogs():
            name = res[0]
            if name.startswith('iter'):
                itrtimings.append(res)
            else:
                testruns.insert(self._testfields.index(res[0]), res[1])
                
        valuessql = "INSERT INTO testruns VALUES(NULL, " 
        for r in testruns:
            valuessql += "'" + r + "',"
        valuessql = valuessql.rstrip(',')
        valuessql += (')')
        cur.execute(valuessql)
        # Save test id for iteration table
        test_id = dbcxn.insert_id()
        
        if len(itrtimings) > 0:
            valuessql = "INSERT INTO iterationtimings VALUES(" + str(test_id) + ','
            for itr in itrtimings:
                values = itr[1].split(' ')
                sql = valuessql + str(values[0]) + ',' + str(values[1]) + ')'
                cur = dbcxn.cursor()
                cur.execute(sql)

        dbcxn.commit()
        cur.close()
        dbcxn.close()
