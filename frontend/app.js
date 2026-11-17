// State Management
let catalog = {};
let currentProfile = {};
let favoriteJobIds = new Set();
let currentJobs = [];

// Selected state in profile
let selectedCategory = "administracao";
let selectedRoles = new Set();
let selectedSkills = new Set();
let selectedShifts = new Set(["integral"]);
let selectedContracts = new Set(["clt"]);

// DOM Elements - Search
const searchForm = document.getElementById("search-form");
const searchQuery = document.getElementById("search-query");
const searchLocation = document.getElementById("search-location");
const searchCategoryFilter = document.getElementById("search-category-filter");
const searchShiftFilter = document.getElementById("search-shift-filter");
const searchContractFilter = document.getElementById("search-contract-filter");
const minMatchFilter = document.getElementById("min-match-filter");
const strictLevelToggle = document.getElementById("strict-level-toggle");
const jobsContainer = document.getElementById("jobs-container");
const loadingState = document.getElementById("loading-state");
const emptyState = document.getElementById("empty-state");
const resultsCount = document.getElementById("results-count");
const resultsTitle = document.getElementById("results-title");

// DOM Elements - Profile
const profileForm = document.getElementById("profile-form");
const profileName = document.getElementById("profile-name");
const profileLocation = document.getElementById("profile-location");
const profileLevel = document.getElementById("profile-level");
const profileEducation = document.getElementById("profile-education");
const profileRemote = document.getElementById("profile-remote");
const profileStrictLevel = document.getElementById("profile-strict-level");

const categorySelectorGrid = document.getElementById("category-selector-grid");
const presetRolesBox = document.getElementById("preset-roles-box");
const presetSkillsBox = document.getElementById("preset-skills-box");
const customRoleInput = document.getElementById("custom-role-input");
const btnAddCustomRole = document.getElementById("btn-add-custom-role");
const customSkillInput = document.getElementById("custom-skill-input");
const btnAddCustomSkill = document.getElementById("btn-add-custom-skill");
const shiftsCheckboxGrid = document.getElementById("shifts-checkbox-grid");
const contractsCheckboxGrid = document.getElementById("contracts-checkbox-grid");

// Top bar & Summary
const navTabs = document.querySelectorAll(".nav-tab");
const tabContents = document.querySelectorAll(".tab-content");
const userStatusPill = document.getElementById("user-status-pill");
const pillName = document.getElementById("pill-name");
const pillLevel = document.getElementById("pill-level");
const favCountBadge = document.getElementById("fav-count");
const btnQuickEdit = document.getElementById("btn-quick-edit-profile");
const activeProfileSummary = document.getElementById("active-profile-summary");
const activeProfileSkills = document.getElementById("active-profile-skills");

// Favorites Elements
const favoritesContainer = document.getElementById("favorites-container");
const favoritesEmpty = document.getElementById("favorites-empty");

// Toast Notification
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

// Tab Switching
function switchTab(tabId) {
    navTabs.forEach(t => t.classList.toggle("active", t.dataset.tab === tabId));
    tabContents.forEach(c => c.classList.toggle("active", c.id === tabId));
    if (tabId === "favorites-section") loadFavorites();
}

navTabs.forEach(tab => tab.addEventListener("click", () => switchTab(tab.dataset.tab)));
if (userStatusPill) userStatusPill.addEventListener("click", () => switchTab("profile-section"));
if (btnQuickEdit) btnQuickEdit.addEventListener("click", () => switchTab("profile-section"));

// Fetch Catalog Data (Categories, Preset Roles, Skills, Shifts, Contracts)
async function fetchCatalog() {
    try {
        const res = await fetch("/api/catalog");
        if (!res.ok) throw new Error("Erro ao carregar catálogo");
        catalog = await res.json();
        renderCategoryGrid();
        renderShiftsGrid();
        renderContractsGrid();
    } catch (err) {
        console.error("Erro no catálogo:", err);
    }
}

// Render Category Selector Grid in Profile
function renderCategoryGrid() {
    categorySelectorGrid.innerHTML = "";
    const categories = catalog.categories || {};
    
    Object.keys(categories).forEach(catKey => {
        const cat = categories[catKey];
        const btn = document.createElement("div");
        btn.className = `category-card-btn ${selectedCategory === catKey ? 'active' : ''}`;
        btn.innerHTML = `
            <i class="fa-solid ${cat.icon || 'fa-briefcase'}"></i>
            <span>${cat.name}</span>
        `;
        btn.addEventListener("click", () => {
            selectedCategory = catKey;
            document.querySelectorAll(".category-card-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            // Re-render presets for this category
            renderPresetRolesAndSkills();
        });
        categorySelectorGrid.appendChild(btn);
    });
}

// Render Preset Roles & Skills Pills (LinkedIn style)
function renderPresetRolesAndSkills() {
    const catData = (catalog.categories && catalog.categories[selectedCategory]) || {};
    const rolesList = catData.roles || [];
    const skillsList = catData.skills || [];

    // Render Roles Pills
    presetRolesBox.innerHTML = "";
    rolesList.forEach(role => {
        const isSelected = selectedRoles.has(role);
        const pill = document.createElement("div");
        pill.className = `preset-pill ${isSelected ? 'active' : ''}`;
        pill.innerHTML = `<i class="fa-solid ${isSelected ? 'fa-check' : 'fa-plus'}"></i> ${role}`;
        pill.addEventListener("click", () => {
            if (selectedRoles.has(role)) {
                selectedRoles.delete(role);
                pill.classList.remove("active");
                pill.innerHTML = `<i class="fa-solid fa-plus"></i> ${role}`;
            } else {
                selectedRoles.add(role);
                pill.classList.add("active");
                pill.innerHTML = `<i class="fa-solid fa-check"></i> ${role}`;
            }
        });
        presetRolesBox.appendChild(pill);
    });

    // Also append any custom roles already in selectedRoles that are not in catalog
    selectedRoles.forEach(customRole => {
        if (!rolesList.includes(customRole)) {
            const pill = document.createElement("div");
            pill.className = "preset-pill active";
            pill.innerHTML = `<i class="fa-solid fa-check"></i> ${customRole}`;
            pill.addEventListener("click", () => {
                selectedRoles.delete(customRole);
                pill.remove();
            });
            presetRolesBox.appendChild(pill);
        }
    });

    // Render Skills Pills
    presetSkillsBox.innerHTML = "";
    skillsList.forEach(skill => {
        const isSelected = selectedSkills.has(skill);
        const pill = document.createElement("div");
        pill.className = `preset-pill ${isSelected ? 'active' : ''}`;
        pill.innerHTML = `<i class="fa-solid ${isSelected ? 'fa-check' : 'fa-plus'}"></i> ${skill}`;
        pill.addEventListener("click", () => {
            if (selectedSkills.has(skill)) {
                selectedSkills.delete(skill);
                pill.classList.remove("active");
                pill.innerHTML = `<i class="fa-solid fa-plus"></i> ${skill}`;
            } else {
                selectedSkills.add(skill);
                pill.classList.add("active");
                pill.innerHTML = `<i class="fa-solid fa-check"></i> ${skill}`;
            }
        });
        presetSkillsBox.appendChild(pill);
    });

    // Also append any custom skills already in selectedSkills
    selectedSkills.forEach(customSkill => {
        if (!skillsList.includes(customSkill)) {
            const pill = document.createElement("div");
            pill.className = "preset-pill active";
            pill.innerHTML = `<i class="fa-solid fa-check"></i> ${customSkill}`;
            pill.addEventListener("click", () => {
                selectedSkills.delete(customSkill);
                pill.remove();
            });
            presetSkillsBox.appendChild(pill);
        }
    });
}

// Add Custom Role Button
btnAddCustomRole.addEventListener("click", () => {
    const val = customRoleInput.value.trim();
    if (val && !selectedRoles.has(val)) {
        selectedRoles.add(val);
        customRoleInput.value = "";
        renderPresetRolesAndSkills();
        showToast(`Cargo "${val}" adicionado!`, "success");
    }
});

// Add Custom Skill Button
btnAddCustomSkill.addEventListener("click", () => {
    const val = customSkillInput.value.trim();
    if (val && !selectedSkills.has(val)) {
        selectedSkills.add(val);
        customSkillInput.value = "";
        renderPresetRolesAndSkills();
        showToast(`Habilidade "${val}" adicionada!`, "success");
    }
});

// Render Shifts Checkbox Grid
function renderShiftsGrid() {
    shiftsCheckboxGrid.innerHTML = "";
    const shifts = catalog.shifts || [];
    shifts.forEach(sh => {
        const isChecked = selectedShifts.has(sh.id);
        const label = document.createElement("label");
        label.className = `checkbox-pill-label ${isChecked ? 'active' : ''}`;
        label.innerHTML = `
            <input type="checkbox" value="${sh.id}" ${isChecked ? 'checked' : ''}>
            <span>${sh.name}</span>
        `;
        const cb = label.querySelector("input");
        cb.addEventListener("change", () => {
            if (cb.checked) {
                selectedShifts.add(sh.id);
                label.classList.add("active");
            } else {
                selectedShifts.delete(sh.id);
                label.classList.remove("active");
            }
        });
        shiftsCheckboxGrid.appendChild(label);
    });
}

// Render Contracts Checkbox Grid
function renderContractsGrid() {
    contractsCheckboxGrid.innerHTML = "";
    const contracts = catalog.contracts || [];
    contracts.forEach(ct => {
        const isChecked = selectedContracts.has(ct.id);
        const label = document.createElement("label");
        label.className = `checkbox-pill-label ${isChecked ? 'active' : ''}`;
        label.innerHTML = `
            <input type="checkbox" value="${ct.id}" ${isChecked ? 'checked' : ''}>
            <span>${ct.name}</span>
        `;
        const cb = label.querySelector("input");
        cb.addEventListener("change", () => {
            if (cb.checked) {
                selectedContracts.add(ct.id);
                label.classList.add("active");
            } else {
                selectedContracts.delete(ct.id);
                label.classList.remove("active");
            }
        });
        contractsCheckboxGrid.appendChild(label);
    });
}

// Load Profile Data
async function loadProfile() {
    try {
        const res = await fetch("/api/profile");
        if (!res.ok) throw new Error("Erro ao carregar perfil");
        currentProfile = await res.json();

        // Populate fields
        profileName.value = currentProfile.full_name || "Candidato";
        profileLocation.value = currentProfile.location || "Brasil";
        profileLevel.value = currentProfile.experience_level || "junior";
        profileEducation.value = currentProfile.education || "Ensino Médio Completo";
        profileRemote.checked = Boolean(currentProfile.remote_only);
        profileStrictLevel.checked = Boolean(currentProfile.strict_level_filter);
        strictLevelToggle.checked = Boolean(currentProfile.strict_level_filter);

        if (currentProfile.category) {
            selectedCategory = currentProfile.category;
            searchCategoryFilter.value = selectedCategory;
        }

        // Sets
        selectedRoles = new Set(currentProfile.roles_list || []);
        selectedSkills = new Set(currentProfile.skills_list || []);
        selectedShifts = new Set(currentProfile.shifts_list || ["integral"]);
        selectedContracts = new Set(currentProfile.contract_types_list || ["clt"]);

        // Update UI
        pillName.textContent = currentProfile.full_name || "Candidato";
        pillLevel.textContent = currentProfile.experience_level || "Júnior";

        renderCategoryGrid();
        renderPresetRolesAndSkills();
        renderShiftsGrid();
        renderContractsGrid();
        updateActiveSummary();

        // Default search placeholder
        if (currentProfile.roles_list && currentProfile.roles_list.length > 0) {
            searchQuery.placeholder = `Ex: ${currentProfile.roles_list[0]}`;
        }
    } catch (err) {
        console.error(err);
    }
}

// Update Active Summary Alert in Search Section
function updateActiveSummary() {
    const rolesStr = Array.from(selectedRoles).slice(0, 2).join(", ") || "Todos os cargos";
    const levelStr = profileLevel.options[profileLevel.selectedIndex]?.text || "Júnior";
    const shiftsStr = Array.from(selectedShifts).join(", ") || "Integral";
    activeProfileSummary.textContent = `${rolesStr} | ${levelStr} | Turnos: ${shiftsStr}`;

    activeProfileSkills.innerHTML = "";
    selectedSkills.forEach(s => {
        const tag = document.createElement("span");
        tag.className = "skill-tag matched";
        tag.textContent = s;
        activeProfileSkills.appendChild(tag);
    });
}

// Save Profile Submit
profileForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
        full_name: profileName.value.trim(),
        category: selectedCategory,
        desired_roles: Array.from(selectedRoles).join(", "),
        skills: Array.from(selectedSkills).join(", "),
        experience_level: profileLevel.value,
        shifts: Array.from(selectedShifts).join(", "),
        contract_types: Array.from(selectedContracts).join(", "),
        strict_level_filter: profileStrictLevel.checked,
        education: profileEducation.value,
        location: profileLocation.value.trim(),
        remote_only: profileRemote.checked
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
        strictLevelToggle.checked = Boolean(currentProfile.strict_level_filter);
        searchCategoryFilter.value = selectedCategory;

        updateActiveSummary();
        showToast("Perfil e preferências salvas com sucesso no SQLite!", "success");
        switchTab("search-section");
        executeSearch();
    } catch (err) {
        console.error(err);
        showToast("Erro ao salvar perfil.", "error");
    }
});

// Format Shift Name with nice icon
function getShiftBadge(shiftId) {
    const map = {
        "manha": { text: "Manhã", icon: "fa-sun" },
        "tarde": { text: "Tarde", icon: "fa-cloud-sun" },
        "noite": { text: "Noturno", icon: "fa-moon" },
        "integral": { text: "Integral (8h)", icon: "fa-clock" },
        "escala": { text: "Escala 12x36/6x1", icon: "fa-calendar-days" },
        "flexivel": { text: "Flexível", icon: "fa-arrows-rotate" }
    };
    const s = map[shiftId] || { text: "Integral", icon: "fa-clock" };
    return `<span class="badge badge-shift"><i class="fa-solid ${s.icon}"></i> ${s.text}</span>`;
}

// Format Contract Name with nice icon
function getContractBadge(contractId) {
    const map = {
        "aprendiz": { text: "Menor / Jovem Aprendiz", icon: "fa-graduation-cap" },
        "estagio": { text: "Estágio", icon: "fa-book-open" },
        "clt": { text: "CLT (Efetivo)", icon: "fa-id-card" },
        "pj": { text: "PJ", icon: "fa-briefcase" },
        "temporario": { text: "Temporário", icon: "fa-hourglass-half" }
    };
    const c = map[contractId] || { text: "CLT", icon: "fa-id-card" };
    return `<span class="badge badge-contract"><i class="fa-solid ${c.icon}"></i> ${c.text}</span>`;
}

// Render Job Card
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
                    <span class="badge badge-site"><i class="fa-solid fa-globe"></i> ${job.site || "Web"}</span>
                    <span class="badge badge-location"><i class="fa-solid fa-location-dot"></i> ${job.location || "Brasil"}</span>
                    ${getShiftBadge(job.detected_shift || job.shift)}
                    ${getContractBadge(job.detected_contract || job.contract_type)}
                    ${job.salary && job.salary !== 'Não divulgado' ? `<span class="badge badge-salary"><i class="fa-solid fa-money-bill-wave"></i> ${job.salary}</span>` : ''}
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
                ${missingPills ? `<div><strong>Faltantes do perfil:</strong> ${missingPills}</div>` : ''}
            </div>
        </div>

        <p class="job-desc-snippet">${job.description || "Sem descrição disponível."}</p>

        <div class="job-actions">
            <span style="font-size: 0.75rem; color: var(--text-muted);">Publicado: ${job.date_posted || "Recente"}</span>
            <a href="${job.url || '#'}" target="_blank" rel="noopener noreferrer" class="btn-secondary">
                Ver Vaga Completa <i class="fa-solid fa-arrow-up-right-from-square"></i>
            </a>
        </div>
    `;

    // Favorite Button Handler
    const favBtn = card.querySelector(".btn-fav");
    favBtn.addEventListener("click", () => toggleFavorite(job, favBtn, isFavoriteView, card));

    return card;
}

// Toggle Favorite Logic
async function toggleFavorite(job, button, isFavoriteView, cardElement) {
    const jobId = String(job.id || job.job_id);
    const isCurrentlyFav = favoriteJobIds.has(jobId);

    try {
        if (isCurrentlyFav) {
            const res = await fetch(`/api/favorites/${jobId}`, { method: "DELETE" });
            if (res.ok) {
                favoriteJobIds.delete(jobId);
                button.classList.remove("saved");
                button.querySelector("i").className = "fa-regular fa-bookmark";
                button.querySelector("span").textContent = "Favoritar";
                showToast("Vaga removida dos favoritos.", "info");
                if (isFavoriteView) {
                    cardElement.remove();
                    if (favoriteJobIds.size === 0) favoritesEmpty.classList.remove("hidden");
                }
            }
        } else {
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
                showToast("Vaga salva nos favoritos!", "success");
            }
        }
        favCountBadge.textContent = favoriteJobIds.size;
    } catch (err) {
        console.error("Erro favorito:", err);
    }
}

// Execute Job Search
async function executeSearch() {
    loadingState.classList.remove("hidden");
    emptyState.classList.add("hidden");
    jobsContainer.innerHTML = "";
    resultsTitle.textContent = "Buscando vagas em tempo real...";
    resultsCount.textContent = "...";

    const checkedSources = Array.from(document.querySelectorAll("input[name='source']:checked")).map(cb => cb.value);

    const payload = {
        query: searchQuery.value.trim(),
        location: searchLocation.value.trim(),
        category: searchCategoryFilter.value,
        shift: searchShiftFilter.value,
        contract: searchContractFilter.value,
        strict_level: strictLevelToggle.checked,
        sources: checkedSources.length ? checkedSources : ["jobspy"],
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

// Real-time filter changes
[searchCategoryFilter, searchShiftFilter, searchContractFilter, minMatchFilter, strictLevelToggle].forEach(el => {
    el.addEventListener("change", () => {
        executeSearch();
    });
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

        favCountBadge.textContent = favs.length;
        favoriteJobIds = new Set(favs.map(f => String(f.job_id)));

        if (favs.length === 0) {
            favoritesEmpty.classList.remove("hidden");
            return;
        }

        favs.forEach(job => {
            favoritesContainer.appendChild(createJobCard(job, true));
        });
    } catch (err) {
        console.error(err);
    }
}

// Initial Boot
document.addEventListener("DOMContentLoaded", async () => {
    await fetchCatalog();
    await loadProfile();
    await loadFavorites();
    executeSearch();
});
