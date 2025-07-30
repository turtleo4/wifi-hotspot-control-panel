document.addEventListener("DOMContentLoaded", function () {
  const refreshBtn = document.getElementById("refresh-status");
  if (!refreshBtn) return;

  refreshBtn.addEventListener("click", function () {
    fetch("/status")
      .then((res) => res.json())
      .then((data) => {
        updateWifiStatus(data.wifi);
        updateEthStatus(data.eth);
        updateScannedNetworks(data.scanned, data.known_visible);
        updateKnownHidden(data.known_hidden);
      })
      .catch((err) => console.error("Refresh error:", err));
  });

  function updateWifiStatus(info) {
    document.querySelector(".wifi-ssid").textContent = info.ssid || "N/A";
    document.querySelector(".wifi-ip").textContent = info.ip || "N/A";
    document.querySelector(".wifi-gateway").textContent = info.gateway || "N/A";
    document.querySelector(".wifi-dns").innerHTML =
      info.dns?.map((d) => `<li><strong>DNS:</strong> ${d}</li>`).join("") ||
      "";
  }

  function updateEthStatus(info) {
    document.querySelector(".eth-ip").textContent = info.ip || "N/A";
    document.querySelector(".eth-gateway").textContent = info.gateway || "N/A";
    document.querySelector(".eth-dns").innerHTML =
      info.dns?.map((d) => `<li><strong>DNS:</strong> ${d}</li>`).join("") ||
      "";
  }

  function updateScannedNetworks(networks, knownVisible) {
    const container = document.querySelector("#networks-container");
    container.innerHTML = "";
    networks.forEach((net) => {
      const known = knownVisible.find((k) => k.ssid === net.ssid);
      const pwd = known ? known.password : "";
      const secure = net.secure ? "🔒" : "🔓";
      const signal = net.signal;
      const html = `
                <div class="card network-card">
                    <form method="post" action="/connect">
                        <div class="network-header">
                            <strong>${net.ssid} ${secure}</strong>
                        </div>
                        <div class="signal-${signal}">
                            Signal: ${signal}
                        </div>
                        ${
                          net.secure
                            ? `<label>Password<input type="password" name="password" value="${pwd}"></label>`
                            : ""
                        }
                        <input type="hidden" name="ssid" value="${net.ssid}">
                        <input type="checkbox" name="save" ${
                          known ? "checked" : ""
                        }> Save
                        <button type="submit">Connect</button>
                    </form>
                </div>`;
      container.innerHTML += html;
    });
  }

  function updateKnownHidden(hidden) {
    const container = document.querySelector("#known-hidden-list");
    container.innerHTML = "";
    hidden.forEach((ssid) => {
      container.innerHTML += `<li>${ssid} <span class="not-found">(not found)</span></li>`;
    });
  }
});
