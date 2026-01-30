from db import get_connection
import bcrypt

email = input("Enter email to reset password: ")
new_password = input("Enter new password: ")

conn = get_connection()
cur = conn.cursor()

# Hash the new password
hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Update password
cur.execute("UPDATE users SET password=%s WHERE email=%s", (hashed, email))
conn.commit()

print(f"Password updated for {email}")
conn.close()