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
  const recipe = RECIPES[dish.id];
  if (!recipe) return;
  $('recipe-pending').hidden = true;
  $('recipe-detail').hidden = false;
  $('detail-back').href = App.dishUrl(dish);
  $('detail-photo').src = App.photo(dish, 1000, 750);
  $('detail-photo').alt = dish.name;
  $('detail-meta').innerHTML = App.cuisineLabel(dish.cuisine);
  $('detail-name').textContent = dish.name;
  $('detail-desc').textContent = dish.desc;
  const facts = [['Khẩu phần', recipe.servings], ['Chuẩn bị', recipe.prep], ['Chế biến', recipe.cook]];
  for (const [title, value] of facts) {
    const group = document.createElement('div');
    const dt = document.createElement('dt');
    const dd = document.createElement('dd');
    dt.textContent = title;
    dd.textContent = value;
    group.append(dt, dd);
    $('recipe-facts').append(group);
  }
  if (recipe.soak) {
    $('recipe-soak').hidden = false;
    $('recipe-soak').textContent = recipe.soak;
  }
  $('ingredients-help').textContent = `Cho ${recipe.servings}. Đánh dấu những gì đã chuẩn bị.`;
  const checks = [];
  const updateProgress = () => {
    const done = checks.filter(input => input.checked).length;
    $('ingredients-progress').textContent = `Đã chuẩn bị ${done}/${checks.length} nguyên liệu.`;
    $('ingredients-reset').disabled = done === 0;
  };
  for (const [quantity, name] of recipe.ingredients) {
    const li = document.createElement('li');
    const label = document.createElement('label');
    const input = document.createElement('input');
    input.type = 'checkbox';
    const text = document.createElement('span');
    const amount = document.createElement('strong');
    amount.textContent = quantity;
    text.append(amount, document.createTextNode(` ${name}`));
    label.append(input, text);
    li.append(label);
    $('recipe-ingredients').append(li);
    checks.push(input);
    input.addEventListener('change', updateProgress);
  }
  $('ingredients-reset').addEventListener('click', () => {
    checks.forEach(input => { input.checked = false; });
    updateProgress();
  });
  updateProgress();
  for (const [title, instruction] of recipe.steps) {
    const step = document.createElement('li');
    const heading = document.createElement('h3');
    const text = document.createElement('p');
    heading.textContent = title;
    text.textContent = instruction;
    step.append(heading, text);
    $('recipe-steps').append(step);
  }
  $('recipe-tip').textContent = recipe.tip;
  $('recipe-source').textContent = `${recipe.source.label} ↗`;
  $('recipe-source').href = recipe.source.url;
})();
