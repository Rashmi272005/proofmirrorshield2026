
/* =====================================================
   PROOFMIRROR SHIELD — DASHBOARD VISUALISATIONS
   Animated risk distribution and statistic counters
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    const canvas = document.getElementById("dashboardRiskChart");

    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    if (!ctx) return;


    // Read actual report counts from the HTML data attributes.
    const low = Math.max(0, Number(canvas.dataset.low) || 0);
    const medium = Math.max(0, Number(canvas.dataset.medium) || 0);
    const high = Math.max(0, Number(canvas.dataset.high) || 0);

    const total = low + medium + high;


    const values = [
        { value: low, color: "#4bd5a0" },
        { value: medium, color: "#f5c15e" },
        { value: high, color: "#ff6874" }
    ];


    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 88;
    const lineWidth = 19;

    const reduceMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;


    // Draw chart background.
    function drawBackground() {

        ctx.beginPath();

        ctx.arc(
            centerX,
            centerY,
            radius,
            0,
            Math.PI * 2
        );

        ctx.strokeStyle = "rgba(255,255,255,0.08)";
        ctx.lineWidth = lineWidth;
        ctx.stroke();

    }


    // Draw risk distribution.
    function drawChart(progress) {

        ctx.clearRect(
            0,
            0,
            canvas.width,
            canvas.height
        );

        drawBackground();

        if (total === 0) return;

        let startAngle = -Math.PI / 2;

        values.forEach(function (item) {

            if (item.value <= 0) return;

            const fullAngle =
                (item.value / total) * Math.PI * 2;

            const animatedAngle = fullAngle * progress;

            ctx.beginPath();

            ctx.arc(
                centerX,
                centerY,
                radius,
                startAngle,
                startAngle + animatedAngle
            );

            ctx.strokeStyle = item.color;
            ctx.lineWidth = lineWidth;
            ctx.lineCap = "round";
            ctx.stroke();

            // Move to the next segment's actual starting angle.
            startAngle += fullAngle;

        });

    }


    // Animate chart drawing.
    function animateChart() {

        if (reduceMotion) {
            drawChart(1);
            return;
        }

        const duration = 1100;
        let startTime = null;

        function frame(timestamp) {

            if (startTime === null) {
                startTime = timestamp;
            }

            const elapsed = timestamp - startTime;

            const progress = Math.min(
                elapsed / duration,
                1
            );

            const easedProgress =
                1 - Math.pow(1 - progress, 3);

            drawChart(easedProgress);

            if (progress < 1) {
                requestAnimationFrame(frame);
            }

        }

        requestAnimationFrame(frame);

    }


    // Animate dashboard number counters.
    function animateCounters() {

        const counters = document.querySelectorAll(
            ".dash-stat-number[data-count]"
        );

        counters.forEach(function (element) {

            const target = Math.max(
                0,
                Number(element.dataset.count) || 0
            );

            if (reduceMotion || target === 0) {
                element.textContent =
                    target.toLocaleString();
                return;
            }

            const duration = 850;
            let startTime = null;

            function countFrame(timestamp) {

                if (startTime === null) {
                    startTime = timestamp;
                }

                const progress = Math.min(
                    (timestamp - startTime) / duration,
                    1
                );

                const eased =
                    1 - Math.pow(1 - progress, 3);

                const currentValue = Math.floor(
                    target * eased
                );

                element.textContent =
                    currentValue.toLocaleString();

                if (progress < 1) {
                    requestAnimationFrame(countFrame);
                } else {
                    element.textContent =
                        target.toLocaleString();
                }

            }

            requestAnimationFrame(countFrame);

        });

    }


    // Update the centre and legend using the same values.
    const centre = document.getElementById("dashChartTotal");

    const lowLabel = document.getElementById("dashLowLabel");
    const mediumLabel = document.getElementById("dashMediumLabel");
    const highLabel = document.getElementById("dashHighLabel");

    if (centre) {
        centre.textContent = total.toLocaleString();
    }

    if (lowLabel) {
        lowLabel.textContent =
            low.toLocaleString() + " reports";
    }

    if (mediumLabel) {
        mediumLabel.textContent =
            medium.toLocaleString() + " reports";
    }

    if (highLabel) {
        highLabel.textContent =
            high.toLocaleString() + " reports";
    }


    animateChart();
    animateCounters();

});
