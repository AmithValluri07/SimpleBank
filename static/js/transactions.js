// =========================================================
// SIMPLEBANK - TRANSACTIONS
// =========================================================


const searchInput =
    document.getElementById("transactionSearch");

const filterSelect =
    document.getElementById("transactionFilter");

const transactionRows =
    document.querySelectorAll(".transaction-row");

const noResults =
    document.getElementById("noResults");


// =========================================================
// FILTER TRANSACTIONS
// =========================================================

function filterTransactions() {

    const searchText =
        searchInput.value.toLowerCase().trim();

    const filterType =
        filterSelect.value;

    let visibleCount = 0;


    transactionRows.forEach(row => {

        const type =
            row.dataset.type;

        const description =
            row.dataset.description;


        const matchesSearch =
            description.includes(searchText);


        const matchesFilter =
            filterType === "all" ||
            type === filterType;


        if (matchesSearch && matchesFilter) {

            row.style.display = "flex";

            visibleCount++;

        } else {

            row.style.display = "none";

        }

    });


    if (visibleCount === 0 && transactionRows.length > 0) {

        noResults.classList.remove("hidden");

    } else {

        noResults.classList.add("hidden");

    }

}


// =========================================================
// EVENTS
// =========================================================

searchInput.addEventListener(
    "input",
    filterTransactions
);


filterSelect.addEventListener(
    "change",
    filterTransactions
);