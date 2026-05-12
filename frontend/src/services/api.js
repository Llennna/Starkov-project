const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://starkov-project.onrender.com/api';

const JSON_HEADERS = {
  "Content-Type": "application/json",
};

async function request(path, options = {}) {
  const fullPath = `${API_BASE_URL}${path}`;
  
  const response = await fetch(fullPath, {
    ...options,
    headers: {
      ...JSON_HEADERS,
      ...(options.headers ?? {}),
    },
  });

  if (response.status === 204) {
    return null;
  }

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    const detail = payload?.detail || payload?.message || "Ошибка запроса.";
    throw new Error(detail);
  }

  return payload;
}

export function getPortfolio() {
  return request("/public/portfolio", { method: "GET" });  // ← убрал /api
}

export function sendMessage(data) {
  return request("/public/messages", {  // ← убрал /api
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function login(data) {
  return request("/admin/login", {  // ← убрал /api
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getAdminProjects(token) {
  return request("/admin/projects", {  // ← убрал /api
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function createProject(token, data) {
  return request("/admin/projects", {  // ← убрал /api
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
}

export function updateProject(token, id, data) {
  return request(`/admin/projects/${id}`, {  // ← убрал /api
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
}

export function deleteProject(token, id) {
  return request(`/admin/projects/${id}`, {  // ← убрал /api
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function getMessages(token) {
  return request("/admin/messages", {  // ← убрал /api
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function markMessageAsRead(token, id) {
  return request(`/admin/messages/${id}/read`, {  // ← убрал /api
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}