        const form = document.getElementById("register-form");
        const messageEl = document.getElementById("message");

        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const email = document.getElementById("email").value;
            const nickname = document.getElementById("nickname").value;
            const password = document.getElementById("password").value;
            const passwordConfirm = document.getElementById("passwordConfirm").value;


            messageEl.textContent = "";

            try {
                const res = await fetch("/auth/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email,
                        nickname,
                        password,
                        passwordConfirm
                    }),
                });

                const data = await res.json();

                if (!res.ok) {
                    messageEl.textContent = data.message || "회원가입 실패";
                    return;
                }

                alert("회원가입 완료! 로그인 페이지로 이동합니다.");
                window.location.href = "/login";

            } catch (err) {
                console.error(err);
                messageEl.textContent = "서버 오류가 발생했습니다.";
            }
        });