document.addEventListener('DOMContentLoaded', function () {
    const cards = document.querySelectorAll('.food-card');
    const searchInput = document.querySelector('.search-bar input');

    // Kartalarga animatsiya qo'shish
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease';

        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });

    // Restoran tugmalariga hover effekti
    const restaurantBtns = document.querySelectorAll('.restaurant-btn');
    restaurantBtns.forEach(btn => {
        btn.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-3px)';
        });
        btn.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0)';
        });
    });

    // Qidiruv funksiyasi
    searchInput.addEventListener('input', function () {
        const searchText = this.value.trim().toLowerCase();

        cards.forEach(card => {
            const foodName = card.querySelector('.food-name').textContent.toLowerCase();
            if (foodName.includes(searchText)) {
                card.style.display = 'block'; // Mos keladigan kartani ko'rsatish
            } else {
                card.style.display = 'none'; // Mos kelmagan kartani yashirish
            }
        });
    });
});