# ERD

This ERD shows the analytical warehouse model used by the dashboard.

```mermaid
erDiagram
    dimCity ||--o{ factDrug : "id = dimCity_id"
    dimConTh ||--o{ factDrug : "id = dimConTh_id"
    dimDrug ||--o{ factDrug : "id = dimDrug_id"
    dimDrugType ||--o{ factDrug : "id = dimDrugType_id"
    dimMan ||--o{ factDrug : "id = dimMan_id"
    dimTime ||--o{ factDrug : "id = dimTime_id"

    dimCity {
        int id PK
        varchar dimName
    }

    dimConTh {
        int id PK
        varchar dimName
    }

    dimDrug {
        int id PK
        varchar dimName
    }

    dimDrugType {
        int id PK
        varchar dimName
    }

    dimMan {
        int id PK
        varchar dimName
    }

    dimTime {
        int id PK
        date timeDay
        int timeWeekDay
        int timeWeekNum
        varchar timeMonth
        int timeYear
    }

    factDrug {
        bigint id PK
        int dimCity_id FK
        int dimConTh_id FK
        int dimDrug_id FK
        int dimDrugType_id FK
        int dimMan_id FK
        int dimTime_id FK
        boolean is_refunded
        int cntDrug
        double sumDrug
        double avgDrug
        double minDrug
        double maxDrug
    }
```

## Cardinalities

- `dimCity 1:N factDrug`
- `dimConTh 1:N factDrug`
- `dimDrug 1:N factDrug`
- `dimDrugType 1:N factDrug`
- `dimMan 1:N factDrug`
- `dimTime 1:N factDrug`

## Notes

- `factDrug` is the central fact table.
- Dimension tables keep descriptive attributes and remove repeated text from the fact table.
- `source_ndc_products` and `source_drug_events` are open-data context tables. They are not part of the core sales star schema because the original backup does not contain stable natural keys for direct product/report joins.
