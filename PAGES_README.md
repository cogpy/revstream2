# GitHub Pages Documentation Site

This repository includes a comprehensive GitHub Pages documentation site that provides:

## 🌐 Live Site

Once deployed, the site will be available at: **https://cogpy.github.io/revstream1/**

## 📚 Site Structure

### Main Pages

1. **[index.md](index.md)** - Home page with executive summary and overview of all three applications
2. **[applications.md](applications.md)** - Comparative analysis of all three applications side-by-side
3. **[evidence-index.md](evidence-index.md)** - Complete evidence catalog with links to all source files

### Application Pages

1. **[application-1.md](application-1.md)** - Ex Parte Interdict (August 13, 2025)
   - Material non-disclosure analysis
   - POPIA violation context (retaliatory motive)
   - Evidence of concealed facts
   
2. **[application-2.md](application-2.md)** - Settlement Enforcement (October 2025)
   - CIPC backdating fraud (critical discovery)
   - R500K fabrication analysis
   - Forensic investigation illegitimacy
   
3. **[application-3.md](application-3.md)** - Contact Interdict (November 4, 2025)
   - Lack of urgency analysis
   - Sequential pattern (3rd in 3 months)
   - Truth suppression evidence

## 🎯 Key Features

### Evidence Linking
- Every claim linked to source documents in `/evidence/` folder
- Direct links to PDF files and markdown conversions
- Cross-references between applications
- Timeline context for all evidence

### Navigation
- Comprehensive navigation between all pages
- Evidence catalog with category organization
- Legal theory mapping
- Timeline visualization

### Content Organization
- **Case Statistics**: R10,269,727.90 total documented losses
- **Timeline**: March 15 - November 18, 2025 (247 days)
- **Evidence Files**: 26 files across 11 categories
- **Legal Theories**: 5 major theories mapped to evidence

## 🔧 Technical Setup

### Jekyll Configuration
- **Theme**: Minima (GitHub Pages default)
- **Markdown**: kramdown with GitHub Flavored Markdown
- **Build**: Automated via GitHub Actions on push to main branch

### Files
- `_config.yml` - Jekyll configuration
- `.gitignore` - Excludes build artifacts
- `.github/workflows/jekyll-gh-pages.yml` - Deployment workflow

## 📂 Evidence Organization

All evidence files are in the `/evidence/` directory:

```
evidence/
├── accounting/       # Financial records (2 files)
├── cipc/            # Corporate registration (2 files)
├── emails/          # Email correspondence (4 files)
├── mediation/       # Mediation notes (1 file)
├── popia/           # POPIA violations (2 files)
├── rezonance/       # Payment system docs (2 files)
├── sage/            # Accounting system (1 file)
├── trademark/       # Trademark registration (1 file)
├── fabricated_accounts/
├── financial/
└── critical_analysis/
```

## 🚀 Deployment

The Jekyll site is built on every push to the `main` branch. Publishing requires GitHub Pages to be enabled once with **Source: GitHub Actions** (Settings → Pages). The default `GITHUB_TOKEN` cannot create that Pages site; either enable it in repository settings, or set a `PAGES_TOKEN` secret (a PAT or GitHub App token that can manage Pages). Until then the build still runs and deployment is skipped.

Once Pages is enabled:

1. GitHub Actions runs the Jekyll build
2. Site is built from markdown files
3. Deployed to GitHub Pages
4. Available at https://cogpy.github.io/revstream1/

## 🔗 Navigation Flow

```
Home (index.md)
├── Applications Overview (applications.md)
│   ├── Application 1 (application-1.md)
│   ├── Application 2 (application-2.md)
│   └── Application 3 (application-3.md)
└── Evidence Index (evidence-index.md)
    ├── POPIA Evidence
    ├── CIPC Evidence
    ├── Email Evidence
    └── [Other categories...]
```

## 📖 Content Highlights

### Critical Revelations
- **Shopify Platform**: Owned by Daniel's UK company since July 2023, not RWD ZA
- **No Independent Revenue**: RWD ZA has no revenue stream of its own
- **R10.27M Losses**: Documented across 158 days of hijacking activity
- **Sequential Interdicts**: 3 applications in 3 months showing pattern

### Evidence Categories
1. **POPIA** (2 files) - July 8, 2025 violation notice (trigger event)
2. **CIPC** (2 files) - Proves backdating fraud (2021-03-09 name change)
3. **ReZonance** (2 files) - Payment system seizure
4. **Sage** (1 file) - Accounting system takeover
5. **Email** (4 files) - Corporate structure and communications
6. **Trademark** (1 file) - Brand ownership documentation
7. **Mediation** (1 file) - Settlement withdrawal context
8. **Accounting** (2 files) - Pre-disruption baseline

### Legal Framework
- **Theory 001**: Abuse of Ex Parte Procedure
- **Theory 002**: Retaliatory Motive (*Beinash v Wixley*)
- **Theory 003**: Corporate Misconduct
- **Theory 004**: Trustee Misconduct
- **Theory 005**: Curatorship Conspiracy

## 🎨 Styling

The site uses the default Minima theme with:
- Clean, professional layout
- Mobile-responsive design
- Easy navigation
- Semantic HTML5
- Accessible content

## 📝 Contributing

To add or update content:

1. Edit the relevant `.md` file
2. Commit and push to main branch
3. GitHub Actions will rebuild and deploy automatically
4. Changes appear live within minutes

## ℹ️ Additional Resources

- [Revenue Stream Documentation](Revenue_Stream/)
- [Data Models](data_models/)
- [Analysis Reports](.) (various `.md` files in root)

---

**Last Updated**: 2025-11-19
**Case**: 2025-137857 - Peter Faucitt v. Jacqueline Faucitt et al.
