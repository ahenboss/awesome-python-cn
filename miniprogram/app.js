const copy = require('./copy.js')

App({
  globalData: {
    tabs: [copy.tabHome, copy.tabCatalog, copy.tabAbout]
  }
})
