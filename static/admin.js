async function loadUsers() {

    const response =
        await fetch("/users");

    const users =
        await response.json();

    const categories =
        [...new Set(
            users.map(
                user => user.category
            )
        )];

    document.getElementById(
        "stats"
    ).innerHTML =
    `
        <div class="stat-card">
            👥 Total Users: ${users.length}
        </div>

        <div class="stat-card">
            📚 Categories: ${categories.length}
        </div>
    `;

    let html = "";

    users.forEach(user => {

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


async function deleteUser(email, category) {

    await fetch(
        `/users/${email}/${category}`,
        {
            method: "DELETE"
        }
    );

    loadUsers();
}


loadUsers();