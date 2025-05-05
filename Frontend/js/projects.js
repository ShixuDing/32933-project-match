// projects.js

// 从本地存储中获取 token 和当前登录用户
const token = localStorage.getItem("token");
const user = JSON.parse(localStorage.getItem("user"));
const supervisorId = user?.id;

if (!token || !supervisorId) {
  alert("You must log in first.");
  window.location.href = "index.html";
}

document.addEventListener("DOMContentLoaded", () => {
  const listDiv = document.getElementById("project-list");
  if (listDiv) loadProjectList();

  const createForm = document.getElementById("create-form");
  if (createForm) handleCreate();

  const editForm = document.getElementById("edit-form");
  if (editForm) handleEdit();
});

function loadProjectList() {
  fetch("http://127.0.0.1:8000/supervisors/me/projects", {
    headers: { Authorization: `Bearer ${token}` }
  })
    .then(res => res.json())
    .then(projects => {
      const listDiv = document.getElementById("project-list");
      listDiv.innerHTML = "";

      projects.forEach(p => {
        const div = document.createElement("div");
        div.className = "project";
        div.innerHTML = `
          <h3>${p.title}</h3>
          <p>${p.description}</p>
          <p><strong>Created:</strong> ${p.created_at || "N/A"}</p>
          <button onclick="editProject('${p.id}')">Edit</button>
          <button onclick="deleteProject('${p.id}')">Delete</button>
        `;
        listDiv.appendChild(div);
      });
    })
    .catch(err => console.error("❌ Failed to load projects:", err));
}

window.editProject = function (id) {
  window.location.href = `project-edit.html?id=${id}`;
};

window.deleteProject = function (id) {
  if (!confirm("Are you sure you want to delete this project?")) return;

  fetch(`http://127.0.0.1:8000/supervisors/${supervisorId}/projects/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
    .then(res => {
      if (!res.ok) return res.text().then(text => { throw new Error(text); });
      alert("✅ Project deleted.");
      loadProjectList();
    })
    .catch(err => alert("❌ Delete failed:\n" + err.message));
};

function handleCreate() {
  const createForm = document.getElementById("create-form");
  createForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();
    const research_field = document.getElementById("research_field").value.trim();
    const group_or_individual = document.getElementById("group_or_individual").value;
    const project_start_time = document.getElementById("project_start_time").value;
    const project_end_time = document.getElementById("project_end_time").value;

    fetch(`http://127.0.0.1:8000/supervisors/${supervisorId}/projects`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        title,
        description,
        research_field,
        group_or_individual,
        project_start_time,
        project_end_time
      })
    })
      .then(res => {
        if (!res.ok) return res.text().then(text => { throw new Error(text); });
        alert("✅ Project created!");
        window.location.href = "projects.html";
      })
      .catch(err => alert("❌ Create failed:\n" + err.message));
  });
}

function handleEdit() {
  const editForm = document.getElementById("edit-form");
  const urlParams = new URLSearchParams(window.location.search);
  const projectId = urlParams.get("id");

  if (!projectId) {
    alert("No project ID found.");
    window.location.href = "projects.html";
    return;
  }

  fetch("http://127.0.0.1:8000/supervisors/me/projects", {
    headers: { Authorization: `Bearer ${token}` }
  })
    .then(res => res.json())
    .then(projects => {
      const target = projects.find(p => p.id == projectId);
      if (!target) throw new Error("Project not found.");

      document.getElementById("title").value = target.title;
      document.getElementById("description").value = target.description;
      if (document.getElementById("research_field")) {
        document.getElementById("research_field").value = target.research_field;
        document.getElementById("group_or_individual").value = target.group_or_individual;
        document.getElementById("project_start_time").value = target.project_start_time?.slice(0, 16);
        document.getElementById("project_end_time").value = target.project_end_time?.slice(0, 16);
      }
    })
    .catch(err => {
      alert("❌ Load project failed:\n" + err.message);
      window.location.href = "projects.html";
    });

  editForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const updated = {
      title: document.getElementById("title").value.trim(),
      description: document.getElementById("description").value.trim()
    };

    if (document.getElementById("research_field")) {
      updated.research_field = document.getElementById("research_field").value.trim();
      updated.group_or_individual = document.getElementById("group_or_individual").value;
      updated.project_start_time = document.getElementById("project_start_time").value;
      updated.project_end_time = document.getElementById("project_end_time").value;
    }

    fetch(`http://127.0.0.1:8000/supervisors/${supervisorId}/projects/${projectId}`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(updated)
    })
      .then(res => {
        if (!res.ok) return res.text().then(text => { throw new Error(text); });
        alert("✅ Project updated!");
        window.location.href = "projects.html";
      })
      .catch(err => alert("❌ Update failed:\n" + err.message));
  });
}

