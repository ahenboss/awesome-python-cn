const store = require('../../utils/store.js')
const LIMIT = 40

Page({
  data: {
    copy: store.copy,
    keyword: '',
    idle: true,
    empty: false,
    hitText: '',
    hitCount: 0,
    limitNote: '',
    results: []
  },

  onLoad(options) {
    wx.setNavigationBarTitle({ title: store.copy.searchTitle })
    if (options.q) {
      this.apply(decodeURIComponent(options.q))
    }
  },

  onInput(event) {
    this.apply(event.detail.value)
  },

  clear() {
    this.apply('')
  },

  apply(keyword) {
    const text = keyword || ''
    const query = text.trim()
    const hits = query ? store.search(query) : []
    this.setData({
      copy: store.copy,
      keyword: text,
      idle: !query,
      empty: !!query && hits.length === 0,
      hitText: query ? store.fill(store.copy.searchHit, { count: hits.length }) : '',
      hitCount: hits.length,
      limitNote: hits.length > LIMIT ? store.fill(store.copy.searchLimitNote, { count: LIMIT }) : '',
      results: hits.slice(0, LIMIT)
    })
  },

  openDetail(event) {
    const id = event.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/detail/detail?id=' + id })
  },

  onShareAppMessage() {
    const query = (this.data.keyword || '').trim()
    return {
      title: query ? store.fill(store.copy.searchHit, { count: this.data.hitCount }) : store.copy.shareHome,
      path: query ? '/pages/search/search?q=' + encodeURIComponent(query) : '/pages/search/search'
    }
  }
})
