// =========================================================
// SIMPLEBANK - DASHBOARD
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // ELEMENTS
    // =====================================================

    const chartCanvas = document.getElementById("spendingChart");
    const periodSelect = document.getElementById("periodSelect");

    const addMoneyButton =
        document.getElementById("addMoneyButton");

    const addMoneyModal =
        document.getElementById("addMoneyModal");

    const addMoneyOverlay =
        document.getElementById("addMoneyOverlay");

    const closeAddMoney =
        document.getElementById("closeAddMoney");

    const addMoneyForm =
        document.getElementById("addMoneyForm");

    const addMoneyAmount =
        document.getElementById("addMoneyAmount");

    const addMoneyDescription =
        document.getElementById("addMoneyDescription");

    const quickAmountButtons =
        document.querySelectorAll(".quick-amounts button");

    let spendingChart = null;


    // =====================================================
    // FORMAT CURRENCY
    // =====================================================

    function formatCurrency(value) {

        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 2
        }).format(value);

    }


    // =====================================================
    // LOAD SPENDING OVERVIEW
    // INCOME VS EXPENSE BAR CHART
    // =====================================================

    async function loadSpendingChart(period = "this_month") {

        if (!chartCanvas) {

            console.error(
                "Spending chart canvas not found."
            );

            return;
        }

        try {

            const response = await fetch(
                `/api/dashboard-chart?period=${encodeURIComponent(period)}`
            );

            const data = await response.json();


            if (!response.ok || !data.success) {

                console.error(
                    "Chart API error:",
                    data.message
                );

                return;
            }


            // =================================================
            // DESTROY PREVIOUS CHART
            // =================================================

            if (spendingChart) {

                spendingChart.destroy();

                spendingChart = null;

            }


            // =================================================
            // CHART CONTEXT
            // =================================================

            const ctx = chartCanvas.getContext("2d");


            // =================================================
            // CREATE BAR CHART
            // =================================================

            spendingChart = new Chart(ctx, {

                type: "bar",

                data: {

                    labels: data.labels,

                    datasets: [

                        // -----------------------------------------
                        // INCOME
                        // -----------------------------------------

                        {
                            label: "Income",

                            data: data.income,

                            backgroundColor:
                                "rgba(255, 107, 0, 0.85)",

                            borderColor:
                                "#ff6b00",

                            borderWidth: 1,

                            borderRadius: 6,

                            borderSkipped: false,

                            barPercentage: 0.7,

                            categoryPercentage: 0.7
                        },


                        // -----------------------------------------
                        // EXPENSES
                        // -----------------------------------------

                        {
                            label: "Expenses",

                            data: data.expenses,

                            backgroundColor:
                                "rgba(25, 25, 25, 0.90)",

                            borderColor:
                                "#191919",

                            borderWidth: 1,

                            borderRadius: 6,

                            borderSkipped: false,

                            barPercentage: 0.7,

                            categoryPercentage: 0.7
                        }

                    ]

                },


                // =================================================
                // CHART OPTIONS
                // =================================================

                options: {

                    responsive: true,

                    maintainAspectRatio: false,


                    interaction: {

                        mode: "index",

                        intersect: false

                    },


                    plugins: {

                        legend: {

                            display: true,

                            position: "top",

                            align: "end",

                            labels: {

                                usePointStyle: true,

                                pointStyle: "rectRounded",

                                padding: 18,

                                font: {

                                    size: 12,

                                    weight: "600"

                                }

                            }

                        },


                        tooltip: {

                            backgroundColor:
                                "#111111",

                            titleColor:
                                "#ffffff",

                            bodyColor:
                                "#ffffff",

                            padding: 12,

                            cornerRadius: 8,

                            displayColors: true,


                            callbacks: {

                                label: function (context) {

                                    return (
                                        " " +
                                        context.dataset.label +
                                        ": " +
                                        formatCurrency(
                                            context.parsed.y || 0
                                        )
                                    );

                                }

                            }

                        }

                    },


                    scales: {

                        x: {

                            stacked: false,

                            grid: {

                                display: false

                            },

                            ticks: {

                                maxRotation: 0,

                                autoSkip: true,

                                maxTicksLimit: 8,

                                font: {

                                    size: 11

                                }

                            }

                        },


                        y: {

                            beginAtZero: true,

                            grid: {

                                color:
                                    "rgba(0, 0, 0, 0.07)",

                                drawBorder: false

                            },

                            ticks: {

                                padding: 8,

                                font: {

                                    size: 11

                                },

                                callback: function (value) {

                                    if (value >= 100000) {

                                        return "₹" +
                                            (value / 100000)
                                                .toFixed(1) +
                                            "L";

                                    }

                                    if (value >= 1000) {

                                        return "₹" +
                                            (value / 1000)
                                                .toFixed(0) +
                                            "K";

                                    }

                                    return "₹" +
                                        Number(value)
                                            .toLocaleString("en-IN");

                                }

                            }

                        }

                    }

                }

            });

        }

        catch (error) {

            console.error(
                "Unable to load spending chart:",
                error
            );

        }

    }


    // =====================================================
    // PERIOD DROPDOWN
    // =====================================================

    if (periodSelect) {

        periodSelect.addEventListener(
            "change",
            function () {

                loadSpendingChart(
                    this.value
                );

            }
        );

    }


    // =====================================================
    // INITIAL CHART LOAD
    // =====================================================

    loadSpendingChart(
        periodSelect
            ? periodSelect.value
            : "this_month"
    );


    // =====================================================
    // ADD MONEY MODAL
    // =====================================================

    function openAddMoneyModal() {

        if (!addMoneyModal) {
            return;
        }

        addMoneyModal.style.display = "flex";

        document.body.style.overflow = "hidden";


        if (addMoneyAmount) {

            setTimeout(function () {

                addMoneyAmount.focus();

            }, 100);

        }

    }


    function closeAddMoneyModal() {

        if (!addMoneyModal) {
            return;
        }

        addMoneyModal.style.display = "none";

        document.body.style.overflow = "";

    }


    if (addMoneyButton) {

        addMoneyButton.addEventListener(
            "click",
            openAddMoneyModal
        );

    }


    if (closeAddMoney) {

        closeAddMoney.addEventListener(
            "click",
            closeAddMoneyModal
        );

    }


    if (addMoneyOverlay) {

        addMoneyOverlay.addEventListener(
            "click",
            closeAddMoneyModal
        );

    }


    // =====================================================
    // QUICK AMOUNTS
    // =====================================================

    quickAmountButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                if (addMoneyAmount) {

                    addMoneyAmount.value =
                        this.dataset.amount;

                    addMoneyAmount.focus();

                }

            }
        );

    });


    // =====================================================
    // ESCAPE KEY
    // =====================================================

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                closeAddMoneyModal();

            }

        }
    );


    // =====================================================
    // ADD MONEY SUBMIT
    // =====================================================

    if (addMoneyForm) {

        addMoneyForm.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();


                const amount =
                    addMoneyAmount.value.trim();


                const description =
                    addMoneyDescription
                        ? addMoneyDescription.value.trim()
                        : "";


                // =================================================
                // VALIDATE AMOUNT
                // =================================================

                if (!amount || Number(amount) <= 0) {

                    alert(
                        "Please enter a valid amount."
                    );

                    return;

                }


                // =================================================
                // CONFIRM BUTTON
                // =================================================

                const confirmButton =
                    document.getElementById(
                        "confirmAddMoney"
                    );


                if (confirmButton) {

                    confirmButton.disabled = true;

                    confirmButton.textContent =
                        "Adding...";

                }


                try {

                    // =================================================
                    // ADD MONEY API
                    // =================================================

                    const response = await fetch(
                        "/api/add-money",
                        {

                            method: "POST",

                            headers: {

                                "Content-Type":
                                    "application/json"

                            },

                            body: JSON.stringify({

                                amount: amount,

                                description:
                                    description

                            })

                        }
                    );


                    const data =
                        await response.json();


                    // =================================================
                    // API ERROR
                    // =================================================

                    if (
                        !response.ok ||
                        !data.success
                    ) {

                        alert(
                            data.message ||
                            "Unable to add money."
                        );

                        return;

                    }


                    // =================================================
                    // UPDATE BALANCE
                    // =================================================

                    const newBalance =
                        Number(data.balance);


                    const dashboardBalance =
                        document.getElementById(
                            "dashboardBalance"
                        );


                    const availableBalance =
                        document.getElementById(
                            "availableBalance"
                        );


                    if (dashboardBalance) {

                        dashboardBalance.textContent =
                            formatCurrency(
                                newBalance
                            );

                    }


                    if (availableBalance) {

                        availableBalance.textContent =
                            formatCurrency(
                                newBalance
                            );

                    }


                    // =================================================
                    // CLOSE MODAL
                    // =================================================

                    closeAddMoneyModal();


                    addMoneyForm.reset();


                    // =================================================
                    // RELOAD CHART
                    // =================================================

                    await loadSpendingChart(
                        periodSelect
                            ? periodSelect.value
                            : "this_month"
                    );


                    // =================================================
                    // REFRESH DASHBOARD
                    // =================================================

                    setTimeout(function () {

                        window.location.reload();

                    }, 400);

                }


                catch (error) {

                    console.error(
                        "ADD MONEY ERROR:",
                        error
                    );


                    alert(
                        "Something went wrong. Please try again."
                    );

                }


                finally {

                    if (confirmButton) {

                        confirmButton.disabled =
                            false;

                        confirmButton.textContent =
                            "Add Money";

                    }

                }

            }
        );

    }

});