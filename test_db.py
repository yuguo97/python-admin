import pytest
from app import create_app, db
from models.user import User

@pytest.fixture
def app():
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_user(app):
    with app.app_context():
        user = User(
            username='test_user',
            email='test@example.com'
        )
        user.set_password('123456')
        user.save()
        
        saved_user = User.query.filter_by(username='test_user').first()
        assert saved_user is not None
        assert saved_user.email == 'test@example.com'
        assert saved_user.check_password('123456')

def test_update_user(app):
    with app.app_context():
        user = User(
            username='test_user',
            email='test@example.com'
        )
        user.save()
        
        user.email = 'new@example.com'
        user.save()
        
        updated_user = User.query.get(user.id)
        assert updated_user.email == 'new@example.com'

def test_delete_user(app):
    with app.app_context():
        user = User(
            username='test_user',
            email='test@example.com'
        )
        user.save()
        
        user_id = user.id
        user.delete()
        
        deleted_user = User.query.get(user_id)
        assert deleted_user is None 