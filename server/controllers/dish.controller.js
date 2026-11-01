import { findDishes, findDishById } from '../models/dish.model.js';

export async function listDishes(req, res, url) {
  const dishes = await findDishes({
    cuisine: url.searchParams.get('cuisine'),
    meal: url.searchParams.get('meal'),
  });
  res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(dishes));
}

export async function showDish(req, res, id) {
  const dish = await findDishById(id);
  res.writeHead(dish ? 200 : 404, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(dish ?? { message: 'Không tìm thấy món ăn.' }));
}
