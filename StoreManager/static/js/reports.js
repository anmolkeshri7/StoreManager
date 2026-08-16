/* =========================================================
   STORE MANAGER
   REPORT EXPORT MODULE
   ========================================================= */


/* =========================================================
   CSV ESCAPE
   ========================================================= */

function csvEscape(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    value = String(value);

    if (
        value.includes(",") ||
        value.includes('"') ||
        value.includes("\n")
    ) {

        value = value.replace(
            /"/g,
            '""'
        );

        return '"' + value + '"';
    }

    return value;
}


/* =========================================================
   DOWNLOAD CSV
   ========================================================= */

function downloadCSV(
    filename,
    headers,
    rows
) {

    let csv = "";

    /*
       Add UTF-8 BOM so Excel correctly
       recognizes the CSV file.
    */

    csv += "\uFEFF";


    /* HEADER */

    if (
        headers &&
        headers.length > 0
    ) {

        csv += headers
            .map(csvEscape)
            .join(",");

        csv += "\n";
    }


    /* DATA */

    rows.forEach(
        function (row) {

            csv += row
                .map(csvEscape)
                .join(",");

            csv += "\n";

        }
    );


    /* CREATE BLOB */

    const blob =
        new Blob(
            [csv],
            {
                type:
                    "text/csv;charset=utf-8;"
            }
        );


    const url =
        URL.createObjectURL(
            blob
        );


    /* CREATE DOWNLOAD LINK */

    const link =
        document.createElement(
            "a"
        );


    link.href = url;

    link.download = filename;

    document.body.appendChild(
        link
    );

    link.click();


    document.body.removeChild(
        link
    );


    URL.revokeObjectURL(
        url
    );
}


/* =========================================================
   READ HTML TABLE
   ========================================================= */

function getTableData(
    table
) {

    const headers = [];

    const rows = [];


    /* =====================================================
       HEADERS
       ===================================================== */

    const headerCells =
        table.querySelectorAll(
            "thead th"
        );


    headerCells.forEach(
        function (cell) {

            headers.push(
                cell.innerText
                    .trim()
                    .replace(
                        /\s+/g,
                        " "
                    )
            );

        }
    );


    /* =====================================================
       BODY
       ===================================================== */

    const bodyRows =
        table.querySelectorAll(
            "tbody tr"
        );


    bodyRows.forEach(
        function (tr) {

            const cells =
                tr.querySelectorAll(
                    "td"
                );


            if (
                cells.length === 0
            ) {
                return;
            }


            const row = [];


            cells.forEach(
                function (cell) {

                    row.push(
                        cell.innerText
                            .trim()
                            .replace(
                                /\s+/g,
                                " "
                            )
                    );

                }
            );


            /* =================================================
               IGNORE EMPTY-STATE ROWS
               ================================================= */

            const completeText =
                row.join(" ")
                    .toLowerCase();


            const emptyMessages = [

                "no sales found",

                "no purchases found",

                "no product sales found",

                "no category sales found",

                "no customer sales found",

                "no employee sales found",

                "no purchases found"

            ];


            const isEmptyRow =
                emptyMessages.some(
                    function (message) {

                        return completeText
                            .includes(message);

                    }
                );


            if (
                !isEmptyRow &&
                row.length > 0
            ) {

                rows.push(row);

            }

        }
    );


    return {
        headers: headers,
        rows: rows
    };
}


/* =========================================================
   EXPORT SINGLE TABLE
   ========================================================= */

function exportTable(
    tableId,
    filename
) {

    const table =
        document.getElementById(
            tableId
        );


    if (!table) {

        alert(
            "Report table could not be found."
        );

        return;
    }


    const data =
        getTableData(
            table
        );


    if (
        data.rows.length === 0
    ) {

        alert(
            "There is no data available to export."
        );

        return;
    }


    downloadCSV(
        filename,
        data.headers,
        data.rows
    );

}


/* =========================================================
   EXPORT ALL REPORT TABLES
   ========================================================= */

function exportAllReports() {

    const tables =
        document.querySelectorAll(
            ".report-export-table"
        );


    if (
        tables.length === 0
    ) {

        alert(
            "No report tables were found."
        );

        return;
    }


    let csv = "\uFEFF";


    tables.forEach(
        function (table) {

            const title =
                table.dataset.title ||
                "Report";


            const data =
                getTableData(
                    table
                );


            if (
                data.rows.length === 0
            ) {

                return;
            }


            /* REPORT TITLE */

            csv +=
                csvEscape(
                    title
                );

            csv += "\n";


            /* HEADERS */

            csv += data.headers
                .map(csvEscape)
                .join(",");

            csv += "\n";


            /* ROWS */

            data.rows.forEach(
                function (row) {

                    csv += row
                        .map(csvEscape)
                        .join(",");

                    csv += "\n";

                }
            );


            /* SEPARATOR */

            csv += "\n";

        }
    );


    if (
        csv === "\uFEFF"
    ) {

        alert(
            "There is no report data available."
        );

        return;
    }


    const blob =
        new Blob(
            [csv],
            {
                type:
                    "text/csv;charset=utf-8;"
            }
        );


    const url =
        URL.createObjectURL(
            blob
        );


    const link =
        document.createElement(
            "a"
        );


    link.href = url;

    link.download =
        "store_manager_reports.csv";


    document.body.appendChild(
        link
    );


    link.click();


    document.body.removeChild(
        link
    );


    URL.revokeObjectURL(
        url
    );

}


/* =========================================================
   EXPORT CURRENT DATE RANGE
   ========================================================= */

function getReportDateRange() {

    const start =
        document.getElementById(
            "start_date"
        );


    const end =
        document.getElementById(
            "end_date"
        );


    let startDate =
        start
            ? start.value
            : "";


    let endDate =
        end
            ? end.value
            : "";


    if (
        startDate &&
        endDate
    ) {

        return (
            startDate +
            "_to_" +
            endDate
        );

    }


    if (startDate) {

        return (
            "from_" +
            startDate
        );

    }


    if (endDate) {

        return (
            "until_" +
            endDate
        );

    }


    return "all_data";
}


/* =========================================================
   EXPORT WITH DATE RANGE
   ========================================================= */

function exportTableWithDate(
    tableId,
    filename
) {

    const dateRange =
        getReportDateRange();


    const extension =
        ".csv";


    let finalFilename =
        filename;


    if (
        finalFilename
            .toLowerCase()
            .endsWith(extension)
    ) {

        finalFilename =
            finalFilename.slice(
                0,
                -extension.length
            );

    }


    finalFilename +=
        "_" +
        dateRange +
        extension;


    exportTable(
        tableId,
        finalFilename
    );

}


/* =========================================================
   PAGE INITIALIZATION
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "Store Manager Reports Export loaded."
        );

    }
);