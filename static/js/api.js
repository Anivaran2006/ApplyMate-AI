const API_BASE = "https://applymate-ai-gz7k.onrender.com";

// ================= AUTH =================

const Auth = {

    getToken() {
        return localStorage.getItem("access_token");
    },

    setToken(token) {
        localStorage.setItem("access_token", token);
    },

    setUser(user) {
        localStorage.setItem("user", JSON.stringify(user));
    },

    getUser() {
        return JSON.parse(
            localStorage.getItem("user") || "{}"
        );
    },

    clear() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
    },

    isLoggedIn() {
        return !!this.getToken();
    }

};

// ================= FETCH =================

async function apiFetch(endpoint, options = {}) {

    const token = Auth.getToken();

    const headers = {
        "Content-Type": "application/json",
        ...(token
            ? { Authorization: `Bearer ${token}` }
            : {}),
        ...(options.headers || {})
    };
    console.log("Endpoint:", endpoint);
console.log("Token:", token);
console.log("Headers:", headers);
    const response = await fetch(
        API_BASE + endpoint,
        {
            ...options,
            headers
        }
    );

    let data = {};

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {
        throw new Error(
            data.detail || "Request Failed"
        );
    }

    return data;
}

// ================= API =================

const API = {

    // ---------- AUTH ----------

    auth: {

        async login(credentials) {

            const data = await apiFetch(
                "/auth/login",
                {
                    method: "POST",
                    body: JSON.stringify(credentials)
                }
            );

            Auth.setToken(data.access_token);

            Auth.setUser({
                email: data.email,
                role: data.role
            });

            return data;
        },

        register(user) {

            return apiFetch(
                "/auth/register",
                {
                    method: "POST",
                    body: JSON.stringify(user)
                }
            );

        },

        logout() {

            Auth.clear();

            window.location.href = "/login";

        }

    },
    forgotPassword(email) {

    return apiFetch(
        "/auth/forgot-password",
        {
            method: "POST",
            body: JSON.stringify({
                email: email
            })
        }
    );

},

    // ---------- USER ----------

    user: {

        me() {
            return apiFetch("/users/me");
        },

        update(data) {

            return apiFetch(
                "/users/profile",
                {
                    method: "PUT",
                    body: JSON.stringify(data)
                }
            );

        },

        changePassword(data) {

            return apiFetch(
                "/users/change-password",
                {
                    method: "PUT",
                    body: JSON.stringify(data)
                }
            );

        },

        updateNotifications(data) {

            return apiFetch(
                "/users/notification-settings",
                {
                    method: "PUT",
                    body: JSON.stringify(data)
                }
            );

        },

        connectTelegram(chatId) {

            return apiFetch(
                "/users/connect-telegram",
                {
                    method: "POST",
                    body: JSON.stringify({
                        telegram_chat_id: chatId
                    })
                }
            );

        },

        disconnectTelegram() {

            return apiFetch(
                "/users/disconnect-telegram",
                {
                    method: "POST"
                }
            );

        }

    },

    // ---------- NOTICES ----------

    notices: {

        list(params = {}) {

            const query =
                new URLSearchParams(params).toString();

            return apiFetch(
                "/notices/" +
                (query ? "?" + query : "")
            );

        },

        get(id) {

            return apiFetch(
                `/notices/${id}`
            );

        },

        delete(id) {

            return apiFetch(
                `/notices/${id}`,
                {
                    method: "DELETE"
                }
            );

        },

        aiAction(id, action) {

            return apiFetch(
                `/notices/${id}/ai-action`,
                {
                    method: "POST",
                    body: JSON.stringify({
                        action
                    })
                }
            );

        }

    },

    // ---------- BOOKMARKS ----------

    bookmarks: {

        list() {

            return apiFetch(
                "/bookmarks/"
            );

        },

        add(id) {

            return apiFetch(
                `/bookmarks/${id}`,
                {
                    method: "POST"
                }
            );

        },

        remove(id) {

            return apiFetch(
                `/bookmarks/${id}`,
                {
                    method: "DELETE"
                }
            );

        }

    },

    // ---------- SUBSCRIPTIONS ----------

    subscriptions: {

        list() {

            return apiFetch(
                "/subscriptions/"
            );

        },

        add(category) {

            return apiFetch(
                "/subscriptions/",
                {
                    method: "POST",
                    body: JSON.stringify({
                        category
                    })
                }
            );

        },

        remove(category) {

    return apiFetch(

        `/subscriptions/${encodeURIComponent(category)}`,

        {
            method: "DELETE"
        }

    );

}

    },
        // ---------- NOTIFICATIONS ----------

    notifications: {

        history(page = 1) {

            return apiFetch(
                `/notifications/history?page=${page}`
            );

        }

    },

    // ---------- PROFILE ----------

    profile: {

        get() {

            return apiFetch(
                "/profile"
            );

        }

    },

    // ---------- DASHBOARD ----------

    dashboard: {

        stats() {

            return apiFetch(
                "/dashboard/stats"
            );

        }

    },

    // ---------- ANALYTICS ----------

    analytics: {

        overview() {

            return apiFetch(
                "/analytics"
            );

        }

    },

    // ---------- AI ASSISTANT ----------

    assistant: {

        chat(question) {

            return apiFetch(
                "/assistant/chat",
                {
                    method: "POST",
                    body: JSON.stringify({
                        question
                    })
                }
            );

        }

    }

};

// ================= GUARDS =================

function requireAuth() {

    if (!Auth.isLoggedIn()) {

        window.location.href = "/login";

        return false;

    }

    return true;

}

function requireGuest() {

    if (Auth.isLoggedIn()) {

        window.location.href = "/dashboard";

        return false;

    }

    return true;

}

// ================= TOAST =================

function showToast(message, type = "success") {

    const toast = document.createElement("div");

    toast.innerHTML = message;

    toast.style.position = "fixed";
    toast.style.top = "30px";
    toast.style.right = "30px";
    toast.style.padding = "15px 25px";
    toast.style.borderRadius = "12px";
    toast.style.zIndex = "9999";
    toast.style.color = "white";
    toast.style.fontWeight = "600";
    toast.style.boxShadow = "0 10px 25px rgba(0,0,0,.3)";
    toast.style.transition = "all .3s ease";

    switch(type){

        case "success":
            toast.style.background = "#10B981";
            break;

        case "error":
            toast.style.background = "#EF4444";
            break;

        case "info":
            toast.style.background = "#3B82F6";
            break;

        case "warning":
            toast.style.background = "#F59E0B";
            break;

        default:
            toast.style.background = "#8B5CF6";
    }

    document.body.appendChild(toast);

    setTimeout(() => {

        toast.style.opacity = "0";

        toast.style.transform = "translateY(-10px)";

        setTimeout(() => toast.remove(), 300);

    },2500);

}