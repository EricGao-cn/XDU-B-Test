const cityNameEl = document.getElementById("city-name");
const provinceValueEl = document.getElementById("province-value");
const districtValueEl = document.getElementById("district-value");
const longitudeValueEl = document.getElementById("longitude-value");
const latitudeValueEl = document.getElementById("latitude-value");
const sourceBadgeEl = document.getElementById("source-badge");
const statusTextEl = document.getElementById("status-text");
const locateButtonEl = document.getElementById("locate-button");
const detailsLinkEl = document.getElementById("details-link");

let mapScriptPromise;

function setStatus(message, type = "muted") {
  statusTextEl.textContent = message;
  sourceBadgeEl.className = `badge ${type === "muted" ? "muted" : ""}`.trim();
}

function renderLocation(location) {
  cityNameEl.textContent = location.city || "未定位";
  provinceValueEl.textContent = location.province || "-";
  districtValueEl.textContent = location.district || "-";
  longitudeValueEl.textContent =
    location.longitude === null || location.longitude === undefined
      ? "-"
      : Number(location.longitude).toFixed(4);
  latitudeValueEl.textContent =
    location.latitude === null || location.latitude === undefined
      ? "-"
      : Number(location.latitude).toFixed(4);
  sourceBadgeEl.textContent = location.source === "ip" ? "IP 兜底定位" : "精确定位";
  detailsLinkEl.classList.remove("disabled");
  detailsLinkEl.removeAttribute("aria-disabled");
}

function ensureBaiduMapScript() {
  if (window.BMap) {
    return Promise.resolve(window.BMap);
  }

  if (!window.APP_CONFIG.baiduMapAk) {
    return Promise.reject(new Error("缺少 BAIDU_MAP_AK，无法加载百度地图定位。"));
  }

  if (!mapScriptPromise) {
    mapScriptPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = `https://api.map.baidu.com/api?v=3.0&ak=${encodeURIComponent(
        window.APP_CONFIG.baiduMapAk
      )}`;
      script.async = true;
      script.onload = () => resolve(window.BMap);
      script.onerror = () => reject(new Error("百度地图脚本加载失败"));
      document.head.appendChild(script);
    });
  }

  return mapScriptPromise;
}

function detectPreciseLocation() {
  return new Promise((resolve, reject) => {
    const geolocation = new window.BMap.Geolocation();
    geolocation.enableSDKLocation();
    geolocation.getCurrentPosition(
      function onPosition(result) {
        if (this.getStatus() !== window.BMAP_STATUS_SUCCESS) {
          reject(new Error("精确定位失败"));
          return;
        }

        resolve({
          city: (result.address && result.address.city) || "",
          province: (result.address && result.address.province) || "",
          district: (result.address && result.address.district) || "",
          longitude: result.point ? result.point.lng : null,
          latitude: result.point ? result.point.lat : null,
          source: "gps",
          locatedAt: new Date().toISOString()
        });
      },
      {
        enableHighAccuracy: true
      }
    );
  });
}

function detectLocationByIp() {
  return new Promise((resolve, reject) => {
    const localCity = new window.BMap.LocalCity();
    localCity.get((result) => {
      if (!result || !result.name) {
        reject(new Error("IP 城市定位失败"));
        return;
      }

      resolve({
        city: result.name,
        province: "",
        district: "",
        longitude: result.center ? result.center.lng : null,
        latitude: result.center ? result.center.lat : null,
        source: "ip",
        locatedAt: new Date().toISOString()
      });
    });
  });
}

async function saveLocation(payload) {
  const response = await fetch("/api/location", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  if (!response.ok || !data.ok) {
    throw new Error(data.message || "服务端保存定位失败");
  }

  return data.location;
}

async function locateAndSave() {
  locateButtonEl.disabled = true;
  setStatus("正在加载百度地图定位能力...");

  try {
    await ensureBaiduMapScript();
    setStatus("正在尝试精确定位...");

    let payload;
    try {
      payload = await detectPreciseLocation();
    } catch (error) {
      setStatus("精确定位失败，正在回退到 IP 城市定位...");
      payload = await detectLocationByIp();
    }

    setStatus("正在将定位城市保存到服务器...");
    const savedLocation = await saveLocation(payload);
    renderLocation(savedLocation);
    setStatus("定位成功，城市信息已保存到服务器。", "");
  } catch (error) {
    setStatus(error.message || "定位失败，请稍后重试。");
  } finally {
    locateButtonEl.disabled = false;
  }
}

locateButtonEl.addEventListener("click", locateAndSave);
