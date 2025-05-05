// 尝试从本地存储中获取 JWT token
const token = localStorage.getItem("token");

// 如果 token 不存在，说明用户未登录，提示并跳转到登录页
if (!token) {
  alert("Please log in first.");
  window.location.href = "index.html";
} else {
  // 获取当前用户信息
  fetch("http://127.0.0.1:8000/api/me", {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
    .then(res => {
      if (!res.ok) throw new Error("Invalid or expired token");
      return res.json();
    })
    .then(data => {
      // 填充基本信息
      document.getElementById("welcome").textContent = `Welcome, ${data.first_name} ${data.last_name}`;
      document.getElementById("email").textContent = data.email;
      document.getElementById("role").textContent = data.user_group_identifier;
      localStorage.setItem("user", JSON.stringify(data));

      // 显示“查看我的项目”按钮
      if (data.user_group_identifier === "supervisor") {
        document.getElementById("supervisor-actions").style.display = "block";
      }

      // 预填编辑表单
      document.getElementById("edit-first-name").value = data.first_name;
      document.getElementById("edit-last-name").value = data.last_name;
    })
    .catch(() => {
      alert("Session expired or invalid. Please log in again.");
      localStorage.clear();
      window.location.href = "index.html";
    });
}

// 显示编辑表单
function showEditForm() {
  document.getElementById("edit-form-container").style.display = "block";
}

// 处理登出
function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}

// 提交编辑表单
document.addEventListener("DOMContentLoaded", () => {
  const editForm = document.getElementById("edit-form");
  if (editForm) {
    editForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const updated = {
        first_name: document.getElementById("edit-first-name").value,
        last_name: document.getElementById("edit-last-name").value
      };

      fetch("http://127.0.0.1:8000/supervisors/me", {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(updated)
      })
        .then(res => {
          if (res.ok) {
            alert("✅ Info updated!");
            window.location.reload();
          } else {
            return res.text().then(text => { throw new Error(text); });
          }
        })
        .catch(err => alert("❌ Update failed:\n" + err.message));
    });
  }
});



