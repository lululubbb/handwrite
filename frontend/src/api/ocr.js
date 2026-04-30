import request from '@/utils/request'

// OCR识别接口适配
export async function ocrProcess(data) {
  const res = await request({
    url: '/api/ocr/process',
    method: 'post',
    data
  })
  // 强制适配前端PaddleOCR格式，让界面能正常显示结果
  if (res.code === 200 && res.data?.text) {
    return {
      code: 200,
      data: {
        // 同时兼容新旧格式，确保前端能读到
        result: [{ text: res.data.text }],
        text: res.data.text
      },
      msg: '识别成功'
    }
  }
  return res
}