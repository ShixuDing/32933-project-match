// 注册逻辑处理
document.getElementById("registerForm")?.addEventListener("submit", async function(e) {
  e.preventDefault();

  // 获取用户填写的注册信息
  const firstName = document.getElementById("firstName").value;
  const lastName = document.getElementById("lastName").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const role = document.getElementById("role").value; // student or supervisor

  // 向后端注册接口发送请求
  const res = await fetch("http://127.0.0.1:8000/api/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      first_name: firstName,
      last_name: lastName,
      email: email,
      password: password,
      user_group_identifier: role
    })
  });

  // 判断注册是否成功
  if (res.ok) {
    alert("Registration successful! Please log in.");
    window.location.href = "index.html"; // 成功后跳转登录页
  } else {
    const msg = await res.text();
    alert("Registration failed: " + msg); // 显示错误信息
  }
});


//  登录逻辑处理
document.getElementById("loginForm")?.addEventListener("submit", async function(e) {
  e.preventDefault(); // 阻止默认提交（防止页面刷新）

  // 获取用户输入的邮箱和密码
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  // 向后端登录接口发出请求
  const res = await fetch("http://127.0.0.1:8000/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  // 如果登录成功，保存 token 并跳转 profile 页面
  if (res.ok) {
    const data = await res.json(); // 获取返回的 token
    localStorage.setItem("token", data.access_token); // 保存 token 到本地
    window.location.href = "profile.html"; // 跳转用户信息页
  } else {
    alert("Login failed. Please check your credentials."); // 登录失败提示
  }
});
