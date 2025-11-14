async function listTools() {
  const configInput = document.getElementById("configInput");
  const config = configInput.value.trim();

  if (!config) {
    showError("Please enter a configuration");
    return;
  }

  // Validate JSON
  try {
    JSON.parse(config);
  } catch (e) {
    showError("Invalid JSON format: " + e.message);
    return;
  }

  // Show loading
  hideAll();
  document.getElementById("loading").classList.remove("hidden");

  try {
    const response = await fetch("/api/list-tools", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ config }),
    });

    const result = await response.json();

    if (result.success) {
      displayResults(result.data);
    } else {
      showError(result.error);
    }
  } catch (error) {
    showError("Network error: " + error.message);
  }
}

function displayResults(data) {
  hideAll();

  // Update summary
  document.getElementById("serverCount").textContent = data.server_count;
  document.getElementById("toolCount").textContent = data.total_tools;

  // Build tools list
  const toolsList = document.getElementById("toolsList");
  toolsList.innerHTML = "";

  for (const [serverName, tools] of Object.entries(data.tools)) {
    const serverSection = createServerSection(serverName, tools);
    toolsList.appendChild(serverSection);
  }

  document.getElementById("results").classList.remove("hidden");
}

function createServerSection(serverName, tools) {
  const section = document.createElement("div");
  section.className = "server-section";

  const header = document.createElement("div");
  header.className = "server-header";
  header.innerHTML = `
        <span class="server-name">📦 ${serverName}</span>
        <span class="tool-count">${tools.length} tools</span>
    `;

  const toolsGrid = document.createElement("div");
  toolsGrid.className = "tools-grid";

  if (tools.length === 0) {
    toolsGrid.innerHTML = '<div class="tool-card">No tools found</div>';
  } else {
    tools.forEach((tool) => {
      const toolCard = createToolCard(tool);
      toolsGrid.appendChild(toolCard);
    });
  }

  section.appendChild(header);
  section.appendChild(toolsGrid);

  return section;
}

function createToolCard(tool) {
  const card = document.createElement("div");
  card.className = "tool-card";

  const name = document.createElement("div");
  name.className = "tool-name";
  name.textContent = tool.name || "Unknown";

  const description = document.createElement("div");
  description.className = "tool-description";
  description.textContent = tool.description || "No description";

  const params = document.createElement("div");
  params.className = "tool-params";
  params.innerHTML = formatParameters(tool.inputSchema);

  card.appendChild(name);
  card.appendChild(description);
  if (params.innerHTML) {
    card.appendChild(params);
  }

  return card;
}

function formatParameters(inputSchema) {
  if (!inputSchema || !inputSchema.properties) {
    return "";
  }

  const properties = inputSchema.properties;
  const required = inputSchema.required || [];
  const params = [];

  for (const [name, details] of Object.entries(properties)) {
    const type = details.type || "any";
    const isRequired = required.includes(name);
    const className = isRequired ? "param-badge required" : "param-badge";
    params.push(
      `<span class="${className}">${name}: ${type}${
        isRequired ? " *" : ""
      }</span>`
    );
  }

  return params.length > 0 ? params.join(" ") : "";
}

function showError(message) {
  hideAll();
  const errorBox = document.getElementById("error");
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function hideAll() {
  document.getElementById("loading").classList.add("hidden");
  document.getElementById("error").classList.add("hidden");
  document.getElementById("results").classList.add("hidden");
}

function clearConfig() {
  document.getElementById("configInput").value = "";
  hideAll();
}

function loadExample() {
  const example = {
    mcpServers: {
      playwright: {
        command: "npx",
        args: ["@playwright/mcp@latest"],
      },
    },
  };
  document.getElementById("configInput").value = JSON.stringify(
    example,
    null,
    2
  );
}
