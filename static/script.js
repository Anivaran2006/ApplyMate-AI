async function loadUsers() {

    const response =
        await fetch("/users");

    const users =
        await response.json();
        const search =
    document.getElementById(
        "search"
    )?.value.toLowerCase() || "";

    const categories =
        [...new Set(
            users.map(
                user => user.category
            )
        )];
        const neetCount =
    users.filter(
        user => user.category === "NEET"
    ).length;

const jeeCount =
    users.filter(
        user => user.category === "JEE"
    ).length;

const cuetCount =
    users.filter(
        user => user.category === "CUET"
    ).length;

const generalCount =
    users.filter(
        user => user.category === "GENERAL"
    ).length;

    document.getElementById(
    "stats"
).innerHTML =
`
    <div class="stats-container">

        <div class="stat-card">
            👥 Total Users: ${users.length}
        </div>

        <div class="stat-card">
            🩺 NEET: ${neetCount}
        </div>

        <div class="stat-card">
            📐 JEE: ${jeeCount}
        </div>

        <div class="stat-card">
            📚 CUET: ${cuetCount}
        </div>

        <div class="stat-card">
            🌐 GENERAL: ${generalCount}
        </div>

    </div>
`;

    let html = "";

   users
.filter(user =>
    user.email
        .toLowerCase()
        .includes(search)
)
.forEach(user => {

        html += `
            <div class="user">

                <div>
                    <strong>${user.email}</strong>
                    <br>

                    <span class="badge">
                        ${user.category}
                    </span>
                </div>

                <button
                    class="delete-btn"
                    onclick="deleteUser('${user.email}','${user.category}')"
                >
                    Delete
                </button>

            </div>
        `;
    });

    document.getElementById(
        "users"
    ).innerHTML = html;
}


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
        '<span class="message-success">✅ User Registered Successfully</span>';

    loadUsers();
}


async function deleteUser(email, category) {

    const confirmed =
        confirm(
            `Delete subscription for ${email} (${category})?`
        );

    if(!confirmed){
        return;
    }

    await fetch(
        `/users/${email}/${category}`,
        {
            method: "DELETE"
        }
    );

    loadUsers();
}


loadUsers();