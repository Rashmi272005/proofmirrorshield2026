document.addEventListener("DOMContentLoaded", function () {

    const canvas = document.getElementById("riskChart");

    if (!canvas) {
        return;
    }

    const low = Math.max(0, Number(canvas.dataset.low) || 0);
    const medium = Math.max(0, Number(canvas.dataset.medium) || 0);
    const high = Math.max(0, Number(canvas.dataset.high) || 0);

    const values = [
        { label: "Lower Risk", value: low, color: "#4bd5a0" },
        { label: "Needs Review", value: medium, color: "#f4c15f" },
        { label: "High Risk", value: high, color: "#ff5b60" }
    ];

    const total = low + medium + high;

    const ctx = canvas.getContext("2d");

    if (!ctx) {
        return;
    }

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 112;
    const thickness = 22;

    const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;


    // Draw the doughnut chart
    function drawChart(progress) {

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Background ring
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);

        ctx.strokeStyle = "rgba(255,255,255,0.07)";
        ctx.lineWidth = thickness;
        ctx.stroke();


        if (total === 0) {

            ctx.fillStyle = "#93a2b5";
            ctx.font = "12px Arial";
            ctx.textAlign = "center";
            ctx.fillText(
                "No report data",
                centerX,
                centerY + radius + 30
            );

            return;
        }


        let startAngle = -Math.PI / 2;

        values.forEach(function (item) {

            if (item.value <= 0) {
                return;
            }

            const fullAngle =
                (item.value / total) * Math.PI * 2;

            const animatedAngle = fullAngle * progress;

            if (animatedAngle <= 0) {
                return;
            }

            ctx.beginPath();

            ctx.arc(
                centerX,
                centerY,
                radius,
                startAngle,
                startAngle + animatedAngle
            );

            ctx.strokeStyle = item.color;
            ctx.lineWidth = thickness;
            ctx.lineCap = "round";
            ctx.stroke();

            startAngle += fullAngle;

        });

    }


    // Animate the doughnut chart
    if (reducedMotion) {

        drawChart(1);

    } else {

        const duration = 1100;
        let startTime = null;

        function animate(timestamp) {

            if (!startTime) {
                startTime = timestamp;
            }

            const elapsed = timestamp - startTime;
            const rawProgress = Math.min(elapsed / duration, 1);

            // Smooth ease-out
            const progress =
                1 - Math.pow(1 - rawProgress, 3);

            drawChart(progress);

            if (rawProgress < 1) {
                requestAnimationFrame(animate);
            }

        }

        requestAnimationFrame(animate);

    }


    // Animate the category comparison bars
    const bars = document.querySelectorAll(".intel-bar-fill");

    const largestValue = Math.max(low, medium, high, 1);

    bars.forEach(function (bar) {

        const value = Math.max(
            0,
            Number(bar.dataset.value) || 0
        );

        const percentage =
            (value / largestValue) * 100;

        if (reducedMotion) {

            bar.style.width = percentage + "%";

        } else {

            requestAnimationFrame(function () {

                bar.style.width = percentage + "%";

            });

        }

    });


    // Update centre and legend values
    const chartTotal = document.getElementById("chartTotal");

    const lowLegend = document.getElementById("lowLegend");
    const mediumLegend = document.getElementById("mediumLegend");
    const highLegend = document.getElementById("highLegend");

    if (chartTotal) {
        chartTotal.textContent = total;
    }

    if (lowLegend) {
        lowLegend.textContent = low + " reports";
    }

    if (mediumLegend) {
        mediumLegend.textContent = medium + " reports";
    }

    if (highLegend) {
        highLegend.textContent = high + " reports";
    }

});