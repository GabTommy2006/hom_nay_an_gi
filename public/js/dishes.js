/* Trang Tất cả món ăn: lưới món và bộ lọc theo ẩm thực, bữa ăn. */
(() => {
  const grid = document.getElementById('dish-grid');
  const empty = document.getElementById('empty');
  const count = document.getElementById('count');
  const filters = { cuisine: 'all', meal: 'all', diet: 'all' };
  const leafIcon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 4c-6-1-13 1-14 7-1 4 2 7 6 6 6-1 8-7 8-13Z"/><path d="M4 21 15 10"/></svg>';
  const isVegetarian = dish => dish.vegetarianReview?.status === 'reviewed';

  const pills = (group, options) => [['all', 'Tất cả'], ...options].map(([value, label]) =>
    `<button class="pill" type="button" data-group="${group}" data-value="${value}" aria-pressed="${value === 'all'}">${label}</button>`).join('');

  document.getElementById('filter-cuisine').innerHTML =
    pills('cuisine', Object.keys(FOOD.CUISINES).map((k) => [k, App.cuisineLabel(k)]));
  document.getElementById('filter-meal').innerHTML =
    pills('meal', Object.entries(FOOD.MEALS).map(([k, m]) => [k, `${App.mealIcon(k)} ${m.label}`]));
  document.getElementById('filter-diet').innerHTML =
    pills('diet', [['vegetarian', `${leafIcon} Món chay`]]);

  function render() {
    const dishes = FOOD.DISHES.filter((d) =>
      (filters.cuisine === 'all' || d.cuisine === filters.cuisine) &&
      (filters.meal === 'all' || d.meals.includes(filters.meal)) &&
      (filters.diet === 'all' || isVegetarian(d)));

    count.textContent = `(${dishes.length})`;
    empty.hidden = dishes.length > 0;
    document.getElementById('diet-note').hidden = filters.diet !== 'vegetarian';
    grid.innerHTML = dishes.map((d) => {
      const meals = d.meals.map(m => `<span class="meal-tag">${App.mealIcon(m)}<span>${FOOD.MEALS[m].label}</span></span>`).join('');
      return `<li><a class="dish" data-cuisine="${d.cuisine}" href="${App.dishUrl(d)}">
        <span class="dish__photo"><img src="${App.photo(d, 560, 420)}" alt="${d.name}" width="560" height="420" loading="lazy"></span>
        <span class="dish__heading"><span class="dish__name">${d.name}</span>${isVegetarian(d) ? `<span class="vegetarian-badge dish__diet" title="Áp dụng cho phiên bản nguyên liệu được mô tả trên website; thành phần tại từng quán có thể khác.">${leafIcon} Ăn chay</span>` : ''}</span>
        <span class="dish__meta">${App.cuisineLabel(d.cuisine)}</span>
        <span class="dish__meals" role="group" aria-label="Bữa ăn phù hợp">${meals}</span>
      </a></li>`;
    }).join('');
  }

  document.querySelector('.filters').addEventListener('click', (e) => {
    const pill = e.target.closest('.pill');
    if (!pill) return;
    filters[pill.dataset.group] = pill.dataset.value;
    document.querySelectorAll(`.pill[data-group="${pill.dataset.group}"]`).forEach((p) =>
      p.setAttribute('aria-pressed', p === pill));
    render();
  });

  document.getElementById('clear-filters').addEventListener('click', () => {
    Object.keys(filters).forEach(key => { filters[key] = 'all'; });
    document.querySelectorAll('.pill').forEach(p => p.setAttribute('aria-pressed', p.dataset.value === 'all'));
    render();
  });

  render();
})();
