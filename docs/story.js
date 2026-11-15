/* Story page: fills images, numbers and charts from story/story.json (built by scripts/site_assets.py). */
(function () {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var $ = function (id) { return document.getElementById(id); };
  function date(s) { return new Date(Date.UTC(+s.slice(0, 4), +s.slice(4, 6) - 1, +s.slice(6, 8))); }
  function dm(s) { return +s.slice(6, 8) + ' ' + MONTHS[+s.slice(4, 6) - 1]; }
  function pairLabel(p) { var a = p.slice(0, 8), b = p.slice(9); return (a.slice(4, 6) === b.slice(4, 6) ? +a.slice(6, 8) : dm(a)) + ' to ' + dm(b); }
  function el(tag, attrs, text) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }
  function svg(host, w, h) { var s = el('svg', { viewBox: '0 0 ' + w + ' ' + h, role: 'img' }); host.appendChild(s); return s; }
  function html(tag, cls, inner) { var e = document.createElement(tag); if (cls) e.className = cls; if (inner != null) e.innerHTML = inner; return e; }

  /* ---- countdown in the top bar ---- */
  (function clock() {
    var secs = [].slice.call(document.querySelectorAll('[data-day]'));
    var n = $('clock-n'), t = $('clock-t');
    function set() {
      var mid = window.innerHeight * 0.4, cur = secs[0];
      secs.forEach(function (s) { if (s.getBoundingClientRect().top <= mid) cur = s; });
      n.textContent = cur.dataset.day;
      t.textContent = cur.dataset.label;
    }
    set();
    window.addEventListener('scroll', set, { passive: true });
    window.addEventListener('resize', set);
  })();

  fetch('story/story.json').then(function (r) { return r.json(); }).then(build).catch(function (e) {
    console.error(e);
  });

  function build(D) {
    var im = D.images;
    place($('hero-mark'), im.source_frac_wide);
    compare(D);
    panels(D);
    strip(D);
    controls(D);
    year(D);
    passes(D);
    flags(D);
    sentinel(D);
    $('k-cm').textContent = Math.abs(D.key_pair.cm_refs[1]).toFixed(1) + ' to ' + Math.abs(D.key_pair.cm_refs[0]).toFixed(1);
    var prev = D.rows.filter(function (r) { return r.pair === '20260702_20260714'; })[0];
    $('k-prev').textContent = Math.abs(prev.cm).toFixed(1);
  }
  function place(node, f) { node.style.left = (f[0] * 100) + '%'; node.style.top = (f[1] * 100) + '%'; }

  /* ---- before / after ---- */
  function compare(D) {
    var o = D.images.optical, kinds = {
      optical: o.before ? { a: 'story/optical_before.webp', b: 'story/optical_after.webp', la: longDate(o.before.date), lb: longDate(o.after.date),
        cap: 'The same ground from the Sentinel-2 camera satellite on the last clear day we found before the collapse and a clear day after it. Monsoon cloud covered the slope for most of the months between. The ring marks the patch.' } : null,
      radar: { a: 'story/radar_before.webp', b: 'story/radar_after.webp', la: '19 August 2026', lb: '31 August 2026',
        cap: 'NISAR radar brightness seven days before and five days after. Radar sees through cloud, and from the side, so the mountain looks unfamiliar. Inside the mapped collapse outline, 41% of the ground changed brightness sharply, against 19% in a quiet fortnight.' }
    };
    var box = $('compare'), range = $('cmp-range');
    place($('cmp-mark'), D.images.source_frac_site);
    function show(kind) {
      var k = kinds[kind] || kinds.radar;
      $('cmp-a').src = k.a; $('cmp-b').src = k.b;
      $('cmp-a').alt = 'The slope on ' + k.la; $('cmp-b').alt = 'The slope on ' + k.lb;
      $('cmp-la').textContent = k.la; $('cmp-lb').textContent = k.lb; $('cmp-cap').textContent = k.cap;
      [].forEach.call(document.querySelectorAll('.tabs button'), function (b) { b.setAttribute('aria-selected', b.dataset.kind === kind); });
    }
    [].forEach.call(document.querySelectorAll('.tabs button'), function (b) { b.addEventListener('click', function () { show(b.dataset.kind); }); });
    range.addEventListener('input', function () { box.style.setProperty('--x', range.value + '%'); });
    show(kinds.optical ? 'optical' : 'radar');
  }
  function longDate(iso) { var p = iso.split('-'); return +p[2] + ' ' + ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][+p[1] - 1] + ' ' + p[0]; }

  /* ---- four phase panels ---- */
  function panels(D) {
    var ph = D.images.phase, host = $('panels');
    var notes = { '20260620_20260702': 'unreadable', '20260702_20260714': '', '20260714_20260726': '', '20260726_20260819': 'a jumble, no number' };
    ph.panels.forEach(function (p) {
      var row = D.rows.filter(function (r) { return r.pair === p.pair; })[0];
      var f = html('figure', 'panel' + (p.pair === D.key_pair.pair ? ' key' : ''));
      var img = new Image(); img.src = 'story/' + p.file; img.alt = 'Radar change map for ' + pairLabel(p.pair);
      var b = html('span', 'box');
      b.style.left = ph.patch_frac[0][0] * 100 + '%'; b.style.top = ph.patch_frac[0][1] * 100 + '%';
      b.style.width = (ph.patch_frac[1][0] - ph.patch_frac[0][0]) * 100 + '%'; b.style.height = (ph.patch_frac[1][1] - ph.patch_frac[0][1]) * 100 + '%';
      var val = row.resolved ? (p.pair === D.key_pair.pair ? Math.abs(D.key_pair.cm_refs[1]).toFixed(1) + ' to ' + Math.abs(D.key_pair.cm_refs[0]).toFixed(1) + ' cm' : Math.abs(row.cm).toFixed(1) + ' cm') : notes[p.pair];
      f.appendChild(img); f.appendChild(b);
      f.appendChild(html('figcaption', '', '<b>' + pairLabel(p.pair) + '</b>' + row.days + ' days · ' + val));
      host.appendChild(f);
    });
  }

  /* ---- film strip ---- */
  function strip(D) {
    var host = $('strip');
    D.images.phase.frames.forEach(function (fr) {
      var f = html('figure', 'frame' + (fr.pair === D.key_pair.pair ? ' key' : ''));
      var img = new Image(); img.src = 'story/' + fr.file; img.loading = 'lazy'; img.alt = '';
      f.appendChild(img); f.appendChild(html('figcaption', '', pairLabel(fr.pair) + (fr.pair.slice(0, 4) === '2025' ? ' 2025' : '')));
      host.appendChild(f);
    });
    var key = host.querySelector('.key');
    if (key) host.scrollLeft = Math.max(0, key.offsetLeft - host.clientWidth / 2);
  }

  /* ---- 361 controls vs Langtang ---- */
  function controls(D) {
    var k = D.key_pair, W = 1000, H = 270, L = 12, R = 60, base = 225;
    var s = svg($('ch-controls'), W, H), max = 6.2;
    var x = function (v) { return L + v / max * (W - L - R); };
    s.appendChild(el('line', { x1: L, x2: W - R, y1: base, y2: base, class: 'axis' }));
    for (var t = 0; t <= 6; t++) { s.appendChild(el('line', { x1: x(t), x2: x(t), y1: base, y2: base + 6, class: 'axis' })); s.appendChild(el('text', { x: x(t), y: base + 24, 'text-anchor': 'middle' }, t + (t === 6 ? ' cm' : ''))); }
    var bins = {};
    D.controls_cm.forEach(function (v) {            /* dot plot: stack dots in 0.06 cm bins */
      var b = Math.round(v / 0.06); bins[b] = (bins[b] || 0) + 1;
      s.appendChild(el('circle', { cx: x(b * 0.06), cy: base - 7 - (bins[b] - 1) * 6.4, r: 2.7, fill: 'currentColor', 'fill-opacity': .55 }));
    });
    s.appendChild(el('line', { x1: x(k.control_max_cm), x2: x(k.control_max_cm), y1: base - 46, y2: base, class: 'axis' }));
    s.appendChild(el('text', { x: x(k.control_max_cm) + 6, y: base - 38 }, 'largest of the others: ' + k.control_max_cm.toFixed(1) + ' cm'));
    s.appendChild(el('circle', { cx: x(k.langtang_cm), cy: base - 12, r: 11, class: 'hot' }));
    s.appendChild(el('text', { x: x(k.langtang_cm), y: base - 34, 'text-anchor': 'middle', class: 'lab' }, 'Langtang patch'));
    s.appendChild(el('text', { x: x(k.langtang_cm), y: base - 52, 'text-anchor': 'middle', class: 'hot', style: 'font:500 26px "Bodoni Moda",serif' }, k.langtang_cm.toFixed(1) + ' cm'));
    s.setAttribute('aria-label', 'Dot plot. ' + k.controls_n + ' comparable slopes all show steps below ' + k.control_max_cm.toFixed(1) + ' centimetres. The Langtang patch shows ' + k.langtang_cm.toFixed(1) + '.');
  }

  /* ---- the year ---- */
  function year(D) {
    var W = 1000, H = 300, L = 44, R = 16, T = 26, B = 46, rows = D.rows;
    var t0 = date(rows[0].start), t1 = date(rows[rows.length - 1].end), col = new Date(D.collapse_utc);
    var x = function (d) { return L + (d - t0) / (t1 - t0) * (W - L - R); };
    var y = function (v) { return T + (6.5 - v) / 6.5 * (H - T - B); };
    var s = svg($('ch-year'), W, H);
    s.appendChild(el('rect', { x: x(date('20260727')), y: T, width: x(date('20260810')) - x(date('20260727')), height: H - T - B, fill: 'currentColor', 'fill-opacity': .1 }));
    [0, 2, 4, 6].forEach(function (v) { s.appendChild(el('line', { x1: L, x2: W - R, y1: y(v), y2: y(v), class: 'axis' })); s.appendChild(el('text', { x: L - 8, y: y(v) + 4, 'text-anchor': 'end' }, v + (v === 6 ? ' cm' : ''))); });
    for (var m = new Date(Date.UTC(2025, 11, 1)); m < t1; m = new Date(Date.UTC(m.getUTCFullYear(), m.getUTCMonth() + 1, 1))) {
      s.appendChild(el('text', { x: x(m), y: H - B + 20 }, MONTHS[m.getUTCMonth()] + (m.getUTCMonth() === 0 ? ' 2026' : '')));
      s.appendChild(el('line', { x1: x(m), x2: x(m), y1: H - B, y2: H - B + 6, class: 'axis' }));
    }
    rows.forEach(function (r) {
      var cx = (x(date(r.start)) + x(date(r.end))) / 2, v = Math.min(6.3, Math.abs(r.cm)), key = r.pair === D.key_pair.pair;
      if (r.resolved) {
        s.appendChild(el('line', { x1: cx, x2: cx, y1: y(0), y2: y(v), stroke: key ? '#f0a63a' : 'currentColor', 'stroke-width': key ? 3 : 1.5 }));
        s.appendChild(el('circle', { cx: cx, cy: y(v), r: key ? 8 : 4.5, fill: key ? '#f0a63a' : 'currentColor' }));
      } else {
        s.appendChild(el('circle', { cx: cx, cy: y(0), r: 4, fill: 'none', stroke: 'currentColor', 'stroke-opacity': .5 }));
      }
      if (key) s.appendChild(el('text', { x: cx - 14, y: y(v) + 4, 'text-anchor': 'end', class: 'lab' }, '14 to 26 July: ' + v.toFixed(1) + ' cm'));
    });
    s.appendChild(el('line', { x1: x(col), x2: x(col), y1: T - 8, y2: H - B, stroke: '#f0a63a', 'stroke-width': 2 }));
    s.appendChild(el('text', { x: x(col) + 7, y: T + 4, class: 'lab' }, 'collapse'));
    s.appendChild(el('text', { x: x(date('20260803')), y: T - 8, 'text-anchor': 'middle' }, 'no data'));
    s.appendChild(el('text', { x: x(date('20260501')), y: y(0) - 14, 'text-anchor': 'middle' }, 'unreadable'));
    s.setAttribute('aria-label', 'Step on the patch in each of 26 radar pairs. Winter pairs show 0.2 to 2.3 centimetres, spring is unreadable, and the 14 to 26 July pair shows 5.6 centimetres.');
  }

  /* ---- every radar pass, June to August ---- */
  function passes(D) {
    var names = Object.keys(D.passes), W = 1000, rowH = 44, T = 30, L = 200, R = 16, H = T + names.length * rowH + 34;
    var t0 = date('20260601'), t1 = date('20260901'), col = new Date(D.collapse_utc);
    var x = function (d) { return L + (d - t0) / (t1 - t0) * (W - L - R); };
    var s = svg($('ch-passes'), W, H);
    s.appendChild(el('rect', { x: x(date('20260727')), y: T - 12, width: x(date('20260810')) - x(date('20260727')), height: names.length * rowH, fill: '#f1f3f2', 'fill-opacity': .1 }));
    ['20260601', '20260701', '20260801'].forEach(function (d) { s.appendChild(el('text', { x: x(date(d)), y: H - 8 }, MONTHS[+d.slice(4, 6) - 1])); s.appendChild(el('line', { x1: x(date(d)), x2: x(date(d)), y1: T - 12, y2: H - 26, class: 'axis' })); });
    names.forEach(function (n, i) {
      var yy = T + i * rowH + 8, nisar = n.indexOf('NISAR') === 0;
      s.appendChild(el('text', { x: 0, y: yy + 4, class: nisar ? 'lab' : '' }, n));
      s.appendChild(el('line', { x1: L, x2: W - R, y1: yy, y2: yy, class: 'axis' }));
      D.passes[n].forEach(function (d) {
        var dt = date(d); if (dt < t0 || dt >= t1) return;
        var gap = dt > date('20260726') && dt < col;
        s.appendChild(el('circle', { cx: x(dt), cy: yy, r: nisar ? 7 : 5.5, fill: nisar ? '#f1f3f2' : (gap ? '#f0a63a' : '#86b7c9') }));
      });
    });
    s.appendChild(el('line', { x1: x(col), x2: x(col), y1: 4, y2: H - 26, stroke: '#f0a63a', 'stroke-width': 2 }));
    s.appendChild(el('text', { x: x(col) - 7, y: 14, 'text-anchor': 'end', class: 'lab' }, 'collapse, 26 Aug'));
    s.setAttribute('aria-label', 'Dates of every radar pass over the slope from June to August 2026 for NISAR and three Sentinel-1 tracks.');
  }

  /* ---- flags ---- */
  function flags(D) {
    var host = $('flagmap');
    D.flags.forEach(function (f) {
      if (f.p[0] < 0 || f.p[0] > 1 || f.p[1] < 0 || f.p[1] > 1) return;
      var i = document.createElement('i'); if (f.lang) i.className = 'hot';
      i.style.left = f.p[0] * 100 + '%'; i.style.top = f.p[1] * 100 + '%'; host.appendChild(i);
    });
    var rows = D.detector.rows.filter(function (r) { return r.has_history; }), W = 1000, H = 230, L = 34, B = 44, T = 16;
    var max = Math.max.apply(null, rows.map(function (r) { return r.flags; })), bw = (W - L) / rows.length;
    var s = svg($('ch-flags'), W, H), y = function (v) { return T + (max - v) / max * (H - T - B); };
    [0, 10, 20, 30].forEach(function (v) { s.appendChild(el('line', { x1: L, x2: W, y1: y(v), y2: y(v), class: 'axis' })); s.appendChild(el('text', { x: L - 8, y: y(v) + 4, 'text-anchor': 'end' }, v)); });
    rows.forEach(function (r, i) {
      var key = r.lang > 0;
      s.appendChild(el('rect', { x: L + i * bw + 3, y: y(r.flags), width: bw - 6, height: Math.max(1, y(0) - y(r.flags)), fill: key ? '#f0a63a' : 'currentColor', 'fill-opacity': key ? 1 : .7 }));
      if (i % 3 === 0 || key) s.appendChild(el('text', { x: L + i * bw + bw / 2, y: H - B + 18, 'text-anchor': 'middle', class: key ? 'lab' : '' }, dm(r.pair.slice(9))));
      if (key) s.appendChild(el('text', { x: L + i * bw + bw / 2, y: y(r.flags) - 8, 'text-anchor': 'middle', class: 'lab' }, r.flags + ' flags, ' + r.lang + ' on Langtang'));
    });
    s.setAttribute('aria-label', 'Flags raised in each of ' + rows.length + ' radar pairs; ' + D.detector.summary.total_flags + ' in total.');
  }

  /* ---- Sentinel-1 slot: placeholder until data/s1/s1_patch.json exists at build time ---- */
  function sentinel(D) {
    var host = $('s1-slot'), S = D.sentinel1;
    if (!S || !S.length) {
      host.appendChild(html('div', 'slot-in', '<h3>Sentinel-1: results pending</h3><p>We ordered 24 Sentinel-1 image pairs covering June to early September 2026 and are measuring the same patch in them with the same rules, fixed before we looked. The numbers will appear here, whatever they show.</p>'));
      return;
    }
    var t19 = S.filter(function (r) { return r.track && !r.error; });
    var res = t19.filter(function (r) { return r.resolved; });
    var rowsHtml = t19.map(function (r) {
      return '<tr><td>' + r.track + '</td><td>' + pairLabel(r.start + '_' + r.end) + '</td><td>' + (r.patch_median_coherence == null ? 'no view' : r.patch_median_coherence.toFixed(2)) + '</td><td>' +
        (r.resolved ? Math.abs(r.los_cm).toFixed(1) + ' cm' : 'unreadable') + '</td></tr>';
    }).join('');
    host.appendChild(html('div', 'slot-in', '<h3>Sentinel-1: ' + (res.length ? res.length + ' of ' + t19.length + ' pairs readable on the patch' : 'the patch is unreadable in all ' + t19.length + ' pairs') + '</h3>' +
      '<p>Same patch, same rules as for NISAR, fixed before we opened the data. Sentinel-1 uses a wave four times shorter, so it loses its reading sooner on rough, fast-changing ground.</p>' +
      (res.length ? '<p>' + (res.every(function (r) { return r.controls_at_or_above / r.controls_resolved >= 0.25; }) ?
        'The readable pairs are early and small: ' + res.map(function (r) { return r.controls_at_or_above + ' of ' + r.controls_resolved; }).join(' and ') + ' comparison patches elsewhere show as much or more. ' : '') +
        'Sentinel-1 gives no reading on the patch in the pairs that cover late July and August, so it neither confirms nor contradicts what NISAR saw, and it does not fill the gap.</p>' : '') +
      '<table><thead><tr><th>Track</th><th>Pair, 2026</th><th>Signal quality on patch</th><th>Step</th></tr></thead><tbody>' + rowsHtml + '</tbody></table>'));
  }
})();
