document.addEventListener("DOMContentLoaded", function() {
    let form = document.getElementById("order-form");

    form.addEventListener("submit", function(event) {
        event.preventDefault();  // Formani avtomatik jo‘natishni to‘xtatamiz

        let formData = new FormData(form);

        fetch(form.action, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": getCookie("csrftoken")  // CSRF token qo‘shamiz
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById("success-message").innerText = "Buyurtma muvaffaqiyatli qo‘shildi!";
                document.getElementById("success-message").style.display = "block";

                // Faqat buyurtma ro‘yxatini yangilash
                updateOrderList();
            } else {
                alert("Xatolik yuz berdi: " + data.message);
            }
        })
        .catch(error => console.error("Xatolik:", error));
    });

    // CSRF token olish uchun funksiya
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            let cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Buyurtmalar ro‘yxatini yangilovchi funksiya
    function updateOrderList() {
        fetch("/orders/list/")  // Backendda buyurtmalar ro‘yxatini olish uchun endpoint
        .then(response => response.text())
        .then(html => {
            document.getElementById("order-list").innerHTML = html;
        })
        .catch(error => console.error("Buyurtmalarni yuklashda xatolik:", error));
    }
});
