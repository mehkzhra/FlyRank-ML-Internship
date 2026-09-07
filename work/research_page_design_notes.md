# Research-page design review

Reviewed 5 September 2026 before building the capstone page.

## Sources and decisions

- [Nature Methods article format](https://www.nature.com/nmeth/content): use a recognizable scientific sequence and give enough technical detail for validation and reproducibility. **Decision:** preserve the assignment's nine canonical sections and make methodology inspectable.
- [Scientific Data submission guidance](https://www.nature.com/sdata/submission-guidelines): write for readers outside the immediate specialty and minimize unexplained jargon. **Decision:** define Precision@50, proxy label, leakage, and client holdout in plain language.
- [W3C guidance for complex images](https://www.w3.org/WAI/tutorials/images/complex/): charts need short identification plus a text equivalent of their essential information. **Decision:** pair every chart with a takeaway and an exact HTML table or values in text.
- [W3C guidance on use of color](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html): meaning cannot depend on color alone. **Decision:** label every bar directly and use position, text, and pattern in addition to color.
- [MDN responsive design](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design): pages should remain usable across screen sizes. **Decision:** use a bounded reading column, fluid type, stacked mobile layout, and horizontally scrollable tables.
- [GitHub Pages publishing-source documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site): a site can publish from the `main` branch's `/docs` folder. **Decision:** ship one self-contained `docs/index.html` with no fragile build step or absolute asset paths.

## Chosen format

A single long-form research page, not a slide deck or decorative portfolio landing page. It opens with the question and five-sentence abstract, gives skimmers three headline numbers, keeps methods and limitations prominent, and ends with ranked operational guidance, reproducibility links, and explicit data credit.

