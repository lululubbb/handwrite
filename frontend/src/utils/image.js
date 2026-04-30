/**
 * 图像处理工具
 * 提供图像预览、压缩等功能
 */

/**
 * 预览图像文件
 * @param {File} file - 图像文件
 * @returns {Promise<string>} - 返回base64格式的图像
 */
export function previewImage(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      resolve(e.target.result)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

/**
 * 压缩图像
 * @param {string} imageUrl - 图像URL
 * @param {number} quality - 压缩质量 (0-1)
 * @param {number} maxWidth - 最大宽度
 * @returns {Promise<string>} - 返回压缩后的base64图像
 */
export function compressImage(imageUrl, quality = 0.8, maxWidth = 1920) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.src = imageUrl
    
    img.onload = () => {
      const canvas = document.createElement('canvas')
      let width = img.width
      let height = img.height
      
      // 如果宽度超过最大值，按比例缩放
      if (width > maxWidth) {
        height = Math.round((height * maxWidth) / width)
        width = maxWidth
      }
      
      canvas.width = width
      canvas.height = height
      
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, width, height)
      
      const compressedUrl = canvas.toDataURL('image/jpeg', quality)
      resolve(compressedUrl)
    }
    
    img.onerror = reject
  })
}

/**
 * 检测图像文件类型
 * @param {File} file - 图像文件
 * @returns {boolean} - 是否为有效图像
 */
export function isValidImage(file) {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
  return validTypes.includes(file.type)
}

/**
 * 获取图像文件大小（MB）
 * @param {File} file - 图像文件
 * @returns {number} - 文件大小
 */
export function getImageSizeMB(file) {
  return (file.size / (1024 * 1024)).toFixed(2)
}
