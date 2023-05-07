import { connect, testDB } from "./duck.js";
import { initPy } from "./loadpy.js"

initPy()
    .then((pyodide) => {
        const duckdb_wasm = {
            test_db: testDB,
            connector: connect
        }
        pyodide.registerJsModule("duckdb_wasm", duckdb_wasm);
        pyodide.runPythonAsync(`
        import platyrhynchos.cruciverbalists.en_simple as en_simple
        en_simple.download_db()

        print("imported")
    `)
});