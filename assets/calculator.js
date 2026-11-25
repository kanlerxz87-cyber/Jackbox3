/* ------------------------------------------------------------------
   Private after-tax calculator.

   PRIVACY CONTRACT
   ----------------
   This file makes NO network requests. There is no fetch, no
   XMLHttpRequest, no sendBeacon, no analytics, no cookies, no
   localStorage, no sessionStorage, no third-party font or script.
   Every value the reader types stays in this tab's memory and is
   discarded when the tab closes. This can be verified by reading this
   file — it is the only script the calculator page loads — or by
   watching the browser's network panel while using the form.

   TAX CONTRACT
   ------------
   Only rules verified from official IRS and California Franchise Tax
   Board publications are applied. Anything unverified is omitted on
   purpose and listed in the result so the reader can see what was
   left out. This is arithmetic applied to the reader's own numbers,
   not tax advice.
   ------------------------------------------------------------------ */
(function () {
  "use strict";

  /* ---- Verified federal rules — IRS Rev. Proc. 2025-32 §4.01, §4.03,
     and IRS Topic 409 ------------------------------------------------ */
  var FED_ORDINARY = {
    single:            [[12400,.10],[50400,.12],[105700,.22],[201775,.24],[256225,.32],[640600,.35],[Infinity,.37]],
    married_joint:     [[24800,.10],[100800,.12],[211400,.22],[403550,.24],[512450,.32],[768700,.35],[Infinity,.37]],
    married_separate:  [[12400,.10],[50400,.12],[105700,.22],[201775,.24],[256225,.32],[384350,.35],[Infinity,.37]],
    head_of_household: [[17700,.10],[67450,.12],[105700,.22],[201750,.24],[256200,.32],[640600,.35],[Infinity,.37]]
  };

  var FED_LTCG = {
    single:            { zero: 49450,  fifteen: 545500 },
    married_joint:     { zero: 98900,  fifteen: 613700 },
    married_separate:  { zero: 49450,  fifteen: 306850 },
    head_of_household: { zero: 66200,  fifteen: 579600 }
  };

  var FED_STANDARD_DEDUCTION = {
    single: 16100, married_joint: 32200, married_separate: 16100, head_of_household: 24150
  };

  var NIIT_RATE = 0.038;
  var NIIT_THRESHOLD = {
    single: 200000, head_of_household: 200000, married_joint: 250000, married_separate: 125000
  };

  /* IRS Topic 409: unrecaptured section 1250 gain is taxed at a MAXIMUM
     rate of 25%. It is a ceiling, not a flat rate. */
  var SECTION_1250_CEILING = 0.25;

  /* ---- Verified California rules — FTB 2025 Form 540 ----------------
     Tax Rate Schedules (line 31) and 2025 Instructions (line 18
     standard deduction chart; line 62 Behavioral Health Services Tax). */
  var CA_ORDINARY = {
    single:            [[11079,.01],[26264,.02],[41452,.04],[57542,.06],[72724,.08],[371479,.093],[445771,.103],[742953,.113],[Infinity,.123]],
    married_joint:     [[22158,.01],[52528,.02],[82904,.04],[115084,.06],[145448,.08],[742958,.093],[891542,.103],[1485906,.113],[Infinity,.123]],
    married_separate:  [[11079,.01],[26264,.02],[41452,.04],[57542,.06],[72724,.08],[371479,.093],[445771,.103],[742953,.113],[Infinity,.123]],
    head_of_household: [[22173,.01],[52530,.02],[67716,.04],[83805,.06],[98990,.08],[505208,.093],[606251,.103],[1010417,.113],[Infinity,.123]]
  };

  var CA_STANDARD_DEDUCTION = {
    single: 5706, married_separate: 5706, married_joint: 11412, head_of_household: 11412
  };

  var CA_BHST_RATE = 0.01;
  var CA_BHST_THRESHOLD = 1000000;

  /* ---- bracket maths -------------------------------------------------- */
  function taxFromBrackets(taxable, brackets) {
    if (!(taxable > 0)) return 0;
    var tax = 0, floor = 0;
    for (var i = 0; i < brackets.length; i++) {
      var ceiling = brackets[i][0], rate = brackets[i][1];
      if (taxable > floor) {
        var slice = Math.min(taxable, ceiling) - floor;
        if (slice > 0) tax += slice * rate;
      }
      floor = ceiling;
      if (taxable <= ceiling) break;
    }
    return tax;
  }

  function marginalRate(taxable, brackets) {
    for (var i = 0; i < brackets.length; i++) {
      if (taxable <= brackets[i][0]) return brackets[i][1];
    }
    return brackets[brackets.length - 1][1];
  }

  /* Federal long-term capital gain, stacked on top of other taxable income. */
  function fedLTCGTax(otherTaxable, gain, status) {
    if (!(gain > 0)) return 0;
    var b = FED_LTCG[status];
    var start = Math.max(0, otherTaxable);
    var end = start + gain;
    var at0 = Math.max(0, Math.min(end, b.zero) - start);
    var at15 = Math.max(0, Math.min(end, b.fifteen) - Math.max(start, b.zero));
    var at20 = Math.max(0, end - Math.max(start, b.fifteen));
    return at0 * 0 + at15 * 0.15 + at20 * 0.20;
  }

  /* Section 1250 recapture: taxed at the lesser of the ordinary marginal
     rate and the 25% ceiling. Verified rule, applied band by band. */
  function recaptureTax(otherTaxable, recapture, status) {
    if (!(recapture > 0)) return 0;
    var brackets = FED_ORDINARY[status];
    var tax = 0, remaining = recapture, cursor = Math.max(0, otherTaxable);
    while (remaining > 0) {
      var rate = Math.min(marginalRate(cursor, brackets), SECTION_1250_CEILING);
      var nextCeiling = Infinity;
      for (var i = 0; i < brackets.length; i++) {
        if (brackets[i][0] > cursor) { nextCeiling = brackets[i][0]; break; }
      }
      var slice = Math.min(remaining, nextCeiling - cursor);
      if (!isFinite(slice) || slice <= 0) slice = remaining;
      tax += slice * rate;
      remaining -= slice;
      cursor += slice;
    }
    return tax;
  }

  function money(n) {
    var rounded = Math.round(n);
    return rounded.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  }
  function money2(n) {
    return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  }
  function num(id) {
    var el = document.getElementById(id);
    var v = parseFloat(el && el.value);
    return isFinite(v) ? v : 0;
  }

  function calculate() {
    var status = document.getElementById("status").value;

    var otherIncome   = num("otherIncome");
    var otherGain     = num("otherGain");
    var price         = num("price");
    var costs         = num("costs");
    var payoff        = num("payoff");
    var basis         = num("basis");
    var improvements  = num("improvements");
    var depreciation  = num("depreciation");

    /* IRS Pub. 544: amount realised = gross price less selling costs;
       adjusted basis = cost + capitalised improvements - depreciation
       allowed or allowable. */
    var adjustedBasis = basis + improvements - depreciation;
    var realised = price - costs;
    var gain = realised - adjustedBasis;

    var lines = [
      ["Contract price", money2(price)],
      ["Less selling costs", "(" + money2(costs) + ")"],
      ["Amount realised", money2(realised)],
      ["Original cost basis", money2(basis)],
      ["Plus capitalised improvements", money2(improvements)],
      ["Less depreciation taken or allowable", "(" + money2(depreciation) + ")"],
      ["Adjusted basis", money2(adjustedBasis)],
      ["Realised gain", money2(gain)]
    ];

    var totalTax = 0, fedTax = 0, caTax = 0, niit = 0, recTax = 0, bhst = 0;
    var taxRows = [];
    var notes = [];

    if (gain < 0) {
      notes.push("The realised amount is below adjusted basis, so this is a loss rather than a gain. Loss " +
        "treatment depends on how the property was held, and those rules were not verified here. No tax has " +
        "been computed. Consult a CPA.");
    } else if (gain === 0) {
      notes.push("Realised amount equals adjusted basis: there is no gain, so no tax has been computed.");
    } else {
      /* --- section 1250 recapture cannot exceed depreciation taken, nor
         the gain itself. ------------------------------------------------ */
      var recapture = Math.min(Math.max(0, depreciation), gain);
      var capGain = Math.max(0, gain - recapture);

      /* --- federal ---------------------------------------------------- */
      var fedTaxableOther = Math.max(0, otherIncome - FED_STANDARD_DEDUCTION[status]);
      var fedOrdTax = taxFromBrackets(fedTaxableOther, FED_ORDINARY[status]);
      var fedGainTax = fedLTCGTax(fedTaxableOther + Math.max(0, otherGain), capGain, status);
      recTax = recaptureTax(fedTaxableOther + Math.max(0, otherGain), recapture, status);
      fedTax = fedOrdTax + fedGainTax + recTax;

      /* --- net investment income tax: 3.8% of the lesser of net
         investment income or MAGI above the threshold ---------------- */
      var magi = otherIncome + gain;
      niit = Math.min(gain, Math.max(0, magi - NIIT_THRESHOLD[status])) * NIIT_RATE;

      /* --- California: no preferential capital-gains rate. The gain is
         added to California taxable income and taxed at ordinary
         brackets, then the 1% Behavioral Health Services Tax applies
         above $1,000,000 of taxable income. --------------------------- */
      var caBase = Math.max(0, otherIncome - CA_STANDARD_DEDUCTION[status]);
      var caTop = caBase + Math.max(0, otherGain) + gain;
      caTax = Math.max(0, taxFromBrackets(caTop, CA_ORDINARY[status]) -
                          taxFromBrackets(caBase, CA_ORDINARY[status]));
      bhst = Math.max(0, caTop - CA_BHST_THRESHOLD) * CA_BHST_RATE;
      caTax += bhst;

      totalTax = fedTax + niit + caTax;

      taxRows = [
        ["Unrecaptured section 1250 gain recognised", money2(recapture),
         "Taxed at the lesser of your ordinary marginal rate and the 25% ceiling"],
        ["Federal tax on that recapture", money2(recTax), "IRS Topic 409: 25% maximum rate"],
        ["Remaining long-term capital gain", money2(capGain),
         "0% / 15% / 20%, stacked on top of your other income"],
        ["Federal tax on the long-term gain", money2(fedGainTax), "Verified 2026 thresholds"],
        ["Net investment income tax", money2(niit),
         "3.8% of the lesser of the gain or MAGI above the threshold"],
        ["California tax on the gain", money2(caTax - bhst),
         "Gain taxed as ordinary income, 1% to 12.3%"],
        ["California Behavioral Health Services Tax", money2(bhst),
         "1% of California taxable income above $1,000,000"]
      ];
    }

    var cashAtClose = realised - payoff;
    var netProceeds = cashAtClose - totalTax;

    var result = document.getElementById("result");
    result.hidden = false;

    var warnClass = netProceeds < 0 ? " res-warn" : "";
    var html = "";
    html += "<h3>Result</h3>";
    html += "<div class='res-hero" + warnClass + "'>";
    html += "<span class='big'>" + money(netProceeds) + "</span>";
    html += "<span class='lbl'>Estimated after-tax cash to you,<br>after selling costs, loan pay-off and estimated tax</span>";
    html += "</div>";

    html += "<div class='grid-2'>";
    html += "<div class='panel'><h3>Sale arithmetic</h3><table class='data'><tbody>";
    for (var i = 0; i < lines.length; i++) {
      html += "<tr><td>" + lines[i][0] + "</td><td class='num'>" + lines[i][1] + "</td></tr>";
    }
    html += "</tbody></table></div>";

    html += "<div class='panel'><h3>Tax and proceeds</h3><table class='data'><tbody>";
    for (var j = 0; j < taxRows.length; j++) {
      html += "<tr><td>" + taxRows[j][0] + "</td><td class='num'>" + taxRows[j][1] + "</td></tr>";
      html += "<tr><td colspan='2' class='muted'>" + taxRows[j][2] + "</td></tr>";
    }
    html += "<tr><td><strong>Total estimated tax</strong></td><td class='num'><strong>" + money(totalTax) + "</strong></td></tr>";
    html += "<tr><td>Less mortgage pay-off</td><td class='num'>(" + money2(payoff) + ")</td></tr>";
    html += "<tr><td><strong>Cash at closing before tax</strong></td><td class='num'><strong>" + money(cashAtClose) + "</strong></td></tr>";
    html += "<tr><td><strong>After-tax cash</strong></td><td class='num'><strong>" + money(netProceeds) + "</strong></td></tr>";
    html += "</tbody></table></div></div>";

    if (notes.length) {
      html += "<div class='callout callout-warn'><h3>Read this</h3><ul>";
      for (var k = 0; k < notes.length; k++) html += "<li>" + notes[k] + "</li>";
      html += "</ul></div>";
    }

    if (gain > 0) {
      html += "<div class='callout callout-warn'><h3>What this figure leaves out &mdash; and which way it errs</h3><ul>";
      html += "<li><strong>Alternative minimum tax</strong> &mdash; California AMT applies above $92,749 of total income " +
              "(single) or $123,667 (joint) but depends on Schedule P (540) preference items. Not modelled.</li>";
      html += "<li><strong>Property tax reassessment after the sale</strong> &mdash; a cost to the buyer and therefore to the price " +
              "you can achieve. Not modelled.</li>";
      html += "<li><strong>FTB Form 593 withholding at closing</strong> &mdash; not modelled.</li>";
      html += "<li><strong>Section 199A, Opportunity Zone provisions, and any depreciation recapture beyond the 25% ceiling</strong> " +
              "&mdash; not verified, so not applied.</li>";
      html += "<li><strong>Your actual filing situation</strong> &mdash; this applies the standard deduction and ignores itemised " +
              "deductions, credits, exemption credits and state apportionment.</li>";
      html += "</ul><p>Have a CPA review any number here before it informs a commitment.</p></div>";
    }

    html += "<div class='callout callout-privacy'><h3>Privacy</h3><p>Every figure above was computed inside this browser tab " +
            "from numbers you typed. Nothing was sent anywhere: there were no network requests, no cookies and no storage. " +
            "Closing the tab discards all of it.</p></div>";

    result.innerHTML = html;
    result.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("calc");
    if (!form) return;
    form.addEventListener("submit", function (e) { e.preventDefault(); calculate(); });
    form.addEventListener("reset", function () {
      var r = document.getElementById("result");
      if (r) { r.hidden = true; r.innerHTML = ""; }
    });
  });
})();
