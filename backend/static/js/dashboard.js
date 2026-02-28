document.addEventListener("DOMContentLoaded", function () {

    const chartData = document.getElementById("chart-data");

    if (!chartData) {
        console.log("Chart data div not found");
        return;
    }

    // Get data from HTML
    const dates = JSON.parse(chartData.dataset.dates || "[]");
    const quantities = JSON.parse(chartData.dataset.quantities || "[]");
    const monthLabels = JSON.parse(chartData.dataset.monthlabels || "[]");
    const monthData = JSON.parse(chartData.dataset.monthdata || "[]");

    console.log("Dates:", dates);
    console.log("Quantities:", quantities);
    console.log("Month Labels:", monthLabels);
    console.log("Month Data:", monthData);

    // Last 7 Days Chart
    const milkCanvas = document.getElementById("milkChart");
    if (milkCanvas && dates.length > 0) {
        new Chart(milkCanvas, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Milk (Liters)',
                    data: quantities,
                    borderWidth: 2
                }]
            }
        });
    } else {
        console.log("Milk chart not created (no data)");
    }

    // Monthly Chart
    const monthCanvas = document.getElementById("monthChart");
    if (monthCanvas && monthLabels.length > 0) {
        new Chart(monthCanvas, {
            type: 'bar',
            data: {
                labels: monthLabels,
                datasets: [{
                    label: 'Monthly Milk',
                    data: monthData,
                    borderWidth: 2
                }]
            }
        });
    } else {
        console.log("Month chart not created (no data)");
    }

});
