const state = {
  data: { nodes: [], edges: [] },
  lang: localStorage.getItem("genshin-demo-lang") || "zh",
};

const UI_TEXT = {
  zh: {
    unknown: "\u672a\u77e5",
    themeDark: "\u591c\u95f4",
    themeLight: "\u767d\u5929",
    fileReadError: "\u6587\u4ef6\u8bfb\u53d6\u5931\u8d25\uff1a{message}",
    fileLoaded: "\u5df2\u5bfc\u5165\u6570\u636e\u6587\u4ef6",
    invalidJson: "JSON \u9700\u8981\u5305\u542b nodes \u548c edges \u6570\u7ec4",
    importPrompt: "\u8bf7\u4ece\u5de6\u4fa7\u9009\u62e9\u672c\u5730\u6570\u636e\u6587\u4ef6\u5bfc\u5165\u6570\u636e\u3002",
  },
  en: {
    unknown: "Unknown",
    themeDark: "Dark",
    themeLight: "Light",
    fileReadError: "Failed to read file: {message}",
    fileLoaded: "Data file imported",
    invalidJson: "JSON must contain nodes and edges arrays",
    importPrompt: "Select a local data file from the left panel to load the dataset.",
  },
};

function qs(selector, root = document) {
  return root.querySelector(selector);
}

function qsa(selector, root = document) {
  return [...root.querySelectorAll(selector)];
}

function getName(node, lang = state.lang) {
  const props = node?.properties || {};
  return props[`name_${lang}`] || props.name_en || node?.id || uiText("unknown", lang);
}

function getOtherName(node, lang = state.lang) {
  const next = lang === "zh" ? "en" : "zh";
  return node?.properties?.[`name_${next}`] || node?.id || "";
}

function edgeTitle(edge, lang = state.lang) {
  const props = edge?.properties || {};
  return props[`content_${lang}`] || props[`title_${lang}`] || props.content_en || props.title_en || edge?.id || "";
}

function edgeEndpoint(edge, side, lang = state.lang) {
  return edge?.properties?.[`${side}_name_${lang}`] || edge?.[`${side}_id`] || "";
}

function setupShell() {
  const root = qs(".app-shell");
  const toggle = qs("[data-sidebar-toggle]");
  const theme = qs("[data-theme-toggle]");
  const savedTheme = localStorage.getItem("genshin-demo-theme");
  const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
  document.documentElement.classList.toggle("dark", savedTheme ? savedTheme === "dark" : prefersDark);
  updateThemeButton();

  toggle?.addEventListener("click", () => {
    root?.classList.toggle("sidebar-collapsed");
  });

  theme?.addEventListener("click", () => {
    document.documentElement.classList.toggle("dark");
    localStorage.setItem("genshin-demo-theme", document.documentElement.classList.contains("dark") ? "dark" : "light");
    updateThemeButton();
  });

  function updateThemeButton() {
    const dark = document.documentElement.classList.contains("dark");
    qsa("[data-theme-icon]").forEach((item) => (item.textContent = dark ? "\u263e" : "\u2600"));
    qsa("[data-theme-label]").forEach((item) => (item.textContent = uiText(dark ? "themeDark" : "themeLight")));
  }
}

function setupFileInput(onData) {
  const input = qs("[data-file-input]");
  const label = qs("[data-file-name]");
  input?.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      normalizeData(data);
      state.data = data;
      if (label) {
        label.dataset.loadedFileName = "true";
        label.textContent = uiText("fileLoaded");
      }
      onData(data);
    } catch (error) {
      alert(formatText(uiText("fileReadError"), { message: error.message }));
    }
  });
}

function normalizeData(data) {
  if (!Array.isArray(data.nodes) || !Array.isArray(data.edges)) {
    throw new Error(uiText("invalidJson"));
  }
  data.nodes.forEach((node) => {
    node.properties = node.properties || {};
  });
  data.edges.forEach((edge) => {
    edge.properties = edge.properties || {};
  });
  return data;
}

async function boot(onData) {
  setupShell();
  setupFileInput(onData);
  const status = qs("[data-status]");
  if (status) status.textContent = uiText("importPrompt");
  onData(state.data);
}

function uiText(key, lang = state.lang) {
  return UI_TEXT[lang]?.[key] || UI_TEXT.en[key] || key;
}

function formatText(template, values = {}) {
  return String(template).replace(/\{(\w+)\}/g, (_, key) => values[key] ?? "");
}
