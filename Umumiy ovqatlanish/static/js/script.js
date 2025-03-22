document.addEventListener("DOMContentLoaded", function () {
    loadData("employee-list", employees, emp =>
        `<td>${emp.name}</td><td>${emp.position}</td><td>${emp.phone}</td><td>${emp.shift}</td>`);

    loadData("certificates", certificates, cert =>
        `<div class="col-md-4 mb-3">
            <div class="card shadow-sm">
                <div class="card-body text-center">
                    <h5 class="card-title">${cert.name}</h5>
                    <p class="card-text">Tasdiqlovchi organ: ${cert.issuedBy}</p>
                    <p class="card-text">Berilgan sana: ${cert.date}</p>
                </div>
            </div>
        </div>`, "div");

    loadData("food-monitoring", foodMonitoring, food =>
        `<td>${food.name}</td><td>${food.sold}</td><td>${food.certificate}</td><td>${food.updated}</td>`);

    loadCharts();
    setupMenu();
});

// Ma'lumotlarni yuklash uchun generik funksiya
function loadData(containerId, data, templateFunc, elementType = "tr") {
    const container = document.getElementById(containerId);
    if (!container) return;
    data.forEach(item => {
        const el = document.createElement(elementType);
        el.innerHTML = templateFunc(item);
        container.appendChild(el);
    });
}

// Tahlil va hisobotlar diagrammalarini yuklash
function loadCharts() {
    const charts = [
        { id: "orderChart", type: "bar", labels: ["Osh", "Shashlik", "Lagmon", "Manti"], data: [120, 80, 100, 60], bgColor: ["#00eaff", "#008cff", "#004e92", "#002766"] },
        { id: "revenueChart", type: "line", labels: ["Yanvar", "Fevral", "Mart", "Aprel", "May"], data: [5, 7, 10, 9, 12], borderColor: "#00eaff" },
        { id: "customerChart", type: "pie", labels: ["Yangi Mijozlar", "Doimiy Mijozlar"], data: [30, 70], bgColor: ["#00eaff", "#008cff"] }
    ];
    charts.forEach(chart => {
        const ctx = document.getElementById(chart.id)?.getContext("2d");
        if (ctx) {
            new Chart(ctx, {
                type: chart.type,
                data: {
                    labels: chart.labels,
                    datasets: [{ label: chart.id, data: chart.data, backgroundColor: chart.bgColor || chart.borderColor, borderColor: chart.borderColor || undefined, fill: false }]
                },
                options: { responsive: false, maintainAspectRatio: false }
            });
        }
    });
}

// Menyu funksiyasi
function setupMenu() {
    const menuToggle = document.querySelector(".menu-toggle");
    const navLinks = document.querySelector(".nav-links");

    if (menuToggle && navLinks) {
        menuToggle.addEventListener("click", () => navLinks.classList.toggle("active"));
        window.addEventListener("resize", () => { if (window.innerWidth > 768) navLinks.classList.remove("active"); });
    }
}

