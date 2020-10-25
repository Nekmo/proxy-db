import shutil

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from proxy_db.models import PROXY_DB_FILE, PROXY_DB_DB_URL, Base, Version


class MigrateBase(object):
    tables = []
    version = None

    def __init__(self, proxy_db_file=None):
        self.proxy_db_file = proxy_db_file or PROXY_DB_FILE

    def get_backup_path_file(self):
        return '{}.bak'.format(self.proxy_db_file)

    def create_backup_file(self):
        shutil.move(self.proxy_db_file, self.get_backup_path_file())

    def create_new_database(self):
        engine = create_engine(PROXY_DB_DB_URL)
        Base.metadata.create_all(engine)
        return sessionmaker(bind=engine)()

    def get_backup_database(self):
        url = '{}.bak'.format(PROXY_DB_DB_URL)
        engine = create_engine(url)
        return sessionmaker(bind=engine)()

    def migrate_data(self):
        old_database_session = self.get_backup_database()
        new_database_session = self.create_new_database()
        for table in self.tables:
            model = table['model']
            fields = table['fields']
            entities = [getattr(model, field) for field in table['fields']]
            rows = old_database_session.query(model).with_entities(*entities).all()
            rows = [model(**{field: getattr(row, field) for field in fields}) for row in rows]
            new_database_session.bulk_save_objects(rows)
            new_database_session.commit()

    def create_version_row(self):
        new_database_session = self.create_new_database()
        new_database_session.add(Version(version=self.version))
        new_database_session.commit()

    def migrate(self):
        self.create_backup_file()
        self.migrate_data()
        self.create_version_row()
