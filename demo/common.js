const state = {
  data: { nodes: [], edges: [] },
  lang: localStorage.getItem("genshin-demo-lang") || "zh",
};

function qs(selector, root = document) {
  return root.querySelector(selector);
}

function qsa(selector, root = document) {
  return [...root.querySelectorAll(selector)];
}

function getName(node, lang = state.lang) {
  const props = node?.properties || {};
  return props[`name_${lang}`] || props.name_en || node?.id || "Unknown";
}

function getOtherName(node, lang = state.lang) {
  const next = lang === "zh" ? "en" : "zh";
  return node?.properties?.[`name_${next}`] || node?.id || "";
}

function edgeTitle(edge, lang = state.lang) {
  return edge?.properties?.[`title_${lang}`] || edge?.properties?.title_en || edge?.id || "";
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
    qsa("[data-theme-icon]").forEach((item) => (item.textContent = dark ? "☾" : "☀"));
    qsa("[data-theme-label]").forEach((item) => (item.textContent = dark ? "夜间" : "白天"));
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
      if (label) label.textContent = file.name;
      onData(data);
    } catch (error) {
      alert(`文件读取失败：${error.message}`);
    }
  });
}

function normalizeData(data) {
  if (!Array.isArray(data.nodes) || !Array.isArray(data.edges)) {
    throw new Error("JSON 需要包含 nodes 和 edges 数组");
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
  if (status) status.textContent = "请从左侧选择本地 genshin_network.json 导入数据。";
  onData(state.data);
}
