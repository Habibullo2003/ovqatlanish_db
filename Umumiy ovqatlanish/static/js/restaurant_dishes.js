// restaurant.js
const currentRestaurantId = String("{{ restaurant.id }}"); // Ensure it's a string
const currentUserId = "{{ request.user.id }}" || "guest";

console.log("currentRestaurantId:", currentRestaurantId);
console.log("currentUserId:", currentUserId);

// Get URLs from data attributes on the script tag
const scriptTag = document.currentScript;
const clearCartUrl = scriptTag.dataset.clearCartUrl;
const saveCartUrl = scriptTag.dataset.saveCartUrl;
const saveRestaurantIdUrl = scriptTag.dataset.saveRestaurantIdUrl;

// LocalStorage'dan cart ma'lumotlarini olish yoki yangi cart yaratish
let cartData = JSON.parse(localStorage.getItem('cart')) || { user_id: null, restaurant_id: null, items: [] };

console.log("Initial cartData:", cartData);

// Restoran yoki user o'zgargan bo'lsa, savatni tozalash
if (
    (cartData.restaurant_id !== null && cartData.restaurant_id !== currentRestaurantId) ||
    (cartData.user_id !== null && cartData.user_id !== currentUserId)
) {
    console.log("Cart cleared due to restaurant/user change");
    cartData = { user_id: currentUserId, restaurant_id: currentRestaurantId, items: [] };
    // Sessiyani tozalash uchun serverga so'rov yuborish
    fetch(clearCartUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({})
    })
        .then(response => {
            if (!response.ok) throw new Error('Tarmoq xatosi yuz berdi');
            return response.json();
        })
        .then(data => {
            console.log("Sessiyadagi cart tozalandi:", data);
        })
        .catch(error => {
            console.error("Sessiyani tozalashda xatolik:", error);
            alert("Savatni tozalashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.");
        });
}

let cart = cartData.items;

function updateCart() {
    try {
        const cartList = document.getElementById('cart-list');
        if (!cartList) {
            console.error("cart-list element not found");
            return;
        }

        cartList.innerHTML = '';

        if (cart.length === 0) {
            const emptyMessage = document.createElement('li');
            emptyMessage.className = 'list-group-item text-center';
            emptyMessage.textContent = "Savat bo'sh.";
            cartList.appendChild(emptyMessage);
        } else {
            cart.forEach(item => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = `${item.name} - ${item.count} ta - ${item.narx * item.count} so'm`;
                cartList.appendChild(li);
            });
        }

        const checkoutButton = document.getElementById('checkout-button');
        if (!checkoutButton) {
            console.error("checkout-button element not found");
            return;
        }
        checkoutButton.style.display = cart.length > 0 ? 'inline-block' : 'none';

        // LocalStorage'ga saqlash
        cartData.items = cart;
        localStorage.setItem('cart', JSON.stringify(cartData));
        console.log("Updated cartData:", cartData);
    } catch (e) {
        console.error("localStorage bilan ishlashda xatolik:", e);
        alert("Savatni saqlashda xatolik yuz berdi. Iltimos, brauzer sozlamalarini tekshiring.");
    }

    // Sessiyaga saqlash uchun serverga so'rov yuborish
    fetch(saveCartUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ cart: cart })
    })
        .then(response => {
            if (!response.ok) throw new Error('Tarmoq xatosi yuz berdi');
            return response.json();
        })
        .then(data => {
            console.log("Cart sessionga saqlandi:", data);
        })
        .catch(error => {
            console.error("Cart sessionga saqlashda xatolik:", error);
            alert("Savatni saqlashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.");
        });

    // Restoran ID'ni sessiyaga saqlash
    fetch(saveRestaurantIdUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ restaurant_id: currentRestaurantId })
    })
        .then(response => {
            if (!response.ok) throw new Error('Tarmoq xatosi yuz berdi');
            return response.json();
        })
        .then(data => {
            console.log("Restoran ID sessionga saqlandi:", data);
        })
        .catch(error => {
            console.error("Restoran ID saqlashda xatolik:", error);
            alert("Restoran ID saqlashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.");
        });
}

document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', function () {
        const taomId = this.getAttribute('data-taom-id');
        const name = this.getAttribute('data-name');
        const narx = parseFloat(this.getAttribute('data-narx')) || 0;
        const index = cart.findIndex(item => item.taom_id === taomId);

        console.log("Adding item:", { taom_id: taomId, name: name, narx: narx });

        if (index > -1) {
            cart[index].count += 1;
        } else {
            cart.push({ taom_id: taomId, name: name, narx: narx, count: 1 });
        }
        console.log("Cart after adding:", cart);
        updateCart();
    });
});

document.querySelectorAll('.remove-from-cart').forEach(button => {
    button.addEventListener('click', function () {
        const taomId = this.getAttribute('data-taom-id');
        const index = cart.findIndex(item => item.taom_id === taomId);

        if (index > -1) {
            cart[index].count -= 1;
            if (cart[index].count <= 0) {
                cart.splice(index, 1);
            }
            console.log("Cart after removing:", cart);
            updateCart();
        }
    });
});

// Sahifa yuklanganda cartni yangilash
updateCart();