import { initDatabase, testDB } from "./duck.js";
import { initPy } from "./loadpy.js"

initDatabase().then((db) => {
    console.log(db)
}
)
initPy().then((pyodide) => {
    const my_js_namespace = { test_db : testDB };
    pyodide.registerJsModule("my_js_namespace", my_js_namespace);
    pyodide.runPythonAsync(`
        from my_js_namespace import test_db

        val = await test_db()
        print(val)
    `);
}
)
