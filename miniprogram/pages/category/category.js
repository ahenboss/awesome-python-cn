const store = require('../../utils/store.js')

Page({
  data: {
    copy: store.copy,
    missing: false,
    name: '',
    summary: '',
    sections: [],
    current: '',
    countText: '',
    visible: []
  },

  onLoad(options) {
    const category = store.getCategory(options.id)
    if (!category) {
      this.setData({ missing: true, copy: store.copy })
      wx.setNavigationBarTitle({ title: store.copy.categoryNav })
      return
    }
    this.category = category
    wx.setNavigationBarTitle({ title: category.name })
    this.showSection('')
  },

  showSection(section) {
    const visible = store.filterItems(this.category, section)
    this.setData({
      missing: false,
      copy: store.copy,
      name: this.category.name,
      summary: this.category.summary || store.copy.summaryFallback,
      sections: store.sectionsOf(this.category),
      current: section,
      countText: store.fill(store.copy.itemCount, { count: visible.length }),
      visible: visible
    })
  },

  switchSection(event) {
    const section = event.currentTarget.dataset.section
    this.showSection(section === '__all__' ? '' : section)
  },

  openDetail(event) {
    const id = event.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/detail/detail?id=' + id })
  },

  onShareAppMessage() {
    if (!this.category) {
      return { title: store.copy.shareHome, path: '/pages/home/home' }
    }
    return {
      title: store.fill(store.copy.shareCategory, { name: this.category.name }),
      path: '/pages/category/category?id=' + this.category.id
    }
  }
})
