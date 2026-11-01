/* Frontend only: recipes will appear once reviewed content is available. */
(() => {
  const id = new URLSearchParams(location.search).get('dish');
  const dish = FOOD.DISHES.find(item => item.id === id);
  const $ = id => document.getElementById(id);
  if (!dish) {
    if (id) {
      $('recipe-status').textContent = 'Không tìm thấy món ăn';
      $('recipe-message').textContent = 'Đường dẫn có thể không còn đúng. Bạn hãy chọn một món trong danh sách nhé.';
    }
    return;
  }
  document.body.dataset.cuisine = dish.cuisine;
  document.title = `Cách nấu ${dish.name} | Hôm nay ăn gì?`;
  $('recipe-meta').innerHTML = App.cuisineLabel(dish.cuisine);
  $('recipe-name').textContent = dish.name;
  $('recipe-desc').textContent = dish.desc;
  $('recipe-back').href = App.dishUrl(dish);
  $('recipe-back').textContent = '← Quay lại món vừa chọn';
  $('recipe-status').textContent = 'Công thức đang được cập nhật';
  $('recipe-message').textContent = 'Nguyên liệu và cách chế biến món này sẽ được bổ sung sau. Trong lúc chờ, bạn có thể tìm quán gần đây hoặc khám phá món khác.';
  $('recipe-maps').href = App.mapsUrl(dish);
  $('recipe-maps').hidden = false;
})();
