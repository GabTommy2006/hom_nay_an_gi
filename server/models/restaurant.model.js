import { readFile } from 'node:fs/promises';

export const normalize = value => value.toLocaleLowerCase('vi').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd');
export async function getRestaurantData() {
  return JSON.parse(await readFile(new URL('../../data/restaurants.json', import.meta.url), 'utf8'));
}
export async function getDishRestaurantLinks() {
  return JSON.parse(await readFile(new URL('../../data/dish-restaurants.json', import.meta.url), 'utf8'));
}
export async function findRestaurants({ q = '', category = '', meal = '', priceTier = '', dishId = '', nutrition = '', page = 1, pageSize = 12 } = {}) {
  const { restaurants, importedAt } = await getRestaurantData();
  const associations = dishId ? (await getDishRestaurantLinks()).links.filter(link => link.dishId === dishId) : [];
  const query = normalize(q.trim());
  const filtered = restaurants.filter(r =>
    (!nutrition || r.nutritionReviews?.some(review => review.key === nutrition && review.status === 'verified' && review.source && review.basis)) &&
    (!dishId || associations.some(link => link.restaurantId === r.id)) &&
    (!query || normalize(`${r.name} ${r.address} ${r.area}`).includes(query)) &&
    (!category || r.category === category) &&
    (!meal || r.suggestedMeals.includes(meal) || r.suggestedMeals.includes('Cả ngày')) &&
    (!priceTier || r.priceTier === priceTier));
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  return {
    items: filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize).map(r => dishId ? { ...r, dishMatch: associations.find(link => link.restaurantId === r.id) } : r),
    total: filtered.length, totalRecords: restaurants.length, page: currentPage, pageSize, totalPages, importedAt,
    facets: {
      categories: [...new Set(restaurants.map(r => r.category))].sort((a, b) => a.localeCompare(b, 'vi')),
      meals: ['Sáng', 'Trưa', 'Chiều', 'Tối', 'Khuya'],
      priceTiers: [...new Set(restaurants.map(r => r.priceTier))].sort((a, b) => a.localeCompare(b, 'vi')),
    },
  };
}
export async function findRestaurantById(id) {
  const { restaurants } = await getRestaurantData();
  return restaurants.find(r => r.id === id);
}
