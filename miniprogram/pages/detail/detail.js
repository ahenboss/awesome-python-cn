const store = require('../../utils/store.js')

Page({
  data: {
    copy: store.copy,
    missing: false,
    item: null,
    related: []
  },

  onLoad(options) {
    const item = store.getItem(options.id)
    if (!item) {
      this.setData({ missing: true, copy: store.copy })
      wx.setNavigationBarTitle({ title: store.copy.detailNav })
      return
    }
    wx.setNavigationBarTitle({ title: item.name })
    this.setData({
      missing: false,
      copy: store.copy,
      item: item,
      related: store.relatedItems(item)
    })
  },

  copyUrl() {
    const item = this.data.item
    if (!item || !item.url) {
      return
    }
    wx.setClipboardData({
      data: item.url,
      success: function () {
        wx.showToast({ title: store.copy.copied, icon: 'none' })
      }
    })
  },

  copyDesc() {
    const item = this.data.item
    if (!item) {
      return
    }
    wx.setClipboardData({
      data: item.name + '：' + item.desc,
      success: function () {
        wx.showToast({ title: store.copy.copiedDesc, icon: 'none' })
      }
    })
  },

  openDetail(event) {
    const id = event.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/detail/detail?id=' + id })
  },

  onShareAppMessage() {
    const item = this.data.item
    if (!item) {
      return { title: store.copy.shareHome, path: '/pages/home/home' }
    }
    const desc = item.desc.length > 36 ? item.desc.slice(0, 36) + '…' : item.desc
    return {
      title: store.fill(store.copy.shareDetail, { name: item.name, desc: desc }),
      path: '/pages/detail/detail?id=' + item.id
    }
  }
})
