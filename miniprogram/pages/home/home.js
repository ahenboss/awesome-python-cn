const store = require('../../utils/store.js')
const view = store.homeView()

Page({
  data: {
    copy: view.copy,
    statsText: view.statsText,
    hot: view.hot,
    groups: view.groups
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
      title: store.copy.shareHome,
      path: '/pages/home/home'
    }
  }
})
