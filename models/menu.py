from . import db
from datetime import datetime

class Menu(db.Model):
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, default=0)
    name = db.Column(db.String(64), nullable=False)
    path = db.Column(db.String(128))
    component = db.Column(db.String(64))
    icon = db.Column(db.String(32))
    sort = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)  # 1: 启用, 0: 禁用
    is_show = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    def to_dict(self):
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'name': self.name,
            'path': self.path,
            'component': self.component,
            'icon': self.icon,
            'sort': self.sort,
            'status': self.status,
            'is_show': self.is_show,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }