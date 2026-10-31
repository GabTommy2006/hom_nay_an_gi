/* Trang Giới thiệu: mood board và danh sách tác giả ảnh. */
(() => {
  const MOOD = ['pho-bo', 'banh-xeo', 'ramen', 'bibimbap', 'pad-thai', 'pizza-margherita'];
  const byId = (id) => FOOD.DISHES.find((d) => d.id === id);

  document.getElementById('mood').innerHTML = MOOD.map((id, i) => {
    const dish = byId(id);
    const wide = i === 0 || i === MOOD.length - 1;
    return `<img src="${App.photo(dish, wide ? 960 : 560, 560)}" alt="${dish.name}" loading="lazy">`;
  }).join('');

  document.getElementById('credits').innerHTML = FOOD.DISHES.map((d) =>
    `<li>${d.name}: <a href="https://unsplash.com/@${d.by}" rel="noopener">@${d.by}</a></li>`).join('');
})();
