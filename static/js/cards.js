// =========================================================
// SIMPLEBANK - MY CARDS
// =========================================================

const freezeCardButton = document.getElementById("freezeCardButton");
const freezeIcon = document.getElementById("freezeIcon");
const freezeText = document.getElementById("freezeText");

const detailsButton = document.getElementById("detailsButton");
const addCardButton = document.getElementById("addCardButton");
const notificationButton = document.getElementById("notificationButton");

const cardMessage = document.getElementById("cardMessage");

const cardStatusBadge = document.getElementById("cardStatusBadge");
const cardStatusText = document.getElementById("cardStatusText");
const statusDot = document.getElementById("statusDot");

const cardDetailsModal = document.getElementById("cardDetailsModal");
const closeModalButton = document.getElementById("closeModalButton");
const modalCardStatus = document.getElementById("modalCardStatus");


// =========================================================
// CARD ID
// =========================================================

const cardId =
    freezeCardButton?.dataset.cardId || null;


// =========================================================
// MESSAGE
// =========================================================

function showCardMessage(message, type = "success") {

    if (!cardMessage) {
        return;
    }

    cardMessage.textContent = message;

    if (type === "error") {

        cardMessage.style.color = "#dc2626";

    } else {

        cardMessage.style.color = "#16a34a";

    }

}


// =========================================================
// UPDATE CARD UI
// =========================================================

function updateCardUI(status) {

    const frozen =
        status.toLowerCase() === "frozen";


    if (frozen) {

        if (freezeIcon) {
            freezeIcon.textContent = "🔓";
        }

        if (freezeText) {
            freezeText.textContent = "Unfreeze Card";
        }

        if (cardStatusBadge) {
            cardStatusBadge.textContent = "● Frozen";
            cardStatusBadge.style.color = "#dc2626";
        }

        if (cardStatusText) {
            cardStatusText.textContent = "Frozen";
            cardStatusText.style.color = "#dc2626";
        }

        if (statusDot) {
            statusDot.style.backgroundColor = "#dc2626";
        }

        if (modalCardStatus) {
            modalCardStatus.textContent = "Frozen";
            modalCardStatus.style.color = "#dc2626";
        }

    } else {

        if (freezeIcon) {
            freezeIcon.textContent = "❄";
        }

        if (freezeText) {
            freezeText.textContent = "Freeze Card";
        }

        if (cardStatusBadge) {
            cardStatusBadge.textContent = "● Active";
            cardStatusBadge.style.color = "#16a34a";
        }

        if (cardStatusText) {
            cardStatusText.textContent = "Active";
            cardStatusText.style.color = "#16a34a";
        }

        if (statusDot) {
            statusDot.style.backgroundColor = "#16a34a";
        }

        if (modalCardStatus) {
            modalCardStatus.textContent = "Active";
            modalCardStatus.style.color = "#16a34a";
        }

    }

}


// =========================================================
// FREEZE / UNFREEZE CARD
// =========================================================

if (freezeCardButton) {

    freezeCardButton.addEventListener("click", async function () {

        if (!cardId) {

            showCardMessage(
                "Card information is missing.",
                "error"
            );

            return;
        }


        freezeCardButton.disabled = true;


        try {

            const response = await fetch(
                "/api/cards/toggle-freeze",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        card_id: cardId
                    })
                }
            );


            const data = await response.json();


            if (data.success) {

                updateCardUI(data.status);

                showCardMessage(
                    data.message,
                    "success"
                );

            } else {

                showCardMessage(
                    data.message,
                    "error"
                );

            }

        } catch (error) {

            console.error(
                "Freeze card error:",
                error
            );

            showCardMessage(
                "Unable to update card status.",
                "error"
            );

        } finally {

            freezeCardButton.disabled = false;

        }

    });

}


// =========================================================
// CARD DETAILS
// =========================================================

if (detailsButton) {

    detailsButton.addEventListener("click", function () {

        if (cardDetailsModal) {

            cardDetailsModal.classList.add("show");

        }

    });

}


// =========================================================
// CLOSE CARD DETAILS
// =========================================================

if (closeModalButton) {

    closeModalButton.addEventListener("click", function () {

        if (cardDetailsModal) {

            cardDetailsModal.classList.remove("show");

        }

    });

}


// =========================================================
// CLOSE MODAL OUTSIDE
// =========================================================

if (cardDetailsModal) {

    cardDetailsModal.addEventListener(
        "click",
        function (event) {

            if (event.target === cardDetailsModal) {

                cardDetailsModal.classList.remove("show");

            }

        }
    );

}


// =========================================================
// ESC KEY
// =========================================================

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Escape") {

            if (cardDetailsModal) {

                cardDetailsModal.classList.remove("show");

            }

            const addCardModal =
                document.getElementById("addCardModal");

            if (addCardModal) {

                addCardModal.classList.remove("show");

            }

        }

    }
);


// =========================================================
// ADD NEW CARD MODAL
// =========================================================

if (addCardButton) {

    addCardButton.addEventListener(
        "click",
        function () {

            const addCardModal =
                document.getElementById("addCardModal");

            if (addCardModal) {

                addCardModal.classList.add("show");

            }

        }
    );

}


// =========================================================
// CLOSE ADD CARD MODAL
// =========================================================

const closeAddCardButton =
    document.getElementById("closeAddCardButton");


if (closeAddCardButton) {

    closeAddCardButton.addEventListener(
        "click",
        function () {

            const addCardModal =
                document.getElementById("addCardModal");

            if (addCardModal) {

                addCardModal.classList.remove("show");

            }

        }
    );

}


// =========================================================
// CREATE NEW CARD
// =========================================================

const createCardButton =
    document.getElementById("createCardButton");


if (createCardButton) {

    createCardButton.addEventListener(
        "click",
        async function () {

            const cardType =
                document.getElementById("newCardType")?.value;

            const cardNetwork =
                document.getElementById("newCardNetwork")?.value;

            const cardHolder =
                document.getElementById("newCardHolder")?.value;


            if (!cardHolder) {

                showCardMessage(
                    "Card holder name is required.",
                    "error"
                );

                return;

            }


            createCardButton.disabled = true;

            createCardButton.textContent =
                "Creating...";


            try {

                const response = await fetch(
                    "/api/cards/create",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({

                            card_type: cardType,

                            card_network:
                                cardNetwork,

                            card_holder:
                                cardHolder

                        })

                    }
                );


                const data =
                    await response.json();


                if (data.success) {

                    showCardMessage(
                        data.message,
                        "success"
                    );


                    const addCardModal =
                        document.getElementById(
                            "addCardModal"
                        );


                    if (addCardModal) {

                        addCardModal.classList.remove(
                            "show"
                        );

                    }


                    // Reload page so new card
                    // information comes from MySQL.

                    setTimeout(
                        function () {

                            window.location.reload();

                        },
                        800
                    );

                } else {

                    showCardMessage(
                        data.message,
                        "error"
                    );

                }

            } catch (error) {

                console.error(
                    "Create card error:",
                    error
                );

                showCardMessage(
                    "Unable to create new card.",
                    "error"
                );

            } finally {

                createCardButton.disabled = false;

                createCardButton.textContent =
                    "Create Card";

            }

        }
    );

}


// =========================================================
// CLOSE ADD CARD MODAL WHEN CLICKING OUTSIDE
// =========================================================

const addCardModal =
    document.getElementById("addCardModal");


if (addCardModal) {

    addCardModal.addEventListener(
        "click",
        function (event) {

            if (event.target === addCardModal) {

                addCardModal.classList.remove(
                    "show"
                );

            }

        }
    );

}


// =========================================================
// NOTIFICATIONS
// =========================================================

if (notificationButton) {

    notificationButton.addEventListener(
        "click",
        function () {

            alert(
                "You have no new notifications."
            );

        }
    );

}