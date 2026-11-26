/* ------------------------------------------------------------------
   Private after-tax & hold-vs-sell calculator.

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
   Only rules verified from official IRS, California Franchise Tax
   Board, California BOE, and City of Los Angeles publications are
   applied. Federal capital-gain and unrecaptured section 1250 gain
   stacking follows the IRS Instructions for Schedule D (Form 1040)
   Schedule D Tax Worksheet (lines 1-47). Every figure is incremental
   to the property sale (with-sale tax minus pre-sale tax). Anything
   unverified is omitted on purpose and listed in the result.
   ------------------------------------------------------------------ */
(function () {
  "use strict";

  /* ---- Verified federal rules — IRS Rev. Proc. 2025-32 §4.01, §4.03,
     IRS Topic 409, IRS NIIT, and IRS Schedule D Tax Worksheet -------- */
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

  /* ---- Verified California & LA rules — FTB 2025 Form 540, Form 593,
     and City of LA Office of Finance Measure ULA (eff. after 2026-06-30) */
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

  var LA_COUNTY_TRANSFER_RATE = 0.0011; /* $1.10 per $1,000 */
  var LA_CITY_BASE_RATE       = 0.0045; /* $2.25 per $500 */
  var LA_ULA_TIER1_FLOOR      = 5400000;
  var LA_ULA_TIER1_RATE       = 0.04;
  var LA_ULA_TIER2_FLOOR      = 10900000;
  var LA_ULA_TIER2_RATE       = 0.055;

  /* ---- bracket & IRS Schedule D Tax Worksheet maths ------------------- */
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

  /* Exact IRS Schedule D (Form 1040) Tax Worksheet (lines 1-47).
     Parameters are taxable income components:
       ordinaryTaxable >= 0  (Form 1040 taxable income excluding LTCG)
       recap1250       >= 0  (Schedule D line 19 unrecaptured §1250 gain)
       pureLtcg        >= 0  (0% / 15% / 20% net capital gain)
     Top of 24% bracket = FED_ORDINARY[status][3][0] ($201,775 Single/MFS,
     $403,550 MFJ, $201,750 HoH for 2026 per Rev. Proc. 2025-32). */
  function schedDTax(ordinaryTaxable, recap1250, pureLtcg, status) {
    var ord = Math.max(0, ordinaryTaxable);
    var recap = Math.max(0, recap1250);
    var ltcg = Math.max(0, pureLtcg);
    var brackets = FED_ORDINARY[status];
    var ltcgRule = FED_LTCG[status];
    var line1 = ord + recap + ltcg;
    if (!(line1 > 0)) return 0;
    if (recap === 0 && ltcg === 0) {
      return taxFromBrackets(line1, brackets);
    }

    var line10 = recap + ltcg;
    var line13 = ltcg;
    var line14 = Math.max(0, line1 - line13); // ordinaryTaxable + recap1250
    var line15 = ltcgRule.zero;
    var line16 = Math.min(line1, line15);
    var line17 = Math.min(line14, line16);
    var line18 = Math.max(0, line1 - line10); // ordinaryTaxable
    var line19 = Math.min(line1, brackets[3][0]); // top of 24% bracket
    var line20 = Math.min(line14, line19);
    var line21 = Math.max(line18, line20);
    var line22 = Math.max(0, line16 - line17); // 0% LTCG

    if (line1 === line16) {
      return taxFromBrackets(line21, brackets);
    }

    var line23 = Math.min(line1, line13);
    var line24 = line22;
    var line25 = Math.max(0, line23 - line24);
    var line26 = ltcgRule.fifteen;
    var line27 = Math.min(line1, line26);
    var line28 = line21 + line22;
    var line29 = Math.max(0, line27 - line28);
    var line30 = Math.min(line25, line29); // 15% LTCG
    var line31 = line30 * 0.15;
    var line32 = line24 + line30;
    var line33 = (line1 === line32) ? 0 : Math.max(0, line23 - line32); // 20% LTCG
    var line34 = line33 * 0.20;

    var line40 = 0;
    if (recap > 0) {
      var line35 = recap;
      var line36 = line10 + line21;
      var line37 = line1;
      var line38 = Math.max(0, line36 - line37);
      var line39 = Math.max(0, line35 - line38); // §1250 slice taxed at 25%
      line40 = line39 * 0.25;
    }

    var line44 = taxFromBrackets(line21, brackets);
    var line45 = line31 + line34 + line40 + line44;
    var line46 = taxFromBrackets(line1, brackets);
    return Math.min(line45, line46);
  }

  function computeSaleTaxes(status, otherIncome, otherGain, gain, depreciation) {
    if (!(gain > 0)) {
      return {
        recapture: 0, capGain: 0, recTax: 0, fedGainTax: 0,
        niit: 0, caOrdTax: 0, bhst: 0, caTax: 0, totalTax: 0
      };
    }

    /* Section 1250 recapture cannot exceed depreciation taken, nor gain. */
    var recapture = Math.min(Math.max(0, depreciation), gain);
    var capGain = Math.max(0, gain - recapture);

    /* Federal: purely incremental tax attributable to the property sale,
       computed via IRS Schedule D Tax Worksheet lines 1-47. */
    var fedTaxableOther = Math.max(0, otherIncome - FED_STANDARD_DEDUCTION[status]);
    var preOtherGain = Math.max(0, otherGain);
    var baseFedTax = schedDTax(fedTaxableOther, 0, preOtherGain, status);
    var midFedTax  = schedDTax(fedTaxableOther, recapture, preOtherGain, status);
    var withFedTax = schedDTax(fedTaxableOther, recapture, preOtherGain + capGain, status);
    var recTax     = Math.max(0, midFedTax - baseFedTax);
    var fedGainTax = Math.max(0, withFedTax - midFedTax);

    /* NIIT: incremental 3.8% of lesser of NII or MAGI above threshold,
       accounting for pre-existing otherGain in both NII and MAGI. */
    var niitFloor = NIIT_THRESHOLD[status];
    var baseNii   = preOtherGain;
    var baseMagi  = otherIncome + baseNii;
    var baseNiit  = Math.min(baseNii, Math.max(0, baseMagi - niitFloor)) * NIIT_RATE;
    var withNii   = baseNii + gain;
    var withMagi  = otherIncome + withNii;
    var withNiit  = Math.min(withNii, Math.max(0, withMagi - niitFloor)) * NIIT_RATE;
    var niit      = Math.max(0, withNiit - baseNiit);

    /* California: incremental ordinary tax + incremental 1% BHST > $1M. */
    var caBase    = Math.max(0, otherIncome - CA_STANDARD_DEDUCTION[status]);
    var caPreSale = caBase + preOtherGain;
    var caTop     = caPreSale + gain;
    var caOrdTax  = Math.max(0, taxFromBrackets(caTop, CA_ORDINARY[status]) -
                                taxFromBrackets(caPreSale, CA_ORDINARY[status]));
    var bhstBase  = Math.max(0, caPreSale - CA_BHST_THRESHOLD) * CA_BHST_RATE;
    var bhst      = Math.max(0, Math.max(0, caTop - CA_BHST_THRESHOLD) * CA_BHST_RATE - bhstBase);
    var caTax     = caOrdTax + bhst;

    return {
      recapture: recapture,
      capGain: capGain,
      recTax: recTax,
      fedGainTax: fedGainTax,
      niit: niit,
      caOrdTax: caOrdTax,
      bhst: bhst,
      caTax: caTax,
      totalTax: recTax + fedGainTax + niit + caTax
    };
  }

  function estimateLaTransferTaxes(price) {
    if (!(price > 100)) return { base: 0, ula: 0, total: 0, ulaRate: 0 };
    var blocks500 = Math.ceil(price / 500);
    var county = blocks500 * 0.55; /* LA County $1.10 per $1,000 ($0.55 per $500) */
    var cityBase = blocks500 * 2.25; /* LA City $2.25 per $500 (0.45%) */
    var base = county + cityBase;
    var ulaRate = 0;
    if (price >= LA_ULA_TIER2_FLOOR) {
      ulaRate = LA_ULA_TIER2_RATE;
    } else if (price > LA_ULA_TIER1_FLOOR) {
      ulaRate = LA_ULA_TIER1_RATE;
    }
    var ula = price * ulaRate;
    return { base: base, ula: ula, total: base + ula, ulaRate: ulaRate };
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
    if (!el) return 0;
    var v = parseFloat(el.value);
    return isFinite(v) ? v : 0;
  }
  function val(id, fallback) {
    var el = document.getElementById(id);
    return el ? el.value : fallback;
  }

  function calculate() {
    var status       = val("status", "single");
    var structure    = val("structure", "outright");
    var ulaMode      = val("ulaMode", "manual");
    var installYears = Math.max(2, Math.min(30, Math.round(num("installYears") || 5)));

    var otherIncome  = Math.max(0, num("otherIncome"));
    var otherGain    = Math.max(0, num("otherGain"));
    var price        = Math.max(0, num("price"));
    var manualCosts  = Math.max(0, num("costs"));
    var payoff       = Math.max(0, num("payoff"));
    var basis        = Math.max(0, num("basis"));
    var improvements = Math.max(0, num("improvements"));
    var depreciation = Math.max(0, num("depreciation"));

    var transferEst = ulaMode === "la_city_2026"
      ? estimateLaTransferTaxes(price)
      : { base: 0, ula: 0, total: 0, ulaRate: 0 };
    var costs = manualCosts + transferEst.total;

    /* IRS Pub. 544: amount realised = gross price less selling costs;
       adjusted basis = cost + capitalised improvements - depreciation
       allowed or allowable. */
    var adjustedBasis = basis + improvements - depreciation;
    var realised = price - costs;
    var gain = realised - adjustedBasis;

    var lines = [
      ["Contract price", money2(price)],
      ["User-entered selling costs", "(" + money2(manualCosts) + ")"]
    ];
    if (transferEst.total > 0) {
      lines.push(["Est. LA City (0.45%) + County (0.11%) transfer tax", "(" + money2(transferEst.base) + ")"]);
      if (transferEst.ula > 0) {
        lines.push(["Est. Measure ULA (" + (transferEst.ulaRate * 100).toFixed(1) + "% gross)", "(" + money2(transferEst.ula) + ")"]);
      }
    }
    lines.push(["Amount realised", money2(realised)]);
    lines.push(["Original cost basis", money2(basis)]);
    lines.push(["Plus capitalised improvements", money2(improvements)]);
    lines.push(["Less depreciation taken or allowable", "(" + money2(depreciation) + ")"]);
    lines.push(["Adjusted basis", money2(adjustedBasis)]);
    lines.push(["Realised gain", money2(gain)]);

    var taxSummary = {
      recapture: 0, capGain: 0, recTax: 0, fedGainTax: 0,
      niit: 0, caOrdTax: 0, bhst: 0, caTax: 0, totalTax: 0
    };
    var taxRows = [];
    var notes = [];
    var structureNote = "";

    if (gain < 0) {
      notes.push("The realised amount is below adjusted basis, so this is a loss rather than a gain. Loss " +
        "treatment depends on how the property was held, and those rules were not verified here. No tax has " +
        "been computed. Consult a CPA.");
    } else if (gain === 0) {
      notes.push("Realised amount equals adjusted basis: there is no gain, so no tax has been computed.");
    } else if (structure === "exchange1031") {
      structureNote = "Section 1031 like-kind exchange selected: assumes 100% reinvestment of net equity with zero taxable boot " +
        "(mortgage relief or cash retained). Federal and California tax are deferred ($0 current tax). California FTB Form 3840 " +
        "tracks deferred gain if replacement property sits outside California.";
    } else if (structure === "installment") {
      /* IRS Pub 537 / Form 6252: gross-profit ratio spread evenly over N equal
         principal payments (excludes interest income). Schedule D allocates
         unrecaptured §1250 gain to earliest principal collections first. */
      var remRecap = Math.min(Math.max(0, depreciation), gain);
      var remCap = Math.max(0, gain - remRecap);
      var annualGain = gain / installYears;
      var yrRecTotal = 0, yrFedTotal = 0, yrNiitTotal = 0, yrCaOrdTotal = 0, yrBhstTotal = 0;

      for (var y = 0; y < installYears; y++) {
        var yrRec = Math.min(remRecap, annualGain);
        var yrCap = Math.min(remCap, Math.max(0, annualGain - yrRec));
        remRecap -= yrRec;
        remCap -= yrCap;
        var resY = computeSaleTaxes(status, otherIncome, otherGain, yrRec + yrCap, yrRec);
        yrRecTotal += resY.recTax;
        yrFedTotal += resY.fedGainTax;
        yrNiitTotal += resY.niit;
        yrCaOrdTotal += resY.caOrdTax;
        yrBhstTotal += resY.bhst;
      }
      taxSummary = {
        recapture: Math.min(Math.max(0, depreciation), gain),
        capGain: Math.max(0, gain - Math.min(Math.max(0, depreciation), gain)),
        recTax: yrRecTotal,
        fedGainTax: yrFedTotal,
        niit: yrNiitTotal,
        caOrdTax: yrCaOrdTotal,
        bhst: yrBhstTotal,
        caTax: yrCaOrdTotal + yrBhstTotal,
        totalTax: yrRecTotal + yrFedTotal + yrNiitTotal + yrCaOrdTotal + yrBhstTotal
      };
      structureNote = "Illustrative " + installYears + "-year equal-principal installment sale (IRS Pub. 537 / Form 6252): " +
        "assumes $0 debt-in-excess-of-basis boot and constant ordinary income across all " + installYears + " years. " +
        "Per Schedule D instructions, unrecaptured §1250 gain is recognised in the earliest collections before 0%/15%/20% LTCG. " +
        "Excludes interest income and IRC §453A interest charge on obligations > $5M.";
    } else {
      taxSummary = computeSaleTaxes(status, otherIncome, otherGain, gain, depreciation);
    }

    if (gain > 0 && structure !== "exchange1031") {
      taxRows = [
        ["Unrecaptured section 1250 gain recognised", money2(taxSummary.recapture),
         "Schedule D Line 19: fills ordinary brackets up to 24%, excess taxed at 25% ceiling"],
        ["Incremental federal tax on §1250 recapture", money2(taxSummary.recTax),
         "Schedule D Tax Worksheet delta above your non-sale baseline"],
        ["Remaining long-term capital gain", money2(taxSummary.capGain),
         "0% / 15% / 20% stacked per IRS Schedule D Tax Worksheet lines 13-34"],
        ["Incremental federal tax on long-term gain", money2(taxSummary.fedGainTax),
         "Verified 2026 thresholds (Rev. Proc. 2025-32)"],
        ["Incremental net investment income tax (3.8%)", money2(taxSummary.niit),
         "Incremental NII & MAGI above $200k/$250k/$125k (includes other LTCG)"],
        ["Incremental California income tax", money2(taxSummary.caOrdTax),
         "Gain taxed at 1%–12.3% ordinary brackets (2025 Form 540)"],
        ["Incremental California Behavioral Health Services Tax", money2(taxSummary.bhst),
         "Incremental 1% of California taxable income above $1,000,000"]
      ];
    }

    var cashAtClose = realised - payoff;
    var netProceeds = cashAtClose - taxSummary.totalTax;

    /* Informative FTB Form 593 prepayment check (not added to tax). */
    var form593Gross = price * (1 / 30);
    var form593Gain  = Math.max(0, gain) * 0.123;

    /* ---- Optional W-02 Hold / Renewal & Combined Stress ---------------- */
    var annualRent   = Math.max(0, num("annualRent"));
    var annualCosts  = Math.max(0, num("annualCosts"));
    var holdYears    = Math.max(0, Math.min(40, Math.floor(num("holdYears"))));
    var discRate     = Math.max(0, num("discountRate")) / 100;
    var terminalVal  = Math.max(0, num("terminalValue"));
    var ordRate      = Math.max(0, Math.min(100, num("ordinaryRate"))) / 100;
    var downtimeMos  = Math.max(0, num("downtimeMonths"));
    var repairCost   = Math.max(0, num("repairCost"));
    var exitHaircut  = Math.max(0, Math.min(100, num("exitHaircut"))) / 100;

    var hasHold = (annualRent > 0 || terminalVal > 0) && holdYears > 0;
    var holdNpv = 0, stressNpv = 0, diffHoldMinusSell = 0, lostRentNet = 0, haircutPv = 0;
    if (hasHold) {
      var netRent = annualRent - annualCosts;
      var afterTaxAnnual = netRent * (1 - ordRate);
      for (var t = 1; t <= holdYears; t++) {
        holdNpv += afterTaxAnnual / Math.pow(1 + discRate, t);
      }
      var termPv = terminalVal / Math.pow(1 + discRate, holdYears);
      holdNpv += termPv;
      lostRentNet = (annualRent / 12) * downtimeMos * (1 - ordRate);
      haircutPv = (terminalVal * exitHaircut) / Math.pow(1 + discRate, holdYears);
      stressNpv = holdNpv - lostRentNet - repairCost - haircutPv;
      diffHoldMinusSell = holdNpv - netProceeds;
    }

    var result = document.getElementById("result");
    result.hidden = false;

    var warnClass = netProceeds < 0 ? " res-warn" : "";
    var html = "";
    html += "<h3>Result</h3>";
    html += "<div class='res-hero" + warnClass + "'>";
    html += "<span class='big'>" + money(netProceeds) + "</span>";
    html += "<span class='lbl'>Estimated after-tax proceeds (" +
            (structure === "exchange1031" ? "§1031 deferred" :
             structure === "installment" ? installYears + "-yr installment" : "outright sale") +
            "),<br>after selling costs, loan pay-off and incremental tax from the sale</span>";
    html += "</div>";

    html += "<div class='grid-2'>";
    html += "<div class='panel'><h3>Sale arithmetic</h3><table class='data'><tbody>";
    for (var i = 0; i < lines.length; i++) {
      html += "<tr><td>" + lines[i][0] + "</td><td class='num'>" + lines[i][1] + "</td></tr>";
    }
    html += "</tbody></table></div>";

    html += "<div class='panel'><h3>Incremental tax and proceeds</h3><table class='data'><tbody>";
    for (var j = 0; j < taxRows.length; j++) {
      html += "<tr><td>" + taxRows[j][0] + "</td><td class='num'>" + taxRows[j][1] + "</td></tr>";
      html += "<tr><td colspan='2' class='muted'>" + taxRows[j][2] + "</td></tr>";
    }
    html += "<tr><td><strong>Total incremental tax from sale</strong></td><td class='num'><strong>" + money(taxSummary.totalTax) + "</strong></td></tr>";
    html += "<tr><td>Less mortgage pay-off</td><td class='num'>(" + money2(payoff) + ")</td></tr>";
    html += "<tr><td><strong>Cash at closing before income tax</strong></td><td class='num'><strong>" + money(cashAtClose) + "</strong></td></tr>";
    html += "<tr><td><strong>After-tax proceeds</strong></td><td class='num'><strong>" + money(netProceeds) + "</strong></td></tr>";
    html += "</tbody></table></div></div>";

    if (gain > 0 && structure === "outright" && price > 0) {
      html += "<div class='callout'><h3>FTB Form 593 closing withholding (prepayment credit, not extra tax)</h3>" +
              "<p>Escrow typically withholds <strong>" + money(form593Gross) + "</strong> (3&#8531;% of contract price) " +
              "or, if you elect the gain method on Form 593 as an individual, <strong>" + money(form593Gain) +
              "</strong> (12.3% of gain). Withholding is credited against your final California tax shown above &mdash; " +
              "it reduces cash wired on closing day if it exceeds final tax until refunded on return filing.</p></div>";
    }

    if (hasHold) {
      html += "<div class='panel'><h3>W-02 Hold / renewal vs. Sell comparison (assumptions)</h3>" +
              "<table class='data'><tbody>" +
              "<tr><td>After-tax Sell proceeds (benchmark)</td><td class='num'>" + money(netProceeds) + "</td></tr>" +
              "<tr><td>Hold / renewal NPV (" + holdYears + " yrs at " + (discRate * 100).toFixed(2) + "%)</td><td class='num'>" + money(holdNpv) + "</td></tr>" +
              "<tr><td><strong>Hold NPV minus After-tax Sell</strong></td><td class='num'><strong>" +
              (diffHoldMinusSell >= 0 ? "+" : "") + money(diffHoldMinusSell) + "</strong></td></tr>" +
              "<tr><td>Combined stress NPV (less " + downtimeMos + " mos vacancy, " + money(repairCost) + " repairs, " +
              (exitHaircut * 100).toFixed(1) + "% exit haircut)</td><td class='num'>" + money(stressNpv) + "</td></tr>" +
              "</tbody></table>" +
              "<p class='muted'>Hold NPV discounts after-tax operating cash flow plus un-taxed terminal value assumption; " +
              "terminal exit capital-gain tax and any lease-renewal TI allowance beyond repair cost are not subtracted.</p></div>";
    }

    if (structureNote) {
      html += "<div class='callout callout-key'><h3>Selected sale structure</h3><p>" + structureNote + "</p></div>";
    }

    if (notes.length) {
      html += "<div class='callout callout-warn'><h3>Read this</h3><ul>";
      for (var k = 0; k < notes.length; k++) html += "<li>" + notes[k] + "</li>";
      html += "</ul></div>";
    }

    if (gain > 0) {
      html += "<div class='callout callout-warn'><h3>What this figure leaves out &mdash; and which way it errs</h3><ul>";
      html += "<li><strong>California alternative minimum tax</strong> &mdash; California AMT applies above $92,749 of total income " +
              "(single) or $123,667 (joint) but depends on Schedule P (540) preference items. Not modelled.</li>";
      html += "<li><strong>Buyer Proposition 13 reassessment</strong> &mdash; Los Angeles County FY24-25 average property tax rate is " +
              "1.181% (BOE Pub 306), which affects what a buyer will bid if leases have tax caps or vacancies occur.</li>";
      html += "<li><strong>Section 199A, Opportunity Zone provisions, and accelerated recapture above the 25% §1250 ceiling</strong> " +
              "&mdash; not verified, so not applied.</li>";
      html += "<li><strong>Your actual filing situation</strong> &mdash; applies the standard deduction and ignores itemised " +
              "deductions, passive-loss carryforwards, credits and exemption credits.</li>";
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
    var structEl = document.getElementById("structure");
    var instWrap = document.getElementById("installYearsWrap");
    if (structEl && instWrap) {
      structEl.addEventListener("change", function () {
        instWrap.hidden = structEl.value !== "installment";
      });
      instWrap.hidden = structEl.value !== "installment";
    }
    form.addEventListener("submit", function (e) { e.preventDefault(); calculate(); });
    form.addEventListener("reset", function () {
      var r = document.getElementById("result");
      if (r) { r.hidden = true; r.innerHTML = ""; }
      if (instWrap) { instWrap.hidden = true; }
    });
  });
})();
