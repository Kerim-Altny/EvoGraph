// ── TAXONOMY CLASS COLORING ──────────────────────────────────────────
const CLASS_COLORS = {
    mammalia: { border: "#ff7b72", glow: "rgba(255,123,114,.35)" },
    aves: { border: "#79c0ff", glow: "rgba(121,192,255,.35)" },
    reptilia: { border: "#56d364", glow: "rgba(86,211,100,.35)" },
    amphibia: { border: "#d2a8ff", glow: "rgba(210,168,255,.35)" },
    actinopterygii: { border: "#ffa657", glow: "rgba(255,166,87,.35)" },
    chondrichthyes: { border: "#ffa657", glow: "rgba(255,166,87,.35)" },
    insecta: { border: "#e3b341", glow: "rgba(227,179,65,.35)" },
    arachnida: { border: "#f0883e", glow: "rgba(240,136,62,.35)" },
};

function classColor(taxonomyClass) {
    if (!taxonomyClass) return null;
    return CLASS_COLORS[taxonomyClass.toLowerCase()] ?? null;
}

// ── TAXONOMY GROUP (parent node) STYLE ───────────────────────────────────
const TAXON_STYLE = {
    shape: "dot",
    size: 14,
    color: {
        background: "#21262d", border: "#58a6ff",
        highlight: { background: "#30363d", border: "#79c0ff" }
    },
    font: { color: "#8b949e", size: 12, face: "Roboto, system-ui" },
    shadow: { enabled: true, color: "rgba(88,166,255,.2)", x: 0, y: 0, size: 12 },
};

// ── Vis.js NETWORK OPTIONS ────────────────────────────────────────────────
const NETWORK_OPTIONS = {
    layout: {
        hierarchical: {
            enabled: true,
            direction: "UD",
            sortMethod: "directed",
            levelSeparation: 150,
            nodeSpacing: 180,
            treeSpacing: 220,
            blockShifting: true,
            edgeMinimization: true,
            parentCentralization: true,
        },
    },
    physics: { enabled: false },
    nodes: {
        shape: "dot",
        size: 28,
        font: {
            color: "#e6edf3",
            size: 13,
            face: "Roboto, system-ui",
            vadjust: 4,
        },
        borderWidth: 3,
        borderWidthSelected: 4,
        shadow: { enabled: true, color: "rgba(0,0,0,.6)", x: 0, y: 4, size: 14 },
    },
    edges: {
        arrows: { to: { enabled: true, scaleFactor: .65 } },
        color: { color: "#30363d", highlight: "#58a6ff", hover: "#58a6ff" },
        width: 2.5,
        smooth: { type: "cubicBezier", forceDirection: "vertical", roundness: .45 },
    },
    interaction: {
        hover: true,
        tooltipDelay: 150,
        zoomView: true,
        dragView: true,
        navigationButtons: false,
    },
};

// ── EMOJI HELPER ───────────────────────────────────────────────────────
function emojiForAnimal(name = "") {
    const n = name.toLowerCase();
    if (["lion", "tiger", "cat", "cheetah", "leopard", "panther"].some(k => n.includes(k))) return "🦁";
    if (["dog", "wolf", "fox", "terrier", "husky", "spaniel"].some(k => n.includes(k))) return "🐺";
    if (["eagle", "hawk", "falcon", "parrot", "owl", "penguin"].some(k => n.includes(k))) return "🦅";
    if (["shark", "fish", "salmon", "tuna", "ray"].some(k => n.includes(k))) return "🦈";
    if (["snake", "gecko", "lizard", "iguana", "crocodile"].some(k => n.includes(k))) return "🐍";
    if (["elephant"].some(k => n.includes(k))) return "🐘";
    if (["whale", "dolphin", "orca"].some(k => n.includes(k))) return "🐋";
    if (["bear", "panda"].some(k => n.includes(k))) return "🐻";
    if (["horse", "zebra", "donkey"].some(k => n.includes(k))) return "🐎";
    if (["frog", "toad", "salamander"].some(k => n.includes(k))) return "🐸";
    if (["spider", "scorpion"].some(k => n.includes(k))) return "🕷";
    if (["bee", "butterfly", "beetle", "ant"].some(k => n.includes(k))) return "🦋";
    return "🐾";
}

// ── DATA → VIS.JS CONVERSION ──────────────────────────────────────────────
function buildGraphData(animals) {
    const nodes = animals.map(a => {
        const cc = classColor(a.taxonomy_class);
        const hasImage = !!a.image_url;

        let nodeStyle;

        if (hasImage) {
            nodeStyle = {
                shape: "circularImage",
                image: a.image_url,
                size: 36,
                color: {
                    border: cc ? cc.border : "#3fb950",
                    background: "#161b22",
                    highlight: { border: cc ? cc.border : "#56d364", background: "#21262d" },
                },
                shadow: cc
                    ? { enabled: true, color: cc.glow, x: 0, y: 0, size: 20 }
                    : { enabled: true, color: "rgba(63,185,80,.25)", x: 0, y: 0, size: 16 },
                font: { color: "#e6edf3", size: 13, face: "Roboto, system-ui", bold: true },
            };
        } else {
            nodeStyle = { ...TAXON_STYLE };
            if (cc) {
                nodeStyle.color = {
                    background: "#21262d",
                    border: cc.border,
                    highlight: { background: "#30363d", border: cc.border },
                };
                nodeStyle.shadow = { enabled: true, color: cc.glow, x: 0, y: 0, size: 10 };
            }
        }

        return {
            id: a.id,
            label: a.name,
            title: a.scientific_name ?? "",
            ...nodeStyle,
            _data: a,
        };
    });

    const edges = animals
        .filter(a => a.ancestor_id !== null && a.ancestor_id !== undefined)
        .map(a => ({
            from: a.ancestor_id,
            to: a.id,
            id: `e-${a.ancestor_id}-${a.id}`,
        }));

    return { nodes, edges };
}

// ── INFO PANEL ──────────────────────────────────────────────────────────
const panel = document.getElementById("info-panel");
const closeBtn = document.getElementById("close-btn");
let activePanelAnimalId = null;

function showPanel(animal) {
    activePanelAnimalId = animal.id;

    document.getElementById("panel-emoji").textContent = emojiForAnimal(animal.name);
    document.getElementById("panel-name").textContent = animal.name;
    document.getElementById("panel-sci").textContent = animal.scientific_name ?? "No scientific name";
    document.getElementById("panel-locations").textContent = animal.locations ?? "—";
    document.getElementById("panel-class").textContent = animal.taxonomy_class ?? "—";
    document.getElementById("panel-lifespan").textContent = animal.lifespan ?? "—";
    document.getElementById("panel-weight").textContent = animal.weight ?? "—";
    document.getElementById("panel-funfact").textContent =
        animal.fun_fact ?? "Not yet generated ";


    const classBadge = document.getElementById("panel-class-badge");
    if (classBadge) {
        const cc = classColor(animal.taxonomy_class);
        classBadge.style.color = cc ? cc.border : "#8b949e";
        classBadge.style.borderColor = cc ? cc.border : "#30363d";
    }


    const imgWrap = document.getElementById("panel-image-wrap");
    const img = document.getElementById("panel-image");
    if (animal.image_url) {
        img.src = animal.image_url;
        img.alt = animal.name;
        imgWrap.classList.remove("hidden");
    } else {
        img.src = "";
        imgWrap.classList.add("hidden");
    }

    panel.classList.remove("hidden");
}

function hidePanel() { panel.classList.add("hidden"); }
closeBtn.addEventListener("click", hidePanel);

// ── DELETE BUTTON ────────────────────────────────────────────────────────
const deleteBtn = document.getElementById("delete-btn");
deleteBtn.addEventListener("click", async () => {
    if (!activePanelAnimalId) return;
    const name = document.getElementById("panel-name").textContent;
    if (!confirm(`Delete "${name}"?\nDescendants will not be deleted, their links will be broken.`)) return;
    try {
        const res = await fetch(`/animals/${activePanelAnimalId}`, { method: "DELETE" });
        if (!res.ok && res.status !== 204) { alert("Delete error: " + res.status); return; }
        hidePanel();
        await init();
    } catch (err) { alert("Connection error: " + err.message); }
});

// ── MAIN INIT ─────────────────────────────────────────────────────────
const loader = document.getElementById("loader");

async function init() {
    let animals;
    try {
        const res = await fetch("/animals/");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        animals = await res.json();
    } catch (err) {
        loader.querySelector("p").textContent = "❌ Failed to fetch data: " + err.message;
        return;
    }

    const edgeCount = animals.filter(a => a.ancestor_id !== null).length;
    document.getElementById("stat-nodes").textContent = `${animals.length} species`;
    document.getElementById("stat-edges").textContent = `${edgeCount} links`;

    if (animals.length === 0) {
        loader.classList.add("done");

        const container = document.getElementById("network");
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🌱</div>
                <h2>No animals yet</h2>
                <p>Start building the evolutionary tree by adding the first animal.</p>
                <button class="add-btn" id="empty-add-btn">＋ Add First Animal</button>
            </div>`;
        document.getElementById("empty-add-btn").addEventListener("click", openModal);
        return;
    }

    const { nodes, edges } = buildGraphData(animals);
    const nodeSet = new vis.DataSet(nodes);
    const edgeSet = new vis.DataSet(edges);

    const container = document.getElementById("network");
    const network = new vis.Network(
        container,
        { nodes: nodeSet, edges: edgeSet },
        NETWORK_OPTIONS
    );

    network.on("click", ({ nodes: clicked }) => {
        if (clicked.length === 0) { hidePanel(); return; }
        const node = nodeSet.get(clicked[0]);
        if (node?._data) showPanel(node._data);
    });
    network.on("hoverNode", () => { container.style.cursor = "pointer"; });
    network.on("blurNode", () => { container.style.cursor = "default"; });

    loader.classList.add("done");
}

init();

// ── ADD ANIMAL MODAL ─────────────────────────────────────────────────────
const modalOverlay = document.getElementById("modal-overlay");
const modalClose = document.getElementById("modal-close");
const addBtn = document.getElementById("add-btn");
const animalInput = document.getElementById("animal-input");
const submitBtn = document.getElementById("modal-submit");
const modalStatus = document.getElementById("modal-status");

const openModal = () => {
    modalOverlay.classList.remove("hidden");
    animalInput.value = "";
    modalStatus.className = "modal-status hidden";
    setTimeout(() => animalInput.focus(), 80);
};
const closeModal = () => modalOverlay.classList.add("hidden");

addBtn.addEventListener("click", openModal);
modalClose.addEventListener("click", closeModal);
modalOverlay.addEventListener("click", e => { if (e.target === modalOverlay) closeModal(); });
animalInput.addEventListener("keydown", e => { if (e.key === "Enter") submitAnimal(); });
submitBtn.addEventListener("click", submitAnimal);

async function submitAnimal() {
    const name = animalInput.value.trim();
    if (!name) { animalInput.focus(); return; }

    submitBtn.disabled = true;
    submitBtn.textContent = "⏳ Adding...";
    modalStatus.className = "modal-status hidden";

    try {
        const res = await fetch("/animals/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name }),
        });
        const data = await res.json();
        if (!res.ok) {
            showModalStatus("error", `❌ Error: ${data.detail ?? "HTTP " + res.status}`);
        } else {
            showModalStatus("success", `✅ ${data.background_task_status ?? data.animal.name + " added!"}`);
            setTimeout(() => { init(); closeModal(); }, 2000);
        }
    } catch (err) {
        showModalStatus("error", `❌ Connection error: ${err.message}`);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Add";
    }
}

function showModalStatus(type, text) {
    modalStatus.className = `modal-status ${type}`;
    modalStatus.textContent = text;
}

// ── LCA (LOWEST COMMON ANCESTOR) MODAL ─────────────────────────────────────
const lcaOverlay = document.getElementById("lca-overlay");
const lcaClose = document.getElementById("lca-close");
const lcaBtn = document.getElementById("lca-btn");
const lcaSelect1 = document.getElementById("lca-select-1");
const lcaSelect2 = document.getElementById("lca-select-2");
const lcaSubmit = document.getElementById("lca-submit");
const lcaStatus = document.getElementById("lca-status");
const lcaResult = document.getElementById("lca-result");


async function populateLcaSelects() {
    const res = await fetch("/animals/");
    if (!res.ok) return;
    const all = await res.json();

    const leaves = all.filter(a => a.scientific_name);

    [lcaSelect1, lcaSelect2].forEach(sel => {
        sel.innerHTML = `<option value="">— Select —</option>`;
        leaves.forEach(a => {
            const opt = document.createElement("option");
            opt.value = a.id;
            opt.textContent = a.name;
            sel.appendChild(opt);
        });
    });
}

const openLca = async () => {
    lcaOverlay.classList.remove("hidden");
    lcaResult.classList.add("hidden");
    lcaStatus.className = "modal-status hidden";
    await populateLcaSelects();
};
const closeLca = () => lcaOverlay.classList.add("hidden");

lcaBtn.addEventListener("click", openLca);
lcaClose.addEventListener("click", closeLca);
lcaOverlay.addEventListener("click", e => { if (e.target === lcaOverlay) closeLca(); });

lcaSubmit.addEventListener("click", async () => {
    const id1 = lcaSelect1.value;
    const id2 = lcaSelect2.value;

    if (!id1 || !id2) {
        lcaStatus.className = "modal-status error";
        lcaStatus.textContent = "❌ Please select two different animals.";
        return;
    }
    if (id1 === id2) {
        lcaStatus.className = "modal-status error";
        lcaStatus.textContent = "❌ You cannot select the same animal twice.";
        return;
    }

    lcaSubmit.disabled = true;
    lcaSubmit.textContent = "⏳ Calculating...";
    lcaStatus.className = "modal-status hidden";
    lcaResult.classList.add("hidden");

    try {
        const res = await fetch(`/animals/common-ancestor?animal1_id=${id1}&animal2_id=${id2}`);
        const data = await res.json();

        if (!res.ok) {
            lcaStatus.className = "modal-status error";
            lcaStatus.textContent = `❌ ${data.detail ?? "An error occurred."}`;
        } else {
            const aca = data.common_ancestor;
            document.getElementById("lca-ancestor-name").textContent = aca.name;
            document.getElementById("lca-ancestor-sci").textContent = aca.scientific_name ?? "";
            document.getElementById("lca-dist-label-1").textContent = lcaSelect1.options[lcaSelect1.selectedIndex].text;
            document.getElementById("lca-dist-label-2").textContent = lcaSelect2.options[lcaSelect2.selectedIndex].text;
            document.getElementById("lca-dist-1").textContent = data.animal1_distance;
            document.getElementById("lca-dist-2").textContent = data.animal2_distance;
            document.getElementById("lca-dist-total").textContent = data.total_distance;
            lcaResult.classList.remove("hidden");
        }
    } catch (err) {
        lcaStatus.className = "modal-status error";
        lcaStatus.textContent = `❌ Connection error: ${err.message}`;
    } finally {
        lcaSubmit.disabled = false;
        lcaSubmit.textContent = "🔍 Find Common Ancestor";
    }
});

