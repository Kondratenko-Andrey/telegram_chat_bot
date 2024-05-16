from .common.models import db, History
from .utils.CRUD import CRUDInterface

db.connect()
db.create_tables([History])

crud = CRUDInterface()

if __name__== "__main__":
    crud()
