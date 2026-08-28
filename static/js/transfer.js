// =========================================================
// SIMPLEBANK - TRANSFER PAGE
// =========================================================


// =========================================================
// ELEMENTS
// =========================================================

const recipientMobile =
    document.getElementById("recipientMobile");

const amountInput =
    document.getElementById("amount");

const descriptionInput =
    document.getElementById("description");

const transferButton =
    document.getElementById("transferButton");

const transferMessage =
    document.getElementById("transferMessage");

const recipientMessage =
    document.getElementById("recipientMessage");


// =========================================================
// HELPER - SHOW TRANSFER MESSAGE
// =========================================================

function showMessage(message, color) {

    transferMessage.textContent = message;

    transferMessage.style.color = color;

}


// =========================================================
// CHECK RECIPIENT
// =========================================================

recipientMobile.addEventListener("blur", async () => {

    const mobile =
        recipientMobile.value.trim();

    recipientMessage.textContent = "";


    // ---------------------------------------------
    // EMPTY MOBILE NUMBER
    // ---------------------------------------------

    if (!mobile) {
        return;
    }


    // ---------------------------------------------
    // BASIC MOBILE VALIDATION
    // ---------------------------------------------

    if (!/^[0-9]{10}$/.test(mobile)) {

        recipientMessage.textContent =
            "Please enter a valid 10-digit mobile number.";

        recipientMessage.style.color =
            "#dc2626";

        return;
    }


    // ---------------------------------------------
    // CHECK RECIPIENT API
    // ---------------------------------------------

    try {

        const response = await fetch(
            "/api/check-recipient",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    mobile_number: mobile

                })
            }
        );


        const data =
            await response.json();


        // -----------------------------------------
        // RECIPIENT FOUND
        // -----------------------------------------

        if (response.ok && data.success) {

            recipientMessage.textContent =
                "✓ " + data.message;

            recipientMessage.style.color =
                "#16a34a";

        }


        // -----------------------------------------
        // RECIPIENT NOT FOUND
        // -----------------------------------------

        else {

            recipientMessage.textContent =
                data.message ||
                "Recipient not found.";

            recipientMessage.style.color =
                "#dc2626";
        }


    } catch (error) {

        console.error(
            "Recipient check error:",
            error
        );

        recipientMessage.textContent =
            "Unable to check recipient.";

        recipientMessage.style.color =
            "#dc2626";

    }

});


// =========================================================
// TRANSFER MONEY
// =========================================================

transferButton.addEventListener(
    "click",
    async () => {


        // -----------------------------------------
        // GET VALUES
        // -----------------------------------------

        const mobile =
            recipientMobile.value.trim();

        const amount =
            parseFloat(amountInput.value);

        const description =
            descriptionInput.value.trim();


        // -----------------------------------------
        // VALIDATE MOBILE
        // -----------------------------------------

        if (!mobile) {

            showMessage(
                "Please enter the recipient mobile number.",
                "#dc2626"
            );

            recipientMobile.focus();

            return;
        }


        if (!/^[0-9]{10}$/.test(mobile)) {

            showMessage(
                "Please enter a valid 10-digit mobile number.",
                "#dc2626"
            );

            recipientMobile.focus();

            return;
        }


        // -----------------------------------------
        // VALIDATE AMOUNT
        // -----------------------------------------

        if (
            Number.isNaN(amount) ||
            amount <= 0
        ) {

            showMessage(
                "Please enter a valid amount.",
                "#dc2626"
            );

            amountInput.focus();

            return;
        }


        // -----------------------------------------
        // LOADING STATE
        // -----------------------------------------

        transferButton.disabled = true;


        transferButton.querySelector(
            "span:first-child"
        ).textContent = "Sending...";


        transferButton.querySelector(
            "span:last-child"
        ).textContent = "↗";


        showMessage(
            "Processing your transfer...",
            "#777777"
        );


        // -----------------------------------------
        // API REQUEST
        // -----------------------------------------

        try {

            const response = await fetch(
                "/api/transfer",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({

                        recipient_mobile: mobile,

                        amount: amount,

                        description:
                            description ||
                            "Money transfer"

                    })
                }
            );


            const data =
                await response.json();


            // -----------------------------------------
            // SUCCESS
            // -----------------------------------------

            if (
                response.ok &&
                data.success
            ) {

                showMessage(
                    "✓ " + data.message,
                    "#16a34a"
                );


                // -------------------------------------
                // CLEAR FORM
                // -------------------------------------

                recipientMobile.value = "";

                amountInput.value = "";

                descriptionInput.value = "";

                recipientMessage.textContent = "";


                // -------------------------------------
                // SUCCESS BUTTON
                // -------------------------------------

                transferButton.querySelector(
                    "span:first-child"
                ).textContent =
                    "Transfer Successful";


                transferButton.querySelector(
                    "span:last-child"
                ).textContent = "✓";


                // -------------------------------------
                // GO TO DASHBOARD
                // -------------------------------------

                setTimeout(() => {

                    window.location.href =
                        "/dashboard";

                }, 1500);


                return;
            }


            // -----------------------------------------
            // TRANSFER ERROR
            // -----------------------------------------

            showMessage(
                data.message ||
                "Transfer failed.",
                "#dc2626"
            );

        }


        // -----------------------------------------
        // CONNECTION ERROR
        // -----------------------------------------

        catch (error) {

            console.error(
                "Transfer error:",
                error
            );

            showMessage(
                "Unable to connect to the server.",
                "#dc2626"
            );

        }


        // -----------------------------------------
        // RESET BUTTON
        // -----------------------------------------

        transferButton.disabled = false;


        transferButton.querySelector(
            "span:first-child"
        ).textContent =
            "Send Money";


        transferButton.querySelector(
            "span:last-child"
        ).textContent =
            "→";

    }
);