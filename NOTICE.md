# Notice — synthetic data & intended use

## Synthetic data only
All datasets in this repository are **entirely synthetic**. They were generated for training
purposes and contain **no real residents and no personal data (PII)**. Any resemblance to real
individuals is coincidental.

- Resident identifiers (`RESIDENT_00001` … `RESIDENT_01500`) are fabricated and shared across the
  Databricks estate and the Fabric uploads only so that the workshop joins resolve.
- Air-quality values are pulled from the public **data.gov.sg** PSI API at runtime (with a safe
  offline fallback); no personal data is involved.

## Intended use
This kit is a hands-on **learning workshop** for Microsoft Fabric (with Azure Databricks). It is not
a production reference architecture. Do not point these notebooks at real resident or patient data.

## Trademarks
Microsoft, Azure, Power BI, and Fabric are trademarks of the Microsoft group of companies.
"Healthy 365" and "Health Promotion Board (HPB)" are referenced for scenario context only.

## Licence
Code and content are provided under the terms in [`LICENSE`](LICENSE).
