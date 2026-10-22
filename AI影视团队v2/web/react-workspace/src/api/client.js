const API_BASE = '/api'

export async function fetchAPI(endpoint) {
  try {
    const ctrl = new AbortController()
    const timer = setTimeout(() => ctrl.abort(), 5000)
    const response = await fetch(API_BASE + endpoint, { signal: ctrl.signal })
    clearTimeout(timer)
    if (!response.ok) throw new Error('HTTP ' + response.status)
    return await response.json()
  } catch (e) {
    return null
  }
}

export async function checkAPIHealth() {
  try {
    const ctrl = new AbortController()
    const timer = setTimeout(() => ctrl.abort(), 5000)
    const response = await fetch(API_BASE + '/health', { signal: ctrl.signal })
    return response.ok
  } catch {
    return false
  }
}

export async function postAPI(endpoint, body, timeoutMs = 8000) {
  try {
    const ctrl = new AbortController()
    const timer = setTimeout(() => ctrl.abort(), timeoutMs)
    const response = await fetch(API_BASE + endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: ctrl.signal,
    })
    clearTimeout(timer)
    if (!response.ok) throw new Error('HTTP ' + response.status)
    return await response.json()
  } catch (e) {
    return null
  }
}

export async function deleteAPI(endpoint) {
  try {
    const response = await fetch(API_BASE + endpoint, { method: 'DELETE' })
    // 返回响应体而不是布尔值：调用方需要 res.restored 才能判断
    // "存档真的被移走了"，HTTP 200 并不代表删除成功。
    const data = await response.json().catch(() => null)
    return data
  } catch {
    return null
  }
}
