package pl.warehouse.app;

import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

@Service
public class SqlServerService {
    private final String sqlcmd = env("SQLCMD_EXE", "sqlcmd");
    private final String server = env("SQLSERVER_INSTANCE", "(localdb)\\MSSQLLocalDB");
    private final String database = env("SQLSERVER_DATABASE", "S");
    private final String user = env("SQLSERVER_USER", "");
    private final String password = env("SQLSERVER_PASSWORD", "");
    private final boolean trustCert = env("SQLSERVER_TRUST_CERT", "0").equals("1");

    public String one(String sql) {
        String json = run(sql, true);
        return json.isBlank() ? "{}" : json;
    }

    public String list(String sql) {
        String json = run(sql, false);
        return json.isBlank() ? "[]" : json;
    }

    private String run(String sql, boolean singleRow) {
        String jsonMode = singleRow ? " FOR JSON PATH, WITHOUT_ARRAY_WRAPPER;" : " FOR JSON PATH;";
        String query = "SET NOCOUNT ON; " + sql + jsonMode;
        List<String> command = command(query);
        try {
            Process process = new ProcessBuilder(command).start();
            byte[] out = process.getInputStream().readAllBytes();
            byte[] err = process.getErrorStream().readAllBytes();
            int code = process.waitFor();
            if (code != 0) {
                throw new RuntimeException(new String(err, StandardCharsets.UTF_8));
            }
            return extractJson(new String(out, StandardCharsets.UTF_8));
        } catch (IOException exc) {
            throw new RuntimeException("Nie udalo sie uruchomic sqlcmd. Sprawdz, czy SQL Server tools sa zainstalowane.", exc);
        } catch (InterruptedException exc) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Przerwano zapytanie SQL.", exc);
        }
    }

    private List<String> command(String query) {
        List<String> command = new ArrayList<>();
        command.add(sqlcmd);
        command.add("-S");
        command.add(server);
        command.add("-d");
        command.add(database);
        command.add("-W");
        command.add("-w");
        command.add("65535");
        if (!user.isBlank()) {
            command.add("-U");
            command.add(user);
            command.add("-P");
            command.add(password);
        }
        if (trustCert) {
            command.add("-C");
        }
        command.add("-Q");
        command.add(query);
        return command;
    }

    private String extractJson(String text) {
        int arrayStart = text.indexOf("[");
        int arrayEnd = text.lastIndexOf("]");
        int objectStart = text.indexOf("{");
        int objectEnd = text.lastIndexOf("}");
        if (arrayStart >= 0 && arrayEnd >= arrayStart) {
            return text.substring(arrayStart, arrayEnd + 1).replace("\r", "").replace("\n", "");
        }
        if (objectStart >= 0 && objectEnd >= objectStart) {
            return text.substring(objectStart, objectEnd + 1).replace("\r", "").replace("\n", "");
        }
        return "";
    }

    private static String env(String name, String fallback) {
        String value = System.getenv(name);
        return value == null || value.isBlank() ? fallback : value;
    }
}
