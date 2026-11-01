/* Frontend editorial adaptations, not copied recipe text. Times are estimates. */
const RECIPES = {
  'xoi-xoai': {
    servings: 3, prep: '15 phút', cook: '35 phút', soak: 'Ngâm nếp ít nhất 3 giờ hoặc qua đêm; chưa tính trong thời gian trên.',
    ingredients: [
      { name: 'Gạo nếp', amount: 150, unit: 'g' },
      { name: 'Nước cốt dừa', amount: 125, unit: 'ml' },
      { name: 'Đường', amount: 1.5, unit: 'thìa canh' },
      { name: 'Muối', amount: 1, unit: 'nhúm' },
      { name: 'Xoài chín', amount: [1, 2], unit: 'quả' },
      { name: 'Kem dừa', amount: [1, 2], unit: 'thìa canh' },
      { name: 'Mè rang', amount: 0.5, unit: 'thìa canh' },
    ],
    steps: [
      ['Ngâm nếp', 'Ngâm ít nhất 3 giờ, sau đó xả và để ráo.'],
      ['Hấp chín', 'Lót khăn sạch trong xửng. Hấp khoảng 30 phút, đảo giữa chừng; hạt phải mềm, không còn lõi cứng.'],
      ['Trộn cốt dừa', 'Hâm cốt dừa với đường và muối cho tan, không đun sôi. Trộn vào nếp nóng, để thấm.'],
      ['Dọn món', 'Gọt và cắt xoài. Xếp cạnh xôi, thêm kem dừa và mè.'],
    ],
    tip: 'Chọn xoài chín thơm, còn giữ được miếng khi cắt.',
    source: { label: 'Mary Cadogan · Good Food — Sticky mango rice', url: 'https://www.bbcgoodfood.com/recipes/sticky-rice-mango' },
  },
  bruschetta: {
    servings: 2, prep: '10 phút', cook: '5 phút',
    ingredients: [
      { name: 'Bánh mì không mỡ động vật', amount: 4, unit: 'lát' },
      { name: 'Cà chua chín', amount: 250, unit: 'g' },
      { name: 'Tỏi', amount: 1, unit: 'tép' },
      { name: 'Dầu ô liu', amount: 1, unit: 'thìa canh' },
      { name: 'Húng quế', text: 'Một ít' },
      { name: 'Muối và tiêu', text: 'Vừa đủ' },
    ],
    steps: [
      ['Chuẩn bị cà chua', 'Rửa, cắt nhỏ cà chua; chắt phần nước dư để bánh không nhanh mềm.'],
      ['Trộn phần phủ', 'Xé húng quế, trộn cùng cà chua và dầu ô liu. Nêm muối, tiêu.'],
      ['Nướng bánh', 'Áp chảo khô hoặc nướng hai mặt đến khi vàng giòn, khoảng 3–5 phút. Chà tỏi lên mặt bánh ấm.'],
      ['Thưởng thức', 'Cho cà chua lên bánh ngay trước khi ăn.'],
    ],
    tip: 'Giữ riêng bánh và cà chua nếu chưa dùng ngay.',
    source: { label: 'Jamie Oliver — Bruschetta with tomato and basil', url: 'https://www.jamieoliver.com/recipes/bread/bruschetta-with-tomato-and-basil/' },
  },
};
