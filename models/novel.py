from datetime import datetime
from . import mongo

class Novel(mongo.Document):
    title = mongo.StringField(required=True)  # 小说标题
    author = mongo.StringField()  # 作者
    source_url = mongo.StringField(required=True, unique=True)  # 来源URL
    description = mongo.StringField()  # 简介
    chapters = mongo.ListField(mongo.DictField(), default=[])  # 章节列表，包含内容
    status = mongo.IntField(default=0)  # 0: 未爬取, 1: 爬取中, 2: 已完成
    created_at = mongo.DateTimeField(default=datetime.now)
    updated_at = mongo.DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'novels',
        'indexes': ['title', 'source_url', 'status']
    }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'author': self.author,
            'source_url': self.source_url,
            'description': self.description,
            'chapters_count': len(self.chapters),
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        } 