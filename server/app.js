import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFile } from 'node:fs/promises';
import { handleDishes } from './routes/dishes.js';
import { getFood } from './repositories/food-repository.js';

const publicDir = fileURLToPath(new URL('../public/', import.meta.url));
const mime = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.ico': 'image/x-icon' };

export const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://localhost');
    if (await handleDishes(req, res, url)) return;
    if (url.pathname.startsWith('/api/')) {
      res.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
      return res.end(JSON.stringify({ message: 'API không tồn tại.' }));
    }
    if (!['GET', 'HEAD'].includes(req.method)) {
      res.writeHead(405, { Allow: 'GET, HEAD' });
      return res.end();
    }
    // Keep existing synchronous frontend scripts working from the shared data source.
    if (url.pathname === '/js/data.js') {
      const food = await getFood();
      res.writeHead(200, { 'Content-Type': mime['.js'] });
      return res.end(req.method === 'HEAD' ? undefined : `const FOOD = ${JSON.stringify(food)};`);
    }
    const relative = decodeURIComponent(url.pathname === '/' ? '/index.html' : url.pathname);
    const filename = path.resolve(publicDir, '.' + relative);
    const within = path.relative(publicDir, filename);
    if (within.startsWith('..') || path.isAbsolute(within)) {
      res.writeHead(403);
      return res.end('Forbidden');
    }
    const body = await readFile(filename);
    res.writeHead(200, { 'Content-Type': mime[path.extname(filename)] || 'application/octet-stream' });
    res.end(req.method === 'HEAD' ? undefined : body);
  } catch (error) {
    const missing = ['ENOENT', 'ENOTDIR', 'EISDIR'].includes(error.code);
    const invalid = error instanceof URIError;
    if (!missing && !invalid) console.error(error);
    res.writeHead(missing ? 404 : invalid ? 400 : 500, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end(missing ? 'Không tìm thấy trang.' : invalid ? 'Đường dẫn không hợp lệ.' : 'Lỗi máy chủ.');
  }
});

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT || 3000);
  const host = process.env.HOST || '127.0.0.1';
  server.listen(port, host, () => console.log(`Website: http://${host}:${port}`));
}
