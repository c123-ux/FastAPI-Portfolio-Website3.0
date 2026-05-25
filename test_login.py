from passlib.context import CryptContext
import sqlite3

conn = sqlite3.connect('D:/PythonProject1/contacts.db')
c = conn.cursor()
c.execute('SELECT hashed_password FROM users')
hash_value = c.fetchone()[0]
print('Hash:', repr(hash_value))

ctx = CryptContext(schemes=['bcrypt'])
print('Verify admin123:', ctx.verify('admin123', hash_value))
