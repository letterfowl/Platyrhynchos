import { database_functions } from "./duck";
importScripts("https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js");

async function loadPyodideAndPackages() {
    self.pyodide = await loadPyodide();
    await self.pyodide.loadPackage("micropip");
    const micropip = self.pyodide.pyimport("micropip");
    self.pyodide.loadPackage("setuptools");
    await micropip.install('http://localhost:8080/platyrhynchos-0.1.1-py3-none-any.whl');
    console.info("Loaded Pyodide");

    const settings = await (await fetch("settings.toml")).text()
    const additional_objects = {
        settings_text: settings,
    }
    pyodide.registerJsModule("_stuff", additional_objects);
    console.log("Registered settings.toml in Pyodide");
}

async function loadDatabase() {
    self.duckdb = await database_functions();
}

async function connectDBtoPyodide() {
    self.pyodide.registerJsModule("_duckdb", self.duckdb);
    console.log("Registered DuckDB WASM client in Pyodide");
};

let DBandPyodideReadyPromise = Promise.all([loadPyodideAndPackages(), loadDatabase()]).then(() => {
    self.pyodide.registerJsModule("_duckdb", self.duckdb)
    console.info("Pyodide and DuckDB loaded");
    return;
});
self.onmessage = async (event) => {
    // make sure loading is done
    await DBandPyodideReadyPromise;

    const { request_id, code_to_run, ...context } = event.data;
    const pyodide = self.pyodide;

    const result = await pyodide.runPythonAsync(code_to_run, context);
    self.postMessage({ request_id, result });
};
