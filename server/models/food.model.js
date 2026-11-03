import { rows } from '../config/database.js';
import { getDocument, ordered, optional } from './catalog-data.model.js';

export async function getFood() {
  const [meals,cuisines,dishes,mealLinks,reviews,profiles,links,order]=await Promise.all([
    rows('SELECT id,label,source_record FROM meals'),
    rows('SELECT id,name,description,cover_dish_id,icon FROM cuisines'),
    rows('SELECT id,cuisine_id,name,description,image_url,photo_id,photo_author,photo_crop,image_source,provenance FROM dishes'),
    rows('SELECT dish_id,meal_id FROM dish_meals ORDER BY sort_order'),
    rows('SELECT dish_id,review_key,status,evidence FROM dish_reviews'),
    rows('SELECT dish_id,profile FROM dish_nutrition_profiles'),
    rows("SELECT dish_id,restaurant_id FROM restaurant_dishes WHERE match_type='dish'"),
    getDocument('catalog-order-v1'),
  ]);
  const MEALS=Object.fromEntries(ordered(meals,order.meals).map(r=>[r.id,{...r.source_record,label:r.label}]));
  const CUISINES=Object.fromEntries(ordered(cuisines,order.cuisines).map(r=>{
    const result={name:r.name,cover:r.cover_dish_id,desc:r.description};optional(result,'icon',r.icon);return [r.id,result];
  }));
  const DISHES=ordered(dishes,order.dishes).map(r=>{
    const direct=links.filter(l=>l.dish_id===r.id).map(l=>l.restaurant_id);
    const result={id:r.id,name:r.name,cuisine:r.cuisine_id,meals:mealLinks.filter(l=>l.dish_id===r.id).map(l=>l.meal_id),desc:r.description,linkedRestaurantCount:direct.length};
    for(const [key,value] of Object.entries({photo:r.photo_id,by:r.photo_author,crop:r.photo_crop,imageUrl:r.image_url,imageSource:r.image_source,source:r.provenance}))optional(result,key,value);
    // Do not retain evidence or labels from the immutable source_record snapshot.
    for(const review of ordered(reviews.filter(review=>review.dish_id===r.id),['vegetarian',...(order.reviews?.[r.id]||[])],'review_key')){
      if(review.review_key==='vegetarian')result.vegetarianReview={...review.evidence,status:review.status};
      else (result.nutritionReviews??=[]).push({...review.evidence,key:review.review_key,status:review.status});
    }
    const profile=profiles.find(p=>p.dish_id===r.id);if(profile)result.nutritionProfile=profile.profile;
    return result;
  });
  return {MEALS,CUISINES,DISHES};
}
