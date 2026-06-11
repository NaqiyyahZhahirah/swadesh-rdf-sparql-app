const API = window.API_BASE || 'http://localhost:5000';

function renderTable(selector, rows) {
  if ($.fn.DataTable.isDataTable(selector)) {
    $(selector).DataTable().clear().destroy();
  }
  const tbody = $(`${selector} tbody`);
  tbody.empty();
  rows.forEach((r, i) => {
    const tr = $('<tr>');
    tr.append(`<td>${i+1}</td>`);
    tr.append(`<td>${r.konsep || ''}</td>`);
    tr.append(`<td>${r.bahasaIndo || ''}</td>`);
    tr.append(`<td>${r.bahasaSunda || ''}</td>`);
    tr.append(`<td>${r.bahasaMelayu || ''}</td>`);
    tbody.append(tr);
  });
  $(selector).DataTable({
    paging: true,
    searching: true,
    info: false,
    lengthChange: false
  });
}

async function fetchJson(path) {
  const res = await fetch(API + path);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// Dashboard
async function loadDashboard() {
  try {
    const data = await fetchJson('/get-data');
    renderTable('#data-table', data);
  } catch (e) {
    alert('Error memuat data: ' + e.message);
  }
}

// Languages & Concepts
async function loadLanguages() {
  try {
    const langs = await fetchJson('/languages');
    const sel = $('#lang-select');
    sel.empty();
    sel.append('<option value="">-- Filter bahasa --</option>');
    langs.forEach(l => sel.append(`<option value="${l.kode}">${l.nama} (${l.kode})</option>`));
  } catch (e) {
    console.warn('Could not load languages', e);
  }
}

async function loadConcepts() {
  try {
    const concepts = await fetchJson('/concepts');
    const sel = $('#concepts-select');
    sel.empty();
    sel.append('<option value="">-- Pilih konsep --</option>');
    concepts.forEach(c => sel.append(`<option value="${c}">${c}</option>`));
  } catch (e) {
    console.warn('Could not load concepts', e);
  }
}

// Search
async function doSearch(keyword) {
  try {
    const data = await fetchJson('/search?keyword=' + encodeURIComponent(keyword));
    renderTable('#search-table', data);
  } catch (e) {
    alert('Error saat search: ' + e.message);
  }
}

// Filter
async function doFilter(lang) {
  try {
    const res = await fetchJson('/filter?lang=' + encodeURIComponent(lang));
    // res: { bahasa, kode, jumlah, data }
    const rows = res.data.map(item => {
      const r = {konsep: item.konsep, bahasaIndo: '', bahasaSunda: '', bahasaMelayu: ''};
      if (res.kode === 'id') r.bahasaIndo = item.kata;
      if (res.kode === 'su') r.bahasaSunda = item.kata;
      if (res.kode === 'mel') r.bahasaMelayu = item.kata;
      return r;
    });
    renderTable('#search-table', rows);
  } catch (e) {
    alert('Filter error: ' + e.message);
  }
}

// Graph
async function loadGraph(concept) {
  try {
    const path = concept ? ('/graph-data?concept=' + encodeURIComponent(concept)) : '/graph-data';
    const json = await fetchJson(path);
    const nodes = json.nodes || [];
    const edges = json.edges || [];

    const palette = {
      concept: '#8BA3C5',
      id: '#496B7D',
      su: '#6B8E9F',
      mel: '#02122F'
    };

    const elements = [];
    nodes.forEach(n => {
      const d = Object.assign({}, n.data);
      if (d.type === 'concept') d.color = palette.concept;
      else d.color = palette[d.language] || '#ffffff';
      elements.push({ data: d, classes: d.type });
    });
    edges.forEach(e => elements.push({ data: e.data }));

    // init cytoscape
    document.getElementById('cy').innerHTML = '';
    const cy = cytoscape({
      container: document.getElementById('cy'),
      elements: elements,
      style: [
        { selector: 'node', style: { 'label': 'data(label)', 'text-valign': 'center', 'text-halign': 'center', 'color': '#fff', 'font-size': 10, 'text-outline-width': 3, 'text-outline-color': '#02122F' } },
        { selector: '.concept', style: { 'width': 80, 'height': 80, 'background-color': 'data(color)', 'shape': 'ellipse', 'border-color': '#fff', 'border-width': 3 } },
        { selector: '.word', style: { 'width': 62, 'height': 62, 'background-color': 'data(color)', 'shape': 'roundrectangle', 'border-color': '#fff', 'border-width': 2, 'text-wrap': 'wrap', 'text-max-width': 90 } },
        { selector: 'edge', style: { 'width': 2, 'line-color': '#496B7D', 'target-arrow-shape': 'triangle', 'target-arrow-color': '#496B7D', 'curve-style': 'bezier', 'label': 'data(label)', 'font-size': 8, 'text-rotation': 'autorotate', 'text-margin-y': -8, 'color': '#02122F', 'text-background-color': '#ffffff', 'text-background-opacity': 0.8, 'text-background-padding': 3 } }
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 500,
        nodeRepulsion: 4500,
        idealEdgeLength: 120,
        edgeElasticity: 0.8,
        gravity: 0.1,
        numIter: 150
      }
    });

    cy.on('tap', 'node', (evt) => {
      const n = evt.target;
      alert(`${n.data('label')}\nType: ${n.data('type') || ''}${n.data('language') ? '\nLanguage: ' + n.data('language') : ''}`);
    });

  } catch (e) {
    alert('Gagal memuat graph: ' + e.message);
  }
}

// Init
$(document).ready(function(){
  loadDashboard();
  loadLanguages();
  loadConcepts();

  $('#search-btn').on('click', ()=>{
    const kw = $('#search-input').val().trim();
    if (!kw) return alert('Masukkan kata untuk mencari.');
    doSearch(kw);
    // switch to search tab
    var tab = new bootstrap.Tab(document.querySelector('#mainTabs a[href="#search"]'));
    tab.show();
  });

  $('#lang-select').on('change', function(){
    const v = $(this).val();
    if (!v) return;
    doFilter(v);
    var tab = new bootstrap.Tab(document.querySelector('#mainTabs a[href="#search"]'));
    tab.show();
  });

  $('#clear-filter').on('click', function(){
    $('#lang-select').val('');
    $('#search-input').val('');
    if ($.fn.DataTable.isDataTable('#search-table')) $('#search-table').DataTable().clear().destroy();
  });

  $('#load-graph').on('click', ()=>{
    const c = $('#concepts-select').val();
    loadGraph(c);
    var tab = new bootstrap.Tab(document.querySelector('#mainTabs a[href="#graph"]'));
    tab.show();
  });
});
