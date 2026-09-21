# Superstore SQL & BI Analysis

An end-to-end analyst project: a real retail transactions dataset, cleaned and
normalised into a relational schema, analysed with SQL (joins, CTEs, window
functions, subqueries).

## Dataset

**Sample Superstore** - 9,994 real transactions, 2014–2017. This is a widely
used public sample dataset (originally distributed with Tableau, also common
on Kaggle), sourced here from a public GitHub mirror. It is not proprietary
company data, and I'm upfront about that. What makes this project non-trivial
is turning one flat CSV into a proper relational database and finding a real
data quality issue in it (see below), not the dataset's origin.

## What I did

1. **Normalised** the flat source file into four related tables: `customers`,
   `products`, `orders`, `order_items` — see `scripts/clean_data.py`.
2. **Fixed a real data quality issue**: 32 Product IDs had more than one
   recorded Product Name (naming drift over time / re-listed products). Each
   was resolved to its most frequently used name.
3. **Loaded** the cleaned tables into a SQLite database — `scripts/build_database.py`.
4. **Analysed** the data in SQL — `sql/analysis.sql` — covering joins, GROUP BY,
   CTEs, window functions (`LAG`, `RANK`), and a subquery.

## Repo structure

```
.
├── data/
│   ├── raw/superstore.csv        # original flat dataset
│   └── clean/                     # normalised relational tables
├── scripts/
│   ├── clean_data.py               # cleans + normalises the raw data
│   └── build_database.py           # loads clean tables into SQLite
├── sql/
│   └── analysis.sql                 # all analytical queries
├── dashboard/                      # Power BI screenshots / exported PDF
├── retail.db                        # SQLite database (generated)
└── requirements.txt
```

## Relational schema

| Table | Key | Notable columns |
|---|---|---|
| `customers` | `customer_id` | customer_name, segment |
| `products` | `product_id` | category, sub_category, product_name |
| `orders` | `order_id` (FK: customer_id) | order_date, ship_date, ship_mode, region |
| `order_items` | `order_item_id` (FK: order_id, product_id) | sales, quantity, discount, profit |

## How to run

```bash
pip install -r requirements.txt
python scripts/clean_data.py
python scripts/build_database.py
```

Then run the queries in `sql/analysis.sql` against `retail.db` with any SQLite
client, or `sqlite3 retail.db < sql/analysis.sql`.

## SQL techniques demonstrated

- **JOIN + GROUP BY** — revenue and profit by region, and by category
- **CTE** — customer lifetime value and tiering
- **Window functions** — month-over-month revenue trend (`LAG`, running `SUM`),
  ranked sub-categories by profit within category (`RANK`)
- **Subquery** — customers spending above the average customer spend
- **HAVING on aggregate** — sub-categories that are unprofitable overall

## Dashboard

![Dashboard overview](dashboard/overview.png)

*(add your Power BI screenshots or an exported PDF to `dashboard/` and update
this section once built)*

## Key findings & recommendations

**Furniture is a revenue driver but barely profitable.** Furniture brings in
£742k in revenue, close to Technology's £836k, but returns only a 2.5% margin
against Technology's 17.4% and Office Supplies' 17.0%. Worth investigating its
cost structure and discounting policy specifically.

**Tables are losing money overall.** The Tables sub-category has £207k in
revenue but a negative profit of -£17.7k, the only sub-category in the
dataset that loses money in aggregate. Worth a direct pricing or SKU review.

**Higher discounting lines up with lower margin.** Furniture has both the
highest average discount (17.4%) and the lowest margin (2.5%); Technology has
the lowest average discount (13.2%) and the highest margin (17.4%). This is a
correlation, not yet shown to be causal, but it supports tightening discount
approval on Furniture specifically.

**Central lags on margin despite solid revenue.** Central generates £501k in
revenue but only £39.7k profit, a noticeably lower profit-to-revenue ratio
than West or East. Worth checking whether its category mix skews toward
lower-margin products before treating it as a demand problem.

**Revenue peaks sharply in Q4 most years.** Nearly every year in the dataset
shows a strong November/December spike, useful for inventory and staffing
planning ahead of that period.

## Honesty note

This is a public sample dataset, used to demonstrate the pipeline and SQL
technique, not a claim of proprietary company data.
