const catalog = require('../data/catalog.js')
const copy = require('../copy.js')

function fill(template, data) {
  return String(template).replace(/\{(\w+)\}/g, function (_match, key) {
    const value = data[key]
    return value == null ? '' : String(value)
  })
}

let cache = null

function getIndex() {
  if (cache) {
    return cache
  }
  const byId = {}
  const itemById = {}
  const items = []
  catalog.categories.forEach(function (category) {
    byId[category.id] = category
    category.items.forEach(function (item) {
      const row = {
        id: item.id,
        name: item.name,
        url: item.url,
        desc: item.desc,
        section: item.section,
        categoryId: category.id,
        categoryName: category.name,
        sourceName: category.sourceName
      }
      itemById[row.id] = row
      items.push(row)
    })
  })
  cache = { byId: byId, itemById: itemById, items: items }
  return cache
}

function categoryCard(category) {
  return {
    id: category.id,
    name: category.name,
    summary: category.summary || copy.summaryFallback,
    count: category.items.length,
    countText: fill(copy.categoryCount, { count: category.items.length })
  }
}

function homeView() {
  const index = getIndex()
  return {
    copy: copy,
    statsText: fill(copy.statsLine, catalog.stats),
    hot: catalog.hotIds.map(function (id) {
      return categoryCard(index.byId[id])
    }),
    groups: catalog.groups.map(function (group) {
      return {
        id: group.id,
        name: group.name,
        desc: group.desc,
        categories: group.categoryIds.map(function (id) {
          return categoryCard(index.byId[id])
        })
      }
    })
  }
}

function getCategory(id) {
  return getIndex().byId[id] || null
}

function sectionsOf(category) {
  const names = []
  category.items.forEach(function (item) {
    if (item.section && names.indexOf(item.section) < 0) {
      names.push(item.section)
    }
  })
  return names
}

function filterItems(category, section) {
  if (!section) {
    return category.items
  }
  return category.items.filter(function (item) {
    return item.section === section
  })
}

function getItem(id) {
  return getIndex().itemById[id] || null
}

function relatedItems(item) {
  const category = getCategory(item.categoryId)
  if (!category) {
    return []
  }
  const same = []
  const rest = []
  category.items.forEach(function (other) {
    if (other.id === item.id) {
      return
    }
    const brief = { id: other.id, name: other.name, desc: other.desc }
    if (item.section && other.section === item.section) {
      same.push(brief)
    } else {
      rest.push(brief)
    }
  })
  return same.concat(rest).slice(0, 6)
}

function search(keyword) {
  const query = String(keyword || '').trim().toLowerCase()
  if (!query) {
    return []
  }
  // 「爬虫」是首页推荐词，原文里同一类条目多用「爬取」。
  const terms = query === '爬虫' ? ['爬虫', '爬取'] : [query]
  return getIndex().items.filter(function (item) {
    const haystack = [item.name, item.desc, item.section, item.categoryName, item.sourceName]
      .join(' ')
      .toLowerCase()
    return terms.some(function (term) {
      return haystack.indexOf(term) >= 0
    })
  })
}

module.exports = {
  copy: copy,
  fill: fill,
  homeView: homeView,
  getCategory: getCategory,
  sectionsOf: sectionsOf,
  filterItems: filterItems,
  getItem: getItem,
  relatedItems: relatedItems,
  search: search
}
