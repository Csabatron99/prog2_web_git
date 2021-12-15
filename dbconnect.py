#!/usr/bin/python
#import MySQLdb
import mysql.connector

def connection_db():
    conn1 = mysql.connector.connect(host="localhost",
                                    user = "alma",
                                    passwd = "Alma1472",
                                    db = "tikva_home_db_01")
    c1 = conn1.cursor()
    return c1, conn1
def connection_rp():
    conn2 = mysql.connector.connect(host="localhost",
                           user = "alma",
                           passwd = "Alma1472",
                           db = "tikva_home_db_rp")
    c2 = conn2.cursor()
    return c2, conn2
