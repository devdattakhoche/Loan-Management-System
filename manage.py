
from project.constants import USERTYPE
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import os
from project.app import app, db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def recreate_db():
    """
    This function recreates the database with single admin.
    """
    from project.models import Users
    from project.constants import USERTYPE
    db.drop_all()
    db.create_all()
    admin = Users(os.environ['ADMIN_USERNAME'], os.environ['ADMIN_EMAIL'],
                  os.environ['ADMIN_PHONE'], os.environ['ADMIN_PASSWORD'], user_type=USERTYPE['Admin'])
    db.session.add(admin)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
