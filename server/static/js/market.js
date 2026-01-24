// static/js/market.js

function getToken() {
  return localStorage.getItem("accessToken");
}

// ----- 마켓 생성 페이지 -----
const marketMakeForm = document.getElementById("market-make-form");
if (marketMakeForm) {
  marketMakeForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(marketMakeForm);
    const name = formData.get("name");
    const token = getToken();

    if (!token) {
      alert("로그인이 필요합니다.");
      return;
    }

    try {
      const res = await fetch("/manage/markets", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token,
        },
        body: JSON.stringify({ name }),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.message || "마켓 생성 실패");
        return;
      }

      alert("마켓 생성 및 참가 완료: " + data.market.name);
      window.location.href = "/";
    } catch (e) {
      console.error(e);
      alert("에러가 발생했습니다.");
    }
  });
}

// ----- 내 마켓 페이지 -----
const myMarketsArea = document.getElementById("my-markets-area");
if (myMarketsArea) {
  (async () => {
    const token = getToken();
    if (!token) {
      myMarketsArea.innerHTML = `
        <p>로그인이 필요합니다.</p>
        <p><a href="/login">로그인</a></p>
      `;
      return;
    }

    try {
      const res = await fetch("/manage/markets/me", {
        headers: {
          "Authorization": "Bearer " + token,
        },
      });

      const data = await res.json();
      if (!res.ok) {
        myMarketsArea.innerHTML = "<p>마켓 정보를 불러오지 못했습니다.</p>";
        return;
      }

      if (data.length === 0) {
        myMarketsArea.innerHTML = "<p>참가한 마켓이 없습니다.</p>";
        return;
      }

      myMarketsArea.innerHTML = `
        <ul>
          ${data
            .map(
              (item) => `
            <li>
              <a href="/markets/${item.market.id}">
                ${item.market.name}
              </a>
              (현금: ${item.shareholder.cashBalance}, 평가: ${item.shareholder.portfolioValue})
            </li>
          `
            )
            .join("")}
        </ul>
      `;
    } catch (e) {
      console.error(e);
      myMarketsArea.innerHTML = "<p>마켓 정보를 불러오지 못했습니다.</p>";
    }
  })();
}

// ----- 마켓 상세 페이지 -----
const marketDetailEl = document.getElementById("market-detail");
const createCompanyBtn = document.getElementById("create-company-btn");
const companyTableBody = document.querySelector("#company-table tbody");
const companyDetailEl = document.querySelector("#company-detail");
const tradeRoot = document.getElementById("trade-root");

if (marketDetailEl) {
  (async () => {
    const marketId = marketDetailEl.dataset.marketId;
    const token = getToken();

    if (!token) {
      marketDetailEl.innerHTML = `
        <p>로그인이 필요합니다.</p>
        <p><a href="/login">로그인</a></p>
      `;
      return;
    }

    try {
      const res = await fetch(`/manage/markets/${marketId}`, {
        headers: {
          "Authorization": "Bearer " + token,
        },
      });

      const data = await res.json();
      if (!res.ok) {
        console.error("market detail error:", data);
        marketDetailEl.innerHTML = "<p>마켓 정보를 불러오지 못했습니다.</p>";
        return;
      }

      // 마켓 기본 정보
      marketDetailEl.innerHTML = `
        <h2>${data.name}</h2>
        <p>참가자 수: ${data.participants.length}명</p>
      `;

      // ADMIN이면 회사 생성 버튼
      if (data.isAdmin && createCompanyBtn) {
        createCompanyBtn.style.display = "inline-block";
        createCompanyBtn.onclick = () => {
          window.location.href = `/markets/${marketId}/companies/new`;
        };
      }

      // 회사 리스트 렌더링
      renderCompanyList(data.companies || [], marketId);
    } catch (e) {
      console.error(e);
      marketDetailEl.innerHTML = "<p>마켓 정보를 불러오지 못했습니다.</p>";
    }
  })();
}

function renderCompanyList(companies, marketId) {
  if (!companyTableBody) return;

  if (!Array.isArray(companies) || companies.length === 0) {
    companyTableBody.innerHTML = `
      <tr><td colspan="6">상장된 회사가 없습니다.</td></tr>
    `;
    return;
  }

  companyTableBody.innerHTML = companies
    .map((c) => {
      const changeSign = Number(c.change) > 0 ? "+" : "";
      return `
        <tr class="company-row" data-company-id="${c.id}" style="cursor:pointer;">
          <td>${c.ticker || ""}</td>
          <td>${c.name}</td>
          <td>${c.currentPrice}</td>
          <td>${c.issuedPrice}</td>
          <td>${changeSign}${c.change}</td>
          <td>${c.changePercent}%</td>
        </tr>
      `;
    })
    .join("");

  // 회사 클릭 시 상세 + 거래 패널 로딩
  document
    .querySelectorAll("#company-table tbody tr.company-row")
    .forEach((tr) => {
      tr.addEventListener("click", () => {
        const companyId = tr.dataset.companyId;
        if (!companyId) return;
        console.log("회사 클릭됨:", companyId);
        loadCompanyDetail(marketId, companyId);
      });
    });
}

async function loadCompanyDetail(marketId, companyId) {
  const token = getToken();
  if (!token) {
    alert("로그인이 필요합니다.");
    return;
  }

  try {
    const res = await fetch(
      `/manage/markets/${marketId}/companies/${companyId}`,
      {
        headers: { "Authorization": "Bearer " + token },
      }
    );

    const data = await res.json();
    if (!res.ok) {
      console.error("company detail error:", data);
      alert(data.message || "회사 상세 정보를 불러오지 못했습니다.");
      return;
    }

    if (companyDetailEl) {
      companyDetailEl.innerHTML = `
        <h3>${data.name} (${data.ticker})</h3>
        <p>현재가: ${data.currentPrice}</p>
        <p>발행가: ${data.issuedPrice}</p>
        <p>시가총액: ${data.marketCap}</p>
        <p>등락률: ${data.changeRate}%</p>
      `;
    }

    if (tradeRoot) {
      tradeRoot.style.display = "block";
      tradeRoot.dataset.companyId = companyId;
    }

    // 호가창 로딩 (trade.js 에서 정의)
    if (typeof window.loadOrderBook === "function") {
      window.loadOrderBook(marketId, companyId);
    }
  } catch (e) {
    console.error(e);
    alert("회사 상세 정보를 불러오지 못했습니다.");
  }
}
