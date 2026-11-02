/* Only explicit, sourced review metadata may create nutrition badges. */
const Nutrition = (() => {
  const svg = path => `<svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${path}</svg>`;
  const entries = [
    { key: 'all', label: 'Ăn kiêng', icon: svg('<path d="M12 3v18M5 7h14M5 17h14"/><circle cx="8" cy="7" r="2"/><circle cx="16" cy="17" r="2"/>') },
    { key: 'low-sugar', label: 'Ít đường', icon: svg('<path d="m12 3 8 5v9l-8 4-8-4V8ZM4 8l8 5 8-5M12 13v8M4 3l16 18"/>') },
    { key: 'low-carb', label: 'Ít tinh bột', icon: svg('<path d="M12 21V5M12 9C5 9 5 4 5 4s7 0 7 5ZM12 14c7 0 7-5 7-5s-7 0-7 5ZM12 19c-7 0-7-5-7-5s7 0 7 5M4 3l16 18"/>') },
    { key: 'low-energy', label: 'Ít năng lượng', icon: svg('<path d="M13 2 5 14h6l-1 8 9-13h-6Z"/>') }
  ];
  const tags = record => entries.slice(1).filter(entry => record.nutritionReviews?.some(review => review.key === entry.key && review.status === 'verified' && review.source && review.basis));
  const matches = (record, key) => key === 'all' || tags(record).some(entry => entry.key === key);
  const escape = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const scope = record => record.nutritionProfile ? `<span class="nutrition-scope">${escape(record.nutritionProfile.scope)}</span>` : '';
  const badges = record => tags(record).map(entry => `<span class="nutrition-badge" data-nutrition="${entry.key}">${entry.icon}${entry.label}${record.nutritionProfile ? "*" : ""}</span>`).join('');
  function setup(id, onChange) {
    return CatalogFilters.createDropdown(document.getElementById(id), document.getElementById(id + '-options'), entries, 'nutrition', 'Chế độ ăn', onChange);
  }
  function note(key) {
    const element = document.getElementById('nutrition-note');
    element.hidden = key === 'all';
    const restaurantPage = Boolean(document.getElementById('restaurant-grid'));
    element.textContent = restaurantPage
      ? 'Chưa có thực đơn dinh dưỡng được xác nhận từ các quán. Nhãn của phiên bản món tham khảo không áp dụng cho quán bán món đó.'
      : key === 'low-carb'
        ? 'Chưa gán nhãn ít tinh bột: chưa có tiêu chí thống nhất cho từng món. Không suy từ ngưỡng carbohydrate của chế độ ăn cả ngày.'
        : 'Dấu *: chỉ áp dụng cho phiên bản ghi dưới nhãn, theo số liệu tham khảo; không xác nhận phần ăn tại quán. Ít đường không đồng nghĩa ít tinh bột hoặc ít năng lượng.';
    const link = document.createElement('a');
    link.href = 'about.html#nutrition-sources';
    link.textContent = ' Xem tiêu chí và nguồn dinh dưỡng →';
    element.append(link);
  }
  return { entries, tags, matches, badges, scope, setup, note };
})();
