const store = require('../../utils/store.js')
const view = store.homeView()

Page({
  data: {
    copy: view.copy,
    statsText: view.statsText
  },

  onLoad() {
    wx.setNavigationBarTitle({ title: store.copy.aboutTitle })
  },

  onShareAppMessage() {
    return {
      title: store.copy.shareHome,
      path: '/pages/about/about'
    }
  }
})
