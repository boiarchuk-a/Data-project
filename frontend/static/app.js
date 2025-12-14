(function () {
  const form = document.getElementById("scoreForm");

  const errorBox = document.getElementById("errorBox");
  const resultCard = document.getElementById("resultCard");

  const labelBadge = document.getElementById("labelBadge");
  const probText = document.getElementById("probText");
  const probBar = document.getElementById("probBar");
  const modelVersion = document.getElementById("modelVersion");
  const customerId = document.getElementById("customerId");
  const predictionId = document.getElementById("predictionId");
  const debugJson = document.getElementById("debugJson");

  function hide(el) { el.classList.add("hidden"); }
  function show(el) { el.classList.remove("hidden"); }

  async function safeReadJson(resp) {

    const ct = resp.headers.get("content-type") || "";
    if (ct.includes("application/json")) return await resp.json();
    const text = await resp.text();
    return { detail: text };
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    hide(errorBox);
    hide(resultCard);

    const Income = Number(document.getElementById("Income").value);
    const Recency = Number(document.getElementById("Recency").value);
    const MntWines = Number(document.getElementById("MntWines").value);

    const payload = { Income, Recency, MntWines };

    try {
      const resp = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await safeReadJson(resp);

      if (!resp.ok) {
        const msg = typeof data === "string"
          ? data
          : JSON.stringify(data, null, 2);

        errorBox.textContent = `Ошибка ${resp.status} — ${resp.statusText}\n\n${msg}`;
        show(errorBox);
        return;
      }

      // ---- успех ----
      const p = Number(data.probability ?? 0);
      const pct = Math.max(0, Math.min(100, p * 100));

      probText.textContent = `${pct.toFixed(2)}%`;
      probBar.style.width = `${pct}%`;

      const isPositive = Number(data.label) === 1;
      labelBadge.textContent = isPositive ? "Откликнется (1)" : "Не откликнется (0)";
      labelBadge.className = "badge " + (isPositive ? "badge-ok" : "badge-bad");

      modelVersion.textContent = data.model_version ?? "-";
      customerId.textContent = data.customer_id ?? "-";
      predictionId.textContent = data.prediction_id ?? "-";

      debugJson.textContent = JSON.stringify(data, null, 2);

      show(resultCard);
    } catch (err) {
      errorBox.textContent = "Ошибка запроса: " + (err?.message || String(err));
      show(errorBox);
    }
  });
})();
