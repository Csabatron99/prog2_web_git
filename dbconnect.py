#!/usr/bin/python
#import MySQLdb
import mysql.connector

def connection_db():
    conn1 = mysql.connector.connect(host="localhost",
                                    user = "root",
                                    passwd = "ShinRayder!472",
                                    db = "tikva_home_db_01")
    c1 = conn1.cursor()
    return c1, conn1
#def connection_rp():
#    conn2 = MySQLdb.connect(host="localhost",
#                           user = "root",
#                           passwd = "ShinRayder!472",
#                           db = "tikva_home_db_rp")
#    c2 = conn2.cursor()
#    return c2, conn2
