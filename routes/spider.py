from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from core.spider import NovelSpider
from models.novel import Novel
import asyncio

spider_bp = Blueprint('spider', __name__)

@spider_bp.route('/novels', methods=['GET'])
@jwt_required()
def get_novels():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        skip = (page - 1) * per_page
        novels = Novel.objects.order_by('-created_at').skip(skip).limit(per_page)
        total = Novel.objects.count()
        
        return jsonify({
            'code': 200,
            'data': {
                'items': [novel.to_dict() for novel in novels],
                'total': total,
                'page': page,
                'per_page': per_page
            }
        })
    except Exception as e:
        current_app.logger.error(f"Get novels error: {str(e)}")
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@spider_bp.route('/crawl', methods=['POST'])
@jwt_required()
def start_crawl():
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({
                'code': 400,
                'message': '请提供要爬取的URL列表'
            }), 400
            
        # 异步执行爬虫任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        novels = loop.run_until_complete(NovelSpider.start_crawl(urls))
        
        return jsonify({
            'code': 200,
            'message': '爬取任务已完成',
            'data': [novel.to_dict() for novel in novels]
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500 

@spider_bp.route('/novels/<novel_id>/chapters', methods=['GET'])
@jwt_required()
def get_chapters(novel_id):
    try:
        novel = Novel.objects(id=novel_id).first()
        if not novel:
            return jsonify({
                'code': 404,
                'message': '小说不存在'
            }), 404
            
        return jsonify({
            'code': 200,
            'data': {
                'title': novel.title,
                'chapters': [{
                    'title': chapter['title'],
                    'content': chapter.get('content', '')
                } for chapter in novel.chapters]
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500 