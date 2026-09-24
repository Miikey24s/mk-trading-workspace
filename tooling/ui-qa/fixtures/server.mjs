import http from 'node:http'
import fs from 'node:fs'

export async function startFixture() {
  const html = fs.readFileSync(new URL('./index.html', import.meta.url))
  let requests = 0
  const server = http.createServer((request, response) => {
    requests += 1
    if (request.method !== 'GET' || !['/', '/favicon.ico'].includes(request.url)) {
      response.writeHead(404); response.end(); return
    }
    response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' })
    response.end(html)
  })
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve) })
  return { url: `http://127.0.0.1:${server.address().port}`, get requests() { return requests },
    close: () => new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve())) }
}
