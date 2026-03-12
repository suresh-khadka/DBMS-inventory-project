"""
Inventory System Package Initialization
Configure PyMySQL to work with Django
"""

import pymysql

# CRITICAL FIX for Django MySQL compatibility
# This makes PyMySQL work as MySQLdb replacement
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.install_as_MySQLdb()
