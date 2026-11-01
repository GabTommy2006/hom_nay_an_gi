/* Trang Kết quả: ?mode=any, ?cuisine=viet (có quay) và ?dish=pho-bo (hiện thẳng). */
(() => {
  // 12 x 60 + 3 x 120 + 200 + 320 = 1600ms: tên món đổi nhanh rồi chậm dần
  const SCHEDULE = [...Array(12).fill(60), 120, 120, 120, 200, 320];

  const $ = (id) => document.getElementById(id);
  const params = new URLSearchParams(location.search);
  const qDish = params.get('dish');
  const qCuisine = params.get('cuisine');
  const card = $('result');
  const meal = App.getMeal();

  let pool = FOOD.DISHES;
  let spinId = 0;
  const photoCache = new Map();

  function preloadPhoto(dish) {
    const url = App.photo(dish, 1200, 900);
    if (photoCache.has(url)) return photoCache.get(url);
    const loading = new Promise(resolve => {
      const photo = new Image();
      let timer;
      const finish = loaded => {
        clearTimeout(timer);
        photo.onload = photo.onerror = null;
        if (!loaded) photoCache.delete(url);
        resolve(loaded);
      };
      photo.onload = () => finish(true);
      photo.onerror = () => finish(false);
      timer = setTimeout(() => finish(false), 2000);
      photo.src = url;
    });
    photoCache.set(url, loading);
    return loading;
  }

  function showPreview(dish) {
    $('dish-name').textContent = dish.name;
    $('dish-photo').src = App.photo(dish, 1200, 900);
    $('dish-photo').alt = dish.name;
  }

  function show(dish) {
    card.dataset.dishId = dish.id;
    const mealKey = dish.meals.includes(meal) ? meal : dish.meals[0];
    document.body.dataset.cuisine = dish.cuisine;
    document.title = `${dish.name} | Hôm nay ăn gì?`;
    $('dish-photo').src = App.photo(dish, 1200, 900);
    $('dish-photo').alt = dish.name;
    $('dish-meta').innerHTML = App.cuisineLabel(dish.cuisine);
    $('dish-meta').append(document.createTextNode(` · ${FOOD.MEALS[mealKey].label}`));
    $('vegetarian-badge').hidden = dish.vegetarianReview?.status !== 'reviewed';
    $('dish-name').textContent = dish.name;
    $('dish-desc').textContent = dish.desc;
    $('btn-maps').href = App.mapsUrl(dish);
    $('btn-recipe').href = `recipe.html?dish=${encodeURIComponent(dish.id)}`;
    $('btn-recipe').hidden = false;
    $('result-live').textContent = `Hôm nay ăn: ${dish.name}`;
    App.setLast(dish.id);
  }

  function showEmpty(title, text) {
    card.hidden = true;
    $('empty-title').textContent = title;
    $('empty-text').textContent = text;
    $('empty').hidden = false;
  }

  async function spin() {
    const id = ++spinId;
    const dish = App.pickDish(pool);
    $('vegetarian-badge').hidden = true;
    card.classList.remove('is-spinning', 'is-revealing', 'is-bounce');
    card.removeAttribute('aria-busy');
    if (App.reduceMotion()) return show(dish);

    card.setAttribute('aria-busy', 'true');
    $('result-live').textContent = 'Đang chọn món ăn...';
    $('dish-meta').textContent = 'Đang chuẩn bị ảnh...';
    $('btn-again').disabled = true;
    // Load a small sample once; never change the name ahead of an unloaded image.
    const candidates = [dish];
    const remaining = pool.filter(item => item.id !== dish.id);
    while (candidates.length < 5 && remaining.length) {
      const next = App.randomItem(remaining);
      candidates.push(next);
      remaining.splice(remaining.indexOf(next), 1);
    }
    const loaded = await Promise.all(candidates.map(preloadPhoto));
    if (id !== spinId) return;
    const previews = candidates.filter((item, index) => loaded[index]);
    if (!previews.length) {
      card.removeAttribute('aria-busy');
      $('btn-again').disabled = false;
      return show(dish);
    }
    void card.offsetWidth;
    card.classList.add('is-spinning');
    $('dish-meta').textContent = 'Đang quay...';
    $('dish-desc').textContent = 'Chờ một chút nhé.';

    for (const ms of SCHEDULE) {
      const options = previews.filter(item => item.name !== $('dish-name').textContent);
      showPreview(App.randomItem(options.length ? options : previews));
      await App.wait(ms);
      if (id !== spinId) return;
    }

    card.classList.remove('is-spinning');
    card.removeAttribute('aria-busy');
    $('btn-again').disabled = false;
    show(dish);
    void card.offsetWidth;
    card.classList.add('is-revealing');
  }

  function init() {
    if (qDish) {
      const dish = FOOD.DISHES.find((d) => d.id === qDish);
      if (!dish) return showEmpty('Món này chưa có trong thực đơn', 'Có thể đường dẫn bị sai. Để tụi mình chọn cho bạn món khác nhé.');
      show(dish);
    } else if (qCuisine) {
      if (!Object.hasOwn(FOOD.CUISINES, qCuisine)) return showEmpty('Chưa có nền ẩm thực này', 'Trong lúc chờ, bạn thử chọn bất kỳ món nào nhé.');
      document.body.dataset.cuisine = qCuisine;
      pool = FOOD.DISHES.filter((d) => d.cuisine === qCuisine);
      spin();
    } else {
      spin();
    }
    $('btn-again').addEventListener('click', spin);
  }

  init();
})();
