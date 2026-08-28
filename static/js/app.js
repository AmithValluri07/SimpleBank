// Get elements from the login page// ============================================
// ELEMENTS
// ============================================

const loginTab = document.getElementById("loginTab");
const signupTab = document.getElementById("signupTab");

const loginSection = document.getElementById("loginSection");
const signupSection = document.getElementById("signupSection");

const heroTitle = document.querySelector(".hero-content h1");
const heroSubtitle = document.querySelector(".hero-content p");


// ============================================
// SWITCH TO LOGIN
// ============================================

function showLogin() {

    loginTab.classList.add("active");
    signupTab.classList.remove("active");

    loginSection.classList.add("active");
    signupSection.classList.remove("active");

    heroTitle.textContent = "Welcome Back";

    heroSubtitle.textContent =
        "Sign in to continue to your account";
}


// ============================================
// SWITCH TO SIGNUP
// ============================================

function showSignup() {

    signupTab.classList.add("active");
    loginTab.classList.remove("active");

    signupSection.classList.add("active");
    loginSection.classList.remove("active");

    heroTitle.textContent = "Create Account";

    heroSubtitle.textContent =
        "Join us today and start your banking journey";
}


// ============================================
// TAB EVENTS
// ============================================

loginTab.addEventListener("click", showLogin);

signupTab.addEventListener("click", showSignup);

document
    .getElementById("createAccount")
    .addEventListener("click", showSignup);

document
    .getElementById("goToLogin")
    .addEventListener("click", showLogin);


// ============================================
// LOGIN PASSWORD
// ============================================

const passwordInput =
    document.getElementById("password");

const togglePassword =
    document.getElementById("togglePassword");


togglePassword.addEventListener("click", () => {

    if (passwordInput.type === "password") {

        passwordInput.type = "text";

        togglePassword.textContent = "◉";

    } else {

        passwordInput.type = "password";

        togglePassword.textContent = "◉";
    }

});


// ============================================
// SIGNUP PASSWORD
// ============================================

const signupPassword =
    document.getElementById("signupPassword");

const toggleSignupPassword =
    document.getElementById("toggleSignupPassword");


toggleSignupPassword.addEventListener("click", () => {

    if (signupPassword.type === "password") {

        signupPassword.type = "text";

    } else {

        signupPassword.type = "password";
    }

});


// ============================================
// LOGIN FORM
// ============================================



const loginForm =
    document.getElementById("loginForm");

const loginButton =
    document.getElementById("loginButton");

const loginMessage =
    document.getElementById("loginMessage");


loginForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const email =
        document.getElementById("email").value.trim();

    const password =
        document.getElementById("password").value;


    loginMessage.textContent = "";


    if (!email || !password) {

        loginMessage.textContent =
            "Please enter your email and password.";

        loginMessage.style.color = "#dc2626";

        return;
    }


    // Loading state

    loginButton.disabled = true;

    loginButton.querySelector("span:last-child").textContent =
        "Signing in...";


    try {

        const response = await fetch("/api/login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })

        });


        const data = await response.json();


        if (response.ok) {

            loginMessage.textContent =
                "✓ Login successful!";

            loginMessage.style.color = "#16a34a";

            // Dashboard will be added later
              setTimeout(() => {
        window.location.href = "/dashboard";
         }, 500);

        } else {

            loginMessage.textContent =
                data.message || "Invalid email or password.";

            loginMessage.style.color = "#dc2626";
        }


    } catch (error) {

        console.error("Login error:", error);

        loginMessage.textContent =
            "Unable to connect to the server.";

        loginMessage.style.color = "#dc2626";

    }


    loginButton.disabled = false;

    loginButton.querySelector("span:last-child").textContent =
        "Swipe to Login";

});



// ============================================
// SIGNUP FORM
// ============================================

const signupForm =
    document.getElementById("signupForm");

const signupButton =
    document.getElementById("signupButton");

const signupMessage =
    document.getElementById("signupMessage");


signupForm.addEventListener("submit", async (event) => {

    event.preventDefault();


    const name =
        document.getElementById("signupName").value.trim();

    const email =
        document.getElementById("signupEmail").value.trim();

    const password =
        document.getElementById("signupPassword").value;

    const confirmPassword =
        document.getElementById("confirmPassword").value;


    signupMessage.textContent = "";


    if (!name || !email || !password || !confirmPassword) {

        signupMessage.textContent =
            "Please complete all fields.";

        signupMessage.style.color = "#dc2626";

        return;
    }


    if (password.length < 6) {

        signupMessage.textContent =
            "Password must contain at least 6 characters.";

        signupMessage.style.color = "#dc2626";

        return;
    }


    if (password !== confirmPassword) {

        signupMessage.textContent =
            "Passwords do not match.";

        signupMessage.style.color = "#dc2626";

        return;
    }


    signupButton.disabled = true;

    signupButton.querySelector("span:last-child").textContent =
        "Creating account...";


    try {

        const response = await fetch("/api/register", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })

        });


        const data = await response.json();


        if (response.ok) {

            signupMessage.textContent =
                "✓ Account created successfully!";

            signupMessage.style.color = "#16a34a";

            // Clear the form

            signupForm.reset();

        } else {

            signupMessage.textContent =
                data.message || "Registration failed.";

            signupMessage.style.color = "#dc2626";
        }


    } catch (error) {

        console.error("Registration error:", error);

        signupMessage.textContent =
            "Unable to connect to the server.";

        signupMessage.style.color = "#dc2626";

    }


    signupButton.disabled = false;

    signupButton.querySelector("span:last-child").textContent =
        "Swipe to Sign Up";

});


// ============================================
// FORGOT PASSWORD
// ============================================

document
    .getElementById("forgotPassword")
    .addEventListener("click", (event) => {

        event.preventDefault();

        alert(
            "Password recovery will be connected to our backend later."
        );

    });