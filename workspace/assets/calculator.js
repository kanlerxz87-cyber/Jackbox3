/* Jackbox3 private browser calculator.
   Runs entirely in the reader's browser: no fetch/XHR/WebSocket, no cookies,
   no localStorage, no sessionStorage, no analytics, no transmission.
   Verified official tax RATES are pre-filled; every property-specific value is
   an assumption and is blank by default. Results are assumptions, not facts. */
(function () {
  'use strict';
  var form = document.getElementById('calc-form');
  if (!form) return;

  var money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
  var blanks = [];

  function num(id) {
    var el = document.getElementById(id);
    if (!el) { return 0; }
    var raw = String(el.value || '').trim();
    if (raw === '') { blanks.push(id); return 0; }
    var v = Number(raw);
    return isFinite(v) ? v : 0;
  }
  function sel(id) {
    var el = document.getElementById(id);
    return el ? el.value : 'no';
  }
  function set(id, text) {
    var el = document.getElementById(id);
    if (el) el.textContent = text;
  }
  function pow(r, t) { return Math.pow(1 + r, t); }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    blanks.length = 0;

    // ---- Sale case -------------------------------------------------------
    var salePrice = num('sale_price');
    var basis = num('basis');
    var sellingCosts = num('selling_costs');
    var gain1250Input = num('gain_1250');
    var fedRate = num('fed_rate') / 100;
    var rate1250 = num('rate_1250') / 100;
    var niitRate = num('niit_rate') / 100;
    var caRate = num('ca_rate') / 100;
    var niitApplies = sel('niit_applies') === 'yes';
    var defer1031 = sel('exchange1031') === 'yes';

    var gain = Math.max(0, salePrice - basis - sellingCosts);
    var gain1250 = Math.min(Math.max(0, gain1250Input), gain);
    var otherGain = Math.max(0, gain - gain1250);
    var fedTax = gain1250 * rate1250 + otherGain * fedRate;
    var niitTax = niitApplies ? gain * niitRate : 0;
    var caTax = gain * caRate;
    if (defer1031) { fedTax = 0; niitTax = 0; caTax = 0; }
    var atse = salePrice - sellingCosts - fedTax - niitTax - caTax;

    // ---- Hold / renewal case --------------------------------------------
    var annualRent = num('annual_rent');
    var annualCosts = num('annual_costs');
    var years = Math.max(0, Math.floor(num('years')));
    var disc = num('discount_rate') / 100;
    var terminal = num('terminal_value');
    var ordinaryRate = num('ordinary_rate') / 100;
    var net = annualRent - annualCosts;
    var afterTaxNet = net * (1 - ordinaryRate);
    var holdNPV = 0;
    for (var t = 1; t <= years; t++) holdNPV += afterTaxNet / pow(disc, t);
    var baseTerminalPV = terminal / pow(disc, years);
    holdNPV += baseTerminalPV;

    // ---- Combined stress -------------------------------------------------
    var downtime = num('downtime_months');
    var repair = num('repair_cost');
    var haircut = num('exit_haircut') / 100;
    var lostRent = (annualRent / 12) * downtime * (1 - ordinaryRate);
    var haircutPV = (terminal * haircut) / pow(disc, years);
    var stressNPV = holdNPV - lostRent - repair - haircutPV;

    var diff = holdNPV - atse;

    set('out_atse', money.format(atse));
    set('out_hold', money.format(holdNPV));
    set('out_diff', money.format(diff));
    set('out_stress', money.format(stressNPV));
    set('out_status',
      'Computed from assumptions only. Blank inputs treated as zero: ' +
      (blanks.length ? blanks.join(', ') : 'none') +
      '. NIIT MAGI thresholds, §1031 boot, and terminal-value gain tax are not modelled. ' +
      'No winner is selected.');

    var warn = document.getElementById('calc-warning');
    if (warn) {
      warn.textContent = 'No winner is selected. Blank property inputs were treated as zero, so these numbers are illustrative only. ' +
        'A decision requires the verified private inputs in the Decision Gates. This calculation never leaves your browser.';
    }
  });

  form.addEventListener('reset', function () {
    blanks.length = 0;
    set('out_atse', '—'); set('out_hold', '—'); set('out_diff', '—'); set('out_stress', '—');
    set('out_status', 'Not computed. Blank inputs are treated as zero and flagged below.');
    var warn = document.getElementById('calc-warning');
    if (warn) warn.textContent = 'No winner is selected. This tool prepares the after-tax sale comparison alongside a negotiated renewal case; a decision requires the verified private inputs listed in the Decision Gates.';
  });
}());
