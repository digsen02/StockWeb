const portfolioArea = document.getElementById("portfolio-area");

function getToken() {
  return localStorage.getItem("accessToken");
}

if (portfolioArea) {
  (async () => {
    const token = getToken();
    if (!token) {
      portfolioArea.innerHTML = `
        <p>로그인이 필요합니다.</p>
        <p><a href="/login">로그인</a></p>
      `;
      return;
    }

    try {
      const res = await fetch("/portfolio/me", {
        headers: {
          "Authorization": "Bearer " + token,
        },
      });

      const data = await res.json();
      if (!res.ok) {
        portfolioArea.innerHTML =
          "<p>포트폴리오 정보를 불러오지 못했습니다.</p>";
        return;
      }

      portfolioArea.innerHTML = `
        <p>현금 잔액: ${data.cashBalance}</p>
        <p>총 평가금액: ${data.portfolioValue}</p>

        <h2>보유 종목</h2>
        <table border="1" cellpadding="4">
          <thead>
            <tr>
              <th>티커</th>
              <th>종목명</th>
              <th>수량</th>
              <th>평균단가</th>
              <th>현재가</th>
              <th>평가금액</th>
            </tr>
          </thead>
          <tbody>
            ${data.items
              .map(
                (item) => `
              <tr>
                <td>${item.ticker}</td>
                <td>${item.name}</td>
                <td>${item.quantity}</td>
                <td>${item.avgPrice}</td>
                <td>${item.currentPrice}</td>
                <td>${item.evalValue}</td>
              </tr>
            `
              )
              .join("")}
          </tbody>
        </table>
      `;
    } catch (e) {
      console.error(e);
      portfolioArea.innerHTML =
        "<p>포트폴리오 정보를 불러오지 못했습니다.</p>";
    }
  })();
}
