// =========================================================
// SIMPLEBANK - SETTINGS JAVASCRIPT
// =========================================================


document.addEventListener("DOMContentLoaded", function () {


    // =====================================================
    // ELEMENTS
    // =====================================================

    const menuItems =
        document.querySelectorAll(".settings-menu-item");

    const sections =
        document.querySelectorAll(".settings-section");


    const profileForm =
        document.getElementById("profileForm");

    const passwordForm =
        document.getElementById("passwordForm");


    const profileMessage =
        document.getElementById("profileMessage");

    const passwordMessage =
        document.getElementById("passwordMessage");


    const saveProfileButton =
        document.getElementById("saveProfileButton");

    const changePasswordButton =
        document.getElementById("changePasswordButton");


    const notificationButton =
        document.getElementById("notificationButton");


    // =====================================================
    // SETTINGS MENU
    // =====================================================

    menuItems.forEach(function (item) {

        item.addEventListener("click", function () {

            const targetId =
                item.dataset.section;


            menuItems.forEach(function (menu) {

                menu.classList.remove("active");

            });


            sections.forEach(function (section) {

                section.classList.remove("active");

            });


            item.classList.add("active");


            const target =
                document.getElementById(targetId);


            if (target) {

                target.classList.add("active");

            }

        });

    });


    // =====================================================
    // PROFILE MESSAGE
    // =====================================================

    function showProfileMessage(
        message,
        type = "success"
    ) {

        if (!profileMessage) {
            return;
        }


        profileMessage.textContent =
            message;


        if (type === "error") {

            profileMessage.style.color =
                "#dc2626";

        } else {

            profileMessage.style.color =
                "#16a34a";

        }

    }


    // =====================================================
    // PASSWORD MESSAGE
    // =====================================================

    function showPasswordMessage(
        message,
        type = "success"
    ) {

        if (!passwordMessage) {
            return;
        }


        passwordMessage.textContent =
            message;


        if (type === "error") {

            passwordMessage.style.color =
                "#dc2626";

        } else {

            passwordMessage.style.color =
                "#16a34a";

        }

    }


    // =====================================================
    // PROFILE UPDATE
    // =====================================================

    if (profileForm) {

        profileForm.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();


                const name =
                    document
                        .getElementById("settingsName")
                        .value
                        .trim();


                const email =
                    document
                        .getElementById("settingsEmail")
                        .value
                        .trim();


                const mobile =
                    document
                        .getElementById("settingsMobile")
                        .value
                        .trim();


                // -----------------------------------------
                // VALIDATION
                // -----------------------------------------

                if (!name || !email) {

                    showProfileMessage(
                        "Name and email are required.",
                        "error"
                    );

                    return;

                }


                if (
                    mobile &&
                    !/^[0-9]{10}$/.test(mobile)
                ) {

                    showProfileMessage(
                        "Please enter a valid 10-digit mobile number.",
                        "error"
                    );

                    return;

                }


                // -----------------------------------------
                // LOADING
                // -----------------------------------------

                saveProfileButton.disabled =
                    true;

                saveProfileButton.textContent =
                    "Saving...";


                try {

                    const response =
                        await fetch(
                            "/api/settings/profile",
                            {

                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({

                                    name: name,

                                    email: email,

                                    mobile_number:
                                        mobile

                                })

                            }
                        );


                    const data =
                        await response.json();


                    if (
                        response.ok &&
                        data.success
                    ) {

                        showProfileMessage(
                            "✓ " + data.message,
                            "success"
                        );


                        // Update topbar name/email

                        const profileName =
                            document.querySelector(
                                ".profile-info strong"
                            );


                        const profileEmail =
                            document.querySelector(
                                ".profile-info small"
                            );


                        const avatar =
                            document.querySelector(
                                ".profile-avatar"
                            );


                        if (profileName) {

                            profileName.textContent =
                                data.user.name;

                        }


                        if (profileEmail) {

                            profileEmail.textContent =
                                data.user.email;

                        }


                        if (avatar) {

                            avatar.textContent =
                                data.user.name
                                    .charAt(0)
                                    .toUpperCase();

                        }


                    } else {

                        showProfileMessage(
                            data.message ||
                            "Unable to update profile.",
                            "error"
                        );

                    }


                } catch (error) {

                    console.error(
                        "Profile update error:",
                        error
                    );


                    showProfileMessage(
                        "Unable to connect to the server.",
                        "error"
                    );

                }


                finally {

                    saveProfileButton.disabled =
                        false;

                    saveProfileButton.textContent =
                        "Save Changes";

                }

            }
        );

    }


    // =====================================================
    // CHANGE PASSWORD
    // =====================================================

    if (passwordForm) {

        passwordForm.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();


                const currentPassword =
                    document
                        .getElementById("currentPassword")
                        .value;


                const newPassword =
                    document
                        .getElementById("newPassword")
                        .value;


                const confirmPassword =
                    document
                        .getElementById("confirmNewPassword")
                        .value;


                // -----------------------------------------
                // VALIDATION
                // -----------------------------------------

                if (
                    !currentPassword ||
                    !newPassword ||
                    !confirmPassword
                ) {

                    showPasswordMessage(
                        "Please complete all password fields.",
                        "error"
                    );

                    return;

                }


                if (newPassword.length < 6) {

                    showPasswordMessage(
                        "New password must contain at least 6 characters.",
                        "error"
                    );

                    return;

                }


                if (newPassword !== confirmPassword) {

                    showPasswordMessage(
                        "New passwords do not match.",
                        "error"
                    );

                    return;

                }


                if (
                    currentPassword ===
                    newPassword
                ) {

                    showPasswordMessage(
                        "New password must be different from the current password.",
                        "error"
                    );

                    return;

                }


                // -----------------------------------------
                // LOADING
                // -----------------------------------------

                changePasswordButton.disabled =
                    true;

                changePasswordButton.textContent =
                    "Changing...";


                try {

                    const response =
                        await fetch(
                            "/api/settings/change-password",
                            {

                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({

                                    current_password:
                                        currentPassword,

                                    new_password:
                                        newPassword

                                })

                            }
                        );


                    const data =
                        await response.json();


                    if (
                        response.ok &&
                        data.success
                    ) {

                        showPasswordMessage(
                            "✓ " + data.message,
                            "success"
                        );


                        passwordForm.reset();


                    } else {

                        showPasswordMessage(
                            data.message ||
                            "Unable to change password.",
                            "error"
                        );

                    }


                } catch (error) {

                    console.error(
                        "Password change error:",
                        error
                    );


                    showPasswordMessage(
                        "Unable to connect to the server.",
                        "error"
                    );

                }


                finally {

                    changePasswordButton.disabled =
                        false;

                    changePasswordButton.textContent =
                        "Change Password";

                }

            }
        );

    }


    // =====================================================
    // PASSWORD VISIBILITY
    // =====================================================

    const passwordToggleButtons =
        document.querySelectorAll(
            ".password-toggle"
        );


    passwordToggleButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const targetId =
                        button.dataset.target;


                    const input =
                        document.getElementById(
                            targetId
                        );


                    if (!input) {
                        return;
                    }


                    if (
                        input.type ===
                        "password"
                    ) {

                        input.type =
                            "text";

                    } else {

                        input.type =
                            "password";

                    }

                }
            );

        }
    );


    // =====================================================
    // NOTIFICATION PREFERENCES
    // =====================================================

    const transactionNotifications =
        document.getElementById(
            "transactionNotifications"
        );


    const securityNotifications =
        document.getElementById(
            "securityNotifications"
        );


    const promotionNotifications =
        document.getElementById(
            "promotionNotifications"
        );


    const saveNotificationButton =
        document.getElementById(
            "saveNotificationButton"
        );


    // =====================================================
    // LOAD NOTIFICATION SETTINGS
    // =====================================================

    function loadNotificationSettings() {

        const saved =
            localStorage.getItem(
                "simplebank_notifications"
            );


        if (!saved) {
            return;
        }


        try {

            const settings =
                JSON.parse(saved);


            transactionNotifications.checked =
                settings.transactions;


            securityNotifications.checked =
                settings.security;


            promotionNotifications.checked =
                settings.promotions;


        } catch (error) {

            console.error(
                "Notification settings error:",
                error
            );

        }

    }


    loadNotificationSettings();


    // =====================================================
    // SAVE NOTIFICATIONS
    // =====================================================

    if (saveNotificationButton) {

        saveNotificationButton.addEventListener(
            "click",
            function () {

                const settings = {

                    transactions:
                        transactionNotifications.checked,

                    security:
                        securityNotifications.checked,

                    promotions:
                        promotionNotifications.checked

                };


                localStorage.setItem(
                    "simplebank_notifications",
                    JSON.stringify(settings)
                );


                saveNotificationButton.textContent =
                    "✓ Saved";


                setTimeout(function () {

                    saveNotificationButton.textContent =
                        "Save Preferences";

                }, 1500);

            }
        );

    }


    // =====================================================
    // APPLICATION PREFERENCES
    // =====================================================

    const compactTransactions =
        document.getElementById(
            "compactTransactions"
        );


    const rememberPreferences =
        document.getElementById(
            "rememberPreferences"
        );


    // =====================================================
    // LOAD APPLICATION PREFERENCES
    // =====================================================

    const savedPreferences =
        localStorage.getItem(
            "simplebank_preferences"
        );


    if (savedPreferences) {

        try {

            const preferences =
                JSON.parse(savedPreferences);


            compactTransactions.checked =
                preferences.compact;


            rememberPreferences.checked =
                preferences.remember;

        } catch (error) {

            console.error(
                "Preference loading error:",
                error
            );

        }

    }


    // =====================================================
    // SAVE APPLICATION PREFERENCES
    // =====================================================

    function saveApplicationPreferences() {

        const preferences = {

            compact:
                compactTransactions.checked,

            remember:
                rememberPreferences.checked

        };


        localStorage.setItem(
            "simplebank_preferences",
            JSON.stringify(preferences)
        );

    }


    compactTransactions.addEventListener(
        "change",
        saveApplicationPreferences
    );


    rememberPreferences.addEventListener(
        "change",
        saveApplicationPreferences
    );


    // =====================================================
    // NOTIFICATION BUTTON
    // =====================================================

    if (notificationButton) {

        notificationButton.addEventListener(
            "click",
            function () {

                alert(
                    "You are all caught up! 🔔"
                );

            }
        );

    }

});