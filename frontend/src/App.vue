<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import {
  createProject,
  deleteProject,
  getAdminProjects,
  getMessages,
  getPortfolio,
  login,
  markMessageAsRead,
  sendMessage,
  updateProject,
} from "./services/api";

const loading = ref(true);
const loadError = ref("");
const savingProject = ref(false);
const sendingMessage = ref(false);
const adminLoading = ref(false);
const adminError = ref("");
const adminSuccess = ref("");
const contactSuccess = ref("");

const portfolio = reactive({
  profile: null,
  timeline: [],
  projects: [],
});

const contactForm = reactive({
  name: "",
  email: "",
  message: "",
});

const contactErrors = reactive({
  name: "",
  email: "",
  message: "",
});

const adminCredentials = reactive({
  username: "admin",
  password: "",
});

const adminState = reactive({
  token: localStorage.getItem("portfolio-admin-token") ?? "",
  username: localStorage.getItem("portfolio-admin-username") ?? "",
  projects: [],
  messages: [],
});

const projectForm = reactive({
  id: null,
  title: "",
  description: "",
  stack: "",
  project_url: "",
  year: new Date().getFullYear(),
  featured: false,
  sort_order: 1,
});

const heroStats = computed(() => {
  if (!portfolio.profile) {
    return [];
  }

  return [
    {
      label: "Возраст",
      value: `${portfolio.profile.age} лет`,
    },
    {
      label: "Проектов",
      value: `${portfolio.projects.length}`,
    },
    {
      label: "Направление",
      value: "Прикладная информатика",
    },
  ];
});

const featuredProjects = computed(() =>
  portfolio.projects.filter((project) => project.featured).slice(0, 2),
);

const unreadMessagesCount = computed(
  () => adminState.messages.filter((message) => !message.is_read).length,
);

function resetProjectForm() {
  projectForm.id = null;
  projectForm.title = "";
  projectForm.description = "";
  projectForm.stack = "";
  projectForm.project_url = "";
  projectForm.year = new Date().getFullYear();
  projectForm.featured = false;
  projectForm.sort_order = adminState.projects.length + 1;
}

function populateProjectForm(project) {
  projectForm.id = project.id;
  projectForm.title = project.title;
  projectForm.description = project.description;
  projectForm.stack = project.stack;
  projectForm.project_url = project.project_url;
  projectForm.year = project.year;
  projectForm.featured = project.featured;
  projectForm.sort_order = project.sort_order;
  adminSuccess.value = "";
  adminError.value = "";
}

function formatDate(value) {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatBirthDate(value) {
  const [year, month, day] = value.split("-").map(Number);
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  }).format(new Date(year, month - 1, day));
}

function scrollToSection(selector) {
  document.querySelector(selector)?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
}

function validateContactForm() {
  contactErrors.name = contactForm.name.trim() ? "" : "Введите имя.";
  contactErrors.email = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contactForm.email.trim())
    ? ""
    : "Введите корректный email.";
  contactErrors.message =
    contactForm.message.trim().length >= 10 ? "" : "Сообщение должно содержать не меньше 10 символов.";

  return !contactErrors.name && !contactErrors.email && !contactErrors.message;
}

async function loadPortfolioData(showLoader = true) {
  if (showLoader) {
    loading.value = true;
  }
  loadError.value = "";

  try {
    const payload = await getPortfolio();
    portfolio.profile = payload.profile;
    portfolio.timeline = payload.timeline;
    portfolio.projects = payload.projects;
  } catch (error) {
    loadError.value = error.message;
  } finally {
    if (showLoader) {
      loading.value = false;
    }
  }
}

async function handleContactSubmit() {
  contactSuccess.value = "";

  if (!validateContactForm()) {
    return;
  }

  sendingMessage.value = true;

  try {
    const payload = await sendMessage({
      name: contactForm.name.trim(),
      email: contactForm.email.trim(),
      message: contactForm.message.trim(),
    });

    contactForm.name = "";
    contactForm.email = "";
    contactForm.message = "";
    contactErrors.name = "";
    contactErrors.email = "";
    contactErrors.message = "";
    contactSuccess.value = payload.message;
  } catch (error) {
    contactErrors.message = error.message;
  } finally {
    sendingMessage.value = false;
  }
}

async function loadAdminData() {
  if (!adminState.token) {
    return;
  }

  adminLoading.value = true;
  adminError.value = "";

  try {
    const [projects, messages] = await Promise.all([
      getAdminProjects(adminState.token),
      getMessages(adminState.token),
    ]);
    adminState.projects = projects;
    adminState.messages = messages;
    resetProjectForm();
  } catch (error) {
    adminError.value = error.message;
    clearSession();
  } finally {
    adminLoading.value = false;
  }
}

function persistSession(token, username) {
  adminState.token = token;
  adminState.username = username;
  localStorage.setItem("portfolio-admin-token", token);
  localStorage.setItem("portfolio-admin-username", username);
}

function clearSession() {
  adminState.token = "";
  adminState.username = "";
  adminState.projects = [];
  adminState.messages = [];
  localStorage.removeItem("portfolio-admin-token");
  localStorage.removeItem("portfolio-admin-username");
  resetProjectForm();
}

async function handleAdminLogin() {
  adminLoading.value = true;
  adminError.value = "";
  adminSuccess.value = "";

  try {
    const payload = await login({
      username: adminCredentials.username.trim(),
      password: adminCredentials.password.trim(),
    });
    persistSession(payload.access_token, payload.username);
    adminSuccess.value = "Вход выполнен. Теперь можно управлять проектами и сообщениями.";
    await loadAdminData();
  } catch (error) {
    adminError.value = error.message;
  } finally {
    adminLoading.value = false;
  }
}

async function handleProjectSubmit() {
  adminError.value = "";
  adminSuccess.value = "";
  savingProject.value = true;

  const payload = {
    title: projectForm.title.trim(),
    description: projectForm.description.trim(),
    stack: projectForm.stack.trim(),
    project_url: projectForm.project_url.trim(),
    year: Number(projectForm.year),
    featured: Boolean(projectForm.featured),
    sort_order: Number(projectForm.sort_order),
  };

  try {
    if (projectForm.id) {
      await updateProject(adminState.token, projectForm.id, payload);
      adminSuccess.value = "Проект обновлен.";
    } else {
      await createProject(adminState.token, payload);
      adminSuccess.value = "Проект добавлен.";
    }

    await Promise.all([loadPortfolioData(false), loadAdminData()]);
    resetProjectForm();
  } catch (error) {
    adminError.value = error.message;
  } finally {
    savingProject.value = false;
  }
}

async function handleDeleteProject(id) {
  adminError.value = "";
  adminSuccess.value = "";
  savingProject.value = true;

  try {
    await deleteProject(adminState.token, id);
    adminSuccess.value = "Проект удален.";
    await Promise.all([loadPortfolioData(false), loadAdminData()]);
    if (projectForm.id === id) {
      resetProjectForm();
    }
  } catch (error) {
    adminError.value = error.message;
  } finally {
    savingProject.value = false;
  }
}

async function handleMarkRead(id) {
  adminError.value = "";
  adminSuccess.value = "";

  try {
    const payload = await markMessageAsRead(adminState.token, id);
    adminSuccess.value = payload.message;
    await loadAdminData();
  } catch (error) {
    adminError.value = error.message;
  }
}

onMounted(async () => {
  await loadPortfolioData();
  if (adminState.token) {
    await loadAdminData();
  } else {
    resetProjectForm();
  }
});
</script>

<template>
  <div class="page-shell">
    <header class="topbar">
      <a class="brand" href="#top">IS</a>
      <nav class="topbar__nav">
        <button type="button" @click="scrollToSection('#about')">О себе</button>
        <button type="button" @click="scrollToSection('#timeline')">Путь</button>
        <button type="button" @click="scrollToSection('#projects')">Проекты</button>
        <button type="button" @click="scrollToSection('#contact')">Контакты</button>
        <button type="button" @click="scrollToSection('#admin')">Админ</button>
      </nav>
    </header>

    <main id="top" class="layout">
      <section v-if="loading" class="status-card">Загрузка портфолио...</section>
      <section v-else-if="loadError" class="status-card status-card--error">
        {{ loadError }}
      </section>

      <template v-else-if="portfolio.profile">
        <section class="hero">
          <div class="hero__copy">
            <p class="eyebrow">Учебное портфолио</p>
            <h1>{{ portfolio.profile.full_name }}</h1>
            <p class="hero__lead">{{ portfolio.profile.tagline }}</p>

            <div class="hero__stats">
              <article v-for="item in heroStats" :key="item.label" class="stat-card">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </article>
            </div>

            <div class="hero__actions">
              <button type="button" class="button button--primary" @click="scrollToSection('#projects')">
                Смотреть проекты
              </button>
              <button type="button" class="button button--ghost" @click="scrollToSection('#contact')">
                Написать мне
              </button>
            </div>
          </div>

          <div class="hero__visual">
            <div class="hero__badge">
              <span>{{ portfolio.profile.city }}</span>
              <strong>{{ formatBirthDate(portfolio.profile.birth_date) }}</strong>
            </div>
            <img
              class="hero__photo"
              :src="portfolio.profile.avatar_path"
              alt="Фотография Ивана Старкова"
            />
          </div>
        </section>

        <section id="about" class="section">
          <div class="section-heading">
            <p class="eyebrow">О себе</p>
            <h2>Кто я и чем занимаюсь</h2>
          </div>

          <div class="about-grid">
            <article class="info-card">
              <h3>Кратко</h3>
              <p>{{ portfolio.profile.intro }}</p>
            </article>

            <article class="info-card">
              <h3>Сейчас</h3>
              <p>{{ portfolio.profile.current_study }}</p>
            </article>

            <article class="info-card">
              <h3>Опыт обучения</h3>
              <p>{{ portfolio.profile.previous_study }}</p>
            </article>

            <article class="quote-card">
              <p>“{{ portfolio.profile.quote }}”</p>
            </article>
          </div>

          <div class="skills-strip">
            <span v-for="interest in portfolio.profile.interests" :key="interest">
              {{ interest }}
            </span>
          </div>
        </section>

        <section id="timeline" class="section">
          <div class="section-heading">
            <p class="eyebrow">Биография</p>
            <h2>Учебный путь и развитие</h2>
          </div>

          <div class="timeline">
            <article
              v-for="event in portfolio.timeline"
              :key="event.id"
              class="timeline-card"
            >
              <span class="timeline-card__period">{{ event.period_label }}</span>
              <h3>{{ event.title }}</h3>
              <p>{{ event.description }}</p>
              <strong>{{ event.location }}</strong>
            </article>
          </div>
        </section>

        <section id="projects" class="section">
          <div class="section-heading">
            <p class="eyebrow">Портфолио</p>
            <h2>Учебные и личные проекты</h2>
          </div>

          <div class="featured-grid">
            <article
              v-for="project in featuredProjects"
              :key="project.id"
              class="featured-card"
            >
              <span>Избранный проект</span>
              <h3>{{ project.title }}</h3>
              <p>{{ project.description }}</p>
              <div class="featured-card__meta">
                <small>{{ project.stack }}</small>
                <small>{{ project.year }}</small>
              </div>
            </article>
          </div>

          <div class="projects-grid">
            <article v-for="project in portfolio.projects" :key="project.id" class="project-card">
              <div class="project-card__head">
                <h3>{{ project.title }}</h3>
                <span>{{ project.year }}</span>
              </div>
              <p>{{ project.description }}</p>
              <div class="project-card__footer">
                <small>{{ project.stack }}</small>
                <a :href="project.project_url" target="_blank" rel="noreferrer">Открыть</a>
              </div>
            </article>
          </div>
        </section>

        <section id="contact" class="section">
          <div class="section-heading">
            <p class="eyebrow">Контакты</p>
            <h2>Форма обратной связи</h2>
          </div>

          <div class="contact-layout">
            <article class="contact-copy">
              <h3>Свяжитесь со мной по проекту или стажировке</h3>
              <p>
                Эта форма сохраняет имя, email и сообщение в базе данных SQLite, как требуется
                в задании.
              </p>
              <ul class="contact-points">
                <li>Frontend: Vue 3</li>
                <li>Backend: FastAPI</li>
                <li>База данных: SQLite + SQLAlchemy</li>
              </ul>
            </article>

            <form class="contact-form" @submit.prevent="handleContactSubmit">
              <label>
                Имя
                <input v-model="contactForm.name" type="text" maxlength="80" placeholder="Ваше имя" />
                <small v-if="contactErrors.name" class="form-error">{{ contactErrors.name }}</small>
              </label>

              <label>
                Email
                <input
                  v-model="contactForm.email"
                  type="email"
                  maxlength="120"
                  placeholder="example@mail.ru"
                />
                <small v-if="contactErrors.email" class="form-error">{{ contactErrors.email }}</small>
              </label>

              <label>
                Сообщение
                <textarea
                  v-model="contactForm.message"
                  rows="5"
                  maxlength="1500"
                  placeholder="Коротко опишите цель обращения"
                ></textarea>
                <small v-if="contactErrors.message" class="form-error">{{ contactErrors.message }}</small>
              </label>

              <button class="button button--primary" type="submit" :disabled="sendingMessage">
                {{ sendingMessage ? "Отправка..." : "Отправить" }}
              </button>
              <p v-if="contactSuccess" class="form-success">{{ contactSuccess }}</p>
            </form>
          </div>
        </section>

        <section id="admin" class="section admin-section">
          <div class="section-heading">
            <p class="eyebrow">Администрирование</p>
            <h2>Управление проектами и сообщениями</h2>
          </div>

          <div class="admin-layout">
            <article class="admin-panel">
              <div class="admin-panel__header">
                <h3>Вход администратора</h3>
                <span v-if="adminState.username">Пользователь: {{ adminState.username }}</span>
              </div>

              <div v-if="!adminState.token" class="admin-login">
                <label>
                  Логин
                  <input v-model="adminCredentials.username" type="text" maxlength="60" />
                </label>
                <label>
                  Пароль
                  <input v-model="adminCredentials.password" type="password" maxlength="120" />
                </label>
                <button class="button button--primary" type="button" @click="handleAdminLogin">
                  {{ adminLoading ? "Вход..." : "Войти" }}
                </button>
              </div>

              <template v-else>
                <div class="admin-toolbar">
                  <p>Непрочитанных сообщений: {{ unreadMessagesCount }}</p>
                  <button class="button button--ghost" type="button" @click="clearSession">
                    Выйти
                  </button>
                </div>

                <form class="project-form" @submit.prevent="handleProjectSubmit">
                  <h4>{{ projectForm.id ? "Редактирование проекта" : "Новый проект" }}</h4>
                  <label>
                    Название
                    <input v-model="projectForm.title" type="text" maxlength="120" required />
                  </label>
                  <label>
                    Описание
                    <textarea v-model="projectForm.description" rows="4" maxlength="1200" required></textarea>
                  </label>
                  <label>
                    Стек
                    <input v-model="projectForm.stack" type="text" maxlength="255" required />
                  </label>
                  <label>
                    Ссылка
                    <input v-model="projectForm.project_url" type="url" maxlength="255" required />
                  </label>

                  <div class="form-grid">
                    <label>
                      Год
                      <input v-model="projectForm.year" type="number" min="2018" max="2100" required />
                    </label>
                    <label>
                      Порядок
                      <input v-model="projectForm.sort_order" type="number" min="0" max="100" required />
                    </label>
                  </div>

                  <label class="checkbox">
                    <input v-model="projectForm.featured" type="checkbox" />
                    Показывать в избранных
                  </label>

                  <div class="form-actions">
                    <button class="button button--primary" type="submit" :disabled="savingProject">
                      {{ savingProject ? "Сохранение..." : projectForm.id ? "Обновить" : "Добавить" }}
                    </button>
                    <button class="button button--ghost" type="button" @click="resetProjectForm">
                      Очистить
                    </button>
                  </div>
                </form>

                <div class="admin-list">
                  <h4>Проекты в базе</h4>
                  <article
                    v-for="project in adminState.projects"
                    :key="project.id"
                    class="admin-item"
                  >
                    <div>
                      <strong>{{ project.title }}</strong>
                      <p>{{ project.stack }} • {{ project.year }}</p>
                    </div>
                    <div class="admin-item__actions">
                      <button class="button button--ghost" type="button" @click="populateProjectForm(project)">
                        Изменить
                      </button>
                      <button class="button button--danger" type="button" @click="handleDeleteProject(project.id)">
                        Удалить
                      </button>
                    </div>
                  </article>
                </div>
              </template>

              <p v-if="adminError" class="form-error">{{ adminError }}</p>
              <p v-if="adminSuccess" class="form-success">{{ adminSuccess }}</p>
            </article>

            <article class="messages-panel">
              <div class="messages-panel__header">
                <h3>Сообщения</h3>
                <span>{{ adminState.messages.length }} записей</span>
              </div>

              <div v-if="!adminState.token" class="status-card">
                Войдите как администратор, чтобы просматривать сообщения.
              </div>
              <div v-else-if="adminLoading" class="status-card">Загрузка панели...</div>
              <div v-else class="messages-list">
                <article
                  v-for="message in adminState.messages"
                  :key="message.id"
                  class="message-card"
                  :class="{ 'message-card--read': message.is_read }"
                >
                  <div class="message-card__head">
                    <div>
                      <strong>{{ message.name }}</strong>
                      <a :href="`mailto:${message.email}`">{{ message.email }}</a>
                    </div>
                    <small>{{ formatDate(message.created_at) }}</small>
                  </div>
                  <p>{{ message.message }}</p>
                  <button
                    v-if="!message.is_read"
                    class="button button--ghost"
                    type="button"
                    @click="handleMarkRead(message.id)"
                  >
                    Отметить прочитанным
                  </button>
                </article>
              </div>
            </article>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>
