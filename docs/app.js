/* SlopeWatch front end. Every number shown is read from docs/data/*.json (built by pipeline/build.py). */
(function () {
  'use strict';
  const D = {};
  const state = { i: 0, layer: 'anom' };
  const $ = (id) => document.getElementById(id);

  function h(tag, attrs, ...kids) {
    const ns = ['svg', 'g', 'line', 'circle', 'rect', 'text', 'path', 'title'].includes(tag);
    const e = ns ? document.createElementNS('http://www.w3.org/2000/svg', tag) : document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') e.setAttribute('class', v);
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v);
    }
    for (const k of kids.flat()) if (k !== null && k !== undefined && k !== false) e.append(k.nodeType ? k : document.createTextNode(String(k)));
    return e;
  }
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const dt = (s) => new Date(Date.UTC(+s.slice(0, 4), +s.slice(4, 6) - 1, +s.slice(6, 8)));
  const fmtDay = (s, year) => `${+s.slice(6, 8)} ${MONTHS[+s.slice(4, 6) - 1]}${year ? ' ' + s.slice(0, 4) : ''}`;
  const fmtPair = (p, year) => `${fmtDay(p.start, p.start.slice(0, 4) !== p.end.slice(0, 4))} → ${fmtDay(p.end, year)}`;
  const f1 = (v) => (v === null || v === undefined ? '–' : v.toFixed(1));
  const f2 = (v) => (v === null || v === undefined ? '–' : v.toFixed(2));
  const pairById = (id) => D.manifest.pairs.findIndex((p) => p.id === id);

  async function load() {
    const names = ['manifest', 'flags', 'evaluation', 'series', 'collapse'];
    const got = await Promise.all(names.map((n) => fetch(`data/${n}.json`).then((r) => { if (!r.ok) throw new Error(n + '.json: HTTP ' + r.status); return r.json(); })));
    names.forEach((n, i) => { D[n] = got[i]; });
    D.outlines = await fetch('data/outlines.geojson').then((r) => r.json());
    D.sensitivity = await fetch('data/sensitivity.json').then((r) => (r.ok ? r.json() : null)).catch(() => null);
  }

  /* ---------- map ---------- */
  let map, radar, flagImg, flagMarks, outlines, evImg, quImg, bases;
  function initMap() {
    const [w, s, e, n] = D.manifest.bounds;
    const bounds = [[s, w], [n, e]];
    map = L.map('map', { zoomSnap: 0.25, attributionControl: true }).fitBounds(bounds);
    bases = {
      sat: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 17, attribution: 'Imagery © Esri and contributors (date of imagery varies; may predate the collapse)' }),
      topo: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', { maxZoom: 17, attribution: 'Map © OpenTopoMap (CC-BY-SA), data © OpenStreetMap contributors' }),
    };
    bases.sat.addTo(map);
    L.control.scale({ imperial: false }).addTo(map);
    map.createPane('radar').style.zIndex = 350;
    map.createPane('flags').style.zIndex = 420;
    radar = L.imageOverlay('', bounds, { pane: 'radar', opacity: 0.85 });
    flagImg = L.imageOverlay('', bounds, { pane: 'flags', opacity: 0.95 });
    evImg = L.imageOverlay('data/img/collapse_event.webp', bounds, { pane: 'radar', opacity: 0.85 });
    quImg = L.imageOverlay('data/img/collapse_quiet.webp', bounds, { pane: 'radar', opacity: 0.85 });
    flagMarks = L.layerGroup().addTo(map);
    const style = (f) => ({ unosat: { color: '#ffd400', weight: 2, fill: false }, patch: { color: '#00e5ff', weight: 2, fill: false }, reference: { color: '#ffffff', weight: 1.5, dashArray: '5 4', fill: false } }[f.properties.kind]);
    outlines = L.geoJSON(D.outlines, { style, onEachFeature: (f, l) => l.bindTooltip(f.properties.name, { sticky: true }) }).addTo(map);
    D.bounds = bounds;
  }

  function showPair() {
    const p = D.manifest.pairs[state.i];
    $('slider').value = state.i;
    $('slider').setAttribute('aria-valuetext', fmtPair(p, true));
    // radar layer
    if (state.layer === 'none') { map.removeLayer(radar); } else {
      radar.setUrl(`data/img/${p.id}_${state.layer}.webp`);
      if (!map.hasLayer(radar)) radar.addTo(map);
    }
    // flags
    flagMarks.clearLayers();
    if ($('ov-flags').checked) {
      flagImg.setUrl(`data/img/${p.id}_flag.webp`);
      if (!map.hasLayer(flagImg)) flagImg.addTo(map);
      (D.flags[p.id] || []).forEach((f, k) => {
        L.circleMarker([f.lonlat[1], f.lonlat[0]], { radius: 11, color: f.at_langtang ? '#ff6bd0' : '#ffffff', weight: 2, fill: false, pane: 'flags' })
          .bindTooltip(`Flag ${k + 1}: ${f.area_km2.toFixed(3)} km², mean step ${f.mean_abs_cm} cm equivalent${f.at_langtang ? ' — Langtang slope' : ''}`).addTo(flagMarks);
      });
    } else if (map.hasLayer(flagImg)) map.removeLayer(flagImg);
    // label
    const lab = $('pairlabel');
    lab.replaceChildren(...[
      h('span', { class: 'dates' }, fmtPair(p, true)),
      h('span', { class: 'tag' }, `${p.days} days apart`),
      h('span', { class: 'tag' }, `${Math.round(p.measurable_fraction * 100)}% of window measurable`),
      p.forward_processed ? h('span', { class: 'tag' }, 'processed at the time') : h('span', { class: 'tag warn' }, p.version === 'unknown' ? 'processing version not recorded' : 'reprocessed after the collapse'),
      !p.has_history ? h('span', { class: 'tag warn' }, 'too early in the record for flags') : h('span', { class: 'tag' + (p.flags_at_langtang ? ' flag' : '') }, `${p.flags} flag${p.flags === 1 ? '' : 's'}${p.flags_at_langtang ? `, ${p.flags_at_langtang} on the Langtang slope` : ''}`),
      p.end > '20260826' && p.start < '20260826' ? h('span', { class: 'tag warn' }, 'spans the collapse') : null,
    ].filter(Boolean));
    drawLegend();
    drawFlagTable();
    document.querySelectorAll('#yeartable tr.click').forEach((tr) => tr.classList.toggle('sel', +tr.dataset.i === state.i));
    document.querySelectorAll('#chart .pt').forEach((c) => c.setAttribute('stroke-width', +c.dataset.i === state.i ? 3 : 1));
  }

  function drawLegend() {
    const L_ = $('legend');
    const kids = [];
    const cm = (Math.PI * D.series.rad_to_cm).toFixed(1);
    if (state.layer === 'anom') kids.push(h('div', {}, 'Phase anomaly: local phase minus the surrounding 1.5 km. Blank where not measurable.'),
      h('div', { class: 'bar', style: 'background:linear-gradient(90deg,#2626ff,#fff,#ff2626)' }),
      h('div', { class: 'ends' }, h('span', {}, `−π (${cm} cm)`), h('span', {}, '0'), h('span', {}, `+π (${cm} cm)`)),
      h('div', {}, 'Line-of-sight equivalent. Which colour means toward or away from the satellite is not verified.'));
    if (state.layer === 'phase') kids.push(h('div', {}, 'Raw wrapped phase, dimmed where coherence is low. One full colour cycle = ' + (2 * Math.PI * D.series.rad_to_cm).toFixed(1) + ' cm along the line of sight.'),
      h('div', { class: 'bar', style: 'background:linear-gradient(90deg,#f00,#ff0,#0f0,#0ff,#00f,#f0f,#f00)' }),
      h('div', { class: 'ends' }, h('span', {}, '−π'), h('span', {}, '+π')));
    if (state.layer === 'coh') kids.push(h('div', {}, 'Coherence: how alike the two passes are. Dark = the surface changed too much to measure.'),
      h('div', { class: 'bar', style: 'background:linear-gradient(90deg,#000,#fff)' }), h('div', { class: 'ends' }, h('span', {}, '0'), h('span', {}, '1')));
    if ($('ov-event').checked || $('ov-quiet').checked) kids.push(h('div', { style: 'margin-top:8px' }, 'Radar brightness change (HH, 50 m average).'),
      h('div', { class: 'bar', style: 'background:linear-gradient(90deg,#2626ff,#fff,#ff2626)' }), h('div', { class: 'ends' }, h('span', {}, '−6 dB'), h('span', {}, '+6 dB')));
    kids.push(h('div', { class: 'key' }, h('span', { class: 'swatch', style: 'border-color:#00e5ff' }), 'Measured patch'),
      h('div', { class: 'key' }, h('span', { class: 'swatch', style: 'border-color:#ffd400' }), 'UNOSAT detachment zone (preliminary)'),
      h('div', { class: 'key' }, h('span', { class: 'swatch', style: 'border-color:#999;border-top-style:dashed' }), 'Reference rock'),
      h('div', { class: 'key' }, h('span', { class: 'swatch fill', style: 'background:#ff00c8' }), 'Flagged pixels'));
    L_.replaceChildren(...kids);
  }

  /* ---------- tables ---------- */
  function drawFlagTable() {
    const p = D.manifest.pairs[state.i];
    const fl = D.flags[p.id] || [];
    $('flags-title').textContent = `Flags in ${fmtPair(p, true)}`;
    if (!p.has_history) { $('flagtable').replaceChildren(h('p', { class: 'note' }, `The rule needs ${D.evaluation.params.history_pairs} earlier pairs. This pair is too early in the record.`)); return; }
    if (!fl.length) { $('flagtable').replaceChildren(h('p', { class: 'note' }, 'No flags in this pair.')); return; }
    const rows = fl.map((f, k) => h('tr', { class: 'click' + (f.at_langtang ? ' lang' : ''), tabindex: 0, role: 'button',
      onclick: () => zoomFlag(f), onkeydown: (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); zoomFlag(f); } } },
      h('td', { class: 'num' }, k + 1), h('td', { class: 'num' }, f.area_km2.toFixed(3)), h('td', { class: 'num' }, f.mean_abs_cm.toFixed(1)),
      h('td', {}, f.at_langtang ? 'Langtang slope' : `${f.lonlat[1].toFixed(4)}°N ${f.lonlat[0].toFixed(4)}°E`)));
    $('flagtable').replaceChildren(h('div', { class: 'tablebox' }, h('table', {},
      h('thead', {}, h('tr', {}, h('th', { class: 'num' }, '#'), h('th', { class: 'num' }, 'Area km²'), h('th', { class: 'num' }, 'Mean step, cm equiv.'), h('th', {}, 'Where'))),
      h('tbody', {}, rows))), h('p', { class: 'note' }, 'Select a row to zoom the map to that flag.'));
  }
  function zoomFlag(f) {
    const [w, s, e, n] = f.bbox;
    map.fitBounds([[s - 0.004, w - 0.004], [n + 0.004, e + 0.004]]);
    $('map').scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  function drawYearTable() {
    const rows = D.evaluation.rows;
    const max = Math.max(1, ...rows.map((r) => r.flags));
    const trs = rows.map((r, i) => {
      const other = r.flags - r.flags_at_langtang;
      return h('tr', { class: 'click', 'data-i': i, tabindex: 0, role: 'button', onclick: () => select(i), onkeydown: (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(i); } } },
        h('td', {}, fmtPair(D.manifest.pairs[i], true)), h('td', { class: 'num' }, r.days),
        h('td', { class: 'num' }, r.measurable_km2.toFixed(0)),
        h('td', {}, r.has_history ? [h('span', { class: 'bar-cell lang', style: `width:${(r.flags_at_langtang / max) * 90}px` }), h('span', { class: 'bar-cell', style: `width:${(other / max) * 90}px` }), `${r.flags}${r.flags_at_langtang ? ` (${r.flags_at_langtang} Langtang)` : ''}`] : '—'));
    });
    $('yeartable').replaceChildren(h('div', { class: 'tablebox' }, h('table', {},
      h('thead', {}, h('tr', {}, h('th', {}, 'Pair'), h('th', { class: 'num' }, 'Days'), h('th', { class: 'num' }, 'Measurable km²'), h('th', {}, 'Flags'))), h('tbody', {}, trs))));
    const s = D.evaluation.summary;
    $('yearsummary').textContent = `${s.pairs_with_history} pairs have enough history for the rule. Together they raise ${s.total_flags} flags (median ${s.median_flags_per_pair} per pair, most ${s.max_flags_per_pair}); ${s.flags_at_langtang_total} are on the Langtang slope. ` +
      `Outside Langtang that is about ${f1(s.mean_unverified_flags_per_100km2_eligible_per_pass)} unverified flags per 100 km² of eligible ground per pass. The window is ${D.evaluation.window_km2.toFixed(0)} km². The rule's settings were adjusted on the Langtang case, so its flagging Langtang is not an independent test.`;
  }
  function drawSensitivity() {
    const S = D.sensitivity;
    if (!S) { $('sensitivity').replaceChildren(h('p', { class: 'note' }, 'Sensitivity table not built yet.')); return; }
    const label = { flag_abs_anomaly_rad: 'Step needed to flag (rad)', quiet_abs_anomaly_rad: 'Quiet limit (rad)', min_blob_pixels: 'Smallest flag (pixels)', min_history_measurable: 'Quiet earlier pairs required', history_pairs: 'Earlier pairs examined', background_box: 'Background box (pixels of 20 m)' };
    const row = (name, val, s) => h('tr', {}, h('td', {}, name), h('td', { class: 'num' }, val), h('td', { class: 'num' }, s.total_flags), h('td', { class: 'num' }, s.flags_at_langtang_total), h('td', {}, s.pairs_with_langtang_flag.map((id) => fmtPair(D.manifest.pairs[pairById(id)])).join('; ') || 'none'));
    $('sensitivity').replaceChildren(h('div', { class: 'tablebox' }, h('table', {},
      h('thead', {}, h('tr', {}, h('th', {}, 'Setting changed'), h('th', { class: 'num' }, 'Value'), h('th', { class: 'num' }, 'All flags'), h('th', { class: 'num' }, 'On Langtang'), h('th', {}, 'Langtang flagged in'))),
      h('tbody', {}, row('Settings used', '', S.base), S.variants.map((v) => row(label[v.parameter] || v.parameter, v.value, v))))),
      h('p', { class: 'note' }, 'One setting changed at a time. All results are shown; none was chosen for looking best.'));
  }

  /* ---------- charts ---------- */
  function drawChart() {
    const rows = D.series.rows;
    const W = 980, H = 300, m = { l: 52, r: 16, t: 16, b: 58 };
    const t0 = dt(rows[0].start).getTime(), t1 = dt(rows[rows.length - 1].end).getTime();
    const X = (t) => m.l + ((t - t0) / (t1 - t0)) * (W - m.l - m.r);
    const ymax = Math.PI * D.series.rad_to_cm;
    const Y = (cm) => H - m.b - (cm / (ymax * 1.05)) * (H - m.t - m.b);
    const svg = h('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Phase step of the Langtang patch per radar pair' });
    for (let c = 0; c <= 6; c += 2) svg.append(h('line', { class: 'axis', x1: m.l, x2: W - m.r, y1: Y(c), y2: Y(c) }), h('text', { x: m.l - 8, y: Y(c) + 4, 'text-anchor': 'end' }, c));
    svg.append(h('line', { x1: m.l, x2: W - m.r, y1: Y(ymax), y2: Y(ymax), stroke: 'currentColor', 'stroke-dasharray': '2 4', opacity: .5 }),
      h('text', { x: W - m.r, y: Y(ymax) - 4, 'text-anchor': 'end' }, `largest readable step (half a cycle, ${ymax.toFixed(1)} cm)`),
      h('text', { x: 14, y: (H - m.b + m.t) / 2, transform: `rotate(-90 14 ${(H - m.b + m.t) / 2})`, 'text-anchor': 'middle' }, 'cm, line-of-sight equivalent'));
    // month ticks
    const d = new Date(t0); d.setUTCDate(1); d.setUTCMonth(d.getUTCMonth() + 1);
    for (; d.getTime() < t1; d.setUTCMonth(d.getUTCMonth() + 1)) {
      svg.append(h('line', { class: 'axis', x1: X(d.getTime()), x2: X(d.getTime()), y1: H - m.b, y2: H - m.b + 5 }),
        h('text', { x: X(d.getTime()), y: H - m.b + 17, 'text-anchor': 'middle' }, MONTHS[d.getUTCMonth()] + (d.getUTCMonth() === 0 ? ' ' + d.getUTCFullYear() : '')));
    }
    const tc = new Date(D.series.collapse_utc).getTime();
    svg.append(h('line', { x1: X(tc), x2: X(tc), y1: m.t, y2: H - m.b, stroke: 'var(--accent)', 'stroke-width': 2 }),
      h('text', { x: X(tc) + 5, y: m.t + 30, style: 'fill:var(--accent)' }, 'collapse, 26 Aug'));
    const strip = H - m.b + 34;
    svg.append(h('text', { x: m.l, y: strip + 16 }, '● Langtang patch    ┄ level that 95% of other slopes stay below in that pair    ○ pair could not be read on this patch'));
    rows.forEach((r) => {
      const i = pairById(r.pair);
      const a = dt(r.start).getTime(), b = dt(r.end).getTime(), xm = X((a + b) / 2);
      const w = r.refs['west block'];
      const all = Object.values(r.refs).filter((v) => v && v.reference_consistency >= 0.6).map((v) => Math.abs(v.los_cm));
      const click = { class: 'pt', 'data-i': i, tabindex: 0, role: 'button', onclick: () => select(i, true), onkeydown: (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(i, true); } } };
      if (r.resolved) {
        const v = Math.abs(w.los_cm);
        const cr = (D.series.control_ranks || {})[r.pair];
        if (cr && cr.control_p95 !== null) svg.append(h('line', { x1: X(a) + 2, x2: X(b) - 2, y1: Y(cr.control_p95 * D.series.rad_to_cm), y2: Y(cr.control_p95 * D.series.rad_to_cm), stroke: 'var(--muted)', 'stroke-width': 2, 'stroke-dasharray': '3 2' },
          h('title', {}, `95% of ${cr.n_controls} other slopes are below ${(cr.control_p95 * D.series.rad_to_cm).toFixed(1)} cm in this pair`)));
        svg.append(h('line', { x1: X(a), x2: X(b), y1: Y(v), y2: Y(v), stroke: 'var(--accent2)', 'stroke-width': 3, opacity: .45 }),
          h('line', { x1: xm, x2: xm, y1: Y(Math.min(...all)), y2: Y(Math.max(...all)), stroke: 'var(--accent2)', 'stroke-width': 1.5 }),
          h('circle', { ...click, cx: xm, cy: Y(v), r: 6, fill: 'var(--accent2)', stroke: 'var(--ink)', 'aria-label': `${fmtPair(D.manifest.pairs[i], true)}: ${v.toFixed(1)} cm equivalent` },
            h('title', {}, `${fmtPair(D.manifest.pairs[i], true)}: ${v.toFixed(1)} cm equivalent (range over five references ${Math.min(...all).toFixed(1)}–${Math.max(...all).toFixed(1)}), patch consistency ${f2(w.consistency)}`)));
      } else {
        svg.append(h('circle', { ...click, cx: xm, cy: strip, r: 5, fill: 'none', stroke: 'var(--muted)', 'aria-label': `${fmtPair(D.manifest.pairs[i], true)}: not readable` },
          h('title', {}, `${fmtPair(D.manifest.pairs[i], true)}: not readable (patch coherence ${f2(r.patch_median_coherence)}${w ? ', consistency ' + f2(w.consistency) : ''})`)));
      }
    });
    $('chart').replaceChildren(svg);
    const key = rows.find((r) => r.pair === '20260714_20260726'), before = rows.find((r) => r.pair === '20260702_20260714'), last = rows.find((r) => r.pair === '20260726_20260819');
    const nres = rows.filter((r) => r.resolved).length;
    const parts = [`Patch: ${D.series.patch_pixels} pixels (${D.series.patch_area_km2.toFixed(3)} km²), chosen after the signal was seen in the 14–26 Jul pair. ${nres} of ${rows.length} pairs are readable on it. Vertical bars show the range across the reference areas that are themselves steady in that pair (up to five).`];
    if (before && before.resolved && key && key.resolved) {
      const rng = (r) => { const a = Object.values(r.refs).filter((v) => v && v.reference_consistency >= 0.6).map((v) => Math.abs(v.los_cm)); return `${Math.min(...a).toFixed(1)}–${Math.max(...a).toFixed(1)}`; };
      parts.push(`2–14 Jul: ${Math.abs(before.refs['west block'].los_cm).toFixed(1)} cm (${rng(before)} across references). 14–26 Jul: ${Math.abs(key.refs['west block'].los_cm).toFixed(1)} cm (${rng(key)}). The 14–26 Jul value is close to half a cycle, so it could equally be read one cycle further the other way.`);
    }
    const CR = D.series.control_ranks || {};
    const early = rows.filter((r) => r.resolved && r.end <= '20260702' && CR[r.pair]);
    if (early.length) {
      const vals = early.map((r) => Math.abs(r.refs['west block'].los_cm));
      const above = early.filter((r) => CR[r.pair].langtang_abs_rad > CR[r.pair].control_p95).length;
      const top = early.filter((r) => CR[r.pair].controls_at_or_above_langtang === 0).length;
      parts.push(`Earlier in the record (${fmtDay(early[0].start, true)} to ${fmtDay(early[early.length - 1].end, true)}) the patch was readable in ${early.length} pairs, with steps of ${Math.min(...vals).toFixed(1)}–${Math.max(...vals).toFixed(1)} cm. In ${above} of them it is above the level 95% of other slopes stay below; in ${top} it is above every other slope. So the patch may have been slightly unusual in winter (snow can do this too), but only 14–26 Jul stands clear of all ${CR['20260714_20260726'] ? CR['20260714_20260726'].n_controls : ''} comparison slopes.`);
    }
    if (last && !last.resolved) parts.push(`26 Jul–19 Aug (24 days): the patch is still coherent (${f2(last.patch_median_coherence)}) but its phase is spatially mixed; the amount is unresolved, not zero.`);
    $('chartnote').textContent = parts.join(' ');
  }

  function drawControls() {
    const c = D.series.controls, vals = D.series.control_values || [];
    if (!c || !c.n_controls) { $('controls').replaceChildren(h('p', { class: 'note' }, 'Control comparison not available.')); return; }
    const k = c.pairs.indexOf('20260714_20260726');
    const key = D.series.rows.find((r) => r.pair === '20260714_20260726');
    const lang = Math.abs(key.refs['west block'].phase_rad);
    const crk = (D.series.control_ranks || {})['20260714_20260726'];
    const W = 760, H = 150, m = { l: 40, r: 16, t: 14, b: 34 }, nb = 32;
    const bins = new Array(nb).fill(0);
    vals.forEach((v) => { bins[Math.min(nb - 1, Math.floor((Math.abs(v[k]) / Math.PI) * nb))]++; });
    const bmax = Math.max(...bins);
    const X = (rad) => m.l + (rad / Math.PI) * (W - m.l - m.r), Y = (n) => H - m.b - (n / bmax) * (H - m.t - m.b);
    const svg = h('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Phase step on control slopes compared with Langtang, 14 to 26 July' });
    bins.forEach((n, i) => { if (n) svg.append(h('rect', { x: X((i / nb) * Math.PI) + 1, y: Y(n), width: (W - m.l - m.r) / nb - 2, height: H - m.b - Y(n), fill: 'var(--muted)' }, h('title', {}, `${n} control slopes`))); });
    svg.append(h('line', { class: 'axis', x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b }));
    [0, 1, 2, 3].forEach((r) => svg.append(h('text', { x: X(r), y: H - m.b + 14, 'text-anchor': 'middle' }, `${r} rad`), h('text', { x: X(r), y: H - m.b + 27, 'text-anchor': 'middle' }, `${(r * D.series.rad_to_cm).toFixed(1)} cm`)));
    svg.append(h('line', { x1: X(lang), x2: X(lang), y1: m.t, y2: H - m.b, stroke: 'var(--flag)', 'stroke-width': 3 }), h('text', { x: X(lang) - 6, y: m.t + 10, 'text-anchor': 'end', style: 'fill:var(--flag)' }, 'Langtang patch'),
      h('text', { x: m.l + 4, y: m.t + 10 }, `${c.n_controls} other slopes`));
    $('controls').replaceChildren(svg);
    $('controlsnote').textContent = `The same measurement on ${c.n_controls} other coherent slopes of the same size in the window, 14–26 Jul. Their largest step is ${f2(c.abs_phase_max[k])} rad; Langtang is ${f2(lang)} rad. ${c.n_with_step_like_langtang} of them go from quiet in 2–14 Jul to a step of 1.5 rad or more in 14–26 Jul. ${crk ? `Counting every slope readable in that pair alone (${crk.n_controls}), ${crk.controls_at_or_above_langtang} reach the Langtang value. ` : ''}This argues against a general atmospheric or processing effect. It does not rule out something specific to this slope other than movement.`;
  }

  /* ---------- text sections ---------- */
  function drawFinding() {
    const key = D.series.rows.find((r) => r.pair === '20260714_20260726'), before = D.series.rows.find((r) => r.pair === '20260702_20260714');
    const ev = D.evaluation.rows.find((r) => r.pair === '20260714_20260726');
    const c = D.series.controls;
    const kids = [];
    if (key && key.resolved) {
      const a = Object.values(key.refs).filter(Boolean).map((v) => Math.abs(v.los_cm));
      kids.push(h('p', {}, h('strong', {}, `Between 14 and 26 July 2026, a small patch of the slope shows a phase step equivalent to about ${Math.min(...a).toFixed(1)}–${Math.max(...a).toFixed(1)} cm along the radar line of sight. `),
        before && before.resolved ? `In the pass before (2–14 July) the same patch shows ${Math.abs(before.refs['west block'].los_cm).toFixed(1)} cm against the same reference. ` : '',
        c && c.n_controls ? `None of ${c.n_controls} comparable slopes nearby shows such a step. ` : '', 'The slope collapsed on 26 August.'));
    }
    if (ev && ev.has_history) kids.push(h('p', {}, `Run on every pass, a simple "new movement" rule raises ${ev.flags} flag${ev.flags === 1 ? '' : 's'} in the ${D.evaluation.window_km2.toFixed(0)} km² window for that pair; ${ev.flags_at_langtang} ${ev.flags_at_langtang === 1 ? 'is' : 'are'} on this slope.`));
    kids.push(h('p', {}, 'This is a pattern in public NISAR products that matches a published analysis. It is not a validated measurement of ground movement and not a warning system. See the limits below.'));
    $('finding').replaceChildren(...kids);
  }
  function drawCollapse() {
    const c = D.collapse.channels.HHHH, v = D.collapse.channels.HVHV;
    $('collapse').replaceChildren(
      h('p', { class: 'hint' }, `Radar brightness (backscatter) before and after the collapse, inside the UNOSAT detachment outline. A pixel counts as changed when its brightness moves by more than ${D.collapse.threshold_db} dB. Tick "Collapse: brightness change" on the map to see the scar and the debris path.`),
      h('div', { class: 'statrow' },
        h('div', { class: 'stat' }, h('b', {}, c.quiet_pct.toFixed(1) + '%'), h('span', {}, 'of pixels changed, 14→26 Jul (comparison)')),
        h('div', { class: 'stat' }, h('b', {}, c.event_pct.toFixed(1) + '%'), h('span', {}, 'changed, 19→31 Aug (across the collapse)')),
        h('div', { class: 'stat' }, h('b', {}, '+' + c.control_event_minus_quiet_max.toFixed(1)), h('span', {}, `points: largest increase among ${c.controls_n} same-shaped areas elsewhere (collapse: +${c.event_minus_quiet.toFixed(1)})`))),
      h('p', { class: 'note' }, `HH channel, ${c.valid_pixels.toLocaleString()} valid 10 m pixels. Cross-polarised (HV): ${v.quiet_pct.toFixed(1)}% → ${v.event_pct.toFixed(1)}%. Brightness also changes with snow, moisture and viewing geometry; this shows that the surface changed, not how much material moved.`));
  }
  function drawLimits() {
    const P = D.evaluation.params, cm = (x) => (x * D.series.rad_to_cm).toFixed(1);
    const pre = D.manifest.pairs.filter((p) => p.end <= '20260819'); const nX = pre.filter((p) => !p.forward_processed).length;
    const items = [
      'That the phase step is ground movement. Atmosphere, terrain-model error, radar layover on steep ground or a change in the surface can also shift phase. The step matches the pattern of a published analysis of this slope and is absent on comparable slopes, which supports movement but does not prove it.',
      'Direction or true size of any movement. Radar measures change along its own line of sight, from one viewing angle here. The step is close to half a cycle, where the value is ambiguous by one cycle.',
      'How much the slope changed in the last 24 days. The radar did not observe between 26 July and 19 August, and the phase in that pair is too mixed to read.',
      'A date when change began. The patch could not be read from mid-March to June (snow and melt), so there is one readable pair directly before the step. Winter pairs show smaller steps that may or may not be related (see the chart).',
      'That anyone could have acted. ' + (nX ? `${nX} of the ${pre.length} pre-collapse pairs shown here exist only as versions reprocessed after the collapse. ` : '') + 'When each product became publicly available was not checked. Nothing here is a forecast.',
      `What the other flags are. They are unverified. Some may be real slow movement, glacier margins or snow effects. The rule was adjusted on the Langtang case, so it has not been tested independently.`,
      `What the rule cannot see: change faster than half a cycle per pair (${cm(Math.PI)} cm), ground that was never coherent (snow, ice, steep faces in radar shadow), and anything in the first ${P.history_pairs} pairs of the record.`,
      'Anywhere else. One 30 km window, one year, one satellite track.',
    ];
    const desc = D.series.descending || [];
    if (desc.length) {
      const ok = desc.filter((d) => d.measurement);
      items.push(`A second viewing angle. The descending track has ${desc.length} pairs; the product has valid data over the patch in ${desc.filter((d) => d.box_valid > 0).length} of them and the patch is readable in ${ok.length}` + (ok.length ? ` (${ok.map((d) => `${fmtDay(d.pair.slice(0, 8))}–${fmtDay(d.pair.slice(9))}: ${Math.abs(d.measurement.los_cm).toFixed(1)} cm equivalent`).join('; ')}).` : '.'));
    } else items.push('A second viewing angle. Descending-track pairs were not available in this build.');
    $('limits').replaceChildren(...items.map((t) => h('li', {}, t)));
  }
  function drawMethod() {
    const P = D.evaluation.params, repo = 'https://github.com/Hamza-Atiq/dancing-with-the-sars/blob/main/';
    $('method').replaceChildren(
      h('p', {}, `Input: the 20 m wrapped interferogram and coherence in NISAR L2 GUNW products, track ${D.manifest.track}, ${D.manifest.pairs.length} consecutive pairs. The 80 m unwrapped layer is not used: it discards this slope.`),
      h('p', {}, `Phase anomaly: coherence-weighted mean phase in a ${P.local_box * 20} m box minus the same over the surrounding ${(P.background_box * 20 / 1000).toFixed(1)} km. A pixel is measurable when local phase consistency ≥ ${P.min_consistency}, coherence ≥ ${P.min_local_coherence} and background strength ≥ ${P.min_background_strength}.`),
      h('p', {}, `Flag: measurable, anomaly ≥ ${P.flag_abs_anomaly_rad} rad (${(P.flag_abs_anomaly_rad * D.series.rad_to_cm).toFixed(1)} cm), and in the previous ${P.history_pairs} pairs measurable at least ${P.min_history_measurable === 1 ? 'once' : P.min_history_measurable + ' times'} and never above ${P.quiet_abs_anomaly_rad} rad; at least ${P.min_blob_pixels} connected pixels (${(P.min_blob_pixels * 400 / 1e6).toFixed(3)} km²).`),
      h('p', {}, 'Records: ', h('a', { href: repo + 'project/spec.md' }, 'specification'), ', ', h('a', { href: repo + 'project/results.md' }, 'results and every calibration trial'), ', ', h('a', { href: repo + 'Langtang%20verification%20-%20Claude.md' }, 'verification record'), ', ', h('a', { href: repo + 'project/review-codex-spec.md' }, 'independent review'), '.'),
      h('p', {}, 'Published analyses of the precursor: ', h('a', { href: 'https://www.ce.washington.edu/news/article/2026-10-19/tracking-mountainside-centimeters-time' }, 'University of Washington account of George Brencher\'s work'), '; ', h('a', { href: 'https://doi.org/10.1007/s12524-026-02611-x' }, 'Roy et al. 2026'), '. Outline: ', h('a', { href: 'https://unosat.org/products/4260' }, 'UNOSAT product 4260'), '.'));
    $('generated').textContent = `Data files generated ${D.manifest.generated_utc.replace('T', ' ').replace('+00:00', ' UTC')}.`;
  }

  /* ---------- wiring ---------- */
  function select(i, scroll) {
    state.i = Math.max(0, Math.min(D.manifest.pairs.length - 1, i));
    showPair();
    if (scroll) $('map-h').scrollIntoView({ behavior: 'smooth' });
  }
  function slopeView() { const c = D.manifest.patch_center; map.setView([c[1], c[0]], 14); }
  function wire() {
    const s = $('slider');
    s.max = D.manifest.pairs.length - 1;
    s.addEventListener('input', () => select(+s.value));
    $('prev').addEventListener('click', () => select(state.i - 1));
    $('next').addEventListener('click', () => select(state.i + 1));
    document.querySelectorAll('input[name=layer]').forEach((r) => r.addEventListener('change', () => { state.layer = r.value; showPair(); }));
    document.querySelectorAll('input[name=base]').forEach((r) => r.addEventListener('change', () => { Object.values(bases).forEach((b) => map.removeLayer(b)); bases[r.value].addTo(map); }));
    $('opacity').addEventListener('input', (e) => { const o = e.target.value / 100; radar.setOpacity(o); evImg.setOpacity(o); quImg.setOpacity(o); });
    $('ov-flags').addEventListener('change', showPair);
    $('ov-outlines').addEventListener('change', (e) => (e.target.checked ? outlines.addTo(map) : map.removeLayer(outlines)));
    $('ov-event').addEventListener('change', (e) => { e.target.checked ? evImg.addTo(map) : map.removeLayer(evImg); drawLegend(); });
    $('ov-quiet').addEventListener('change', (e) => { e.target.checked ? quImg.addTo(map) : map.removeLayer(quImg); drawLegend(); });
    $('go-slope').addEventListener('click', slopeView);
    $('go-window').addEventListener('click', () => map.fitBounds(D.bounds));
    $('go-key').addEventListener('click', () => { const i = pairById('20260714_20260726'); if (i >= 0) select(i); slopeView(); });
  }

  load().then(() => {
    initMap(); wire(); drawFinding(); drawYearTable(); drawSensitivity(); drawChart(); drawControls(); drawCollapse(); drawLimits(); drawMethod();
    const k = pairById('20260714_20260726');
    select(k >= 0 ? k : D.manifest.pairs.length - 1);
    slopeView();
  }).catch((err) => {
    $('finding').replaceChildren(h('div', { class: 'err' }, 'Could not load the data files (' + err.message + '). Run "python pipeline/build.py" and serve the docs folder over HTTP.'));
    console.error(err);
  });
})();
