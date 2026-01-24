function getToken() {
  return localStorage.getItem("accessToken");
}

// 로그인 처리
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(loginForm);
    const email = formData.get("email");
    const password = formData.get("password");

    try {
      const res = await fetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.message || "로그인 실패");
        return;
      }

      localStorage.setItem("accessToken", data.accessToken);
      alert("로그인 성공");
      window.location.href = "/";
    } catch (e) {
      console.error(e);
      alert("에러가 발생했습니다.");
    }
  });
}

// 회원가입 처리
const registerForm = document.getElementById("register-form");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(registerForm);
    const email = formData.get("email");
    const nickname = formData.get("nickname");
    const password = formData.get("password");
    const passwordConfirm = formData.get("passwordConfirm");

    try {
      const res = await fetch("/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, nickname, password, passwordConfirm }),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.message || "회원가입 실패");
        return;
      }

      alert("회원가입 완료. 이제 로그인 해주세요.");
      window.location.href = "/login";
    } catch (e) {
      console.error(e);
      alert("에러가 발생했습니다.");
    }
  });
}
