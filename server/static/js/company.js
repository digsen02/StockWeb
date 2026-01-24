function getToken() {
  return localStorage.getItem("accessToken");
}

const companyForm = document.getElementById("company-form");
const messageEl = document.getElementById("message");

if (companyForm) {
  const marketId = companyForm.dataset.marketId;

  companyForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = getToken();
    if (!token) {
      alert("로그인이 필요합니다.");
      return;
    }

    const name = document.getElementById("name").value;
    const age = document.getElementById("age").value;
    const issuedShares = document.getElementById("issuedShares").value;
    const issuedPrice = document.getElementById("issuedPrice").value;
    const ticker = document.getElementById("ticker").value || null;
    const parValue = document.getElementById("parValue").value || null;
    const logoSrc = document.getElementById("logoSrc").value || null;

    messageEl.textContent = "";

    try {
      const res = await fetch(`/manage/markets/${marketId}/companies`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token,
        },
        body: JSON.stringify({
          name,
          age,
          issuedShares,
          issuedPrice,
          ticker,
          parValue,
          logoSrc,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        messageEl.textContent = data.message || "회사 생성 실패";
        return;
      }

      alert("회사 생성 완료!");
      window.location.href = `/`;
    } catch (err) {
      console.error(err);
      messageEl.textContent = "서버 오류가 발생했습니다.";
    }
  });
}
