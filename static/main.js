// --- DATA SETTINGS ---
const issues = [
  { id: 1, title: 'Anna Salai Cave-in', category: 'Pothole', state: 'Tamil Nadu', city: 'Chennai', location: 'Anna Salai, Chennai', sev: 'red', votes: 1248, dept: 'PWD', lat: 13.0550, lng: 80.2417 },
  { id: 2, title: 'Juhu Beach Littering', category: 'Garbage Overflow', state: 'Maharashtra', city: 'Mumbai', location: 'Juhu, Mumbai', sev: 'amber', votes: 999, dept: 'Sanitation', lat: 19.1003, lng: 72.8260 },
  { id: 3, title: 'Dark Zone Hazard', category: 'Streetlight', state: 'Karnataka', city: 'Bangalore', location: 'MG Road, Bangalore', sev: 'amber', votes: 342, dept: 'BESCOM', lat: 12.9752, lng: 77.6063 },
  { id: 4, title: 'Main Pipe Burst', category: 'Water Leak', state: 'Maharashtra', city: 'Pune', location: 'FC Road, Pune', sev: 'amber', votes: 671, dept: 'Water Dept', lat: 18.5204, lng: 73.8567 },
  { id: 5, title: 'Road Crack Hazard', category: 'Pothole', state: 'Tamil Nadu', city: 'Chennai', location: 'Nungambakkam, Chennai', sev: 'red', votes: 1104, dept: 'PWD', lat: 13.0569, lng: 80.2425 },
  { id: 6, title: 'Connaught Sewage Leak', category: 'Drainage', state: 'Delhi', city: 'New Delhi', location: 'Connaught Place, Delhi', sev: 'red', votes: 1380, dept: 'MCD', lat: 28.6315, lng: 77.2167 },
];

const locationData = {
  "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
  "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
  "Karnataka": ["Bangalore", "Mysore"],
  "Delhi": ["New Delhi"]
};

let selectedState = '';
let selectedCity = '';
let voted = {};
let vMap = null;
let mapMarkers = [];

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
  initFilters();
  initVoteMap();
  renderVotes();
});

// --- FILTER CONTROLS ---
function initFilters() {
  const stateSel = document.getElementById('state-select');
  stateSel.innerHTML = '<option value="">All States</option>' + 
    Object.keys(locationData).map(st => `<option value="${st}">${st}</option>`).join('');
}

function handleStateChange(val) {
  selectedState = val;
  selectedCity = '';
  const citySel = document.getElementById('city-select');
  
  if (val && locationData[val]) {
    citySel.disabled = false;
    citySel.innerHTML = '<option value="">All Cities</option>' + 
      locationData[val].map(ct => `<option value="${ct}">${ct}</option>`).join('');
  } else {
    citySel.disabled = true;
    citySel.innerHTML = '<option value="">All Cities</option>';
  }
  
  renderVotes();
  updateVoteMap();
}

function handleCityChange(val) {
  selectedCity = val;
  renderVotes();
  updateVoteMap();
}

// --- VOTE ACTION ---
function castVote(id) {
  if (voted[id]) return;
  voted[id] = true;
  const target = issues.find(i => i.id === id);
  if (target) {
    target.votes += 1;
  }
  renderVotes();
  updateVoteMap();
}

// --- RENDER ISSUE CARDS ---
function renderVotes() {
  const filtered = issues.filter(i => {
    if (i.sev === 'green') return false;
    const matchState = !selectedState || i.state === selectedState;
    const matchCity = !selectedCity || i.city === selectedCity;
    return matchState && matchCity;
  });

  const grid = document.getElementById('vote-grid');
  
  if (filtered.length === 0) {
    grid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-dim); padding: 3rem;">No issues found for the selected State/City filter.</div>`;
    return;
  }

  grid.innerHTML = filtered.map(i => {
    const pct = Math.min((i.votes / 1000) * 100, 100).toFixed(0);
    const esc = i.votes >= 1000;
    
    return `
      <div class="vote-card ${esc ? 'esc' : ''}">
        ${esc ? '<div class="esc-tag">ESCALATED</div>' : ''}
        
        <div class="vc-top">
          <span class="sev-tag ${i.sev === 'red' ? 'high' : 'medium'}">● ${i.sev === 'red' ? 'HIGH' : 'MEDIUM'} SEVERITY</span>
          <span class="badge ${esc ? 'red' : 'amber'}">${esc ? '🚨 RED ALERT' : 'NORMAL QUEUE'}</span>
        </div>
        
        <!-- ISSUE CATEGORY BADGE -->
        <div style="margin-top: 0.6rem;">
          <span class="badge-category">${i.category}</span>
        </div>

        <h3 style="margin-top: 0.4rem;">${i.title}</h3>
        <div class="loc">📍 ${i.location}</div>

        <div class="vpm">
          <span class="vc-num">${i.votes.toLocaleString()} / 1000 Votes</span>
          <span>${pct}%</span>
        </div>

        <div class="progress-track">
          <div class="progress-fill" style="width: ${pct}%"></div>
        </div>

        <button 
          class="vote-action ${voted[i.id] ? 'done' : ''}" 
          style="margin-top: 1.2rem;" 
          onclick="castVote(${i.id})">
          ${voted[i.id] ? '✅ Voted' : '⬆ VOTE ISSUE'}
        </button>
      </div>
    `;
  }).join('');
}

// --- MAP FUNCTIONS (BRIGHT CARTODB MAP) ---
function initVoteMap() {
  // Center near India by default
  vMap = L.map('vote-map').setView([20.5937, 78.9629], 5);

  // CartoDB Voyager Bright Map Tile Layer
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    maxZoom: 19
  }).addTo(vMap);

  updateVoteMap();
}

function updateVoteMap() {
  if (!vMap) return;

  // Clear existing markers
  mapMarkers.forEach(m => vMap.removeLayer(m));
  mapMarkers = [];

  const filtered = issues.filter(i => {
    if (i.sev === 'green') return false;
    const matchState = !selectedState || i.state === selectedState;
    const matchCity = !selectedCity || i.city === selectedCity;
    return matchState && matchCity;
  });

  const bounds = [];

  filtered.forEach(i => {
    const marker = L.circleMarker([i.lat, i.lng], {
      radius: 8,
      fillColor: i.sev === 'red' ? '#e53935' : '#fb8c00',
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.9
    }).addTo(vMap);

    marker.bindPopup(`
      <strong style="font-size: 1rem;">${i.title}</strong><br/>
      <span style="color: #666; font-size: 0.8rem;">Category: <b>${i.category}</b></span><br/>
      <span style="color: #666; font-size: 0.8rem;">📍 ${i.location}</span><br/>
      <span style="font-size: 0.85rem; font-weight: bold; color: #333;">Votes: ${i.votes}</span>
    `);

    mapMarkers.push(marker);
    bounds.push([i.lat, i.lng]);
  });

  // Fit map view around filtered markers
  if (bounds.length > 0) {
    vMap.fitBounds(bounds, { padding: [40, 40], maxZoom: 13 });
  }
}