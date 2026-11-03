import { rows } from '../config/database.js';
import { getDocument, ordered, optional } from './catalog-data.model.js';

export const normalize = value => value.toLocaleLowerCase('vi').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd');
export async function getRestaurantData() {
  const [restaurants,mealLinks,meals,metadata,order]=await Promise.all([
    rows('SELECT * FROM restaurants'),
    rows('SELECT restaurant_id,meal_id FROM restaurant_meals ORDER BY sort_order'),
    rows('SELECT id,label FROM meals'),getDocument('restaurants'),getDocument('catalog-order-v1'),
  ]);
  const labels=new Map(meals.map(m=>[m.id,m.label]));
  return {...metadata,restaurants:ordered(restaurants,order.restaurants).map(r=>{
    const keys=mealLinks.filter(m=>m.restaurant_id===r.id).map(m=>m.meal_id);
    const allDay=r.source_record.suggestedMeals?.includes('Cả ngày')&&keys.length===meals.length&&meals.every(m=>keys.includes(m.id));
    const result={id:r.id,sourceNumber:r.source_record.sourceNumber,name:r.name,category:r.category,originalCategory:r.original_category,suggestedMeals:allDay?['Cả ngày']:keys.map(key=>labels.get(key)),priceLabel:r.price_label,priceTier:r.price_tier,address:r.address,area:r.area,verification:r.verification,photo:r.photo,source:r.provenance};
    optional(result,'website',r.website);return result;
  })};
}
export async function getDishRestaurantLinks() {
  const [links,metadata,order]=await Promise.all([rows('SELECT dish_id,restaurant_id,match_type,offering,source_record FROM restaurant_dishes'),getDocument('associations'),getDocument('catalog-order-v1')]);
  const records=links.map(r=>optional({id:r.dish_id+'/'+r.restaurant_id,dishId:r.dish_id,restaurantId:r.restaurant_id,type:r.match_type,offering:r.offering},'evidence',r.source_record.evidence));
  return {...metadata,links:ordered(records,order.links).map(({id,...record})=>record)};
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
