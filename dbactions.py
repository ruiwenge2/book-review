# FOR DEBUGGING PURPOSES

from replit import db
import pickledb
allposts = pickledb.load("allposts.json", True)

def info():
	return dict(db)

def accounts():
  return db["accounts"]

def delete_post(bookid):
  allposts.rem(bookid)

def delete_account(username):
  del db["accounts"][username]