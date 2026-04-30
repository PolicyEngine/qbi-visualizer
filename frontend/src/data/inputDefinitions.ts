// Per-input definitions: short plain-English description plus links to the
// authoritative source(s) — IRC, IRS form/schedule, and PolicyEngine variable.

export interface InputLink {
  label: string;
  url: string;
}

export interface InputDefinition {
  description: string;
  statute?: InputLink;
  form?: InputLink;
  policyengine?: InputLink;
}

const PE_VARIABLES_BASE =
  'https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/variables';
const CORNELL_199A = 'https://www.law.cornell.edu/uscode/text/26/199A';

export const INPUT_DEFINITIONS: Record<string, InputDefinition> = {
  // ───── Filing context ─────
  filing_status: {
    description:
      'Tax filing status (single, joint, head of household, etc.). Determines the §199A(e) threshold and the standard deduction.',
    statute: { label: '§1(a)–(d)', url: 'https://www.law.cornell.edu/uscode/text/26/1' },
    form: { label: 'Form 1040', url: 'https://www.irs.gov/pub/irs-pdf/f1040.pdf' },
  },
  year: {
    description:
      'Tax year for the calculation. Affects inflation-adjusted thresholds and post-2025 OBBBA changes (phase-in length, $400 minimum-deduction floor).',
  },

  // ───── QBI Income Sources (Form 8995 Line 1) ─────
  self_employment_income: {
    description:
      'Net earnings from a non-SSTB trade or business carried on as a sole proprietorship or single-member LLC. Reported on Schedule C/F and flows into Form 8995 Line 1.',
    statute: { label: '§199A(c)(1)', url: `${CORNELL_199A}#c_1` },
    form: { label: 'Schedule C / Form 8995 L1', url: 'https://www.irs.gov/pub/irs-pdf/f1040sc.pdf' },
    policyengine: {
      label: 'self_employment_income.py',
      url: `${PE_VARIABLES_BASE}/household/income/person/self_employment/self_employment_income.py`,
    },
  },
  partnership_s_corp_income: {
    description:
      'Distributive share of ordinary business income from a non-SSTB partnership or S-corporation. From K-1 box 1 (or box 1 of Schedule K-1, Form 1120-S). Excludes guaranteed payments and reasonable compensation per §199A(c)(4).',
    statute: { label: '§199A(c)(1) + §707(c)', url: `${CORNELL_199A}#c_1` },
    form: { label: 'Schedule K-1 / Form 8995 L1', url: 'https://www.irs.gov/pub/irs-pdf/i1065sk1.pdf' },
  },
  farm_operations_income: {
    description:
      'Net farm income from a §162 trade or business. Reported on Schedule F and flows into Form 8995 Line 1 as a non-SSTB qualified trade or business.',
    statute: { label: '§199A(c)(1)', url: `${CORNELL_199A}#c_1` },
    form: { label: 'Schedule F', url: 'https://www.irs.gov/pub/irs-pdf/f1040sf.pdf' },
  },
  farm_rent_income: {
    description:
      'Rental income from farmland. Qualifies as QBI only if the activity rises to the level of a §162 trade or business (passive rental does not qualify per §469).',
    statute: { label: '§469', url: 'https://www.law.cornell.edu/uscode/text/26/469' },
    form: { label: 'Form 4835', url: 'https://www.irs.gov/pub/irs-pdf/f4835.pdf' },
  },
  rental_income: {
    description:
      'Net income from rental real estate. Qualifies as QBI only if it rises to a §162 trade or business — see Rev. Proc. 2019-38 safe harbor (250+ hours of rental services per year).',
    statute: { label: '§469 + Rev. Proc. 2019-38', url: 'https://www.irs.gov/pub/irs-drop/rp-19-38.pdf' },
    form: { label: 'Schedule E', url: 'https://www.irs.gov/pub/irs-pdf/f1040se.pdf' },
  },
  estate_income: {
    description:
      'QBI passed through from an estate or trust to a beneficiary on Schedule K-1 (Form 1041).',
    statute: { label: '§199A(c)(1)', url: `${CORNELL_199A}#c_1` },
    form: { label: 'Schedule K-1 (Form 1041)', url: 'https://www.irs.gov/pub/irs-pdf/i1041sk1.pdf' },
  },

  // ───── SSTB Income (Form 8995-A Schedule A) ─────
  sstb_self_employment_income: {
    description:
      'Net self-employment income from a Specified Service Trade or Business (SSTB) — health, law, accounting, actuarial, performing arts, consulting, athletics, financial / brokerage services, investing, or any business whose principal asset is reputation or skill of its owners. Phased out above the §199A threshold per §199A(d)(3).',
    statute: { label: '§199A(d)(2)', url: `${CORNELL_199A}#d_2` },
    form: { label: 'Form 8995-A Schedule A', url: 'https://www.irs.gov/pub/irs-pdf/f8995a.pdf' },
    policyengine: {
      label: 'sstb_self_employment_income.py',
      url: `${PE_VARIABLES_BASE}/household/income/person/self_employment/sstb_self_employment_income.py`,
    },
  },

  // ───── Wage & Property Limitation (Form 8995-A Part II) ─────
  w2_wages_from_qualified_business: {
    description:
      'Total W-2 wages paid by the qualified trade or business during the year. Used to compute the §199A(b)(2)(B) wage limitation: max(50% × W-2, 25% × W-2 + 2.5% × UBIA). Only matters above the threshold.',
    statute: { label: '§199A(b)(4)', url: `${CORNELL_199A}#b_4` },
    form: { label: 'Form 8995-A Part II / W-3', url: 'https://www.irs.gov/pub/irs-pdf/f8995a.pdf' },
    policyengine: {
      label: 'w2_wages_from_qualified_business.py',
      url: `${PE_VARIABLES_BASE}/household/income/person/self_employment/w2_wages_from_qualified_business.py`,
    },
  },
  unadjusted_basis_qualified_property: {
    description:
      'Unadjusted basis immediately after acquisition (UBIA) of qualified depreciable property used in the trade or business, summed across all qualified property within its depreciable period.',
    statute: { label: '§199A(b)(6)', url: `${CORNELL_199A}#b_6` },
    form: { label: 'Form 8995-A Part II', url: 'https://www.irs.gov/pub/irs-pdf/f8995a.pdf' },
    policyengine: {
      label: 'unadjusted_basis_qualified_property.py',
      url: `${PE_VARIABLES_BASE}/household/income/person/self_employment/unadjusted_basis_qualified_property.py`,
    },
  },
  sstb_w2_wages_from_qualified_business: {
    description:
      'The portion of total W-2 wages allocable to the SSTB component, used for the SSTB-specific wage cap calculation. Total W-2 minus SSTB allocable = non-SSTB wage cap basis.',
    statute: { label: '§199A(b)(4) + §199A(d)(3)', url: `${CORNELL_199A}#d_3` },
    form: { label: 'Form 8995-A Schedule A', url: 'https://www.irs.gov/pub/irs-pdf/f8995a.pdf' },
  },
  sstb_unadjusted_basis_qualified_property: {
    description:
      'The portion of UBIA allocable to the SSTB component. Used for the SSTB-specific 2.5% × UBIA cap calculation.',
    statute: { label: '§199A(b)(6) + §199A(d)(3)', url: `${CORNELL_199A}#d_3` },
    form: { label: 'Form 8995-A Schedule A', url: 'https://www.irs.gov/pub/irs-pdf/f8995a.pdf' },
  },

  // ───── REIT / PTP ─────
  qualified_reit_and_ptp_income: {
    description:
      'Qualified REIT dividends (Form 1099-DIV box 5) plus qualified publicly traded partnership income. Get a flat 20% deduction with no wage cap or UBIA limitation, only the income limit at the end.',
    statute: { label: '§199A(b)(1)(B), §857, §7704', url: `${CORNELL_199A}#b_1_B` },
    form: { label: 'Form 8995 L6 / 1099-DIV box 5', url: 'https://www.irs.gov/pub/irs-pdf/f1099div.pdf' },
    policyengine: {
      label: 'qualified_reit_and_ptp_income.py',
      url: `${PE_VARIABLES_BASE}/household/income/person/dividends/qualified_reit_and_ptp_income.py`,
    },
  },

  // ───── Other Income (taxable income context) ─────
  employment_income: {
    description:
      'Regular W-2 wages from employment. Does not qualify as QBI (per §199A(d)(1)(B)) but contributes to AGI and taxable income, which sets the §199A(e) threshold and the income limit cap.',
    statute: { label: '§3401', url: 'https://www.law.cornell.edu/uscode/text/26/3401' },
    form: { label: 'Form W-2 box 1', url: 'https://www.irs.gov/pub/irs-pdf/fw2.pdf' },
  },
  long_term_capital_gains: {
    description:
      'Net long-term capital gain (gains held > 1 year). Excluded from the income limit base under §199A(a)(1)(B)(ii) so it doesn\'t inflate the QBID cap.',
    statute: { label: '§1(h)', url: 'https://www.law.cornell.edu/uscode/text/26/1#h' },
    form: { label: 'Schedule D', url: 'https://www.irs.gov/pub/irs-pdf/f1040sd.pdf' },
  },
  short_term_capital_gains: {
    description:
      'Net short-term capital gain (gains held ≤ 1 year). Taxed as ordinary income; does not reduce the §199A income limit base.',
    statute: { label: '§1222(1)', url: 'https://www.law.cornell.edu/uscode/text/26/1222' },
    form: { label: 'Schedule D', url: 'https://www.irs.gov/pub/irs-pdf/f1040sd.pdf' },
  },
  qualified_dividend_income: {
    description:
      'Dividends taxed at long-term capital gain rates per §1(h)(11). Excluded from the §199A income limit base.',
    statute: { label: '§1(h)(11)', url: 'https://www.law.cornell.edu/uscode/text/26/1#h_11' },
    form: { label: 'Form 1099-DIV box 1b', url: 'https://www.irs.gov/pub/irs-pdf/f1099div.pdf' },
  },
  taxable_interest_income: {
    description:
      'Interest income includible in gross income under §61(a)(4). Adds to AGI and the income limit base.',
    statute: { label: '§61(a)(4)', url: 'https://www.law.cornell.edu/uscode/text/26/61' },
    form: { label: 'Form 1099-INT box 1', url: 'https://www.irs.gov/pub/irs-pdf/f1099int.pdf' },
  },
};

// Definition shared by every "_would_be_qualified" boolean flag.
export const QUALIFIED_FLAG_DEFINITION: InputDefinition = {
  description:
    'Whether this income source rises to the level of a §162 trade or business and is therefore qualified business income. Investment-only activities, employee wages, and hobbies do not qualify.',
  statute: { label: '§199A(d)(1) + §162', url: `${CORNELL_199A}#d_1` },
};
