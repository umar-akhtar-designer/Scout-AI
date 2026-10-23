/* ============================================================
   ScoutAI frontend logic
   Chat flow -> /api/run -> SSE stream -> rendered report
   ============================================================ */

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const el = {
    html: document.documentElement,
    stage: $("#stage"),
    messages: $("#messages"),
    empty: $("#empty"),
    composer: $("#composer"),
    prompt: $("#prompt"),
    sendBtn: $("#sendBtn"),
    attachBtn: $("#attachBtn"),
    fileInput: $("#fileInput"),
    attachments: $("#attachments"),
    demoBanner: $("#demoBanner"),
    demoBannerText: $("#demoBannerText"),
    demoBannerClose: $("#demoBannerClose"),
    suggestions: $("#suggestions"),
    modelSelect: $("#modelSelect"),
    modelPillLabel: $("#modelPillLabel"),
    themeToggle: $("#themeToggle"),
    iconMoon: $("#iconMoon"),
    iconSun: $("#iconSun"),
    newChat: $("#newChat"),
    sidebar: $("#sidebar"),
    sidebarClose: $("#sidebarClose"),
    sidebarBackdrop: $("#sidebarBackdrop"),
    menuBtn: $("#menuBtn"),
    profileBtn: $("#profileBtn"),
    profileMenu: $("#profileMenu"),
    profileName: $("#profileName"),
    avatar: $("#avatar"),
    avatarInput: $("#avatarInput"),
    settingsBackdrop: $("#settingsBackdrop"),
    settingsClose: $("#settingsClose"),
    settingsCancel: $("#settingsCancel"),
    settingsSave: $("#settingsSave"),
    settingsName: $("#settingsName"),
    settingsPhotoBtn: $("#settingsPhotoBtn"),
    settingsRemovePhoto: $("#settingsRemovePhoto"),
    settingsAvatar: $("#settingsAvatar"),
    themeSegment: $("#themeSegment"),
    settingsModel: $("#settingsModel"),
};

const STEP_NAMES = ["Plan", "Search", "Extract", "Verify", "Write"];
const MODEL_LABELS = {
    "nemotron-nano": "Nemotron Nano",
    "nemotron-super": "Nemotron Super",
    "nemotron-ultra": "Nemotron Ultra",
};

/* ---------------- theme ---------------- */
function applyTheme(pref) {
    const theme = pref === "system" ? (prefersDark ? "dark" : "light") : pref;
    if (theme === "dark") {
        el.html.setAttribute("data-theme", "dark");
        el.iconMoon.style.display = "none";
        el.iconSun.style.display = "block";
    } else {
        el.html.removeAttribute("data-theme");
        el.iconMoon.style.display = "block";
        el.iconSun.style.display = "none";
    }
}
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
const savedTheme = localStorage.getItem("scoutai-theme") || "system";
applyTheme(savedTheme);

el.themeToggle.addEventListener("click", () => {
    const next = el.html.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(next);
    localStorage.setItem("scoutai-theme", next);
});

/* ---------------- sidebar (mobile) ---------------- */
function openSidebar() {
    el.sidebar.classList.add("open");
}
function closeSidebar() {
    el.sidebar.classList.remove("open");
}
el.menuBtn.addEventListener("click", openSidebar);
el.sidebarClose.addEventListener("click", closeSidebar);
el.sidebarBackdrop.addEventListener("click", closeSidebar);

/* ---------------- model selector ---------------- */
function syncModelLabel() {
    el.modelPillLabel.textContent = MODEL_LABELS[el.modelSelect.value] || el.modelSelect.value;
}
el.modelSelect.addEventListener("change", () => {
    syncModelLabel();
    localStorage.setItem("scoutai-model", el.modelSelect.value);
});

/* ---------------- profile + settings ---------------- */
const DEFAULT_PROFILE = { name: "Umar Akhtar", avatar: null };
let profile = loadProfile();

function loadProfile() {
    try {
        return { ...DEFAULT_PROFILE, ...JSON.parse(localStorage.getItem("scoutai-profile") || "{}") };
    } catch {
        return { ...DEFAULT_PROFILE };
    }
}
function saveProfile() {
    localStorage.setItem("scoutai-profile", JSON.stringify(profile));
}
function initialOf(name) {
    const parts = String(name || "").trim().split(/\s+/).filter(Boolean);
    const first = (parts[0] || "U")[0] || "U";
    const second = parts[1] ? parts[1][0] : "";
    return (first + second).toUpperCase();
}
function applyProfile() {
    const name = profile.name || "Guest";
    el.profileName.textContent = name;
    const initial = escapeHtml(initialOf(name));
    if (profile.avatar) {
        el.avatar.innerHTML = `<img src="${profile.avatar}" alt="">`;
        el.settingsAvatar.innerHTML = `<img src="${profile.avatar}" alt="">`;
    } else {
        el.avatar.innerHTML = `<span>${initial}</span>`;
        el.settingsAvatar.innerHTML = `<span>${initial}</span>`;
    }
}

function openProfileMenu() {
    el.profileMenu.hidden = false;
    el.profileBtn.setAttribute("aria-expanded", "true");
}
function closeProfileMenu() {
    el.profileMenu.hidden = true;
    el.profileBtn.setAttribute("aria-expanded", "false");
}
el.profileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    if (el.profileMenu.hidden) openProfileMenu();
    else closeProfileMenu();
});
document.addEventListener("click", (e) => {
    if (!el.profileMenu.hidden && !e.target.closest(".profile-wrap")) closeProfileMenu();
});

el.profileMenu.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const action = btn.dataset.action;
    closeProfileMenu();
    if (action === "settings") openSettings();
    else if (action === "photo") el.avatarInput.click();
    else if (action === "name") {
        openSettings();
        setTimeout(() => el.settingsName.focus(), 60);
    } else if (action === "logout") logout();
});

function openSettings() {
    el.settingsName.value = profile.name || "";
    el.settingsModel.value = el.modelSelect.value;
    const themePref = localStorage.getItem("scoutai-theme") || "system";
    $$("#themeSegment button").forEach((b) => {
        b.classList.toggle("active", b.dataset.themeValue === themePref);
    });
    applyProfile();
    el.settingsBackdrop.hidden = false;
    setTimeout(() => el.settingsName.focus(), 60);
}
function closeSettings() {
    el.settingsBackdrop.hidden = true;
}
el.settingsClose.addEventListener("click", closeSettings);
el.settingsCancel.addEventListener("click", closeSettings);
el.settingsBackdrop.addEventListener("click", (e) => {
    if (e.target === el.settingsBackdrop) closeSettings();
});
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        closeSettings();
        closeProfileMenu();
    }
});

el.themeSegment.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-theme-value]");
    if (!btn) return;
    $$("#themeSegment button").forEach((b) => b.classList.toggle("active", b === btn));
});

function handleAvatarFile(file) {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
        toast("Please choose an image file");
        return;
    }
    if (file.size > 2.5 * 1024 * 1024) {
        toast("Image is larger than 2.5 MB");
        return;
    }
    const reader = new FileReader();
    reader.onload = () => {
        profile.avatar = reader.result;
        saveProfile();
        applyProfile();
        toast("Profile photo updated");
    };
    reader.readAsDataURL(file);
}
el.avatarInput.addEventListener("change", () => {
    handleAvatarFile(el.avatarInput.files[0]);
    el.avatarInput.value = "";
});
el.settingsPhotoBtn.addEventListener("click", () => el.avatarInput.click());
el.settingsRemovePhoto.addEventListener("click", () => {
    profile.avatar = null;
    saveProfile();
    applyProfile();
    toast("Profile photo removed");
});

el.settingsSave.addEventListener("click", () => {
    const newName = el.settingsName.value.trim();
    profile.name = (newName || "Guest").slice(0, 40);
    saveProfile();
    applyProfile();

    const activeTheme = $("#themeSegment button.active");
    const themePref = activeTheme ? activeTheme.dataset.themeValue : "system";
    applyTheme(themePref);
    localStorage.setItem("scoutai-theme", themePref);

    el.modelSelect.value = el.settingsModel.value;
    syncModelLabel();
    localStorage.setItem("scoutai-model", el.modelSelect.value);

    closeSettings();
    toast("Settings saved");
});

function logout() {
    const ok = window.confirm("Log out? This clears your local profile, theme, and chat on this device.");
    if (!ok) return;
    localStorage.removeItem("scoutai-profile");
    localStorage.removeItem("scoutai-theme");
    localStorage.removeItem("scoutai-model");
    localStorage.removeItem("scoutai-chat");
    location.reload();
}

/* ---------------- attachments ---------------- */
const attachments = [];
const MAX_FILE_BYTES = 1.5 * 1024 * 1024;
const MAX_CONTEXT_CHARS = 24000;
const TEXT_FILE_RE = /\.(txt|md|markdown|csv|tsv|json|log|html?|xml|ya?ml)$/i;

let toastTimer;
function toast(message) {
    let node = $(".toast");
    if (!node) {
        node = document.createElement("div");
        node.className = "toast";
        document.body.appendChild(node);
    }
    node.textContent = message;
    node.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => node.classList.remove("show"), 2800);
}

function humanSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function renderAttachments() {
    el.attachments.innerHTML = "";
    if (!attachments.length) {
        el.attachments.hidden = true;
        return;
    }
    el.attachments.hidden = false;

    attachments.forEach((file, index) => {
        const chip = document.createElement("span");
        chip.className = "attach-chip";

        const name = document.createElement("span");
        name.className = "fname";
        name.textContent = file.name;

        const size = document.createElement("span");
        size.className = "fsize";
        size.textContent = humanSize(file.size);

        const remove = document.createElement("button");
        remove.type = "button";
        remove.className = "attach-remove";
        remove.setAttribute("aria-label", `Remove ${file.name}`);
        remove.innerHTML = '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>';
        remove.addEventListener("click", () => {
            attachments.splice(index, 1);
            renderAttachments();
            syncSendState();
            el.prompt.focus();
        });

        chip.append(name, size, remove);
        el.attachments.appendChild(chip);
    });
}

const MAX_BINARY_BYTES = 12 * 1024 * 1024;
const BINARY_FILE_RE = /\.(pdf|docx|png|jpe?g|webp|gif)$/i;

async function extractBinaryFile(file) {
    const body = new FormData();
    body.append("file", file, file.name);
    const res = await fetch("/api/extract-file", { method: "POST", body });
    if (!res.ok) {
        let detail = "";
        try { detail = (await res.json()).detail || ""; } catch {}
        throw new Error(detail || `could not read file (${res.status})`);
    }
    const data = await res.json();
    return { name: data.name || file.name, text: (data.text || "").trim() };
}

async function handleFiles(fileList) {
    const files = [...fileList];
    let added = 0;

    for (const file of files) {
        const isBinary = BINARY_FILE_RE.test(file.name)
            || (file.type && (file.type.startsWith("image/") || file.type === "application/pdf"));

        if (isBinary) {
            if (file.size > MAX_BINARY_BYTES) {
                toast(`${file.name} is larger than 12 MB`);
                continue;
            }
            toast(`Reading ${file.name}…`);
            try {
                const { name, text } = await extractBinaryFile(file);
                if (!text) {
                    toast(`${name}: no readable text found`);
                    continue;
                }
                attachments.push({ name, size: file.size, content: text });
                added += 1;
            } catch (err) {
                toast(`${file.name}: ${err.message || "could not read file"}`);
            }
            continue;
        }

        const looksText = TEXT_FILE_RE.test(file.name) || (file.type && file.type.startsWith("text"));
        if (!looksText) {
            toast(`${file.name}: unsupported file type`);
            continue;
        }
        if (file.size > MAX_FILE_BYTES) {
            toast(`${file.name} is larger than 1.5 MB`);
            continue;
        }
        try {
            const content = await file.text();
            attachments.push({ name: file.name, size: file.size, content });
            added += 1;
        } catch {
            toast(`Could not read ${file.name}`);
        }
    }

    if (added) {
        renderAttachments();
        syncSendState();
        el.prompt.focus();
    }
}

el.attachBtn.addEventListener("click", () => {
    el.attachBtn.animate(
        [{ transform: "rotate(0)" }, { transform: "rotate(-14deg)" }, { transform: "rotate(0)" }],
        { duration: 260, easing: "ease" }
    );
    el.fileInput.click();
});

el.fileInput.addEventListener("change", () => {
    handleFiles(el.fileInput.files);
    el.fileInput.value = "";
});

["dragenter", "dragover"].forEach((type) => {
    el.composer.addEventListener(type, (e) => {
        e.preventDefault();
        el.composer.classList.add("dragover");
    });
});
["dragleave", "dragend", "drop"].forEach((type) => {
    el.composer.addEventListener(type, (e) => {
        e.preventDefault();
        if (type === "dragleave" && el.composer.contains(e.relatedTarget)) return;
        el.composer.classList.remove("dragover");
    });
});
el.composer.addEventListener("drop", (e) => {
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length) {
        handleFiles(e.dataTransfer.files);
    }
});

function clearAttachments() {
    attachments.length = 0;
    renderAttachments();
}

function withAttachmentContext(question) {
    if (!attachments.length) return question;
    let budget = MAX_CONTEXT_CHARS;
    const blocks = [];
    for (const file of attachments) {
        if (budget <= 0) break;
        const slice = file.content.slice(0, budget);
        budget -= slice.length;
        blocks.push(`--- FILE: ${file.name} ---\n${slice}`);
    }
    return `${question}\n\nAttached reference material (use it to inform the research):\n\n${blocks.join("\n\n")}`;
}

/* ---------------- demo / status banner ---------------- */
async function loadStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();
        if (!data.demo) {
            el.demoBanner.hidden = true;
            return;
        }
        if (sessionStorage.getItem("scoutai-demo-dismissed") === "1") return;
        el.demoBanner.hidden = false;
        el.demoBannerText.textContent = data.missing && data.missing.length
            ? `Demo mode — missing ${data.missing.join(", ")}. Add them to .env to enable live research.`
            : "Demo mode — add API keys to enable live research.";
    } catch { /* status is optional */ }
}
el.demoBannerClose.addEventListener("click", () => {
    el.demoBanner.hidden = true;
    sessionStorage.setItem("scoutai-demo-dismissed", "1");
});

/* ---------------- composer behaviour ---------------- */
function autosize() {
    el.prompt.style.height = "auto";
    el.prompt.style.height = Math.min(el.prompt.scrollHeight, 200) + "px";
}
function syncSendState() {
    el.sendBtn.disabled = el.prompt.value.trim().length === 0 && attachments.length === 0;
}
el.prompt.addEventListener("input", () => {
    autosize();
    syncSendState();
});
el.prompt.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        submitPrompt();
    }
});

el.composer.addEventListener("submit", (e) => {
    e.preventDefault();
    submitPrompt();
});

$$(".suggestion").forEach((btn) => {
    btn.addEventListener("click", () => {
        el.prompt.value = btn.dataset.q;
        autosize();
        syncSendState();
        submitPrompt();
    });
});

/* ---------------- chat rendering ---------------- */
function enterChatMode() {
    el.stage.classList.remove("is-empty");
}

function scrollToBottom() {
    el.messages.scrollTop = el.messages.scrollHeight;
}

function addUserMessage(text, files = []) {
    const wrap = document.createElement("div");
    wrap.className = "msg user";

    const stack = document.createElement("div");
    stack.className = "user-stack";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;
    stack.appendChild(bubble);

    if (files.length) {
        const list = document.createElement("div");
        list.className = "bubble-files";
        files.forEach((file) => {
            const chip = document.createElement("span");
            chip.className = "bubble-file";
            chip.textContent = file.name;
            list.appendChild(chip);
        });
        stack.appendChild(list);
    }

    wrap.appendChild(stack);
    el.messages.appendChild(wrap);
    scrollToBottom();
}

function addAssistantMessage(text) {
    const wrap = document.createElement("div");
    wrap.className = "msg assistant";

    const mark = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    mark.setAttribute("class", "mark");
    mark.setAttribute("viewBox", "0 0 32 32");
    mark.innerHTML = '<use href="#brand-mark"/>';

    const content = document.createElement("div");
    content.className = "content";

    const answer = document.createElement("div");
    answer.className = "answer";
    answer.innerHTML = formatReport(text);

    content.appendChild(answer);
    wrap.appendChild(mark);
    wrap.appendChild(content);
    el.messages.appendChild(wrap);
    scrollToBottom();
}

function addAssistantShell() {
    const wrap = document.createElement("div");
    wrap.className = "msg assistant";

    const mark = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    mark.setAttribute("class", "mark");
    mark.setAttribute("viewBox", "0 0 32 32");
    mark.innerHTML = '<use href="#brand-mark"/>';

    const content = document.createElement("div");
    content.className = "content";

    const status = document.createElement("div");
    status.className = "status-card";
    status.innerHTML = '<div class="status-steps"></div>';

    const answer = document.createElement("div");
    answer.className = "answer";
    answer.innerHTML = '<div class="typing"><i></i><i></i><i></i></div>';

    content.appendChild(status);
    content.appendChild(answer);
    wrap.appendChild(mark);
    wrap.appendChild(content);
    el.messages.appendChild(wrap);
    scrollToBottom();

    return { wrap, status, answer };
}

function renderStatusSteps(statusEl, currentIndex, done = false) {
    const holder = statusEl.querySelector(".status-steps");
    holder.innerHTML = "";
    STEP_NAMES.forEach((name, i) => {
        const chip = document.createElement("span");
        chip.className = "pstep";
        if (done || i < currentIndex) chip.classList.add("done");
        else if (i === currentIndex) chip.classList.add("active");
        chip.innerHTML = `<span class="dot"></span>${name}`;
        holder.appendChild(chip);
    });
}

/* ---------------- report formatting (lightweight markdown) ---------------- */
function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}
function inlineFormat(s) {
    let out = escapeHtml(s);
    out = out.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    out = out.replace(/\*(.+?)\*/g, "<em>$1</em>");
    out = out.replace(/(https?:\/\/[^\s<)]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    return out;
}
function formatReport(text) {
    const lines = String(text).split(/\r?\n/);
    let html = "";
    let listType = null;
    const closeList = () => {
        if (listType) {
            html += `</${listType}>`;
            listType = null;
        }
    };

    for (const raw of lines) {
        const line = raw.trim();
        if (!line) {
            closeList();
            continue;
        }

        let m;
        if ((m = line.match(/^#{1,6}\s+(.*)$/))) {
            closeList();
            html += `<h4>${inlineFormat(m[1])}</h4>`;
            continue;
        }

        if ((m = line.match(/^([A-Z][A-Z0-9 &/\-]{2,}):\s*(.*)$/)) && (m[1].includes(" ") || m[1].length >= 5)) {
            closeList();
            html += `<h4>${inlineFormat(m[1])}</h4>`;
            if (m[2]) html += `<p>${inlineFormat(m[2])}</p>`;
            continue;
        }

        if ((m = line.match(/^[-*]\s+(.*)$/))) {
            if (listType !== "ul") { closeList(); html += "<ul>"; listType = "ul"; }
            html += `<li>${inlineFormat(m[1])}</li>`;
            continue;
        }

        if ((m = line.match(/^\d+[.)]\s+(.*)$/))) {
            if (listType !== "ol") { closeList(); html += "<ol>"; listType = "ol"; }
            html += `<li>${inlineFormat(m[1])}</li>`;
            continue;
        }

        closeList();
        html += `<p>${inlineFormat(line)}</p>`;
    }
    closeList();
    return html;
}

/* ---------------- pipeline run ---------------- */
let activeRun = null;

/* ---------------- small talk (answered directly, no research) ---------------- */
function conversationalReply(text) {
    const q = text.trim();
    const lower = q.toLowerCase();
    if (!q || q.length > 90) return null;

    if (/\b(what('?s| is)?\s+your\s+name|who are you|what are you)\b/.test(lower)) {
        return "Hi! I'm **ScoutAI**, a multi-model deep research assistant. I run a 5-step pipeline — plan, search, extract, verify, write — using NVIDIA Nemotron models plus live web search, then return a cited brief.\n\nAsk me something like *What are the latest trends in AI governance?* and I'll get to work.";
    }
    if (/^(hi|hello|hey|yo|hiya|howdy|good (morning|afternoon|evening))\b/.test(lower)) {
        return "Hi! I'm **ScoutAI**. What would you like me to research? I can dig into markets, technologies, companies, or policy and return a cited brief.";
    }
    if (/^(how are you|how'?s it going|what'?s up)\b/.test(lower)) {
        return "I'm running well, thanks for asking. Ready when you are — what should I research?";
    }
    if (/(what can you do|how do you work|what is scoutai|^help$|help me get started)/.test(lower)) {
        return "ScoutAI turns a question into a researched brief. It plans sub-questions, searches the web, extracts facts, verifies claims across sources, and writes a report with citations.\n\nTry: *Compare EV battery technologies* or *What's the current market size of cloud computing?*";
    }
    if (/^(thanks|thank you|thx|cheers)\b/.test(lower)) {
        return "You're welcome! Want me to dig into anything else?";
    }
    if (/^(bye|goodbye|see you|good night)\b/.test(lower)) {
        return "Goodbye! Come back whenever you have a question worth researching.";
    }
    if (/^(ok|okay|cool|nice|great|got it)\b/.test(lower) && q.length < 20) {
        return "Sounds good. Send a research question whenever you're ready.";
    }
    return null;
}

function submitPrompt() {
    const typed = el.prompt.value.trim();
    if (!typed && attachments.length === 0) return;

    const text = typed || "Summarize and analyze the attached material.";
    const files = attachments.map((f) => ({ name: f.name, size: f.size }));
    const question = withAttachmentContext(text);
    const direct = attachments.length === 0 ? conversationalReply(text) : null;

    el.prompt.value = "";
    autosize();
    syncSendState();

    enterChatMode();
    addUserMessage(text, files);
    clearAttachments();

    if (direct) {
        addAssistantMessage(direct);
        return;
    }

    const shell = addAssistantShell();
    let step = 0;
    renderStatusSteps(shell.status, step);

    // gentle visual progression while waiting for real events
    const ticker = setInterval(() => {
        step = Math.min(step + 1, STEP_NAMES.length - 1);
        renderStatusSteps(shell.status, step);
    }, 1300);

    runPipeline(question, shell, ticker, text);
}

async function runPipeline(question, shell, ticker, demoQuestion) {
    let finished = false;

    const finish = (reportText, note) => {
        if (finished) return;
        finished = true;
        clearInterval(ticker);
        renderStatusSteps(shell.status, STEP_NAMES.length, true);
        setTimeout(() => {
            shell.status.style.transition = "opacity .3s ease";
            shell.status.style.opacity = "0.55";
        }, 600);

        const body = reportText && reportText.trim()
            ? formatReport(reportText)
            : `<p>No report content was returned. ${note || ""}</p>`;
        shell.answer.innerHTML = body;
        scrollToBottom();
    };

    const fallbackToDemo = async (note) => {
        try {
            const res = await fetch("/api/demo", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: demoQuestion || question, model: el.modelSelect.value }),
            });
            if (!res.ok) throw new Error("demo failed");
            const data = await res.json();
            finish(data.report, note);
        } catch {
            finish("", note || "The research service is unavailable right now.");
        }
    };

    let runId;
    try {
        const res = await fetch("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question, model: el.modelSelect.value }),
        });
        if (!res.ok) throw new Error("run failed");
        const data = await res.json();
        runId = data.run_id;
        if (!runId) throw new Error("no run id");
    } catch {
        fallbackToDemo("Showing a demo report while live research is unavailable.");
        return;
    }

    // Stream results over fetch so we fully control errors/aborts
    const ctrl = new AbortController();
    const safety = setTimeout(() => {
        if (!finished) {
            ctrl.abort();
            fallbackToDemo("Live research timed out — showing a demo report.");
        }
    }, 315000);

    const onEvent = (msg) => {
        clearInterval(ticker);
        if (msg.type === "progress") {
            const stepName = String((msg.data && msg.data.step) || "").toLowerCase();
            const idx = STEP_NAMES.findIndex((s) => s.toLowerCase() === stepName);
            const done = msg.data && msg.data.status === "done";
            const current = idx >= 0 ? (done ? idx + 1 : idx) : 0;
            renderStatusSteps(shell.status, current);
        } else if (msg.type === "complete") {
            clearTimeout(safety);
            const report = msg.data && msg.data.report;
            if (report && report.trim()) finish(report);
            else fallbackToDemo("Live run finished without content — showing a demo report.");
        } else if (msg.type === "error") {
            clearTimeout(safety);
            fallbackToDemo("The research run reported an error — showing a demo report.");
        }
    };

    try {
        await streamSse(`/sse/${encodeURIComponent(runId)}`, onEvent, ctrl.signal);
        if (!finished) {
            clearTimeout(safety);
            fallbackToDemo("The research stream ended before a report was ready — showing a demo report.");
        }
    } catch {
        if (!finished) {
            clearTimeout(safety);
            fallbackToDemo("Lost connection to the research stream — showing a demo report.");
        }
    }
}

async function streamSse(url, onEvent, signal) {
    const res = await fetch(url, {
        signal,
        headers: { Accept: "text/event-stream" },
    });
    if (!res.ok || !res.body) throw new Error(`stream ${res.status}`);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true }).replace(/\r/g, "");

        let idx;
        while ((idx = buffer.indexOf("\n\n")) !== -1) {
            const chunk = buffer.slice(0, idx);
            buffer = buffer.slice(idx + 2);
            for (const line of chunk.split("\n")) {
                if (line.startsWith("data:")) {
                    const data = line.slice(5).trim();
                    if (!data) continue;
                    try { onEvent(JSON.parse(data)); } catch {}
                }
            }
        }
    }
}

/* ---------------- new chat ---------------- */
function resetChat() {
    activeRun = null;
    el.messages.innerHTML = "";
    el.stage.classList.add("is-empty");
    el.prompt.value = "";
    autosize();
    syncSendState();
    el.prompt.focus();
    closeSidebar();
}
el.newChat.addEventListener("click", resetChat);

/* ---------------- init ---------------- */
autosize();
syncSendState();
loadStatus();
applyProfile();
const savedModel = localStorage.getItem("scoutai-model");
if (savedModel && MODEL_LABELS[savedModel]) {
    el.modelSelect.value = savedModel;
    syncModelLabel();
}
el.prompt.focus();
