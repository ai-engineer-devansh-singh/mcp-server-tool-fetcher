// Store current config and tools globally
let currentConfig = null;
let currentTools = null;

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
      // Store config and tools for AI queries
      currentConfig = config;
      currentTools = result.data.tools;
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

// AI Chat Functions
async function sendQuery() {
  const queryInput = document.getElementById("queryInput");
  const query = queryInput.value.trim();

  if (!query) {
    return;
  }

  if (!currentConfig || !currentTools) {
    showError("Please load tools first before asking questions");
    return;
  }

  // Clear input and disable send button
  queryInput.value = "";
  const sendBtn = document.getElementById("sendQueryBtn");
  sendBtn.disabled = true;
  sendBtn.textContent = "Thinking...";

  // Add user message to chat
  addChatMessage(query, "user");

  try {
    const response = await fetch("/api/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        config: currentConfig,
        query: query,
        tools: currentTools,
      }),
    });

    const result = await response.json();

    if (result.success) {
      // Add AI response to chat
      const timing = result.elapsed_time ? ` (${result.elapsed_time}s)` : "";
      addChatMessage(result.response, "assistant", result.tool_calls, timing);
    } else {
      addChatMessage("Sorry, I encountered an error: " + result.error, "error");
    }
  } catch (error) {
    addChatMessage("Network error: " + error.message, "error");
  } finally {
    // Re-enable send button
    sendBtn.disabled = false;
    sendBtn.textContent = "Send";
  }
}

function addChatMessage(content, role, toolCalls = null, timing = "") {
  const chatMessages = document.getElementById("chatMessages");
  const messageDiv = document.createElement("div");
  messageDiv.className = `chat-message ${role}-message`;

  if (role === "user") {
    messageDiv.innerHTML = `
      <div class="message-header">You</div>
      <div class="message-content">${escapeHtml(content)}</div>
    `;
  } else if (role === "assistant") {
    let toolCallsHtml = "";
    if (toolCalls && toolCalls.length > 0) {
      toolCallsHtml = '<div class="tool-calls">';
      toolCalls.forEach((call) => {
        toolCallsHtml += `
          <div class="tool-call-item">
            <span class="tool-call-badge">🔧 ${call.server}.${call.tool}</span>
          </div>
        `;
      });
      toolCallsHtml += "</div>";
    }

    messageDiv.innerHTML = `
      <div class="message-header">AI Assistant${
        timing ? '<span class="timing">' + timing + "</span>" : ""
      }</div>
      ${toolCallsHtml}
      <div class="message-content">${escapeHtml(content)}</div>
    `;
  } else if (role === "error") {
    messageDiv.innerHTML = `
      <div class="message-header">Error</div>
      <div class="message-content">${escapeHtml(content)}</div>
    `;
  }

  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Clear server connection cache
async function clearCache() {
  try {
    const response = await fetch("/api/clear-cache", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const result = await response.json();

    if (result.success) {
      // Also clear frontend cache
      currentConfig = null;
      currentTools = null;
      hideAll();
      alert("Cache cleared! Please reload your configuration.");
    } else {
      alert("Failed to clear cache: " + result.error);
    }
  } catch (error) {
    alert("Network error: " + error.message);
  }
}

// Allow Enter key to send query
document.addEventListener("DOMContentLoaded", function () {
  const queryInput = document.getElementById("queryInput");
  if (queryInput) {
    queryInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendQuery();
      }
    });
  }
});
