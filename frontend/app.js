const PREVIEW_TRACK_COUNT = 7;
const FULL_TRACK_COUNT = 15;
const STORAGE_KEY = "league-spotify:lastRecommendation";

const form = document.querySelector("#recommendation-form");
const riotIdInput = document.querySelector("#riot-id");
const regionInput = document.querySelector("#region");
const submitButton = document.querySelector("#submit-button");
const statusMessage = document.querySelector("#status-message");
const tracksList = document.querySelector("#tracks-list");
const clusterLabel = document.querySelector("#cluster-label");
const traitsPanel = document.querySelector("#traits-panel");
const traitsList = document.querySelector("#traits-list");
const genreExplanation = document.querySelector("#genre-explanation");
const tracksCount = document.querySelector("#tracks-count");
const fullPlaylistButton = document.querySelector("#full-playlist-button");
const playlistLink = document.querySelector("#playlist-link");

let currentRecommendation = null;
let spotifyAuthenticated = false;

const TRAIT_ORDER = ["aggression", "stability", "teamwork", "control", "scaling"];

const TRAIT_LABELS = {
  aggression: "Aggression",
  stability: "Stability",
  teamwork: "Teamwork",
  control: "Control",
  scaling: "Scaling",
};

const TRAIT_DESCRIPTIONS = {
  aggression: {
    low: "You play safe and pick fights carefully.",
    mid: "You mix pressure with patience in lane and skirmishes.",
    high: "You force fights and snowball whenever you see an opening.",
  },
  stability: {
    low: "Your games swing hard — high risk, high reward.",
    mid: "You stay reasonably consistent across games.",
    high: "You rarely throw leads and keep games under control.",
  },
  teamwork: {
    low: "You prefer solo carry lines and independent picks.",
    mid: "You join key fights without over-committing.",
    high: "You play around your team and show up for every objective.",
  },
  control: {
    low: "You focus on fighting over map control.",
    mid: "You balance vision and tempo with combat.",
    high: "You dictate the map with vision and objective setups.",
  },
  scaling: {
    low: "You want early impact and fast-paced games.",
    mid: "You can play both early skirmishes and late teamfights.",
    high: "You farm up and win through late-game scaling.",
  },
};

const TRAIT_LEVELS = {
  low: { max: 0.34, label: "Low" },
  mid: { max: 0.67, label: "Mid" },
  high: { max: 1, label: "High" },
};

const GENRE_REASONS = {
  pop: "catchy, balanced energy that fits versatile playstyles",
  kpop: "polished, high-energy production with strong momentum",
  jpop: "bright melodies with focused, rhythmic drive",
  hiphop: "confident groove and bounce from your tempo profile",
  rap: "sharp, assertive rhythm that matches a front-foot playstyle",
  trap: "hard-hitting low end and urgency from high aggression",
  drill: "dark, aggressive cadence aligned with fight-first tendencies",
  edm: "big drops and high energy from your combat intensity",
  electronic: "intense, synthetic drive for fast-paced decision making",
  house: "steady four-on-the-floor pulse with teamfight flow",
  techno: "relentless tempo for high-control, high-pressure games",
  rock: "raw momentum that suits all-in, volatile match histories",
  alternative: "edgy, mid-energy texture for unpredictable lanes",
  indie: "laid-back but purposeful feel for measured scaling",
  chillhop: "calm, low-aggression vibes for safe, steady games",
  downtempo: "slow-burn atmosphere for controlled, patient play",
};

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
}

function getTraitLevel(value) {
  if (value <= TRAIT_LEVELS.low.max) {
    return "low";
  }
  if (value <= TRAIT_LEVELS.mid.max) {
    return "mid";
  }
  return "high";
}

function getTraitLevelLabel(value) {
  return TRAIT_LEVELS[getTraitLevel(value)].label;
}

function getTopTraits(personalityVector) {
  return TRAIT_ORDER.map((trait) => ({
    trait,
    value: personalityVector[trait] ?? 0,
  }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 2);
}

function buildGenreExplanation(cluster, personalityVector) {
  const topTraits = getTopTraits(personalityVector);
  const dominant = topTraits
    .map(({ trait, value }) => `${getTraitLevelLabel(value).toLowerCase()} ${TRAIT_LABELS[trait].toLowerCase()}`)
    .join(" and ");
  const genreReason = GENRE_REASONS[cluster] || "a sound profile that matches your recent ranked games";
  return `${cluster.toUpperCase()} was picked because your ${dominant} playstyle maps to ${genreReason}.`;
}

function renderTraits(data) {
  const personality = data.personality_vector;
  if (!personality) {
    traitsPanel.classList.add("hidden");
    return;
  }

  traitsPanel.classList.remove("hidden");
  traitsList.innerHTML = "";
  genreExplanation.textContent = buildGenreExplanation(data.cluster, personality);

  TRAIT_ORDER.forEach((trait) => {
    const value = personality[trait] ?? 0;
    const level = getTraitLevel(value);
    const levelLabel = TRAIT_LEVELS[level].label;
    const percent = Math.round(value * 100);

    const item = document.createElement("article");
    item.className = "trait-item";

    item.innerHTML = `
      <div class="trait-top">
        <span class="trait-name">${TRAIT_LABELS[trait]}</span>
        <span class="trait-level trait-level-${level}">${levelLabel}</span>
      </div>
      <div class="trait-slider" aria-hidden="true">
        <div class="trait-slider-fill" style="width: ${percent}%"></div>
      </div>
      <p class="trait-copy">${TRAIT_DESCRIPTIONS[trait][level]}</p>
    `;

    traitsList.appendChild(item);
  });
}

function renderEmpty(message) {
  tracksList.innerHTML = "";
  const item = document.createElement("li");
  item.className = "empty-state";
  item.textContent = message;
  tracksList.appendChild(item);
  tracksCount.textContent = message;
  fullPlaylistButton.classList.add("hidden");
  playlistLink.classList.add("hidden");
}

function getSpotifyTrackId(url) {
  return url.split("/track/")[1]?.split("?")[0];
}

function createTrackEmbed(track, rank) {
  const item = document.createElement("li");
  item.className = "track-item";

  const rankEl = document.createElement("span");
  rankEl.className = "track-rank";
  rankEl.textContent = String(rank);
  item.appendChild(rankEl);

  const trackId = getSpotifyTrackId(track.spotify_url);
  if (trackId) {
    const embed = document.createElement("iframe");
    embed.src = `https://open.spotify.com/embed/track/${trackId}?utm_source=generator&theme=0`;
    embed.loading = "lazy";
    embed.allow = "autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture";
    embed.title = `${track.name} by ${track.artists.join(", ")}`;
    item.appendChild(embed);
  }

  return item;
}

function renderTracks(data, showFullPlaylist = false) {
  currentRecommendation = data;
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));

  tracksList.innerHTML = "";
  clusterLabel.textContent = data.cluster || "Generated";
  renderTraits(data);

  const totalAvailable = data.recommendations.length;
  const visibleCount = showFullPlaylist
    ? Math.min(FULL_TRACK_COUNT, totalAvailable)
    : Math.min(PREVIEW_TRACK_COUNT, totalAvailable);

  data.recommendations.slice(0, visibleCount).forEach((track, index) => {
    tracksList.appendChild(createTrackEmbed(track, index + 1));
  });

  const hasMoreTracks = totalAvailable > PREVIEW_TRACK_COUNT;
  if (showFullPlaylist) {
    tracksCount.textContent = `Showing ${visibleCount} of ${totalAvailable} recommended tracks.`;
    fullPlaylistButton.classList.add("hidden");
  } else if (hasMoreTracks) {
    tracksCount.textContent = `Previewing top ${visibleCount} tracks. Log in with Spotify for the full playlist.`;
    fullPlaylistButton.classList.remove("hidden");
  } else {
    tracksCount.textContent = `Showing ${visibleCount} recommended tracks.`;
    fullPlaylistButton.classList.add("hidden");
  }
}

async function checkSpotifyStatus() {
  try {
    const response = await fetch("/api/spotify/status");
    if (!response.ok) {
      return false;
    }
    const data = await response.json();
    return Boolean(data.authenticated);
  } catch {
    return false;
  }
}

async function createSpotifyPlaylist(data) {
  const trackIds = data.recommendations
    .slice(0, FULL_TRACK_COUNT)
    .map((track) => track.spotify_id || getSpotifyTrackId(track.spotify_url))
    .filter(Boolean);

  const response = await fetch("/api/spotify/create-playlist", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      track_ids: trackIds,
      riot_id: data.riot_id,
      cluster: data.cluster,
    }),
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || "Could not create Spotify playlist.");
  }

  return payload;
}

function showPlaylistLink(url, name) {
  playlistLink.classList.remove("hidden");
  playlistLink.innerHTML = `Saved to Spotify: <a href="${url}" target="_blank" rel="noopener noreferrer">${name}</a>`;
}

async function unlockFullPlaylist() {
  if (!currentRecommendation) {
    return;
  }

  if (!spotifyAuthenticated) {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(currentRecommendation));
    window.location.href = "/api/spotify/login";
    return;
  }

  renderTracks(currentRecommendation, true);
  setStatus("Spotify connected. Building your full playlist...");

  try {
    const playlist = await createSpotifyPlaylist(currentRecommendation);
    showPlaylistLink(playlist.playlist_url, playlist.playlist_name);
    setStatus(`Full playlist ready for ${currentRecommendation.riot_id}.`);
  } catch (error) {
    renderTracks(currentRecommendation, true);
    setStatus(error.message, true);
  }
}

async function handleOAuthReturn() {
  const params = new URLSearchParams(window.location.search);
  const authResult = params.get("spotify_auth");
  if (!authResult) {
    return;
  }

  window.history.replaceState({}, "", window.location.pathname);

  if (authResult === "error") {
    setStatus("Spotify login failed. Try again.", true);
    return;
  }

  spotifyAuthenticated = true;

  const stored = sessionStorage.getItem(STORAGE_KEY);
  if (!stored) {
    setStatus("Spotify connected. Generate a playlist to unlock the full track list.");
    return;
  }

  currentRecommendation = JSON.parse(stored);
  renderTracks(currentRecommendation, true);
  setStatus("Spotify connected. Creating your full playlist...");

  try {
    const playlist = await createSpotifyPlaylist(currentRecommendation);
    showPlaylistLink(playlist.playlist_url, playlist.playlist_name);
    setStatus(`Full playlist saved for ${currentRecommendation.riot_id}.`);
  } catch (error) {
    setStatus(error.message, true);
  }
}

fullPlaylistButton.addEventListener("click", unlockFullPlaylist);

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
  traitsPanel.classList.add("hidden");
  clusterLabel.textContent = "Working";
  playlistLink.classList.add("hidden");

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

    renderTracks(data, spotifyAuthenticated);
    setStatus(`Generated for ${data.riot_id} on ${data.region}.`);
  } catch (error) {
    renderEmpty("No tracks to show yet.");
    traitsPanel.classList.add("hidden");
    clusterLabel.textContent = "Try again";
    setStatus(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});

(async function init() {
  spotifyAuthenticated = await checkSpotifyStatus();
  await handleOAuthReturn();
})();
