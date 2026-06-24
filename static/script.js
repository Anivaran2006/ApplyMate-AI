async function registerUser() {


const email =
    document.getElementById(
        "email"
    ).value.trim();

const category =
    document.getElementById(
        "category"
    ).value;

if(email === ""){

    document.getElementById(
        "message"
    ).innerHTML =
        '<span class="message-error">❌ Please enter an email</span>';

    return;
}

const emailRegex =
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

if(!emailRegex.test(email)){

    document.getElementById(
        "message"
    ).innerHTML =
        '<span class="message-error">❌ Invalid Email Address</span>';

    return;
}

const response = await fetch(
    "/register",
    {
        method: "POST",

        headers: {
            "Content-Type":
                "application/json"
        },

        body: JSON.stringify({
            email,
            category
        })
    }
);

const result =
    await response.json();

if(result.message === "User already exists"){

    document.getElementById(
        "message"
    ).innerHTML =
        '<span class="message-warning">⚠️ User already subscribed</span>';

    return;
}

document.getElementById(
    "email"
).value = "";

document.getElementById(
    "category"
).value = "NEET";

document.getElementById(
    "message"
).innerHTML =
    '<span class="message-success">✅ Successfully subscribed!</span>';


}
