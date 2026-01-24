// static/js/home.js
(function () {
  function getToken() {
    return localStorage.getItem("accessToken");
  }

  // 헤더
  const authControls = document.getElementById("auth-controls");

  // 왼쪽: 마켓 / 회사
  const joinedMarketsEl = document.getElementById("joined-markets");
  const companyTableBody = document.getElementById("company-table-body");
  // 마켓 참가 패널(예: <div id="markets-area"></div>)
  const marketsArea = document.getElementById("markets-area");

  // 중앙: 마켓 패널 / 회사 패널
  const marketDetailPanel = document.getElementById("market-detail-panel");
  const marketNameEl = document.getElementById("market-name");
  const marketCreatedAtEl = document.getElementById("market-created-at");
  const marketParticipantsCountEl = document.getElementById(
    "market-participants-count"
  );
  const marketParticipantsListEl = document.getElementById(
    "market-participants-list"
  );
  const btnCreateCompanyMain = document.getElementById(
    "btn-create-company-main"
  );

  const companyPanel = document.getElementById("company-panel");
  const mainSymbol = document.getElementById("main-symbol");
  const mainCompanyName = document.getElementById("main-company-name");
  const mainPrice = document.getElementById("main-price");
  const mainChangeText = document.getElementById("main-change-text");

  const chartPlaceholder = document.getElementById("chart-placeholder");
  const priceChartCanvas = document.getElementById("price-chart");

  const csTicker = document.getElementById("cs-ticker");
  const csName = document.getElementById("cs-name");
  const csCurrent = document.getElementById("cs-current");
  const csIssued = document.getElementById("cs-issued");
  const csChange = document.getElementById("cs-change");
  const csChangeRate = document.getElementById("cs-change-rate");

  // 오른쪽: 주문 / 호가
  const orderForm = document.getElementById("order-form");
  const orderSideInput = document.getElementById("order-side");
  const btnBuy = document.getElementById("btn-buy");
  const btnSell = document.getElementById("btn-sell");
  const orderResultEl = document.getElementById("order-result");
  const orderbookArea = document.getElementById("orderbook-area");

  let selectedMarketId = null;
  let selectedCompanyId = null;

  function showMarketPanel() {
    if (!marketDetailPanel || !companyPanel) return;
    marketDetailPanel.classList.remove("hidden");
    companyPanel.classList.add("hidden");
  }

  function showCompanyPanel() {
    if (!marketDetailPanel || !companyPanel) return;
    marketDetailPanel.classList.add("hidden");
    companyPanel.classList.remove("hidden");
  }

  // -------- 로그인 & 헤더 --------
  async function loadMeAndInit() {
    const token = getToken();
    if (!authControls) return;

    if (!token) {
      authControls.innerHTML = `
        <button class="text-sm text-primary hover:underline" type="button" onclick="window.location.href='/login'">로그인</button>
        <span class="text-gray-500">/</span>
        <button class="text-sm text-primary hover:underline" type="button" onclick="window.location.href='/register'">회원가입</button>
      `;
      return;
    }

    try {
      const res = await fetch("/auth/me", {
        headers: { Authorization: "Bearer " + token },
      });
      const data = await res.json();

      if (!res.ok) {
        console.error("auth/me error:", data);
        localStorage.removeItem("accessToken");
        authControls.innerHTML = `
          <span class="text-xs text-red-400 mr-2">로그인 정보가 만료되었습니다.</span>
          <button class="text-sm text-primary hover:underline" type="button" onclick="window.location.href='/login'">다시 로그인</button>
        `;
        return;
      }

      authControls.innerHTML = `
        <span class="text-sm text-gray-700 dark:text-gray-300">${data.userNickname}</span>
        <button id="btn-logout" class="text-xs text-gray-500 hover:text-red-400" type="button">로그아웃</button>
        <button id="btn-create-market" class="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary hover:bg-primary/20" type="button">
          마켓 생성
        </button>
        <button id="btn-join-market" class="rounded-full bg-gray-200/60 dark:bg-gray-800/60 px-3 py-1 text-xs font-semibold text-gray-700 dark:text-gray-200 hover:bg-gray-300/80 dark:hover:bg-gray-700/80" type="button">
          마켓 참가
        </button>
      `;

      document.getElementById("btn-logout").onclick = () => {
        localStorage.removeItem("accessToken");
        window.location.reload();
      };

      document.getElementById("btn-create-market").onclick = () => {
        window.location.href = "/markets/new";
      };

      document.getElementById("btn-join-market").onclick = showJoinMarketFlow;

      await loadJoinedMarkets();
    } catch (e) {
      console.error(e);
      authControls.innerHTML = `
        <span class="text-xs text-red-400 mr-2">서버 오류</span>
        <button class="text-sm text-primary hover:underline" type="button" onclick="window.location.href='/login'">다시 로그인</button>
      `;
    }
  }

  // -------- 마켓 참가 (UI 버전) --------
  async function showJoinMarketFlow() {
    const token = getToken();
    if (!token) {
      alert("로그인이 필요합니다.");
      return;
    }

    // marketsArea가 없으면 기존 prompt 방식으로 fallback
    if (!marketsArea) {
      try {
        const res = await fetch("/manage/markets", {
          headers: { Authorization: "Bearer " + token },
        });
        const data = await res.json();
        if (!res.ok) {
          console.error("showJoinMarketFlow error:", data);
          alert("마켓 목록을 불러오지 못했습니다.");
          return;
        }

        if (!Array.isArray(data) || data.length === 0) {
          alert("참가 가능한 마켓이 없습니다.");
          return;
        }

        const text = data.map((m, i) => `${i + 1}. ${m.name}`).join("\n");
        const idxStr = prompt(`참가할 마켓 번호를 입력하세요:\n${text}`);
        if (!idxStr) return;

        const idx = parseInt(idxStr, 10) - 1;
        if (idx < 0 || idx >= data.length) {
          alert("잘못된 번호입니다.");
          return;
        }

        const market = data[idx];

        const joinRes = await fetch("/manage/markets/join", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + token,
          },
          body: JSON.stringify({ marketId: market.id }),
        });

        const joinData = await joinRes.json();
        if (!joinRes.ok) {
          console.error("join market error:", joinData);
          alert(joinData.message || "참가 실패");
          return;
        }

        alert("마켓 참가 완료: " + market.name);
        await loadJoinedMarkets();
      } catch (e) {
        console.error(e);
        alert("에러가 발생했습니다.");
      }
      return;
    }

    // 여기부터는 카드형 UI로 렌더링
    try {
      const res = await fetch("/manage/markets", {
        headers: {
          Authorization: "Bearer " + token,
        },
      });

      const data = await res.json();
      if (!res.ok) {
        console.error("showJoinMarketFlow error:", data);
        alert("마켓 목록을 불러오지 못했습니다.");
        return;
      }

      if (!Array.isArray(data) || data.length === 0) {
        marketsArea.innerHTML = `
          <p class="text-sm text-gray-500 dark:text-gray-400">
            현재 참가 가능한 마켓이 없습니다.
          </p>
        `;
        return;
      }

      // 참가 가능한 마켓 리스트를 marketsArea에 뿌려줌
      marketsArea.innerHTML = `
        <h2 class="px-2 text-base font-semibold text-gray-900 dark:text-white mb-2">
          참가 가능한 마켓
        </h2>
        <div class="space-y-1" id="join-markets-list"></div>
      `;

      const listEl = document.getElementById("join-markets-list");

      data.forEach((mkt) => {
        const row = document.createElement("div");
        row.className =
          "flex items-center justify-between rounded p-3 hover:bg-primary/10 transition";

        row.innerHTML = `
          <div class="flex flex-col">
            <p class="font-semibold text-gray-900 dark:text-white">${mkt.name}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              초기 자본: ${mkt.initialCash?.toLocaleString?.() ?? "-"}
            </p>
          </div>
          <button
            class="rounded-full bg-primary/90 px-3 py-1 text-xs font-semibold text-white shadow-sm hover:bg-primary join-btn"
            data-market-id="${mkt.id}">
            참가
          </button>
        `;

        listEl.appendChild(row);
      });

      // join 버튼들에 이벤트
      listEl.querySelectorAll(".join-btn").forEach((btn) => {
        btn.addEventListener("click", async (e) => {
          const marketId = e.currentTarget.getAttribute("data-market-id");
          if (!marketId) return;

          if (!confirm("이 마켓에 참가하시겠습니까?")) return;

          try {
            const joinRes = await fetch("/manage/markets/join", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token,
              },
              body: JSON.stringify({ marketId }),
            });

            const joinData = await joinRes.json();
            if (!joinRes.ok) {
              console.error("join market error:", joinData);
              alert(joinData.message || "참가 실패");
              return;
            }

            alert("마켓 참가 완료");
            await loadJoinedMarkets();

            // 성공 후 목록 갱신/숨기고 싶으면 여기에서 처리
            // marketsArea.innerHTML = "";
          } catch (err) {
            console.error(err);
            alert("참가 중 에러가 발생했습니다.");
          }
        });
      });
    } catch (e) {
      console.error(e);
      alert("에러가 발생했습니다.");
    }
  }

  // -------- 내 마켓 목록 (/manage/markets/me) --------
  async function loadJoinedMarkets() {
    if (!joinedMarketsEl) return;
    const token = getToken();
    if (!token) {
      joinedMarketsEl.innerHTML = `
        <li class="px-2 py-1 text-xs text-gray-500">로그인이 필요합니다.</li>
      `;
      return;
    }

    try {
      const res = await fetch("/manage/markets/me", {
        headers: { Authorization: "Bearer " + token },
      });
      const data = await res.json();

      if (!res.ok) {
        console.error("loadJoinedMarkets error:", data);
        joinedMarketsEl.innerHTML = `
          <li class="px-2 py-1 text-xs text-red-500">마켓 목록을 불러오지 못했습니다.</li>
        `;
        return;
      }

      if (!Array.isArray(data) || data.length === 0) {
        joinedMarketsEl.innerHTML = `
          <li class="px-2 py-1 text-xs text-gray-500">참가한 마켓이 없습니다.</li>
        `;
        return;
      }

      joinedMarketsEl.innerHTML = data
        .map(
          (item) => `
        <li
          class="group cursor-pointer rounded p-2 hover:bg-primary/10"
          data-market-id="${item.market.id}"
        >
          <div class="flex items-center justify-between">
            <div class="flex flex-col">
              <p class="font-semibold text-gray-900 dark:text-white">
                ${item.market.name}
              </p>
            </div>
            <div class="text-right text-xs">
              <p class="text-gray-700 dark:text-gray-200">
                현금: ${item.shareholder.cashBalance}
              </p>
              <p class="text-gray-500 dark:text-gray-400">
                평가: ${item.shareholder.portfolioValue}
              </p>
            </div>
          </div>
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
            loadMarketDetail(marketId);
          });
        });
    } catch (e) {
      console.error(e);
      joinedMarketsEl.innerHTML = `
        <li class="px-2 py-1 text-xs text-red-500">마켓 목록을 불러오지 못했습니다.</li>
      `;
    }
  }

  // -------- 마켓 상세 (/manage/markets/<market_id>) + 회사 리스트 --------
  async function loadMarketDetail(marketId) {
    const token = getToken();
    if (!token) {
      if (marketNameEl) marketNameEl.textContent = "로그인이 필요합니다.";
      return;
    }

    showMarketPanel();

    try {
      const res = await fetch(`/manage/markets/${marketId}`, {
        headers: { Authorization: "Bearer " + token },
      });
      const data = await res.json();

      if (!res.ok) {
        console.error("loadMarketDetail error:", data);
        if (marketNameEl)
          marketNameEl.textContent = "마켓 정보를 불러오지 못했습니다.";
        return;
      }

      // 중앙 마켓 정보
      if (marketNameEl) marketNameEl.textContent = data.name || "마켓";
      if (marketCreatedAtEl)
        marketCreatedAtEl.textContent = data.createdAt
          ? `생성일: ${data.createdAt}`
          : "-";

      const participants = Array.isArray(data.participants)
        ? data.participants
        : [];
      if (marketParticipantsCountEl)
        marketParticipantsCountEl.textContent = String(participants.length);

      if (marketParticipantsListEl) {
        if (participants.length === 0) {
          marketParticipantsListEl.innerHTML =
            '<p class="text-xs text-gray-500">참가자가 없습니다.</p>';
        } else {
          marketParticipantsListEl.innerHTML = participants
            .map(
              (p) => `
            <div class="flex items-center justify-between text-xs py-1 border-b border-gray-200/40 dark:border-gray-700/40">
              <span class="text-gray-700 dark:text-gray-200">
                ${p.userNickname}
              </span>
              <span class="text-gray-500 dark:text-gray-400">
                평가: ${p.portfolioValue}
              </span>
            </div>
          `
            )
            .join("");
        }
      }

      // ADMIN이면 회사 생성 버튼 보이기
      if (btnCreateCompanyMain) {
        if (data.isAdmin) {
          btnCreateCompanyMain.classList.remove("hidden");
          btnCreateCompanyMain.onclick = () => {
            window.location.href = `/markets/${marketId}/companies/new`;
          };
        } else {
          btnCreateCompanyMain.classList.add("hidden");
          btnCreateCompanyMain.onclick = null;
        }
      }

      // 상장 회사 테이블
      const companies = Array.isArray(data.companies) ? data.companies : [];
      if (!companyTableBody) return;

      if (companies.length === 0) {
        companyTableBody.innerHTML = `
          <tr>
            <td colspan="3" class="px-2 py-2 text-xs text-gray-500">
              상장 회사가 없습니다.
            </td>
          </tr>
        `;
      } else {
        companyTableBody.innerHTML = companies
          .map(
            (c) => `
          <tr
            class="company-row cursor-pointer hover:bg-primary/5"
            data-company-id="${c.id}"
          >
            <td class="px-2 py-1 text-xs font-semibold text-gray-900 dark:text-white">
              ${c.ticker || ""}
            </td>
            <td class="px-2 py-1 text-xs text-gray-700 dark:text-gray-200">
              ${c.name}
            </td>
            <td class="px-2 py-1 text-xs text-right text-gray-900 dark:text-white">
              ${c.currentPrice}
            </td>
          </tr>
        `
          )
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
      }
    } catch (e) {
      console.error(e);
      if (marketNameEl)
        marketNameEl.textContent = "마켓 정보를 불러오지 못했습니다.";
    }
  }

  function clearCompanySelectionUI() {
    // 마켓 패널은 그대로, 회사 패널 초기화
    showMarketPanel();

    mainSymbol.textContent = "종목을 선택하세요";
    mainCompanyName.textContent = "-";
    mainPrice.textContent = "-";
    mainChangeText.textContent = "";

    csTicker.textContent = "-";
    csName.textContent = "-";
    csCurrent.textContent = "-";
    csIssued.textContent = "-";
    csChange.textContent = "0.00";
    csChangeRate.textContent = "0%";

    if (chartPlaceholder && priceChartCanvas) {
      chartPlaceholder.classList.remove("hidden");
      priceChartCanvas.classList.add("hidden");
    }

    if (orderResultEl) orderResultEl.textContent = "";
    if (orderbookArea)
      orderbookArea.textContent = "회사를 선택하면 호가가 표시됩니다.";
  }

  // -------- 회사 상세 (/manage/markets/<mid>/companies/<cid>) --------
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

      showCompanyPanel();

      mainSymbol.textContent = `${data.ticker} / USD`;
      mainCompanyName.textContent = data.name;
      mainPrice.textContent = data.currentPrice;

      const current = parseFloat(data.currentPrice);
      const issued = parseFloat(data.issuedPrice);
      const diff = current - issued;
      const rate = issued > 0 ? (diff / issued) * 100 : 0;
      const sign = diff > 0 ? "+" : diff < 0 ? "-" : "";
      const colorClass =
        diff > 0 ? "text-green-500" : diff < 0 ? "text-red-500" : "text-gray-500";

      mainChangeText.className = `text-md font-medium ${colorClass}`;
      mainChangeText.textContent = `${sign}${Math.abs(diff).toFixed(2)} (${sign}${Math.abs(
        rate
      ).toFixed(2)}%)`;

      csTicker.textContent = data.ticker;
      csName.textContent = data.name;
      csCurrent.textContent = data.currentPrice;
      csIssued.textContent = data.issuedPrice;
      csChange.textContent = diff.toFixed(2);
      csChangeRate.textContent = rate.toFixed(2) + "%";

      if (chartPlaceholder && priceChartCanvas) {
        chartPlaceholder.classList.add("hidden");
        priceChartCanvas.classList.remove("hidden");
        renderDummyChart();
      }

      await loadOrderBook(marketId, companyId);
    } catch (e) {
      console.error(e);
      alert("회사 상세 정보를 불러오지 못했습니다.");
    }
  }

  // -------- 더미 차트 --------
  function renderDummyChart() {
    if (!priceChartCanvas) return;
    const canvas = priceChartCanvas;
    const ctx = canvas.getContext("2d");
    const w = canvas.width || 400;
    const h = canvas.height || 200;

    canvas.width = w;
    canvas.height = h;

    ctx.clearRect(0, 0, w, h);

    ctx.strokeStyle = "#9ca3af";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(40, 10);
    ctx.lineTo(40, h - 30);
    ctx.lineTo(w - 10, h - 30);
    ctx.stroke();

    const points = 20;
    const minY = 20;
    const maxY = h - 50;
    ctx.strokeStyle = "#111827";
    ctx.beginPath();
    for (let i = 0; i < points; i++) {
      const x = 40 + ((w - 60) * i) / (points - 1);
      const y = minY + Math.random() * (maxY - minY);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }

  // -------- 호가 (/trade/orderbook) --------
  async function loadOrderBook(marketId, companyId) {
    const token = getToken();
    if (!token) {
      orderbookArea.innerHTML =
        '<p class="text-xs text-gray-500">로그인이 필요합니다.</p>';
      return;
    }

    try {
      const url = `/trade/orderbook?marketId=${encodeURIComponent(
        marketId
      )}&companyId=${encodeURIComponent(companyId)}`;
      const res = await fetch(url, {
        headers: { Authorization: "Bearer " + token },
      });
      const data = await res.json();

      if (!res.ok) {
        console.error("orderbook error:", data);
        orderbookArea.innerHTML =
          '<p class="text-xs text-red-500">호가 정보를 불러오지 못했습니다.</p>';
        return;
      }

      const bids = data.bids || [];
      const asks = data.asks || [];

      orderbookArea.innerHTML = `
        <div class="grid grid-cols-2 gap-3 text-xs">
          <div>
            <p class="mb-1 font-semibold text-gray-900 dark:text-white">매도(ASK)</p>
            ${
              asks.length === 0
                ? '<p class="text-gray-500">매도 호가 없음</p>'
                : `
              <table class="w-full border-collapse">
                <thead>
                  <tr class="text-[10px] text-gray-500">
                    <th class="px-1 py-0.5 text-right">가격</th>
                    <th class="px-1 py-0.5 text-right">수량</th>
                  </tr>
                </thead>
                <tbody>
                  ${asks
                    .map(
                      (a) => `
                    <tr>
                      <td class="px-1 py-0.5 text-right text-gray-900 dark:text-white">${a.price}</td>
                      <td class="px-1 py-0.5 text-right text-gray-700 dark:text-gray-200">${a.quantity}</td>
                    </tr>
                  `
                    )
                    .join("")}
                </tbody>
              </table>
            `
            }
          </div>
          <div>
            <p class="mb-1 font-semibold text-gray-900 dark:text-white">매수(BID)</p>
            ${
              bids.length === 0
                ? '<p class="text-gray-500">매수 호가 없음</p>'
                : `
              <table class="w-full border-collapse">
                <thead>
                  <tr class="text-[10px] text-gray-500">
                    <th class="px-1 py-0.5 text-right">가격</th>
                    <th class="px-1 py-0.5 text-right">수량</th>
                  </tr>
                </thead>
                <tbody>
                  ${bids
                    .map(
                      (b) => `
                    <tr>
                      <td class="px-1 py-0.5 text-right text-gray-900 dark:text-white">${b.price}</td>
                      <td class="px-1 py-0.5 text-right text-gray-700 dark:text-gray-200">${b.quantity}</td>
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
      orderbookArea.innerHTML =
        '<p class="text-xs text-red-500">호가 정보를 불러오지 못했습니다.</p>';
    }
  }

  // -------- 주문 (/trade/orders) --------
  if (btnBuy && btnSell && orderSideInput) {
    btnBuy.addEventListener("click", () => {
      orderSideInput.value = "BUY";
      btnBuy.classList.add("bg-green-500/30");
      btnSell.classList.remove("bg-red-500/30");
    });
    btnSell.addEventListener("click", () => {
      orderSideInput.value = "SELL";
      btnSell.classList.add("bg-red-500/30");
      btnBuy.classList.remove("bg-green-500/30");
    });
  }

  if (orderForm) {
    orderForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      if (!selectedMarketId || !selectedCompanyId) {
        alert("먼저 마켓과 회사를 선택해 주세요.");
        return;
      }

      const side = orderSideInput.value;
      const quantity = document.getElementById("order-quantity").value;
      const price = document.getElementById("order-price").value;

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

        await loadOrderBook(selectedMarketId, selectedCompanyId);
      } catch (err) {
        console.error(err);
        orderResultEl.textContent = "서버 오류가 발생했습니다.";
      }
    });
  }

  // 초기 실행
  loadMeAndInit();
})();
