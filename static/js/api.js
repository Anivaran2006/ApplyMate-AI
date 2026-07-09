const API_BASE = "http://127.0.0.1:8000";

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
        return JSON.parse(localStorage.getItem("user") || "{}");
    },

    clear() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
    },

    isLoggedIn() {
        return !!this.getToken();
    }

};

// ================= API =================

async function apiFetch(endpoint, options = {}) {

    const token = Auth.getToken();

    const headers = {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers || {})
    };

    const response = await fetch(API_BASE + endpoint, {
        ...options,
        headers
    });

    
    let data = {};

try {
    data = await response.json();
} catch (e) {
    data = {};
}

if (!response.ok) {
    throw new Error(data.detail || "Something went wrong");
}

return data;
}

// ================= ENDPOINTS =================
const API = {

    // ================= AUTH =================

    auth: {

        async login(credentials) {

            const data = await apiFetch("/auth/login", {
                method: "POST",
                body: JSON.stringify(credentials)
            });

            Auth.setToken(data.access_token);

            Auth.setUser({
                email: data.email,
                role: data.role
            });

            return data;
        },

        register(user) {
            return apiFetch("/auth/register", {
                method: "POST",
                body: JSON.stringify(user)
            });
        },

        logout() {
            Auth.clear();
            window.location.href = "/login";
        }

    },

    // ================= USER =================

    user: {

        me() {
            return apiFetch("/users/me");
        }

    },

    // ================= NOTICES =================

    notices: {

        list(params = {}) {

            const query = new URLSearchParams(params).toString();

            return apiFetch(
                "/notices" + (query ? "?" + query : "")
            );

        }

    }

};
// ================= ROUTE GUARDS =================

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
function showToast(message){

    const toast=document.createElement("div");

    toast.innerHTML=message;

    toast.style.position="fixed";
    toast.style.top="30px";
    toast.style.right="30px";
    toast.style.background="#8B5CF6";
    toast.style.color="white";
    toast.style.padding="15px 25px";
    toast.style.borderRadius="12px";
    toast.style.zIndex="9999";
    toast.style.boxShadow="0 10px 25px rgba(0,0,0,.3)";

    document.body.appendChild(toast);

    setTimeout(()=>{

        toast.remove();

    },2500);

}