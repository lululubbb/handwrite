/**
 * 通用工具函数
 * 提供各种辅助功能
 */

/**
 * 防抖函数
 * @param {Function} fn - 要防抖的函数
 * @param {number} delay - 延迟时间
 * @returns {Function} - 防抖后的函数
 */
export function debounce(fn, delay = 300) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {Function} fn - 要节流的函数
 * @param {number} delay - 延迟时间
 * @returns {Function} - 节流后的函数
 */
export function throttle(fn, delay = 300) {
  let lastTime = 0
  return function(...args) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      fn.apply(this, args)
      lastTime = now
    }
  }
}

/**
 * 格式化时间
 * @param {Date|string} date - 日期
 * @param {string} format - 格式
 * @returns {string} - 格式化后的时间
 */
export function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return '未登录'
  
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 生成唯一ID
 * @returns {string} - 唯一ID
 */
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

/**
 * 下载文件
 * @param {string} url - 文件URL
 * @param {string} filename - 文件名
 */
export function downloadFile(url, filename) {
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 */
export function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    console.log('复制成功')
  }).catch(err => {
    console.error('复制失败:', err)
  })
}
