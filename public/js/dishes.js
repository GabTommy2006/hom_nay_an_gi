/* Trang Tất cả món ăn: lưới món và bộ lọc theo ẩm thực, bữa ăn. */
(() => {
  const grid = document.getElementById('dish-grid');
  const empty = document.getElementById('empty');
  const count = document.getElementById('count');
  const filters = { cuisine: 'all', meal: 'all', diet: 'all', linked: 'all' };
  const search = document.getElementById('dish-search');
  const normalize = value => value.trim().toLocaleLowerCase('vi').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd');
  const leafIcon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 4c-6-1-13 1-14 7-1 4 2 7 6 6 6-1 8-7 8-13Z"/><path d="M4 21 15 10"/></svg>';
  const isVegetarian = App.isVegetarian;

  const cuisineSelect = document.getElementById('filter-cuisine');
  const mealSelect = document.getElementById('filter-meal');
  const dietToggle = document.getElementById('filter-diet');
  const linkedToggle = document.getElementById('filter-linked');
  const clearButton = document.getElementById('catalog-clear');
  const globe = '<svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/></svg>';
  const dropdowns = [];
  function createDropdown(trigger, list, entries, kind, title, onChange) {
    const options = [];
    let selected = 'all';
    let typing = '';
    let typingTimer;
    function close(focus = false) {
      list.hidden = true;
      trigger.setAttribute('aria-expanded', 'false');
      clearTimeout(typingTimer);
      typing = '';
      if (focus) trigger.focus();
    }
    function open() {
      dropdowns.forEach(dropdown => dropdown.close());
      list.hidden = false;
      trigger.setAttribute('aria-expanded', 'true');
      const active = options.find(option => option.dataset.value === selected) || options[0];
      active.focus();
      active.scrollIntoView({ block: 'nearest' });
    }
    function setValue(value) {
      selected = value;
      trigger.value = value;
      const entry = entries.find(item => item.key === value) || entries[0];
      document.getElementById(trigger.id + '-label').textContent = entry.label;
      trigger.setAttribute('aria-label', title + ': ' + entry.label);
      options.forEach(option => option.setAttribute('aria-selected', String(option.dataset.value === value)));
    }
    entries.forEach(entry => {
      const option = document.createElement('div');
      option.className = 'catalog-option';
      option.setAttribute('role', 'option');
      option.setAttribute('aria-selected', 'false');
      option.tabIndex = -1;
      option.dataset.value = entry.key;
      option.dataset[kind] = entry.key;
      const icon = document.createElement('span');
      icon.className = 'catalog-option__icon';
      icon.setAttribute('aria-hidden', 'true');
      icon.innerHTML = entry.icon;
      const label = document.createElement('span');
      label.textContent = entry.label;
      const check = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      check.setAttribute('viewBox', '0 0 24 24');
      check.setAttribute('class', 'catalog-option__check');
      check.setAttribute('aria-hidden', 'true');
      check.innerHTML = '<path d="m5 12 4 4L19 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>';
      option.append(icon, label, check);
      option.addEventListener('click', () => { setValue(entry.key); onChange(entry.key); close(true); });
      list.append(option);
      options.push(option);
    });
    trigger.addEventListener('click', () => list.hidden ? open() : close());
    trigger.addEventListener('keydown', event => {
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') { event.preventDefault(); open(); }
    });
    list.addEventListener('keydown', event => {
      const index = options.indexOf(document.activeElement);
      let next;
      if (event.key === 'ArrowDown') next = (index + 1) % options.length;
      else if (event.key === 'ArrowUp') next = (index - 1 + options.length) % options.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = options.length - 1;
      else if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); options[index]?.click(); return; }
      else if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
        typing += normalize(event.key);
        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => { typing = ''; }, 650);
        const found = entries.findIndex(entry => normalize(entry.label).startsWith(typing));
        if (found >= 0) next = found;
      }
      if (next != null) { event.preventDefault(); options[next].focus(); options[next].scrollIntoView({ block: 'nearest' }); }
    });
    trigger.parentElement.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !list.hidden) { event.preventDefault(); event.stopPropagation(); close(true); }
    });
    trigger.parentElement.addEventListener('focusout', event => {
      if (!trigger.parentElement.contains(event.relatedTarget)) close();
    });
    const api = { close, setValue };
    dropdowns.push(api);
    return api;
  }
  const cuisineEntries = [{ key: 'all', label: 'Mọi ẩm thực', icon: globe }, ...Object.entries(FOOD.CUISINES).map(([key, cuisine]) => {
    const label = document.createElement('span');
    label.innerHTML = App.cuisineLabel(key);
    return { key, label: cuisine.name, icon: label.firstElementChild.outerHTML };
  })];
  const mealEntries = [{ key: 'all', label: 'Mọi bữa ăn', icon: App.mealIcon('trua') }, ...Object.entries(FOOD.MEALS).map(([key, meal]) => ({ key, label: meal.label, icon: App.mealIcon(key) }))];
  const cuisineDropdown = createDropdown(cuisineSelect, document.getElementById('filter-cuisine-options'), cuisineEntries, 'cuisine', 'Ẩm thực', value => { filters.cuisine = value; render(); });
  const mealDropdown = createDropdown(mealSelect, document.getElementById('filter-meal-options'), mealEntries, 'meal', 'Bữa ăn', value => { filters.meal = value; render(); });
  document.addEventListener('pointerdown', event => {
    if (!cuisineSelect.parentElement.contains(event.target)) cuisineDropdown.close();
    if (!mealSelect.parentElement.contains(event.target)) mealDropdown.close();
  });
  function updateControls() {
    cuisineDropdown.setValue(filters.cuisine);
    mealDropdown.setValue(filters.meal);
    cuisineSelect.parentElement.dataset.cuisine = filters.cuisine;
    cuisineSelect.parentElement.dataset.active = String(filters.cuisine !== 'all');
    mealSelect.parentElement.dataset.meal = filters.meal;
    mealSelect.parentElement.dataset.active = String(filters.meal !== 'all');
    dietToggle.setAttribute('aria-pressed', String(filters.diet === 'vegetarian'));
    linkedToggle.setAttribute('aria-pressed', String(filters.linked === 'available'));
    const active = Object.values(filters).filter(value => value !== 'all').length + Number(Boolean(search.value.trim()));
    clearButton.hidden = active === 0;
    clearButton.textContent = 'Xóa lọc (' + active + ')';
    const icon = document.getElementById('catalog-cuisine-icon');
    if (filters.cuisine === 'all') icon.innerHTML = globe;
    else {
      const label = document.createElement('span');
      label.innerHTML = App.cuisineLabel(filters.cuisine);
      icon.replaceChildren(label.firstElementChild);
    }
    document.getElementById('catalog-meal-icon').innerHTML = App.mealIcon(filters.meal === 'all' ? 'trua' : filters.meal);
  }

  function render() {
    updateControls();
    const dishes = FOOD.DISHES.filter((d) =>
      (filters.cuisine === 'all' || d.cuisine === filters.cuisine) &&
      (filters.meal === 'all' || d.meals.includes(filters.meal)) &&
      (filters.diet === 'all' || isVegetarian(d)) &&
      (filters.linked === 'all' || d.linkedRestaurantCount > 0) &&
      (!search.value.trim() || normalize(d.name).includes(normalize(search.value))));

    count.textContent = `(${dishes.length})`;
    empty.hidden = dishes.length > 0;
    document.getElementById('diet-note').hidden = filters.diet !== 'vegetarian';
    grid.innerHTML = dishes.map((d) => {
      const meals = d.meals.map(m => `<span class="meal-tag">${App.mealIcon(m)}<span>${FOOD.MEALS[m].label}</span></span>`).join('');
      return `<li><a class="dish" data-cuisine="${d.cuisine}" href="${App.dishUrl(d)}">
        <span class="dish__photo"><img src="${App.photo(d, 560, 420)}" alt="${d.name}" width="560" height="420" loading="lazy">${d.source?.type === 'restaurant-catalog' ? '<span class="dish__image-note">Ảnh minh họa</span>' : ''}</span>
        <span class="dish__heading"><span class="dish__name">${d.name}</span>${isVegetarian(d) ? `<span class="vegetarian-badge dish__diet" title="${App.vegetarianNote(d)}">${leafIcon} Ăn chay</span>` : ''}</span>
        <span class="dish__meta">${App.cuisineLabel(d.cuisine)}</span>
        <span class="dish__meals" role="group" aria-label="Bữa ăn phù hợp">${meals}</span>
        ${d.linkedRestaurantCount ? `<span class="dish__linked">${d.linkedRestaurantCount} địa điểm liên quan <span aria-hidden="true">→</span></span>` : ''}
      </a></li>`;
    }).join('');
  }

  dietToggle.addEventListener('click', () => { filters.diet = filters.diet === 'all' ? 'vegetarian' : 'all'; render(); });
  linkedToggle.addEventListener('click', () => { filters.linked = filters.linked === 'all' ? 'available' : 'all'; render(); });
  function resetFilters() {
    search.value = '';
    Object.keys(filters).forEach(key => { filters[key] = 'all'; });
    dropdowns.forEach(dropdown => dropdown.close());
    render();
  }
  document.getElementById('clear-filters').addEventListener('click', resetFilters);
  clearButton.addEventListener('click', resetFilters);
  search.addEventListener('input', render);
  document.getElementById('dish-search-form').addEventListener('submit', event => { event.preventDefault(); render(); });

  render();
})();
