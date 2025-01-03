import request from './request'

// 获取小说列表
export function getNovels(params) {
  return request({
    url: '/spider/novels',
    method: 'get',
    params: {
      page: params.page || 1,
      per_page: params.per_page || 10
    }
  })
}

// 开始爬取任务
export function startCrawl(urls) {
  return request({
    url: '/spider/crawl',
    method: 'post',
    data: { urls }
  })
}

// 获取章节内容
export function getChapters(novelId) {
  return request({
    url: `/spider/novels/${novelId}/chapters`,
    method: 'get'
  })
} 