// static/js/trade.js

(function () {
  const tradeRoot = document.getElementById("trade-root");
  if (!tradeRoot) return; // 이 페이지가 아니면 아무 것도 안 함

  const orderForm = document.getElementById("order-form");
  const orderResultEl = document.getElementById("order-result");
  const orderbookArea = document.getElementById("orderbook-area");

  function getToken() {
    return localStorage.getItem("accessToken");
  }

  // 호가창 로딩 (market.js 에서 회사 클릭 시 호출)
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
        <h3>호가창</h3>
        <div style="display:flex; gap:20px;">
          <div>
            <h4>매도(ASK)</h4>
            ${
              asks.length === 0
                ? "<p>매도 호가 없음</p>"
                : `
              <table border="1" cellpadding="4">
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
          <div>
            <h4>매수(BID)</h4>
            ${
              bids.length === 0
                ? "<p>매수 호가 없음</p>"
                : `
              <table border="1" cellpadding="4">
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

  // 전역 등록 → market.js 에서 호출
  window.loadOrderBook = loadOrderBook;

  // 주문 전송
  if (orderForm) {
    orderForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const marketId = tradeRoot.dataset.marketId;
      const companyId = tradeRoot.dataset.companyId;

      if (!companyId) {
        alert("먼저 회사를 선택해 주세요.");
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
            marketId,
            companyId,
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
        await loadOrderBook(marketId, companyId);
      } catch (err) {
        console.error(err);
        orderResultEl.textContent = "서버 오류가 발생했습니다.";
      }
    });
  }
})();
