const filterButtons = document.querySelectorAll('.tournament-filter-button');

filterButtons.forEach(button => {
  const container = button.closest('.tournament-filter');
  const modal = container.querySelector('.tournament-filter-modal');
  const content = container.querySelector('.tournament-filter-modal-content');
  const img = button.querySelector('.open-filter-icon');

  const firstSrc  = '/static/img/open_filter_icon_no_active.svg';
  const secondSrc = '/static/img/open_filter_icon_active.svg';

  button.addEventListener('click', () => {
    const isActive = button.classList.contains('active');

    // Сначала закрываем ВСЕ открытые модалки
    filterButtons.forEach(otherBtn => {
      const otherContainer = otherBtn.closest('.tournament-filter');
      const otherModal     = otherContainer.querySelector('.tournament-filter-modal');
      const otherContent   = otherContainer.querySelector('.tournament-filter-modal-content');
      const otherImg       = otherBtn.querySelector('.open-filter-icon');
      otherModal.style.display   = 'none';
      otherContent.style.display = 'none';
      otherBtn.classList.remove('active');
      // сбрасываем иконку в неактивное состояние
      otherImg.src = firstSrc;
    });

    // Если у текущей кнопки уже было открыто — то просто закрыть (мы это уже сделали выше)
    if (isActive) {
      return;
    }

    // Иначе — открыть текущее меню и сделать его активным
    modal.style.display   = 'block';
    content.style.display = 'flex';
    img.src = secondSrc;
    button.classList.add('active');
  });

  // Закрываем по клику на оверлей
  modal.addEventListener('click', () => {
    modal.style.display   = 'none';
    content.style.display = 'none';
    img.src = firstSrc;
    button.classList.remove('active');
  });
});