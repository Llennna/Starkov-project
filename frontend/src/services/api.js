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
  return request("/api/public/portfolio", { method: "GET" });
}

export function sendMessage(data) {
  return request("/api/public/messages", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function login(data) {
  return request("/api/admin/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getAdminProjects(token) {
  return request("/api/admin/projects", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function createProject(token, data) {
  return request("/api/admin/projects", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
}

export function updateProject(token, id, data) {
  return request(`/api/admin/projects/${id}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
}

export function deleteProject(token, id) {
  return request(`/api/admin/projects/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function getMessages(token) {
  return request("/api/admin/messages", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function markMessageAsRead(token, id) {
  return request(`/api/admin/messages/${id}/read`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}