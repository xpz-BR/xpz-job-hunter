// State Management
let currentProfile = {};
let favoriteJobIds = new Set();
let currentJobs = [];

// DOM Elements
const searchForm = document.getElementById("search-form");
const searchQuery = document.getElementById("search-query");
const searchLocation = document.getElementById("search-location");
const minMatchFilter = document.getElementById("min-match-filter");
const jobsContainer = document.getElementById("jobs-container");
const loadingState = document.getElementById("loading-state");
const emptyState = document.getElementById("empty-state");
const resultsCount = document.getElementById("results-count");
const resultsTitle = document.getElementById("results-title");

// Profile Elements
const profileForm = document.getElementById("profile-form");
const profileName = document.getElementById("profile-name");
const profileRoles = document.getElementById("profile-roles");
const profileSkills = document.getElementById("profile-skills");
const profileLevel = document.getElementById("profile-level");
const profileEducation = document.getElementById("profile-education");
const profileLocation = document.getElementById("profile-location");
const profileSalary = document.getElementById("profile-salary");
const profileRemote = document.getElementById("profile-remote");
const profileBio = document.getElementById("profile-bio");
const skillsPreview = document.getElementById("profile-skills-preview");
const activeProfileSkills = document.getElementById("active-profile-skills");

// Navigation & Tabs
const navTabs = document.querySelectorAll(".nav-tab");
const tabContents = document.querySelectorAll(".tab-content");
const userStatusPill = document.getElementById("user-status-pill");
const pillName = document.getElementById("pill-name");
const pillLevel = document.getElementById("pill-level");
const favCountBadge = document.getElementById("fav-count");
const btnQuickEdit = document.getElementById("btn-quick-edit-profile");

// Favorites Elements
const favoritesContainer = document.getElementById("favorites-container");
const favoritesEmpty = document.getElementById("favorites-empty");

// Toast Notification Helper
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let icon = "fa-circle-info";
    if (type === "success") icon = "fa-circle-check";
    if (type === "error") icon = "fa-triangle-exclamation";

    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%)";
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Tab Switching Logic
function switchTab(tabId) {
    navTabs.forEach(t => {
        t.classList.toggle("active", t.dataset.tab === tabId);
    });
    tabContents.forEach(c => {
        c.classList.toggle("active", c.id === tabId);
    });
    if (tabId === "favorites-section") {
        loadFavorites();
    }
}

navTabs.forEach(tab => {
    tab.addEventListener("click", () => switchTab(tab.dataset.tab));
});

if (userStatusPill) {
    userStatusPill.addEventListener("click", () => switchTab("profile-section"));
}

if (btnQuickEdit) {
    btnQuickEdit.addEventListener("click", () => switchTab("profile-section"));
}

// Live Skills Preview in Profile Form
function updateSkillsPreview() {
    const text = profileSkills.value;
    const skills = text.split(",").map(s => s.strip ? s.strip() : s.trim()).filter(Boolean);
    skillsPreview.innerHTML = "";
    skills.forEach(s => {
        const tag = document.createElement("span");
        tag.className = "skill-tag matched";
        tag.innerHTML = `<i class="fa-solid fa-check"></i> ${s}`;
        skillsPreview.appendChild(tag);
    });
}
profileSkills.addEventListener("input", updateSkillsPreview);

// Load Profile Data from SQLite API
async function loadProfile() {
    try {
        const res = await fetch("/api/profile");
        if (!res.ok) throw new Error("Erro ao carregar perfil");
        currentProfile = await res.json();

        // Populate form
        profileName.value = currentProfile.full_name || "";
        profileRoles.value = currentProfile.desired_roles || "";
        profileSkills.value = currentProfile.skills || "";
        profileLevel.value = currentProfile.experience_level || "junior";
        profileEducation.value = currentProfile.education || "";
        profileLocation.value = currentProfile.location || "";
        profileSalary.value = currentProfile.min_salary || "";
        profileRemote.checked = Boolean(currentProfile.remote_only);
        profileBio.value = currentProfile.bio || "";

        // Update Nav Pill
        pillName.textContent = currentProfile.full_name || "Candidato";
        pillLevel.textContent = currentProfile.experience_level || "Júnior";

        // Update default search query placeholder if empty
        if (!searchQuery.value && currentProfile.roles_list && currentProfile.roles_list.length > 0) {
            searchQuery.placeholder = `Ex: ${currentProfile.roles_list[0]}`;
        }

        // Update active profile skills chips
        renderProfileSkillsChips();
        updateSkillsPreview();
    } catch (err) {
        console.error(err);
        showToast("Não foi possível carregar o perfil do candidato.", "error");
    }
}

// Render active profile skills chips
function renderProfileSkillsChips() {
    activeProfileSkills.innerHTML = "";
    const skills = currentProfile.skills_list || [];
    if (skills.length === 0) {
        activeProfileSkills.innerHTML = `<span style="color: var(--text-muted); font-size: 0.8rem;">Nenhuma habilidade cadastrada ainda. Adicione no seu perfil!</span>`;
        return;
    }
    skills.forEach(s => {
        const tag = document.createElement("span");
        tag.className = "skill-tag matched";
        tag.textContent = s;
        activeProfileSkills.appendChild(tag);
    });
}

// Save Profile to SQLite API
profileForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
        full_name: profileName.value.trim(),
        desired_roles: profileRoles.value.trim(),
        skills: profileSkills.value.trim(),
        experience_level: profileLevel.value,
        education: profileEducation.value.trim(),
        location: profileLocation.value.trim(),
        min_salary: parseFloat(profileSalary.value) || 0,
        remote_only: profileRemote.checked,
        bio: profileBio.value.trim()
    };

    try {
        const res = await fetch("/api/profile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        currentProfile = data.profile;
        pillName.textContent = currentProfile.full_name || "Candidato";
        pillLevel.textContent = currentProfile.experience_level || "Júnior";
        renderProfileSkillsChips();
        showToast("Perfil atualizado com sucesso no SQLite!", "success");
        
        // Re-score currently listed jobs if any
        if (currentJobs.length > 0) {
            executeSearch();
        }
    } catch (err) {
        console.error(err);
        showToast("Erro ao salvar perfil.", "error");
    }
});

// Load Favorites Count and IDs
async function refreshFavoritesCount() {
    try {
        const res = await fetch("/api/favorites");
        if (res.ok) {
            const data = await res.json();
            favoriteJobIds = new Set(data.favorites.map(f => String(f.job_id)));
            favCountBadge.textContent = data.total;
        }
    } catch (err) {
        console.error("Erro ao sincronizar favoritos", err);
    }
}

// Render a Job Card
function createJobCard(job, isFavoriteView = false) {
    const card = document.createElement("div");
    card.className = "job-card";

    const score = job.match_score || 0;
    let scoreClass = "score-low";
    let matchLabel = "Match Regular";
    if (score >= 80) {
        scoreClass = "score-high";
        matchLabel = "Super Match";
    } else if (score >= 60) {
        scoreClass = "score-mid";
        matchLabel = "Bom Match";
    }

    const siteLower = (job.site || "web").toLowerCase();
    let siteBadgeClass = "badge-site";
    if (siteLower.includes("linkedin")) siteBadgeClass += " linkedin";
    else if (siteLower.includes("indeed")) siteBadgeClass += " indeed";
    else if (siteLower.includes("remotive")) siteBadgeClass += " remotive";

    const isFav = favoriteJobIds.has(String(job.id || job.job_id));

    // Matched skills pills
    const matchedPills = (job.matched_skills || [])
        .map(s => `<span class="skill-tag matched"><i class="fa-solid fa-check"></i> ${s}</span>`)
        .join("");

    // Missing skills pills
    const missingPills = (job.missing_skills || [])
        .slice(0, 3)
        .map(s => `<span class="skill-tag missing"><i class="fa-solid fa-minus"></i> ${s}</span>`)
        .join("");

    // Extra skills in job
    const extraPills = (job.extra_tech || [])
        .slice(0, 3)
        .map(s => `<span class="skill-tag extra"><i class="fa-solid fa-plus"></i> ${s}</span>`)
        .join("");

    card.innerHTML = `
        <div class="job-card-top">
            <div class="job-meta-header">
                <div class="job-company">
                    <i class="fa-regular fa-building"></i> ${job.company || "Empresa Confidencial"}
                </div>
                <a href="${job.url || '#'}" target="_blank" rel="noopener noreferrer" class="job-title">
                    ${job.title}
                </a>
                <div class="job-badges">
                    <span class="${siteBadgeClass}">
                        <i class="fa-solid fa-arrow-up-right-from-square"></i> ${job.site || "Web"}
                    </span>
                    <span class="badge badge-location">
                        <i class="fa-solid fa-location-dot"></i> ${job.location || "Remoto"}
                    </span>
                    ${job.salary && job.salary !== 'Não divulgado' ? `<span class="badge badge-salary"><i class="fa-solid fa-money-bill-wave"></i> ${job.salary}</span>` : ''}
                    ${job.is_remote ? `<span class="badge badge-remote"><i class="fa-solid fa-house-laptop"></i> Remoto</span>` : ''}
                </div>
            </div>

            <button class="btn-fav ${isFav ? 'saved' : ''}" data-id="${job.id || job.job_id}" title="Favoritar vaga">
                <i class="fa-${isFav ? 'solid' : 'regular'} fa-bookmark"></i>
                <span>${isFav ? 'Salva' : 'Favoritar'}</span>
            </button>
        </div>

        <!-- COMPATIBILITY BAR -->
        <div class="match-container ${scoreClass}">
            <div class="match-header">
                <div class="match-title">
                    <i class="fa-solid fa-chart-pie"></i> ${matchLabel}
                </div>
                <div class="match-percent">${score}% de Compatibilidade</div>
            </div>
            <div class="match-bar-bg">
                <div class="match-bar-fill" style="width: ${score}%;"></div>
            </div>
            <div class="skills-comparison-row">
                ${matchedPills ? `<div><strong>Correspondências:</strong> ${matchedPills}</div>` : ''}
                ${missingPills ? `<div><strong>Não encontradas:</strong> ${missingPills}</div>` : ''}
                ${extraPills ? `<div><strong>Diferenciais pedidos:</strong> ${extraPills}</div>` : ''}
            </div>
        </div>

        <p class="job-desc-snippet">${job.description || "Sem descrição disponível."}</p>

        <div class="job-actions">
            <span style="font-size: 0.75rem; color: var(--text-muted);">Publicado: ${job.date_posted || "Recentemente"}</span>
            <a href="${job.url || '#'}" target="_blank" rel="noopener noreferrer" class="btn-secondary">
                Ver Vaga Completa <i class="fa-solid fa-arrow-up-right-from-square"></i>
            </a>
        </div>
    `;

    // Attach Favorite event
    const favBtn = card.querySelector(".btn-fav");
    favBtn.addEventListener("click", () => toggleFavorite(job, favBtn, isFavoriteView, card));

    return card;
}

// Toggle Favorite Handler
async function toggleFavorite(job, button, isFavoriteView, cardElement) {
    const jobId = String(job.id || job.job_id);
    const isCurrentlyFav = favoriteJobIds.has(jobId);

    try {
        if (isCurrentlyFav) {
            // Remove
            const res = await fetch(`/api/favorites/${jobId}`, { method: "DELETE" });
            if (res.ok) {
                favoriteJobIds.delete(jobId);
                button.classList.remove("saved");
                button.querySelector("i").className = "fa-regular fa-bookmark";
                button.querySelector("span").textContent = "Favoritar";
                showToast("Vaga removida dos favoritos.", "info");
                if (isFavoriteView) {
                    cardElement.remove();
                    if (favoriteJobIds.size === 0) {
                        favoritesEmpty.classList.remove("hidden");
                    }
                }
            }
        } else {
            // Add
            const res = await fetch("/api/favorites", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ job })
            });
            if (res.ok) {
                favoriteJobIds.add(jobId);
                button.classList.add("saved");
                button.querySelector("i").className = "fa-solid fa-bookmark";
                button.querySelector("span").textContent = "Salva";
                showToast("Vaga guardada nos favoritos!", "success");
            }
        }
        favCountBadge.textContent = favoriteJobIds.size;
    } catch (err) {
        console.error("Erro ao alternar favorito", err);
        showToast("Erro ao processar favorito.", "error");
    }
}

// Search Jobs Logic
async function executeSearch() {
    loadingState.classList.remove("hidden");
    emptyState.classList.add("hidden");
    jobsContainer.innerHTML = "";
    resultsTitle.textContent = "Buscando vagas em tempo real...";
    resultsCount.textContent = "...";

    // Selected sources
    const checkedSources = Array.from(document.querySelectorAll("input[name='source']:checked")).map(cb => cb.value);

    const payload = {
        query: searchQuery.value.trim(),
        location: searchLocation.value.trim(),
        sources: checkedSources.length ? checkedSources : ["remotive", "arbeitnow", "jobspy"],
        min_match: parseInt(minMatchFilter.value) || 0
    };

    try {
        const res = await fetch("/api/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Erro na busca de vagas");

        const data = await res.json();
        currentJobs = data.jobs || [];

        loadingState.classList.add("hidden");
        resultsTitle.textContent = `Vagas para "${data.query}"`;
        resultsCount.textContent = `${currentJobs.length} vagas encontradas`;

        if (currentJobs.length === 0) {
            emptyState.classList.remove("hidden");
            return;
        }

        currentJobs.forEach(job => {
            jobsContainer.appendChild(createJobCard(job));
        });
    } catch (err) {
        console.error(err);
        loadingState.classList.add("hidden");
        emptyState.classList.remove("hidden");
        showToast("Erro ao conectar com o motor de busca.", "error");
    }
}

// Search Form submit
searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    executeSearch();
});

// Filter change instant update
minMatchFilter.addEventListener("change", () => {
    if (currentJobs.length > 0) {
        executeSearch();
    }
});

// Load Favorites Tab
async function loadFavorites() {
    favoritesContainer.innerHTML = "";
    favoritesEmpty.classList.add("hidden");

    try {
        const res = await fetch("/api/favorites");
        if (!res.ok) throw new Error("Erro ao buscar favoritos");
        const data = await res.json();
        const favs = data.favorites || [];

        if (favs.length === 0) {
            favoritesEmpty.classList.remove("hidden");
            return;
        }

        favs.forEach(job => {
            favoritesContainer.appendChild(createJobCard(job, true));
        });
    } catch (err) {
        console.error(err);
        showToast("Erro ao carregar favoritos.", "error");
    }
}

// Initial Boot
document.addEventListener("DOMContentLoaded", async () => {
    await loadProfile();
    await refreshFavoritesCount();
    // Trigger initial search with default profile
    executeSearch();
});
