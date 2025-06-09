from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_admin(username, password):
    app = create_app()
    with app.app_context():
        if User.query.filter_by(username=username).first():
            print('User already exists!')
            return
        user = User(username=username, email=f'{username}@example.com', password_hash=generate_password_hash(password), is_admin=True)
        db.session.add(user)
        db.session.commit()
        print(f'Admin user {username} created successfully!')

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('Usage: python create_admin.py <username> <password>')
    else:
        create_admin(sys.argv[1], sys.argv[2]) 