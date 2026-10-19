const store = require('../../utils/store.js')
const view = store.homeView()

Page({
  data: {
    copy: view.copy,
    groups: view.groups
  },

  onLoad() {
    wx.setNavigationBarTitle({ title: store.copy.catalogTitle })
  },

  goSearch() {
    wx.navigateTo({ url: '/pages/search/search' })
  },

  openCategory(event) {
    const id = event.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/category/category?id=' + id })
  },

  onShareAppMessage() {
    return {
      title: store.copy.catalogTitle,
      path: '/pages/catalog/catalog'
    }
  }
})
