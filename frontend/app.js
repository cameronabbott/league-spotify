const form = document.querySelector("#recommendation-form");
const riotIdInput = document.querySelector("#riot-id");
const regionInput = document.querySelector("#region");
const submitButton = document.querySelector("#submit-button");
const statusMessage = document.querySelector("#status-message");
const tracksList = document.querySelector("#tracks-list");
const clusterLabel = document.querySelector("#cluster-label");

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
}

function renderEmpty(message) {
  tracksList.innerHTML = "";
  const item = document.createElement("li");
  item.className = "empty-state";
  item.textContent = message;
  tracksList.appendChild(item);
}

function renderTracks(data) {
  tracksList.innerHTML = "";
  clusterLabel.textContent = data.cluster || "Generated";

  data.recommendations.forEach((track, index) => {
    const item = document.createElement("li");
    item.className = "track-item";

    const rank = document.createElement("span");
    rank.className = "track-rank";
    rank.textContent = index + 1;

    const meta = document.createElement("div");

    const name = document.createElement("p");
    name.className = "track-name";
    name.textContent = track.name;

    const artists = document.createElement("p");
    artists.className = "track-artists";
    artists.textContent = track.artists.join(", ");

    const link = document.createElement("a");
    link.className = "track-link";
    link.href = track.spotify_url;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = "Open";

    meta.append(name, artists);
    item.append(rank, meta, link);
    tracksList.appendChild(item);
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const riotId = riotIdInput.value.trim();
  const region = regionInput.value;

  if (!riotId.includes("#")) {
    setStatus("Use Riot ID format GameName#TAG.", true);
    riotIdInput.focus();
    return;
  }

  submitButton.disabled = true;
  setStatus("Checking match history and building recommendations...");
  renderEmpty("Loading tracks...");
  clusterLabel.textContent = "Working";

  try {
    const response = await fetch("/api/recommendations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        riot_id: riotId,
        region,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Recommendation request failed.");
    }

    renderTracks(data);
    setStatus(`Generated for ${data.riot_id} on ${data.region}.`);
  } catch (error) {
    renderEmpty("No tracks to show yet.");
    clusterLabel.textContent = "Try again";
    setStatus(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});
