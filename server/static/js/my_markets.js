// static/js/my_markets.js

(function () {
  // ---- 공통 ----
  function getToken() {
    return localStorage.getItem("accessToken");
  }

  const joinedMarketsEl = document.getElementById("joined-markets");
  const companyTableBody = document.querySelector("#company-table tbody");
  const orderPanel = document.getElementById("order-panel");
  const orderbookPanel = document.getElementById("orderbook-panel");
  const orderForm = document.getElementById("order-form");
  const orderResultEl = document.getElementById("order-result");
  const orderbookArea = document.getElementById("orderbook-area");

  const priceChartCanvas = document.getElementById("price-chart");
  const chartPlaceholderText = document.getElementById("chart-placeholder-text");
  const companySummary = document.getElementById("company-summary");
  const csTicker = document.getElementById("cs-ticker");
  const csName = document.getElementById("cs-name");
  const csCurrent = document.getElementById("cs-current");
  const csIssued = document.getElementById("cs-issued");
  const csChange = document.getElementById("cs-change");
  const csChangeRate = document.getElementById("cs-change-rate");

  let selectedMarketId = null;
  let selectedCompanyId = null;

  // ---- 차트 (샘플: 회사 바뀔 때마다 대충 꺾은선 하나 그려주는 정도) ----
  function renderDummyChart() {
    if (!priceChartCanvas) return;
    const ctx = priceChartCanvas.getContext("2d");
    ctx.clearRect(0, 0, priceChartCanvas.width, priceChartCanvas.height);

    const w = priceChartCanvas.width;
    const h = priceChartCanvas.height;

    // 축
    ctx.strokeStyle = "#ccc";
    ctx.beginPath();
    ctx.moveTo(40, 10);
    ctx.lineTo(40, h - 30);
    ctx.lineTo(w - 10, h - 30);
    ctx.stroke();

    // 랜덤 곡선
    ctx.strokeStyle = "#333";
    ctx.beginPath();
    const points = 20;
    for (let i = 0; i < points; i++) {
      const x = 40 + ((w - 60) * i) / (points - 1);
      const y = 20 + Math.random() * (h - 60);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }

  // ---- 내 마켓 목록 로딩 ----
  async function loadJoinedMarkets() {
    if (!joinedMarketsEl) return;

    const token = getToken();
    if (!token) {
      joinedMarketsEl.innerHTML = `
        <li>
          <p>로그인이 필요합니다.</p>
          <a href="/login">로그인</a>
        </li>
      `;
      return;
    }

    try {
      const res = await fetch("/manage/markets/me", {
        headers: {
          Authorization: "Bearer " + token,
        },
      });
      const data = await res.json();

      if (!res.ok) {
        console.error("loadJoinedMarkets error:", data);
        joinedMarketsEl.innerHTML = `<li>마켓 목록을 불러오지 못했습니다.</li>`;
        return;
      }

      if (!Array.isArray(data) || data.length === 0) {
        joinedMarketsEl.innerHTML = `<li>참가한 마켓이 없습니다.</li>`;
        return;
      }

      joinedMarketsEl.innerHTML = data
        .map(
          (item) => `
          <li data-market-id="${item.market.id}" style="cursor:pointer;">
            ${item.market.name}
            (현금: ${item.shareholder.cashBalance}, 평가: ${item.shareholder.portfolioValue})
          </li>
        `
        )
        .join("");

      joinedMarketsEl
        .querySelectorAll("li[data-market-id]")
        .forEach((li) => {
          li.addEventListener("click", () => {
            const marketId = li.dataset.marketId;
            if (!marketId) return;
            selectedMarketId = marketId;
            selectedCompanyId = null;
            clearCompanySelectionUI();
            loadMarketCompanies(marketId);
          });
        });
    } catch (e) {
      console.error(e);
      joinedMarketsEl.innerHTML = `<li>마켓 목록을 불러오지 못했습니다.</li>`;
    }
  }

  // ---- 마켓의 회사 목록 로딩 ----
  async function loadMarketCompanies(marketId) {
    const token = getToken();
    if (!token) {
      companyTableBody.innerHTML =
        `<tr><td colspan="6">로그인이 필요합니다.</td></tr>`;
      return;
    }

    try {
      const res = await fetch(`/manage/markets/${marketId}`, {
        headers: {
          Authorization: "Bearer " + token,
        },
      });
      const data = await res.json();

      if (!res.ok) {
        console.error("loadMarketCompanies error:", data);
        companyTableBody.innerHTML =
          `<tr><td colspan="6">마켓 정보를 불러오지 못했습니다.</td></tr>`;
        return;
      }

      const companies = data.companies || [];
      if (!Array.isArray(companies) || companies.length === 0) {
        companyTableBody.innerHTML =
          `<tr><td colspan="6">상장 회사가 없습니다.</td></tr>`;
        return;
      }

      companyTableBody.innerHTML = companies
        .map((c) => {
          const changeSign = Number(c.change) > 0 ? "+" : "";
          return `
          <tr class="company-row" data-company-id="${c.id}">
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

      companyTableBody
        .querySelectorAll("tr.company-row")
        .forEach((tr) => {
          tr.addEventListener("click", () => {
            const companyId = tr.dataset.companyId;
            if (!companyId) return;
            selectedCompanyId = companyId;
            loadCompanyDetail(selectedMarketId, selectedCompanyId);
          });
        });
    } catch (e) {
      console.error(e);
      companyTableBody.innerHTML =
        `<tr><td colspan="6">마켓 정보를 불러오지 못했습니다.</td></tr>`;
    }
  }

  // ---- 회사 상세 + 중앙 패널 + 주문/호가 패널 ----
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
          headers: { Authorization: "Bearer " + token },
        }
      );
      const data = await res.json();

      if (!res.ok) {
        console.error("company detail error:", data);
        alert(data.message || "회사 상세 정보를 불러오지 못했습니다.");
        return;
      }

      // 중앙 회사 정보
      if (companySummary && csTicker && csName) {
        csTicker.textContent = data.ticker;
        csName.textContent = data.name;
        csCurrent.textContent = data.currentPrice;
        csIssued.textContent = data.issuedPrice;

        // 등락, 등락률
        const current = parseFloat(data.currentPrice);
        const issued = parseFloat(data.issuedPrice);
        const diff = current - issued;
        const rate = issued > 0 ? (diff / issued) * 100 : 0;
        csChange.textContent = diff.toFixed(2);
        csChangeRate.textContent = rate.toFixed(2) + "%";

        companySummary.style.display = "block";
      }

      // 차트
      if (chartPlaceholderText && priceChartCanvas) {
        chartPlaceholderText.style.display = "none";
        priceChartCanvas.style.display = "block";
        renderDummyChart();
      }

      // 주문/호가 패널 활성화
      if (orderPanel) orderPanel.style.display = "block";
      if (orderbookPanel) orderbookPanel.style.display = "block";

      // 호가 로딩
      await loadOrderBook(marketId, companyId);
    } catch (e) {
      console.error(e);
      alert("회사 상세 정보를 불러오지 못했습니다.");
    }
  }

  function clearCompanySelectionUI() {
    // 회사 관련 패널 초기화 (마켓만 선택된 상태)
    if (companySummary) {
      companySummary.style.display = "none";
    }
    if (priceChartCanvas) {
      priceChartCanvas.style.display = "none";
    }
    if (chartPlaceholderText) {
      chartPlaceholderText.style.display = "block";
      chartPlaceholderText.textContent =
        "회사를 선택하면 차트가 표시됩니다.";
    }
    if (orderPanel) {
      orderPanel.style.display = "none";
      if (orderResultEl) orderResultEl.textContent = "";
    }
    if (orderbookPanel) {
      orderbookPanel.style.display = "none";
      if (orderbookArea)
        orderbookArea.innerHTML = "회사를 선택하면 호가가 표시됩니다.";
    }
  }

  // ---- 호가창 ----
  async function loadOrderBook(marketId, companyId) {
    const token = getToken();
    if (!token) {
      orderbookArea.innerHTML = `
        <p>로그인이 필요합니다.</p>
        <p><a href="/login">로그인</a></p>
      `;
      return;
    }

    try {
      const url = `/trade/orderbook?marketId=${encodeURIComponent(
        marketId
      )}&companyId=${encodeURIComponent(companyId)}`;

      const res = await fetch(url, {
        headers: {
          Authorization: "Bearer " + token,
        },
      });

      const data = await res.json();
      if (!res.ok) {
        console.error("orderbook error:", data);
        orderbookArea.innerHTML = "<p>호가 정보를 불러오지 못했습니다.</p>";
        return;
      }

      const bids = data.bids || [];
      const asks = data.asks || [];

      orderbookArea.innerHTML = `
        <div style="display:flex; gap:12px;">
          <div style="flex:1;">
            <h4>매도(ASK)</h4>
            ${
              asks.length === 0
                ? "<p>매도 호가 없음</p>"
                : `
              <table border="1" cellpadding="4" style="width:100%; border-collapse:collapse;">
                <thead>
                  <tr>
                    <th>가격</th>
                    <th>수량</th>
                  </tr>
                </thead>
                <tbody>
                  ${asks
                    .map(
                      (a) => `
                    <tr>
                      <td>${a.price}</td>
                      <td>${a.quantity}</td>
                    </tr>
                  `
                    )
                    .join("")}
                </tbody>
              </table>
            `
            }
          </div>
          <div style="flex:1;">
            <h4>매수(BID)</h4>
            ${
              bids.length === 0
                ? "<p>매수 호가 없음</p>"
                : `
              <table border="1" cellpadding="4" style="width:100%; border-collapse:collapse;">
                <thead>
                  <tr>
                    <th>가격</th>
                    <th>수량</th>
                  </tr>
                </thead>
                <tbody>
                  ${bids
                    .map(
                      (b) => `
                    <tr>
                      <td>${b.price}</td>
                      <td>${b.quantity}</td>
                    </tr>
                  `
                    )
                    .join("")}
                </tbody>
              </table>
            `
            }
          </div>
        </div>
      `;
    } catch (e) {
      console.error(e);
      orderbookArea.innerHTML = "<p>호가 정보를 불러오지 못했습니다.</p>";
    }
  }

  // ---- 주문 처리 ----
  if (orderForm) {
    orderForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      if (!selectedMarketId || !selectedCompanyId) {
        alert("먼저 마켓과 회사를 선택해 주세요.");
        return;
      }

      const formData = new FormData(orderForm);
      const side = formData.get("side");
      const quantity = formData.get("quantity");
      const price = formData.get("price");

      if (!side || !quantity || !price) {
        alert("side, quantity, price는 필수입니다.");
        return;
      }

      const token = getToken();
      if (!token) {
        alert("로그인이 필요합니다.");
        return;
      }

      try {
        const res = await fetch("/trade/orders", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + token,
          },
          body: JSON.stringify({
            marketId: selectedMarketId,
            companyId: selectedCompanyId,
            side,
            quantity,
            price,
          }),
        });

        const data = await res.json();

        if (!res.ok) {
          console.error("order error:", data);
          orderResultEl.textContent = data.message || "주문 실패";
          return;
        }

        const o = data.order;
        orderResultEl.textContent = `주문 완료 - 상태: ${o.status}, 체결수량: ${o.filledQuantity}, 잔량: ${o.remainingQuantity}`;

        // 주문 후 호가 다시 로딩
        await loadOrderBook(selectedMarketId, selectedCompanyId);
      } catch (err) {
        console.error(err);
        orderResultEl.textContent = "서버 오류가 발생했습니다.";
      }
    });
  }

  // ---- 초기 실행 ----
  loadJoinedMarkets();
})();
