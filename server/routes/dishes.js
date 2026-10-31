import { getFood } from '../repositories/food-repository.js';

export async function handleDishes(req, res, url) {
  if (url.pathname !== '/api/dishes' && !url.pathname.startsWith('/api/dishes/')) return false;
  if (req.method !== 'GET') {
    res.writeHead(405, { Allow: 'GET', 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ message: 'Phương thức không được hỗ trợ.' }));
    return true;
  }
  const food = await getFood();
  let result;
  if (url.pathname === '/api/dishes') {
    const cuisine = url.searchParams.get('cuisine');
    const meal = url.searchParams.get('meal');
    result = food.DISHES.filter(d => (!cuisine || d.cuisine === cuisine) && (!meal || d.meals.includes(meal)));
  } else {
    const id = decodeURIComponent(url.pathname.slice('/api/dishes/'.length));
    result = food.DISHES.find(d => d.id === id);
  }
  res.writeHead(result ? 200 : 404, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(result ?? { message: 'Không tìm thấy món ăn.' }));
  return true;
}
