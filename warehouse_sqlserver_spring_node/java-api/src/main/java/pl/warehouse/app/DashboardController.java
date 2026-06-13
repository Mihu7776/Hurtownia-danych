package pl.warehouse.app;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@CrossOrigin(origins = "*")
public class DashboardController {
    private final SqlServerService sql;

    public DashboardController(SqlServerService sql) {
        this.sql = sql;
    }

    @GetMapping(value = "/api/summary", produces = MediaType.APPLICATION_JSON_VALUE)
    public String summary() {
        return sql.one("SELECT * FROM dbo.v_dashboard_summary");
    }

    @GetMapping(value = "/api/monthly", produces = MediaType.APPLICATION_JSON_VALUE)
    public String monthly() {
        return sql.list("SELECT * FROM dbo.v_sales_by_month ORDER BY year_number, month_name");
    }

    @GetMapping(value = "/api/top-drugs", produces = MediaType.APPLICATION_JSON_VALUE)
    public String topDrugs() {
        return sql.list("SELECT * FROM dbo.v_top_drugs");
    }

    @GetMapping(value = "/api/manufacturers", produces = MediaType.APPLICATION_JSON_VALUE)
    public String manufacturers() {
        return sql.list("SELECT * FROM dbo.v_top_manufacturers");
    }

    @GetMapping(value = "/api/cities", produces = MediaType.APPLICATION_JSON_VALUE)
    public String cities() {
        return sql.list("SELECT * FROM dbo.v_city_sales");
    }

    @GetMapping(value = "/api/sources", produces = MediaType.APPLICATION_JSON_VALUE)
    public String sources() {
        return sql.list("SELECT * FROM dbo.v_open_source_summary");
    }
}
